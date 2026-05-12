import pandas as pd
import requests
import time
from tqdm import tqdm  # 进度条

# Poe API 配置
POE_API_URL = "https://api.poe.com/v1/chat/completions"
POE_API_KEY = "hZTKL-AFHKqE5vo6Uw2MoVOUlIlDbnCcgxZNj2N_z18"  # 替换为您的 Poe API 密钥

# 分段处理的大小
BATCH_SIZE = 10  # 每段处理 10 条数据

# 解析 AI 返回结果的函数
def parse_ai_response(response_text):
    chinese_name = ""
    english_name = ""
    chinese_location = ""
    english_location = ""

    lines = response_text.split("\n")
    for line in lines:
        if line.startswith("繁體中文人名："):
            chinese_name = line.replace("繁體中文人名：", "").strip()
        elif line.startswith("英文人名："):
            english_name = line.replace("英文人名：", "").strip()
        elif line.startswith("繁體中文地名："):
            chinese_location = line.replace("繁體中文地名：", "").strip()
        elif line.startswith("英文地名："):
            english_location = line.replace("英文地名：", "").strip()

    return chinese_name, english_name, chinese_location, english_location

# 请求翻译的函数
def request_translation(prompt, headers):
    try:
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "你是一個翻譯助手，可以進行準確的繁體中文與英文翻譯。"},
                {"role": "user", "content": prompt},
            ],
        }

        response = requests.post(POE_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"翻譯請求失敗，狀態碼: {response.status_code}")
            return ""

    except Exception as e:
        print(f"翻譯請求異常：{e}")
        return ""

# 单段处理的函数
def process_batch(batch_df):
    headers = {
        "Authorization": f"Bearer {POE_API_KEY}",
        "Content-Type": "application/json",
    }

    results = []

    for _, row in tqdm(batch_df.iterrows(), total=len(batch_df), desc="Processing batch"):
        document_no = row["DocumentNo"]
        name = row["Name"] if not pd.isna(row["Name"]) else ""
        location = row["Location"] if not pd.isna(row["Location"]) else ""

        # 跳过噪声数据
        if name in ["未提及", "#NAME?"] or location in ["未提及", "#NAME?"]:
            continue

        input_text = f"""請提取以下文本中的人名和地名，並分別給出繁體中文和英文的結果：

        文本範例：
        Name: {name}
        Location: {location}

        請僅返回以下格式的結果（繁體中文和英文必須對應）：
        繁體中文人名：...
        英文人名：...
        繁體中文地名：...
        英文地名：...
        """

        try:
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "你是一個數據分析助手，幫助提取繁體中文人名、英文人名和地名。"},
                    {"role": "user", "content": input_text},
                ],
            }

            response = requests.post(POE_API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                api_result = response.json()["choices"][0]["message"]["content"]
                chinese_name, english_name, chinese_location, english_location = parse_ai_response(api_result)

                results.append({
                    "DocumentNo": document_no,
                    "ChineseName": chinese_name,
                    "EnglishName": english_name,
                    "ChineseLocation": chinese_location,
                    "EnglishLocation": english_location,
                })

            else:
                print(f"API 請求失敗 (DocumentNo: {document_no})，狀態碼: {response.status_code}")

        except Exception as e:
            print(f"API 調用異常 (DocumentNo: {document_no})，錯誤: {e}")

        time.sleep(2)  # 防止触发速率限制

    return results

# 主程序
if __name__ == "__main__":
    # 读取输入文件
    input_file = r"C:\Users\D3NG_\Desktop\extracted_results(1.0).csv" # 替换为您的输入文件路径
    df = pd.read_csv(input_file)

    # 分段处理
    total_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE  # 计算总批次数
    all_results = []

    for i in range(total_batches):
        start = i * BATCH_SIZE
        end = start + BATCH_SIZE
        batch_df = df.iloc[start:end]  # 获取当前段的数据

        print(f"正在处理第 {i + 1}/{total_batches} 段数据...")
        batch_results = process_batch(batch_df)  # 处理单段
        all_results.extend(batch_results)  # 合并结果

        # 保存当前段的临时结果
        temp_output_file = f"temp_results_batch_{i + 1}.csv"
        pd.DataFrame(batch_results).to_csv(temp_output_file, index=False, encoding="utf-8-sig")
        print(f"第 {i + 1} 段数据处理完成，已保存到 {temp_output_file}")

    # 保存所有结果
    output_file = "final_cleaned_results(2).csv"
    pd.DataFrame(all_results).to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"所有批次数据已处理完成，最终结果保存到 {output_file}")