import json


dataset_path = 'outputs/Yi-1.5-9B-Chat/instruction_29_result_on_Yi-1.5-9B-Chat.json'

with open(dataset_path, 'r') as f:
    if dataset_path.endswith('.jsonl'):
        data = [json.loads(line) for line in f]
    else:
        data = json.load(f)
    print(f"all process {len(data)} datas")
