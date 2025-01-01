import json
import os


def purify_result(instruction_num):
    input_files = f'./outputs/all_merge/instruction_{instruction_num}_result.json'
    output_file = f'./outputs/all_purify/instruction_{instruction_num}_result.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(input_files, 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    errors = []  # 用于记录所有错误信息
    purify_data_list = []

    for line_num, data in enumerate(data_list, start=1):
        try:
            # check data
            assert isinstance(data, dict), "data 必须是一个字典"
            assert set(data.keys()) == {"类别", "输入", "输出"}, "data 的 key 必须且只能包括 '类别', '输入', '输出'"
            assert all(isinstance(value, str) for value in data.values()), "data 的所有 value 必须是字符串类型"
        except AssertionError as e:
            errors.append(str(e))
            continue

        purify_data_list.append(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(purify_data_list, f, ensure_ascii=False, indent=4)

    print('-' * 50)
    print(f"instruction_{instruction_num} 清洗完成")
    print("清洗前的数据数量:", len(data_list))
    print("错误信息数量:", len(errors))
    print("清洗后的数据数量:", len(purify_data_list))

if __name__ == '__main__':
    for instruction_num in range(20, 34):
        purify_result(instruction_num)
