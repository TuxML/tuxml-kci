import argparse
import calendar
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import glob

import os
from os import path
from kernelci import build, shell_cmd, print_flush
from kernelci.config.build import BuildEnvironment

kerBuild = "/kernel/build"
krnl = "/kernel"
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
        help="The architecture of the kernel, can only be x86_64 or x86_32.",
        default="x86_64",
        nargs="?",
        required=True
    )

    # marker 1 done (squelette du script avec argparse )
    return parser.parse_args()


def download_kernel(args):
    argxz = args + ".tar.xz"  # it take the stable versions
    base_url = "https://mirrors.edge.kernel.org/pub/linux/kernel"

    # for kernel versions 5.x.x
    if args.startswith("5."):
        url = base_url + "/v5.x/linux-" + argxz
        # for kernel version 4.x.x
    else:
        url = base_url + "/v4.x/linux-" + argxz

    downloaded_filename = "/shared_volume/kernel_versions/" + argxz

    # downloaded_filename = argxz

    # create dir [kernel_versions] into shared volume if not exist
    if not (path.exists("/shared_volume/kernel_versions")):
        subprocess.call("mkdir /shared_volume/kernel_versions", shell=True)

        # if exist check, if downloaded_filename exists unpack else download
    if not (path.exists(downloaded_filename)):
        print(f"{downloaded_filename} is downloading.\n")
        urllib.request.urlretrieve(url, downloaded_filename)
    else:
        print(f"{downloaded_filename} already downladed.")

    dir_name = "linux-" + args
    if not (path.exists(dir_name)):
        fname = args + '.tar.xz'
        tar = tarfile.open("/shared_volume/kernel_versions/" + fname, "r:xz")
        print(f"Extracting {fname}.")
        tar.extractall()
        tar.close()
        print(f"{fname} has been extracted into {dir_name}")
    else:
        print(f"{dir_name} has been already extracted.")
    # TODO: use variable for "kernel" folder name
    # clean folder and sources
    if (path.exists(krnl)):
        subprocess.call("rm -r -f ./" + krnl, shell=True)
    subprocess.call(f"mv {dir_name} ./" + krnl, shell=True)
    os.chdir(krnl)
    print("Cleaning the source code . . .")
    subprocess.call("make distclean", shell=True)
    os.chdir("..")


# The function that will build the kernel with the .config or a randconfig
# suppos that you  have already do the step 0, step1 and step2 of the how to build kernel with kernel_ci
# and import everything you have to import to use those command
def kernel(config, arch=None):
    current = os.getcwd()

    if arch == "x86_32":
        build_env = BuildEnvironment("build_config", "gcc", "8", "i386")
        build.build_kernel(build_env, current + "/kernel/", "i386")
        # subprocess.run(
        #   args="python3 kci_build build_kernel --build-env=gcc-8 --arch=i386 --kdir=" + current +
        #   "/kernel/ --verbose ", shell=True, check=True)
    else:
        build_env = BuildEnvironment("build_config", "gcc", "8", arch)
        build.build_kernel(build_env, current + "/kernel/", arch)
        # subprocess.run(
        #        args="python3 kci_build build_kernel --build-env=gcc-8 --arch=x86_64 --kdir=" + current +
        #        "/kernel/ --verbose ", shell=True, check=True
        # )

    print(f'End of Build.')

    # first version, need to change the tree-url and branch value I guess
    build.install_kernel(current + "/" + krnl, kv, git_url, "master")
    # subprocess.run(
    #            args="python3 kci_build install_kernel --tree-name=%s --tree-url=%s --branch=master --kdir=%s/%s"
    #            %(kv, git_url, current, krnl), shell=True, check=True
    # )


if __name__ == "__main__":
    # Get line parameters
    args = vars(argparser())
    config = args['config']
    kv = args['kernel_version']
    c = args['build_env']
    arch = args['arch']

    git_url = git_url + kv

    # Get and unzip kernel archive
    if kv is not None:
        download_kernel(kv)
        current = os.getcwd()

    # default configurations (we preset some options for randconfig and tinyconfig, since the architecture should be consistent)
    if config == 'tinyconfig' or config == 'randconfig' or config == 'defconfig':
        # enter in the kernel folder
        os.chdir(krnl)
        print("Trying to make " + config + " into " + os.getcwd())
        # create the config using facilities

        if arch == "x86_32":
            subprocess.call('KCONFIG_ALLCONFIG=../x86_32.config make ' + config, shell=True)

        else:
            subprocess.call('KCONFIG_ALLCONFIG=../x86_64.config make ' + config, shell=True)

        # move .config into build directory
        subprocess.call("mkdir build", shell=True)
        subprocess.call('mv .config ./build', shell=True)
        # this step is actually important: it cleans all compiled files due to make rand|tiny|def config
        # otherwise kernel sources are not clean and kci complains 
        subprocess.call('make mrproper', shell=True)
        # back
        os.chdir("..")

    # .config given, move it into the /kernel/build/ directory
    else:
        path_config = os.getcwd()
        print(path_config)
        subprocess.call("mkdir ." + kerBuild, shell=True)
        subprocess.call("mv ../%s .%s/.config" % (config, kerBuild), shell=True)
        os.chdir("./kernel")
        subprocess.call(f'make KCONFIG_ALLCONFIG=/build/.config allnoconfig', shell=True)
        subprocess.call(f'make KCONFIG_ALLCONFIG=/build/.config alldefconfig', shell=True)
        os.chdir("..")

    kernel(os.getcwd() + kerBuild + "/", arch)
    os.chdir("..")

    print(os.getcwd())
    # print the bmeta.json
    f = open(os.getcwd() + "/tuxml-kci" + kerBuild + "/bmeta.json", "r")
    print(f.read())

# marker 5 done(on lance le build du kernel)

# reste a prendre les outputs
    print_flush("Build of {b_env}_{arch} complete.".format(b_env=b_env, arch=arch))
