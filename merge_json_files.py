import json
import os

def merge_json_files(model_names, instruction_num):
    input_files = [
        f'./outputs/{model}/instruction_{instruction_num}_result_on_{model}.json' for model in model_names
    ]
    output_file = f'./outputs/all_merge/instruction_{instruction_num}_result.json'

    merged_data = []

    for file_path in input_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.extend(data)
        else:
            print(f"File not found: {file_path}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    print(f"Merged data saved to {output_file}")



if __name__ == '__main__':
    model_names = ["Qwen2.5-7B-Instruct", "deepseek-llm-7b-chat", "glm-4-9b-chat", "Yi-1.5-9B-Chat"]
    for instruction_num in range(20, 34):
        merge_json_files(model_names, instruction_num)

