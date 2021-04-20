import argparse
import calendar
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import glob
import sys
import os
from os import path

sys.path.append("/kernelci-core/kernelci")
import build, config.build as c_build

kernel_versions_path = "/shared_volume/kernel_versions"
base_path = "/tuxml-kci"
git_url = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"


def argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--config",
        help="Use a config that you already have setup with your .config or randconfig to run with a random"
             "config.",
        default="tinyconfig",
        nargs='?',
        required=True
    )

    parser.add_argument(
        "-k",
        "--kernel_version",
        help="The kernel version to use",
        nargs='?',
        required=True
    )

    parser.add_argument(
        "-b",
        "--build_env",
        help="Specify the version of gcc compiler.",
        default="gcc-8",
        nargs='?',
        required=True
    )

    parser.add_argument(
        "-a",
        "--arch",
        help="The architecture of the kernel, could be x86_64 or x86_32. Precise only with 32 or 64.",
        default="x86_64",
        nargs="?",
        required=True
    )

    # marker 1 done (squelette du script avec argparse )
    return parser.parse_args()


def download_extract_kernel(kver):

    filename = kver + ".tar.xz"
    url = "https://mirrors.edge.kernel.org/pub/linux/kernel/v%s.x/linux-%s" % (kver.strip('.')[0], filename)
    extract_dir = tempfile.mkdtemp()
    print(f"Downloading {filename} into {extract_dir} . . .")
    result = build.pull_tarball(kdir=extract_dir,
                                url=url,
                                dest_filename=f"{kernel_versions_path}/{filename}",
                                retries=1,
                                delete=False)
    print(f"Download done.")
    return extract_dir+ f"/linux-{kver}" if result else None


def build_kci_kernel(kdir, arch,b_env, config=None, jopt=None,
                 verbose=True, output_path=None, mod_path=None):
    known_configs = ["tinyconfig", "defconfig", "randconfig"]
    os.chdir(kdir)

    build_env = c_build.BuildEnvironment("build_config",b_env[:3], b_env[4:])

    if config in known_configs:
        build.build_kernel(build_env=build_env, arch=arch, kdir=extraction_path, defconfig=config,
                           output_path=output_folder)
    else:
        os.mkdir(f"{output_path}")
        subprocess.call(f'make KCONFIG_ALLCONFIG={config} allnoconfig', shell=True)
        subprocess.call(f'make KCONFIG_ALLCONFIG={config} alldefconfig', shell=True)
        shutil.copy(f"{config}", f"{output_path}/.config")
        os.mkdir(f"{extraction_path}/build")
        shutil.copy(f"{config}", f"{extraction_path}/build/.config")
        # this step is actually important: it cleans all compiled files due to make rand|tiny|def config
        # otherwise kernel sources are not clean and kci complains
        subprocess.call('make mrproper', shell=True)
        build.build_kernel(build_env=build_env, arch=arch, kdir=extraction_path, defconfig=None,
                           output_path=output_folder)
    print(f"Build ended.")

    # first version, need to change the tree-url and branch value I guess
    install_path = os.path.join(output_folder, '_install_')
    build.install_kernel(kdir, "tree_name", git_url, "master", git_commit=git_url, describe="From Tuxml-Kci",
                         describe_v="Tuxml-Kci Repo", output_path=output_path, install_path=install_path)
    print("Install finished.")


if __name__ == "__main__":
    # Get line parameters
    args = argparser()
    config = args.config
    kver = args.kernel_version
    b_env = args.build_env
    arch = args.arch

    extraction_path = download_extract_kernel(kver)
    if not extraction_path:
        print("Download or extraction failed.")
        exit(-1)
    current_date = calendar.timegm(time.gmtime())
    output_folder = "/shared_volume/{b_env}_{arch}/{timestamp}_{kver}".format(b_env=b_env, arch=arch,
                                                                              timestamp=current_date, kver=kver)

    build_kci_kernel(arch=arch, kdir=extraction_path, config=config, output_path=output_folder,b_env=b_env)

    install_path = os.path.join(output_folder, '_install_')

    shutil.rmtree(extraction_path)

    build.print_flush("Build of {b_env}_{arch} complete.".format(b_env=b_env, arch=arch))

    os.chdir("/kernelci-core")
    f = open("config/core/lab-configs.yaml", "a")
    f.write(
    "\n"
    "  lab-local:\n"
    "    lab_type: lava\n"
    "    url: 'http://master1'\n"
    "    filters:\n"
    "      - passlist:\n"
    "          plan:\n"
    "            - baseline\n")
    f.close()
    bmeta_path = os.path.join(install_path, 'bmeta.json')
    dtbs_path = os.path.join(install_path, 'dtbs.json')
    job_path = os.path.join(install_path, 'job_docker.yaml')
    cmd_generate = f"python3 kci_test generate --bmeta-json={bmeta_path} --dtbs-json={dtbs_path} --plan=baseline_qemu --target=qemu_x86_64 --user=admin --lab-config=lab-local --lab-token=8ec4c0aeaf934ed1dce98cdda800c81c --storage=http://storage/ > {job_path}"
    os.system(cmd_generate)

    with open(job_path, "rt") as fp:
        content = fp.read()
        content = content.replace(f"http://storage/tree_name/master/From Tuxml-Kci/{arch}/{config}/build_config", f"http://storage/{output_folder}/_install_/")

    with open(job_path, "wt") as fp:
        fp.write(content)

    cmd_submit = f"python3 kci_test submit --user=admin --lab-config=lab-local --lab-token=8ec4c0aeaf934ed1dce98cdda800c81c --jobs={job_path}"
    os.system(cmd_submit)