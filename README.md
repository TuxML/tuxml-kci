# Tuxml-kci

### A bridge with Kernel-CI

The tuxml_kci.py script is used to compile a linux kernel thanks to [kernel-ci](https://github.com/kernelci/kernelci-core). Part of kernelci’s job is to compile and install a kernel, gathering useful information on the fly for statistical purposes. We use their hard work to compare this data with that produced by Tuxml.

To compile and install a linux kernel, it is necessary to specify compilation parameters which are as follows:

* The architecture of the kernel

* Its compiler

* His version

* And its configuration.

However, to use the script, a suitable environment is also essential. Indeed, in order to be able to retrieve compilation
data such as the size of the produced kernel or its compilation time, the information must be grouped in a file whose 
location is known. This environment is prepared by kci_generator explained [here](https://github.com/TuxML/kci-builder). 
The shared_volume directory is in fact the results warehouse, and it is necessary that it be located at the root of the
system (hence the use of a container, in addition to its other advantages), moreover the library kernelci is required.

When the container is created and running, we can run our script there. You have to go to the tuxml_kci directory located
at the root. It contains the script and other files necessary for the program to run smoothly. When the script finishes 
executing, the results are located in a directory in the shared space, whose name depends on the parameters passed.

### Example
```
cd / tuxml-kci

python3 tuxml_kci.py -a x86_64 –b gcc-8 –k 5.9 -c tinyconfig
```
Or in a more explicit way:
```
python3 tuxml_kci.py --arch x86_64 –build_env gcc-8 --kernel_version 5.9 --config tinyconfig
```
###Results

The logs of the execution will therefore be displayed in the console and will also be available in the results. These results can be found in /shared_volume/gcc-8_x86_64/1618829975_5.9/_install_. Note that the names of the directories depend on the parameters and the date of the machine at runtime. In this folder we then find:

* Execution logs

* The configuration file used

* The image of the kernel

* His table of symbols

* And a JSON file

This last file named bmeta.json is the one that interests us the most, since it contains the information necessary to compare our results with Tuxml.
```
{
    "arch": "x86_64",
    "build_environment": "gcc-8",
    "build_log": "build.log",
    "build_platform": [
        "Linux",
        "localhost.localdomain",
        "5.3.7-301.fc31.x86_64",
        "#1 SMP Mon Oct 21 19:18:58 UTC 2019",
        "x86_64",
        "x86_64"
    ],
    "build_threads": 10,
    "build_time": 645.82,
    "compiler": "gcc",
    "compiler_version": "8",
    "compiler_version_full": "gcc (GCC) 9.2.1 20190827 (Red Hat 9.2.1-1)",
    "cross_compile": "",
    "defconfig": "none",
    "defconfig_full": "none",
    "status": "PASS",
    "vmlinux_bss_size": 1007616,
    "vmlinux_data_size": 1601984,
    "vmlinux_file_size": 59455512,
    "vmlinux_text_size": 14684375
}
```

At least, results obtained will be forwarded to the Tuxml database. See [tuxml-web](https://github.com/TuxML/tuxml-web).
### Update
 * The script allow the 4.x and 5.x versions of linux.
 