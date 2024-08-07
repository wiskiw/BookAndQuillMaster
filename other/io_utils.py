import json
import os

import json5

from model.text_unit import TextUnit


def export_text_unit(file_path: str, text_unit: TextUnit):
    unit_dict = text_unit.get_dict()
    save_json5(file_path, unit_dict)


def save_json5(file_path: str, json_data: any):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json5.dump(json_data, file, ensure_ascii=False, indent=4)


def write_json(file_path: str, json_data: any):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)


def read_file(file_path: str):
    with open(file_path, 'r') as file:
        text_content = file.read()
        return str(text_content)


def write_file(file_path: str, content: str):
    f = open(file_path, "w")
    f.write(content)
    f.close()
