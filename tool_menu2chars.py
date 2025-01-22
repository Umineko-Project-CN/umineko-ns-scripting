import os
import re

# 路径
root_dir = os.path.dirname(os.path.abspath(__file__))
menu_path = os.path.abspath(os.path.join(root_dir, r"script\cn\menu.txt"))  # menu路径
chars_path = os.path.abspath(os.path.join(root_dir, r"characters.txt"))
tips_path = os.path.abspath(os.path.join(root_dir, r"tips.txt"))

# 首尾行
chars_start_line = ";Char texts"
chars_end_line = ";bern quiz"

r_tips_start_line = ";Tips"
tips_start_line = ";Tips texts"
r_tips_end_line = tips_end_line = ";ep8"

# 匹配
BRACKET_replaces = {
    # 特殊排序
    r"chars_(.*?)_sak_": lambda m: rf"chars_{m.group(1)}_s99_", # 樱太郎
    r"chars_6_3_ama_1": r"chars_6_3_enj_99", # EP6天草
    r"(.*)chars_6_3_enj_2(.*)": r"", # EP6缘寿多余
    # 特殊标点
    r"，": r"ゞ",
    r"\.": r"–",
    # 符号替换
    r"\{n\}": r"@r", # 换行符
    r"\{fit\}": r"", # fit
    r"\{w:[0-9]+:}": r"", # 宽度
    r"\{ruby:(.*?):(.*?)\}": lambda m: rf"@b{m.group(1)}.@<{m.group(2)}@>", # 注音
    r"\{p:[0-9]+:(.*?)\}": lambda m: rf"{m.group(1)}", # 特殊字体
    r"\{c:FF0000:(.*?)\}": lambda m: rf"@c900{m.group(1)}@c.", # 红字
}

# 读取内容的匹配
chars_LINE_pattern = r'stralias chars_(.*?),":s;#FFFFFF`(.*?)@r@r(.*?)"'
r_tips_LINE_pattern = r'stralias r_tips_(.*?),":s;#C7C7C7#FFFFFF`(.*?)"'
tips_LINE_pattern = r'stralias tips_(.*?),":s;#FFFFFF`(.*?)"'

# 处理
def menu_parse(start_line, end_line, LINE_pattern):
    # 读取文件内容
    with open(menu_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # 提取开始和结束行之间的内容
    start_index = next((i for i, line in enumerate(content) if line.strip() == start_line), None)
    end_index = next((i for i, line in enumerate(content[start_index + 1:], start=start_index + 1) 
                      if line.strip() == end_line), None)

    if start_index is None or end_index is None or start_index >= end_index:
        raise ValueError("首尾行匹配错误。")

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
        if match and match.lastindex == 3:
            num = match.group(1)
            name = match.group(2)
            desc = match.group(3)
            lines.append([num, rf"'{name}', '{desc}'"])
        elif match and match.lastindex == 2:
            desc = match.group(2)
            lines.append(desc)
    return lines

# 排序（按num字段的自然顺序）
def natural_key(item):
    def sort_key(c):
        if c.isdigit():
            return (1, int(c))  # 数字排序
        else:
            return (0, c)  # 字母排序
    
    return [sort_key(c) for c in item[0]]

# 开始处理
chars_lines = menu_parse(chars_start_line, chars_end_line, chars_LINE_pattern)
chars_lines.sort(key=natural_key)

r_tips_lines = menu_parse(r_tips_start_line, r_tips_end_line, r_tips_LINE_pattern)
tips_lines = menu_parse(tips_start_line, tips_end_line, tips_LINE_pattern)
tips_lines = list(zip(r_tips_lines, tips_lines))

# 保存到文件
with open(chars_path, 'w', encoding='utf-8') as output_file:
    for _, line in chars_lines:
        output_file.write(f"{line}\n")
# with open(tips_path, 'w', encoding='utf-8') as output_file:
#     for a, b in tips_lines:
#         output_file.write(f"'{a}', '{b}'\n")

print(f"已保存。")
