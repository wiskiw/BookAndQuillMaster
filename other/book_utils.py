import shutil


def fill_up_raw_template(raw_template: str, args_dictionary):
    raw_content = raw_template
    for arg_key, arg_value in args_dictionary.items():
        raw_content = raw_content.replace(f"{{{{{arg_key}}}}}", str(arg_value))

    return raw_content


def move_to_bookcopy_dir(file_path, file_name):
    minecraft_folder = '/Users/wiskiw/Library/Application Support/PrismLauncher/instances/1.21 + Fabric Lite/.minecraft/config/bookcopy'
    destination_file_path = f"{minecraft_folder}/{file_name}"
    shutil.copy(file_path, destination_file_path)
    print(f"File copied to {destination_file_path}")
