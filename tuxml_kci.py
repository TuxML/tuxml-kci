#!usr/bin/env python

import argparse 
import subprocess
import tarfile
import urllib.request
from pygments.lexers import make
import os





###########################################################
def parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        help ="Use a config that you already have setup with yourconfig.config or randconfig to run with a random"
        "config.",
        default ="randconfig",
        nargs = '?'
    )

    parser.add_argument(
        "--kernel_version",
        help="The kernel version to use",
        nargs='?'
    )
        
    parser.add_argument(
        "--compiler",
        help="Specify the version of gcc compiler.",
        default ="gcc6",
        nargs = '?'
    )
 # marker 1 done (squelette du script avec argparse )
    return parser.parse_args()


def download_kernel(args):
        url = "https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-" + args + ".tar.xz" 
        downloaded_filename = args + '.tar.xz'
        urllib.request.urlretrieve(url, downloaded_filename)

        fname = args + '.tar.xz' 

        if fname.endswith("tar.xz"):
            tar = tarfile.open(fname, "r:xz")
            tar.extractall()
            tar.close()
            subprocess.call("mv linux-"+args+ " kernel", shell = True)

#The function that will build the kernel with the .config or a randconfig
#suppos that you  have already do the step 0, step1 and step2 of the how to build kernel with kernel_ci
#and import everything you have to import to use those command
def kernel(config):
    current = os.getcwd()
    print(current)
    os.chdir("../kernelci-core")
    print(os.getcwd()+"\n")
    subprocess.run(args="python3 kci_build build_kernel --arch=x86_64 --build-env=gcc-8 --kdir="+current+"/kernel/ --verbose", shell=True, check=True)

if __name__ == "__main__":
    args = parser()
    config = args.config
    kv=args.kernel_version
    c=args.compiler
    
    if kv is not None:
        download_kernel(kv)
#marker 2 done (telecharger et decompresser mon archive kernel dans mon path courant)

    subprocess.call('mkdir build', shell=True)

    if config == 'randconfig':
        current = os.getcwd()
        os.chdir("kernel")
        subprocess.call('make randconfig', shell=True)
        subprocess.call('mv .config ./build', shell=True)
        config = ".config"
        os.chdir(current)

#marker 3 done(générer un randconfig si pas de .config passer sinon le .config reste dans config)
    else : 
        path_config = os.getcwd()
        subprocess.call("mv "+path_config+"/"+config +" ./kernel/build", shell=True)
    print(config)
    kernel(config)
 
#marker 5 done(on lance le build du kernel)

#reste a prendre les outputs
