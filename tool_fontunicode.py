import os
import re
import unicodedata
from itertools import chain

# 指定路径
script_path = ''  # 可选
story_path = 'story_cn'
output_path = 'catbox/replace_chars.txt'
# 不属于GB2312、Shift-JIS范围的汉字
add_set = ['呣', '呴', '咘', '咜', '哱', '唦', '唭', '啨', '啰', '喼', '嗙', '嗞', '嗰', '嘡', '瘆', '祂', '觍']

# 读取文件
def read_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 读取字符
def read_characters(file_paths):
    unique_chars = set()
    for path in file_paths:
        text = read_text(path)
        unique_chars.update(text)
    return sorted(list(unique_chars))

# 过滤为汉字
def filter_chinese(char_list):
    chinese_characters = [char for char in char_list if re.match(r'^[\u4e00-\u9fa5]$', char)]
    return chinese_characters

# 生成GB2312、Shift-JIS、Big5、（GBK）字符集
def chars_set(mode):
    # 非中文字符
    nonchinese_chars = set()
    for code in range(0x0000, 0x10FFFF + 1):  # Unicode 全范围
        char = chr(code)
        try:
            # 检查字符是否是 CJK UNIFIED IDEOGRAPH
            if not unicodedata.name(char).startswith("CJK UNIFIED IDEOGRAPH"):
                nonchinese_chars.add(char)
        except ValueError:
            # 忽略没有名字的字符
            nonchinese_chars.add(char)

    # GB2312范围：第一字节0xA1 - 0xF7，第二字节0xA1 - 0xFE
    gb2312_chars = set()
    for lead in range(0xA1, 0xF7 + 1):
        for trail in range(0xA1, 0xFE + 1):
            try:
                char = bytes([lead, trail]).decode('gb2312')
                gb2312_chars.add(char)
            except UnicodeDecodeError:
                continue

    # Shift-JIS范围：第一字节0x81 - 0x9F, 0xE0 - 0xEF，第二字节0x40 - 0x7E, 0x80 - 0xFC
    shiftjis_chars = set()
    for lead in chain(range(0x81, 0x9F + 1), range(0xE0, 0xEF + 1)):
        for trail in chain(range(0x40, 0x7E + 1), range(0x80, 0xFC + 1)):
            if trail == 0x7F:
                continue
            try:
                char = bytes([lead, trail]).decode('shift-jis')
                shiftjis_chars.add(char)
            except UnicodeDecodeError:
                continue
    for lead in range(0xF0, 0xFC + 1):
        for trail in chain(range(0x40, 0x7E + 1), range(0x80, 0xFC + 1)):
            if trail == 0x7F:
                continue
            try:
                char = bytes([lead, trail]).decode('shift-jis')
                shiftjis_chars.add(char)
            except UnicodeDecodeError:
                continue
    
    # Big5范围：第一字节0xA1 - 0xF9，第二字节0x40 - 0x7E, 0xA1 - 0xFE
    big5_chars = set()
    for lead in range(0xA1, 0xF9 + 1):
        for trail in chain(range(0x40, 0x7F), range(0xA1, 0xFE + 1)):
            try:
                char = bytes([lead, trail]).decode("big5")
                big5_chars.add(char)
            except UnicodeDecodeError:
                continue

    # GBK范围：第一字节0x81 - 0xFE，第二字节0x40 - 0xFE
    gbk_chars = set()
    for lead in range(0x81, 0xFE + 1):
        for trail in range(0x40, 0xFE + 1):
            if trail == 0x7F:  # 跳过无效组合
                continue
            try:
                char = bytes([lead, trail]).decode("gbk")
                gbk_chars.add(char)
            except UnicodeDecodeError:
                continue

    charset = gb2312_chars.union(shiftjis_chars).union(nonchinese_chars)
    if mode == 1:
        return sorted(list(charset))
    elif mode == 2:
        return sorted(list(gbk_chars - shiftjis_chars))

# unicode转十进制
def unicode_10(string_list):
    result = []
    for string in string_list:
        result.extend([ord(char) for char in string])
    return result


mode = int(input("请选择模式 (1: 根据字符集得出多余汉字 , 2: 导出replace_chars)："))
# 得到对应模式的字符集
text_set = chars_set(mode)

if mode == 1:
    # 获取所有文件路径
    file_paths = []
    try:
        try_path = script_path
        if os.path.exists(try_path):
            file_paths.append(try_path)
    except NameError:
        pass
    file_paths.extend([os.path.join(story_path, file) for file in os.listdir(story_path) if file.endswith('.txt')])

    # 读取所有文本中的字符
    text = read_characters(file_paths)
    # 过滤出仅包含汉字的列表
    text = filter_chinese(text)
    text_set = filter_chinese(text_set)
    # 找出text中存在但text_set中不存在的字符
    extra_chars = sorted(set(text) - set(text_set))
    extra_uni = unicode_10(extra_chars)

    # print超出范围的汉字
    print(f"超出范围的汉字:\n{''.join(extra_chars)}")
    print(" ".join(map(str, extra_uni)))
    print(f"add_set = {extra_chars}" )

elif mode == 2:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # 保存到文件
    with open(output_path, "w", encoding="utf-8") as file:
        for item in text_set:
            file.write(item + "\n")