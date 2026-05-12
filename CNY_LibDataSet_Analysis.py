import pandas as pd
import asyncio
import httpx
from tqdm import tqdm

# 替换为你的 Poe API Token
POE_API_TOKEN = "pzUvzMCxxnefhJVDxuc9ia0XNGeyGOB2viVKiQnDEYk"

# 输入和输出文件路径
input_file = r"C:\Users\D3NG_\Desktop\ultimate_ultimate_ultimate_result.csv" # 替换为你的输入文件路径
output_file = "6657yang_zhengning_analysis_output.csv"  # 替换为你的输出文件路径

# Poe API 调用函数
async def query_poe(prompt):
    """
    调用 Poe 平台的 API，发送消息并获取响应。
    """
    url = "https://api.poe.com/v1"  # 确保替换为正确的 URL
    headers = {
        "Authorization": f"Bearer {POE_API_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    payload = {
        "bot": "gpt-5.2-pro",  # 指定使用的模型，例如 ChatGPT
        "message": prompt  # 你的提示词
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()  # 如果 HTTP 响应码不是 2xx，会抛出异常
            return response.json()  # 返回 JSON 格式的响应
    except httpx.HTTPStatusError as e:
        print(f"HTTP 错误: {e.response.status_code}, 响应内容: {e.response.text}")
    except Exception as e:
        print(f"调用 Poe 出错：{e}")
    return None

# 调用 Poe 获取信息
async def get_info_from_poe(item_title, chs_forsearching):
    """
    构造提示词并调用 Poe API 提取中英文人名和地名。
    """
    prompt = (
        f"以下是一段文档的部分内容：\n"
        f"标题: {item_title}\n"
        f"研究描述: {chs_forsearching}\n\n"
        f"请提取以下信息，并确保内容与著名物理学家杨振宁相关：\n"
        f"1. 中文名\n"
        f"2. 英文名\n"
        f"3. 中文地点\n"
        f"4. 英文地点\n\n"
        f"如果上下文中没有明确提到杨振宁，请根据相关描述进行推理。\n\n"
        f"请以 JSON 格式返回结果，例如：\n"
        f"{{'ChineseName': '杨振宁', 'EnglishName': 'Chen-Ning Yang', 'ChineseLocation': '合肥', 'EnglishLocation': 'Hefei'}}。"
    )

    result = await query_poe(prompt)
    if result:
        return result.get("data")  # 根据 Poe 返回的接口字段提取数据
    return None

# 分析和处理数据
async def process_data(df):
    """
    主函数：处理数据，筛选杨振宁相关记录，并补全缺失值。
    """
    analyzed_rows = []

    # 遍历数据，逐行分析
    with tqdm(total=len(df), desc="处理中", ncols=100) as pbar:
        for _, row in df.iterrows():
            item_title = row.get("itemtitle", "")
            chs_forsearching = row.get("chs_forsearching", "")
            chinesename = row.get("chinesename", "")
            englishname = row.get("englishname", "")
            chineselocation = row.get("chineselocation", "")
            englishlocation = row.get("englishlocation", "")

            # 检查是否与杨振宁相关
            if "杨振宁" in item_title or "Chen-Ning Yang" in item_title or "杨振宁" in chs_forsearching:
                # 如果任何字段缺失，调用 Poe 补全
                if not chinesename or not englishname or not chineselocation or not englishlocation:
                    result = await get_info_from_poe(item_title, chs_forsearching) or {}
                    chinesename = result.get("ChineseName", chinesename)
                    englishname = result.get("EnglishName", englishname)
                    chineselocation = result.get("ChineseLocation", chineselocation)
                    englishlocation = result.get("EnglishLocation", englishlocation)

                # 添加分析后的记录
                analyzed_rows.append({
                    "documentno": row.get("documentno", ""),
                    "itemtitle": item_title,
                    "chs_forsearching": chs_forsearching,
                    "chinesename": chinesename,
                    "englishname": englishname,
                    "chineselocation": chineselocation,
                    "englishlocation": englishlocation
                })
            else:
                # 如果未直接提及杨振宁，但可能相关，尝试使用 Poe 推断
                result = await get_info_from_poe(item_title, chs_forsearching) or {}
                if "杨振宁" in result.get("ChineseName", "") or "Chen-Ning Yang" in result.get("EnglishName", ""):
                    analyzed_rows.append({
                        "documentno": row.get("documentno", ""),
                        "itemtitle": item_title,
                        "chs_forsearching": chs_forsearching,
                        "chinesename": result.get("ChineseName", chinesename),
                        "englishname": result.get("EnglishName", englishname),
                        "chineselocation": result.get("ChineseLocation", chineselocation),
                        "englishlocation": result.get("EnglishLocation", englishlocation)
                    })

            pbar.update(1)

    # 返回分析后的 DataFrame
    return pd.DataFrame(analyzed_rows)

# 保存数据
def save_data(df, file_path):
    """
    保存更新后的 DataFrame 到 CSV 文件。
    """
    try:
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"文件已成功保存到 {file_path}")
    except Exception as e:
        print(f"保存文件失败：{e}")

# 加载数据
def load_data(file_path):
    """
    加载 CSV 文件。
    """
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        df.columns = df.columns.str.strip().str.lower()  # 标准化列名
        return df
    except Exception as e:
        print(f"加载文件失败：{e}")
        raise

# 主程序入口
if __name__ == "__main__":
    # 加载数据
    data = load_data(input_file)

    # 异步运行数据处理
    analyzed_data = asyncio.run(process_data(data))

    # 保存分析后的数据
    save_data(analyzed_data, output_file)