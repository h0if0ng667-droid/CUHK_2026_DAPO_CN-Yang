import os

def find_file(filename, search_path):
    """
    递归搜索指定路径下的文件
    :param filename: 要查找的文件名
    :param search_path: 搜索起始路径
    :return: 文件完整路径，未找到返回None
    """
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

if __name__ == "__main__":
    # 输入要查找的文件名
    filename = input("请输入要查找的文件名（含扩展名）: ")

    # 搜索路径（从脚本所在目录开始）
    search_path = os.getcwd()  # 当前工作目录

    # 查找文件
    file_path = find_file(filename, search_path)

    if file_path:
        print(f"文件已找到! 文件路径为: {file_path}")
    else:
        print(f"未找到文件 {filename}，请确认文件是否存在。")