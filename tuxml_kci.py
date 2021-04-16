import argparse
import calendar
import subprocess
import tarfile
import time
import urllib.request
import glob
import tempfile
import shutil
import os
from os import path
from kernelci import build, shell_cmd, print_flush
from kernelci.config.build import BuildEnvironment

###########################################################

kerBuild = "/kernel/build"
kv = "";
git_url = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tag/?h=v";

kernel_versions_path = "/shared_volume/kernel_versions"
base_path = "/tuxml-kci"

def parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--config",
        help="Use a config that you already have setup with yourconfig.config or randconfig to run with a random"
             "config.",
        default="randconfig",
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
        default="gcc6",
        nargs='?',
        required=True
    )

    parser.add_argument(
        "-a",
        "--arch",
        help="The architecture of the kernel, could be x86_64 or x86_32. Precise only with 32 or 64.",
        default="64",
        nargs="?",
        required=True
    )

    # marker 1 done (squelette du script avec argparse )
    return parser.parse_args()

def extract_kernel(kver):
    filename = kver + ".tar.xz"
    # create a temporary directory where the tarball will be extracted
    extract_dir = tempfile.mkdtemp()
    print('The created temporary directory is %s' % extract_dir)

    # Check if the kernel to extract is actually available
    if not (os.path.exists("{base_path}/{filename}".format(base_path=base_path, filename=filename))):
        tar = tarfile.open("{kvp}/{filename}".format(kvp=kernel_versions_path, filename=filename), "r:xz")
        print(f"Extracting {filename}.")
        tar.extractall(extract_dir)
        tar.close()
        print(f"{filename} has been extracted into {extract_dir}/linux-{kver}")
    extract_dir = f"{extract_dir}/linux-{kver}"
    # clean source code
    tmp_current = os.getcwd()
    os.chdir(f"{extract_dir}/kernel")
    print("Cleaning the source code . . .")
    subprocess.call("make distclean", shell=True)
    os.chdir(tmp_current)

    return extract_dir

def download_kernel(kver):
    filename = kver + ".tar.xz"

    # fetch the kernel version at this address
    url = "https://mirrors.edge.kernel.org/pub/linux/kernel/v%s.x/linux-%s" % (kver.strip('.')[0], filename)

    # Check if folder that will contain tarballs exists. If not then create it
    if not (os.path.exists(kernel_versions_path)):
        os.mkdir(kernel_versions_path)

    # If the tarball isn't available locally, then download it otherwise do nothing
    if not (os.path.exists("{}/{}".format(kernel_versions_path, filename))):
        print(f"{filename} is downloading.")
        urllib.request.urlretrieve(url, "{}/{}".format(kernel_versions_path, filename))
    else:
        print(f"{filename} already downladed.")



# The function that will build the kernel with the .config or a randconfig
# suppos that you  have already do the step 0, step1 and step2 of the how to build kernel with kernel_ci
# and import everything you have to import to use those command
def kernel(sources_path, install_path,output_path, arch=None):
    current = os.getcwd()

    if arch == "32":
        build_env = BuildEnvironment("build_config", "gcc", "8", "i386")
        build.build_kernel(build_env, sources_path + "/kernel", "i386", output_path=output_path)
        # subprocess.run(
        #   args="python3 kci_build build_kernel --build-env=gcc-8 --arch=i386 --kdir=" + current +
        #   "/kernel/ --verbose ", shell=True, check=True)
    else:
        build_env = BuildEnvironment("build_config", "gcc", "8", "x86_64")
        build.build_kernel(build_env, sources_path + "/kernel", "x86_64", output_path=output_path)
        # subprocess.run(
        #        args="python3 kci_build build_kernel --build-env=gcc-8 --arch=x86_64 --kdir=" + current +
        #        "/kernel/ --verbose ", shell=True, check=True
        # )

    print(f'End of Build.')

    # first version, need to change the tree-url and branch value I guess
    build.install_kernel(f"{sources_path}/kernel", kv,git_url, "master",output_path=output_path, install_path=install_path)
    # subprocess.run(
    #            args="python3 kci_build install_kernel --tree-name=%s --tree-url=%s --branch=master --kdir=%s/%s"
    #            %(kv, git_url, current, krnl), shell=True, check=True
    # )


if __name__ == "__main__":
    # Get line parameters
    args = vars(parser())
    config = args['config']
    kv = args['kernel_version']
    c = args['build_env']
    arch = args['arch']

    git_url = git_url + kv

    # Prepare path
    current_date = calendar.timegm(time.gmtime())
    output_folder = "/shared_volume/{b_env}_{arch}/{timestamp}_{kver}".format(b_env=c, arch=arch,timestamp=current_date, kver=kv)
    install_path = os.path.join(output_folder, '_install_')

    # Get and unzip kernel archive
    download_kernel(kv)
    extraction_path = extract_kernel(kv)

    # default configurations (we preset some options for randconfig and tinyconfig, since the architecture should be consistent)
    if config == 'tinyconfig' or config == 'randconfig' or config == 'defconfig':
        # enter in the kernel folder
        os.chdir(f"{extraction_path}")
        print("Trying to make " + config + " into " + os.getcwd())
        # create the config using facilities

        if arch == "32":
            subprocess.call('KCONFIG_ALLCONFIG=/tuxml-kci/x86_32.config make ' + config, shell=True)

        else:
            subprocess.call('KCONFIG_ALLCONFIG=/tuxml-kci/x86_64.config make ' + config, shell=True)

        # move .config into build directory
        subprocess.call("mkdir build", shell=True)
        subprocess.call(f'mv .config ./build', shell=True)
        # this step is actually important: it cleans all compiled files due to make rand|tiny|def config
        # otherwise kernel sources are not clean and kci complains 
        subprocess.call('make mrproper', shell=True)
        # back

    # .config given, move it into the /kernel/build/ directory
    else:
        path_config = os.getcwd()
        print(path_config)
        subprocess.call("mkdir ." + kerBuild, shell=True)
        subprocess.call("mv ../%s .%s/.config" % (config, f"{extraction_path}/build"), shell=True)
        os.chdir("./kernel")
        subprocess.call(f'make KCONFIG_ALLCONFIG=../build/.config allnoconfig', shell=True)
        subprocess.call(f'make KCONFIG_ALLCONFIG=../build/.config alldefconfig', shell=True)
        os.chdir("..")

    kernel(extraction_path,install_path,output_folder, arch)

    print(os.getcwd())
    # print the bmeta.json
    f = open(os.getcwd() + "/tuxml-kci" + kerBuild + "/bmeta.json", "r")
    print(f.read())

    shutil.rmtree(extraction_path)

    print_flush("Build of {b_env}_{arch} complete.".format(b_env=c,arch=arch))

# marker 5 done(on lance le build du kernel)

# reste a prendre les outputs
