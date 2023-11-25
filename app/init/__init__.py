import json
import os

from app.core.config import OPEN_API_KEY


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
                elif isinstance(value, bool):
                    line.append(f'{key}: {value}')
                else:
                    line.append(str(value).replace('\n', ' '))
            f.write(','.join(line) + '\n')


os.environ["OPENAI_API_KEY"] = OPEN_API_KEY
handle_json_file('app/resources/data.json', 'app/resources/data_processed.txt')