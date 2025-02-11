import os
import sys

# 解决路径问题
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_txt_files_with_lines(folder):
    txt_files_lines = {}
    # 遍历文件夹及其子文件夹
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".txt"):
                # 获取相对路径
                relative_path = os.path.relpath(os.path.join(root, file), folder)
                # 读取文件行数
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                # 记录相对路径及其行数
                txt_files_lines[relative_path] = line_count
    return txt_files_lines

def compare_folders(folder1, folder2):
    folder1_files = get_txt_files_with_lines(folder1)
    folder2_files = get_txt_files_with_lines(folder2)

    # 查找两个文件夹中相同的文件名并比较行数
    for file in folder1_files:
        # 文件名在两个文件夹中是否存在
        if file in folder2_files:
            lines1 = folder1_files[file]
            lines2 = folder2_files[file]
            if lines1 != lines2:
                print(f"文件 {file} 的行数不一致: NS = {lines1}, CN = {lines2}")

# 示例使用
folder1 = 'story_ns'
folder2 = 'story_cn'
compare_folders(folder1, folder2)
