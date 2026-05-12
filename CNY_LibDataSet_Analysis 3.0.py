import pandas as pd
import requests
import time
from tqdm import tqdm  # 用于显示进度条

# Poe API 配置
POE_API_URL = "https://api.poe.com/v1/chat/completions"
POE_API_KEY = "hZTKL-AFHKqE5vo6Uw2MoVOUlIlDbnCcgxZNj2N_z18"  # 替换为您的 Poe API 密钥

# 分段大小
BATCH_SIZE = 10  # 每次处理 10 条数据

# 从 API 响应中提取人名、地名和国家的函数
def parse_ai_response(response_text):
    chinese_name = ""
    english_name = ""
    chinese_location = ""
    english_location = ""
    country = ""

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
        elif line.startswith("國家："):
            country = line.replace("國家：", "").strip()

    return chinese_name, english_name, chinese_location, english_location, country

# 调用 API 的函数
def request_translation(prompt, headers):
    try:
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "你是一個專業的語言和地理數據解析助手，請幫助提取中英文人名、地名和地名所在的國家。"},
                {"role": "user", "content": prompt},
            ],
        }

        response = requests.post(POE_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")
            return ""

    except Exception as e:
        print(f"API 請求異常：{e}")
        return ""

# 处理每一段数据的函数
def process_batch(batch_df):
    headers = {
        "Authorization": f"Bearer {POE_API_KEY}",
        "Content-Type": "application/json",
    }

    results = []

    for _, row in tqdm(batch_df.iterrows(), total=len(batch_df), desc="Processing batch"):
        item_title = row["ItemTitle"]
        chs_for_searching = row["CHS_forSearching"]

        # 构建 API 输入内容
        input_text = f"""請從以下文本中提取人名和地名，並標註地名所在的國家：
        
        文本1：{item_title}
        文本2：{chs_for_searching}

        返回格式如下：
        繁體中文人名：...
        英文人名：...
        繁體中文地名：...
        英文地名：...
        國家：...
        """

        # 调用 API 并解析结果
        try:
            response_text = request_translation(input_text, headers)
            chinese_name, english_name, chinese_location, english_location, country = parse_ai_response(response_text)

            results.append({
                "itemTitle": item_title,
                "CHS_forSearching": chs_for_searching,
                "ChineseName": chinese_name,
                "EnglishName": english_name,
                "ChineseLocation": chinese_location,
                "EnglishLocation": english_location,
                "Country": country,
            })

        except Exception as e:
            print(f"處理失敗，錯誤：{e}")
            continue

        # 加入延迟，避免触发速率限制
        time.sleep(2)

    return results

# 主程序
if __name__ == "__main__":

    input_file = r"C:data for student.csv" # 替换为您的输入文件路径
    df = pd.read_csv(input_file)

    filtered_df = df[df["Type"].isin(["P", "M"])]


    total_batches = (len(filtered_df) + BATCH_SIZE - 1) // BATCH_SIZE  # 计算总批次数
    all_results = []

    for i in range(total_batches):
        start = i * BATCH_SIZE
        end = start + BATCH_SIZE
        batch_df = filtered_df.iloc[start:end]

        print(f"正在處理第 {i + 1}/{total_batches} 段數據...")
        batch_results = process_batch(batch_df)
        all_results.extend(batch_results)

        temp_output_file = f"temp_results_batch_{i + 1}.csv"
        pd.DataFrame(batch_results).to_csv(temp_output_file, index=False, encoding="utf-8-sig")
        print(f"第 {i + 1} 段數據處理完成，已保存到 {temp_output_file}")

    output_file = "final_cleaned_results.csv"
    pd.DataFrame(all_results).to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"所有批次數據處理完成，最終結果已保存到 {output_file}")