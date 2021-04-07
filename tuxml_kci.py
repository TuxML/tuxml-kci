#!usr/bin/env python

import argparse
import json
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import calendar
import time
import os
import shutil
import stat
import platform
import fnmatch

import elftools.elf.constants as elfconst
import elftools.elf.elffile as elffile
import io

import kernelci.elf
from  kernelci import build,shell_cmd, print_flush
from  kernelci.config.build import BuildEnvironment

git_url = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tag/?h=v";
build_config="./shared_volume/configs/build-configs.yaml"


# sys.path.append(os.path.abspath("/kernelci-core"))
# import kernelci.build as kci_build
# import kernelci.config.build as kci_build_config
kernel_versions_path = "/shared_volume/kernel_versions"
base_path = "/tuxml-kci"

# Hard-coded make targets for each CPU architecture
MAKE_TARGETS = {
    'arm': 'zImage',
    'arm64': 'Image',
    'arc': 'uImage',
}

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
    return extract_dir

if __name__ == "__main__":
    # Get line parameters
    args = argparser()
    config = args.config
    kver = args.kernel_version
    b_env = args.build_env
    arch = args.arch

    download_kernel(kver)
    extraction_path = extract_kernel(kver)


    current_date = calendar.timegm(time.gmtime())
    output_folder = "/shared_volume/{b_env}_{arch}/{timestamp}_{kver}".format(b_env=b_env, arch=arch, timestamp=current_date, kver=kver)
    # for gcc-8 => b_env[:-2]-> gcc ,b_env[4:]-> 8
    build_env = BuildEnvironment("build_config",b_env[:-2],b_env[4:])
    build.build_kernel(build_env,extraction_path,arch)
    #build.build_kernel(b_env=b_env, arch=arch, kdir=extraction_path, defconfig=config, output_path=output_folder)

    install_path = os.path.join(output_folder, '_install_')

    build.install_kernel(install_path,kver,git_url,"master")
    #build.install_kernel(kdir=extraction_path, output_path=output_folder, install_path=install_path)

    shutil.rmtree(extraction_path)

    print_flush("Build of {b_env}_{arch} complete.".format(b_env=b_env,arch=arch))