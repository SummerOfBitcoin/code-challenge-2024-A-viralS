import json
import os

def read_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        json.dump(content, file)

def file_exists(file_path):
    return os.path.exists(file_path)
