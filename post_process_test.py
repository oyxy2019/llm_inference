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


def post_process2(item):
    # 查找 "输出": 的位置
    idx1 = item.find('"输出":"') + len('"输出":"')
    if idx1 == -1:
        print("未找到 '\"输出\":\"'，无需处理")
        return item
    # 查找字符串最后一个双引号的位置
    idx2 = item.rfind('"')
    if idx2 == -1 or idx2 <= idx1:
        print("未找到合适的结尾双引号，无法处理")
        return item
    # 对双引号添加转义
    output_content = item[idx1:idx2]
    escaped_output_content = output_content.replace('"', '\\"')
    processed_item = item[:idx1] + escaped_output_content + item[idx2:]
    return processed_item


error_list_path = "./outputs/instruction_20_error_list.json"

with open(error_list_path, "r", encoding="utf-8") as file:
    error_list = json.load(file)

for item in error_list:
    item_new = post_process2(item)
    print("item0", repr(item))
    print("item1", repr(item_new))
    result, is_success = try_parse_json(item_new, attempt=1)
    if is_success:
        print("解析成功！！！")
    else:
        print()
