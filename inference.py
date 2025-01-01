"""
author: oyxy2019

准备工作：
1.先用hf-mirror下载大模型

2.再用vllm启动本地大模型服务：
vllm serve Qwen2.5-7B-Instruct --gpu_memory_utilization 0.9 --max_model_len 8000
"""
import os
import json
import re


os.environ['OPENAI_API_KEY'] = "EMPTY"
os.environ['OPENAI_API_BASE'] = "http://localhost:8000/v1"
model_name = "Qwen2.5-7B-Instruct"
model_name = "deepseek-llm-7b-chat"
model_name = "glm-4-9b-chat"
# model_name = "Yi-1.5-9B-Chat"
from models import gpt
from send_email_utils import send_email


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompts = json.load(file)

    # 将100条变为1条
    prompts = [re.sub(r"帮我生成\d+条高质量的指令微调数据", "帮我生成1条高质量的指令微调数据", prompt) for prompt in prompts]

    # 增加一些关键词
    add_info = "\n输出的字数不超过500字，确保只生成一条数据，不要生成多条数据。以'{'开始，以'}'结束，确保生成的数据可以被json.loads()成功解析。"
    new_prompts = [prompt+add_info for prompt in prompts]
    return new_prompts


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


def main(file_name="instruction_12"):
    # 设置路径
    file_path = f'./instructions/{file_name}.json'
    output_path = f'./outputs/{model_name}/{file_name}_result_on_{model_name}.json'
    raw_outputs_path = f'./outputs/{file_name}_raw_outputs.json'
    error_list_path = f'./outputs/{file_name}_error_list.json'

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prompts = read_file(file_path)

    # 生成输出
    outputs = []
    for i, prompt in enumerate(prompts):
        print("generating output for prompt", i)
        output_list = gpt(prompt, model=model_name, max_tokens=1000, n=120)  # 先设置小一点测试，跑通后再改为100
        outputs.extend(output_list)

    # 保存原始输出
    # with open(raw_outputs_path, "w", encoding="utf-8") as file:
    #     json.dump(outputs, file, ensure_ascii=False, indent=4)

    # 解析输出
    parsed_results = []
    error_count = 0
    error_list = []
    for item in outputs:
        # 第一次尝试解析
        result, is_success = try_parse_json(item, attempt=1)

        # 如果解析失败，进行后处理
        if not is_success:
            item_new = post_process(item)
            result, is_success = try_parse_json(item_new, attempt=2)

        # 如果解析失败，进行第二次后处理
        if not is_success:
            item_new = post_process2(item_new)
            result, is_success = try_parse_json(item_new, attempt=3)

        # 如果所有解析都失败，将错误数据保存到 error_list
        if not is_success:
            result = {
                "类别": "错误数据",
                "输入": "None",
                "输出": "None"
            }
            error_count += 1
            error_list.append(item)

        # 将结果保存到 parsed_results
        if is_success:
            parsed_results.append(result)

    # 保存解析结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_results, f, indent=4, ensure_ascii=False)
    print(f"Parsed results saved to {output_path}")

    # 保存错误数据
    with open(error_list_path, "w", encoding="utf-8") as file:
        json.dump(error_list, file, ensure_ascii=False, indent=4)

    send_email(f"{file_name}运行完成，错误数量：{error_count}")


if __name__ == '__main__':
    # 测试接口
    # prompt = "你好！能为我介绍一下Python编程语言吗？"
    # output = gpt(prompt, model=model_name, n=5)
    # print(output)

    for i in range(20, 34):
    # for i in [20]:
        main(f"instruction_{i}")
