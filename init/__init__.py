import json
import os


def handle_json_file(file_path_input, file_path_output: str):
    with open(file_path_input) as f:
        data = json.load(f)
    items = data['data']
    with open(file_path_output, 'w') as f:
        for item in items:
            line = [f'id: {item["item_id"]}']
            for key, value in item.items():
                if key == 'id':
                    continue
                if value is None or value == '':
                    continue
                line.append(f"{key}: {str(value)} ")
            f.write(','.join(line).replace('\n', '') + '\n')


def check_an_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


