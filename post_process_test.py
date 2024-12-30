import json
import re


def try_parse_json(item, attempt):
    try:
        return json.loads(item, strict=False), True
    except json.JSONDecodeError as e:
        print(f"第 {attempt} 次解析出错:", end="")
        print(f"解析出错的字符串: {repr(item)}")
        print(f"错误信息: {e}")
        return None, False


def post_process(item):
    if not item.endswith('\"\n}'):
        # 从后往前找到第一个非特殊符号的索引位置
        for i in range(len(item) - 1, -1, -1):
            if item[i] not in {'\"', '}', '\n', '\\', ' ', '`'}:
                item = item[:i + 1]  # 截取
                break
        # 加上 `\"\n}`
        item += '\"\n}'
    return item


error_list_path = "./outputs/instruction_15_error_list.json"

with open(error_list_path, "r", encoding="utf-8") as file:
    error_list = json.load(file)

for item in error_list:
    item_new = post_process(item)
    print("item0", repr(item))
    print("item1", repr(item_new))
    result, is_success = try_parse_json(item_new, attempt=1)
    if is_success:
        print("解析成功！！！")
