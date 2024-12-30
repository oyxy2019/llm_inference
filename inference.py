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
from models import gpt
from send_email_utils import send_email


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompts = json.load(file)

    # 将100条变为1条
    prompts = [prompt.replace("帮我生成100条高质量的指令微调数据", "帮我生成1条高质量的指令微调数据") for prompt in prompts]

    # 增加一些关键词
    add_info = "\n输出的字数不超过500字，确保只生成一条数据，不要生成多条数据。以'{'开始，以'}'结束，确保生成的数据可以被json.loads()成功解析。"
    new_prompts = [prompt+add_info for prompt in prompts]
    return new_prompts


def main(file_name="instruction_12"):
    # 设置路径
    file_path = f'./instructions/{file_name}.json'
    output_path = f'./outputs/{file_name}_result.json'
    raw_outputs_path = f'./outputs/{file_name}_raw_outputs.json'
    error_list_path = f'./outputs/{file_name}_error_list.json'

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prompts = read_file(file_path)

    # 生成输出
    outputs = []
    for i, prompt in enumerate(prompts):
        print("generating output for prompt", i)
        output_list = gpt(prompt, model=model_name, max_tokens=1000, n=100)  # 先设置小一点测试，跑通后再改为100
        outputs.extend(output_list)

    # 保存原始输出
    # with open(raw_outputs_path, "w", encoding="utf-8") as file:
    #     json.dump(outputs, file, ensure_ascii=False, indent=4)

    # 解析输出
    parsed_results = []
    error_count = 0
    error_list = []
    for item in outputs:
        # 对item进行后处理
        # item = item.replace("\r", "\\r").replace("\t", "\\t")
        # item = re.sub(r'[\x00-\x1f\x7f]', '', item)
        try:
            parsed_results.append(json.loads(item, strict=False))
        except json.JSONDecodeError as e:
            print(f"解析出错的字符串: {repr(item)}")
            print(f'错误信息: {e}')
            parsed_results.append({
                "类别": "错误数据",
                "输入": "None",
                "输出": "None"
            })
            error_count += 1
            error_list.append(item)

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
    # output = gpt(prompt, model="Qwen2.5-0.5B-Instruct", n=5)
    # print(output)

    for i in [12]:
        main(f"instruction_{i}")
