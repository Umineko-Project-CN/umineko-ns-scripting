import os
import re

# 路径
root_dir = os.path.dirname(os.path.abspath(__file__))
menu_path = os.path.abspath(os.path.join(root_dir, r"script\cn\menu.txt"))  # menu路径
chars_path = os.path.abspath(os.path.join(root_dir, r"characters.txt"))

# 首尾行
start_line = ";Char texts"
end_line = ";bern quiz"

# 匹配
BRACKET_replaces = {
    # 特殊排序
    r"chars_(.*?)_sak_": lambda m: rf"chars_{m.group(1)}_s99_", # 樱太郎
    r"chars_6_3_ama_1": r"chars_6_3_enj_99", # EP6天草
    r"(.*)chars_6_3_enj_2(.*)": r"", # EP6缘寿多余
    # 符号替换
    r"\.": r"\\.", # 点号
    r"\{n\}": r"@r", # 换行符
    r"\{fit\}": r"", # fit
    r"\{ruby:(.*?):(.*?)\}": lambda m: rf"@b{m.group(1)}.@<{m.group(2)}@>", # 注音
    r"\{p:3:(.*?)\}": lambda m: rf"{m.group(1)}", # 特殊字体
    r"\{c:FF0000:(.*?)\}": lambda m: rf"@c900{m.group(1)}@c.", # 红字
}
LINE_pattern = r'^.*?chars_(.*?),":s;#FFFFFF`.*?(.*?)@r@r(.*?)"'


# 读取文件内容
with open(menu_path, 'r', encoding='utf-8') as file:
    content = file.readlines()

# 提取开始和结束行之间的内容
start_index = next((i for i, line in enumerate(content) if line.strip() == start_line), None)
end_index = next((i for i, line in enumerate(content) if line.strip() == end_line), None)

if start_index is None or end_index is None or start_index >= end_index:
    raise ValueError("Invalid file structure: Unable to find the required start and end markers.")

# 提取内容（去掉头尾标记）
menu_text = content[start_index + 1:end_index]

# 应用替换规则
replaced_text = []
for line in menu_text:
    for pattern, replacement in BRACKET_replaces.items():
        if callable(replacement):
            line = re.sub(pattern, replacement, line)
        else:
            line = re.sub(pattern, replacement, line)
    replaced_text.append(line)

# 按行匹配正则表达式，提取所需字段
lines = []
for i, line in enumerate(replaced_text):
    match = re.match(LINE_pattern, line)
    if match:
        num = match.group(1)
        name = match.group(2)
        desc = match.group(3)
        lines.append([num, rf"'{name}', '{desc}'"])

# 排序（按num字段的自然顺序）
def natural_key(item):
    def sort_key(c):
        if c.isdigit():
            return (1, int(c))  # 数字排序
        else:
            return (0, c)  # 字母排序
    
    return [sort_key(c) for c in item[0]]
lines.sort(key=natural_key)

# 保存到文件
with open(chars_path, 'w', encoding='utf-8') as output_file:
    for _, line in lines:
        output_file.write(f"{line}\n")

print(f"已保存为'{chars_path}'.")
