import sys,os
from environment import get_environment_details
def json_generation(compilation_result1, compilation_result2, compilation_result3, compilation_result4, compilation_result5,
compilation_result6, compilation_result7, compilation_result8, compilation_result9, compilation_result10,
compilation_result11, compilation_result12, compilation_result13, compilation_result14 ,
compilation_result15, compilation_result16, compilation_result17, compilation_result18, compilation_result21 ,
compilation_result20, compilation_result22, compilation_result19, gcc_version, tiny, config_file, boot) :

    json_structure = {
        'cid' : 0,
        'compilation_date' : compilation_result1,
        'compilation_time' : compilation_result2,
        'compiled_kernel_size' : compilation_result3,
        'compiled_kernel_version' : compilation_result4,
        'dependencies' : compilation_result5,
        'number_cpu_core_used' : compilation_result6,
        'compressed_compiled_kernel_size' : compilation_result7,
        'stdout_log_file' : compilation_result8,
        'stderr_log_file' : compilation_result9,
        'user_output_file' : compilation_result10,
        'gcc_version' : gcc_version,
        'tiny' : tiny,
        'config_file' : config_file,
        'boot' : boot,
        'cpu_brand_name' : compilation_result11,
        'cpu_max_frequency' : compilation_result12,
        'ram_size' : compilation_result13,
        'architecture': compilation_result14,
        'number_cpu_core' : compilation_result15,
        'mechanical_disk' : compilation_result16,
        'libc_version' : compilation_result17,
        'tuxml_version' : compilation_result18,
        'system_kernel' : compilation_result19,
        'linux_distribution' : compilation_result20,
        'linux_distribution_version' : compilation_result21,
        'system_kernel_version' : compilation_result22
    }

    return json_structure


if __name__=='__main__':

    build_path = argv[1]
    env = get_environment_details()
    environmenthard = env['hardware']
    environmentsoft = env['software']

    json_data = json_generation(
                compilation_result1 = 0,
                compilation_result2 = 0,
                compilation_result3 = 0,
                compilation_result4 = 0,
                compilation_result5 = 0,

                compilation_result6 = 0,
                compilation_result7 = 0,

                compilation_result8 = open(os.path.join(build_path,"_install_/build.log"), "r").read(),
                compilation_result9 = 0,
                compilation_result10 = 0,
                gcc_version = environmentsoft["gcc_version"],
                tiny=0,
                config_file= open(os.path.join(build_path,"_install_/kernel.config").format(build_path), "r").read(),
                boot=0,
                compilation_result11 = environmenthard['cpu_brand_name'],
                compilation_result12 = environmenthard['cpu_max_frequency'],
                compilation_result13 = environmenthard['ram_size'],
                compilation_result14 = environmenthard['architecture'],
                compilation_result15 = environmenthard['number_cpu_core'],
                compilation_result16 = environmenthard['mechanical_disk'],

                compilation_result17 = environmentsoft['libc_version'],
                compilation_result18 = environmentsoft['tuxml_version'],
                compilation_result19 = environmentsoft['system_kernel'],
                compilation_result20 = environmentsoft['linux_distribution'],
                compilation_result21 = environmentsoft['linux_distribution_version'],
                compilation_result22 = environmentsoft['system_kernel_version'],
            )


