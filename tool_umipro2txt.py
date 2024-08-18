import os
import re
import shutil

# 定义源目录和目标目录
source_dir = 'story'
target_dir = 'story_umipro_cn'

# 括号类
BRACKET_replaces = {
    r"\{n\}": r"",  # 删除
    r"\{p:[0-9]+:(.*?)\}": r"<ln>{text}<rn>",  # 颜色字
    # r"<n>([…]+)<ln>": r"<ln>{text}",  # 颜色字外左标点
    r"<rn>([！？。ッ…]+)": r"{text}<rn>",  # 颜色字外右标点
    r"<[lr]n>": r"<n>",  # 颜色字外右标点
    r"\{t\}": r"<n>",  # 换行
    r"\{i:(.*?)\}": r"@{{{text}@}}", # 粗体
    r"<n>　": r"<n>",
    r"\{[abcefgmoy]:.*?:(.*?)\}": r"{text}",  # 其他特殊
    r"\{ruby:(.*?):(.*?)\}": r"@b{kanji}.@<{ruby}@>",  # ruby注音
}

OTHER_replaces = {
    r"\{[abcefgmoy]:.*?:(.*?)\}": r"\n{text}"  # 其他特殊
}

# 递归匹配与替换函数
def recursive_replace(text, patterns):
    # 先找最外层的括号，优先替换
    for pattern, replace in patterns.items():
        def replace_func(m):
            # 检查捕获组是否存在
            if m.groups():
                inner_text = m.group(1)
                replaced_inner_text = recursive_replace(inner_text, patterns)
            else:
                replaced_inner_text = ""
            
            if r"ruby" in replace:
                kanji, ruby = m.groups()
                return replace.format(kanji=kanji, ruby=ruby)
            elif r"text" in replace:
                return replace.format(text=replaced_inner_text)
            else:
                return replace

        # 使用正则表达式的替换函数处理
        text = re.sub(pattern, replace_func, text)
    
    return text


# 如果目标目录不存在，则创建它
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 遍历每个 ep 文件夹
for ep in range(1, 9):
    cn_folder = os.path.join(source_dir, f'ep{ep}', 'cn')
    
    # 确保 cn 文件夹存在
    if os.path.exists(cn_folder):
        # 遍历 cn 文件夹中的所有 .txt 文件
        for file_name in os.listdir(cn_folder):
            if file_name.endswith('.txt'):
                # 构建目标文件路径
                target_file = os.path.join(target_dir, file_name)

                # 如果目标文件已存在，则先删除它
                if os.path.exists(target_file):
                    os.remove(target_file)
                
                # 复制文件到目标目录
                source_file = os.path.join(cn_folder, file_name)
                shutil.copy(source_file, target_file)
                
                # 如果文件名以 _op.txt 结尾，则重命名为 _0.txt
                if target_file.endswith('op.txt'):
                    new_name = target_file.replace('op.txt', '0.txt')
                    # 如果目标文件名已经存在，则先删除它
                    if os.path.exists(new_name):
                        os.remove(new_name)
                    # 重命名文件
                    os.rename(target_file, new_name)
                    target_file = new_name

                # 删除每行左右两侧的反引号
                with open(target_file, 'r', encoding='utf-8') as f:
                    lines = [line.rstrip('\n') for line in f.readlines()]
                    lines = [line.strip('`') for line in lines]
                # 用唯一占位符将 lines 列表转换为一个单独的字符串
                placeholder = "<n>"
                combined_text = placeholder.join(lines)

                combined_text = recursive_replace(combined_text, BRACKET_replaces)      

                previous_combined_text = None
                while combined_text != previous_combined_text:
                    # 保存上一次的 combined_text
                    previous_combined_text = combined_text
                    # 处理 OTHER_replaces
                    for pattern, replace in OTHER_replaces.items():
                        combined_text = re.sub(pattern, lambda m: replace.format(text=m.group(1)) if len(m.groups()) > 0 else "", combined_text)       

                # 将处理后的字符串使用占位符分割回原来的行列表
                processed_lines = combined_text.split(placeholder)

                with open(target_file, 'w', encoding='utf-8') as f:
                    for line in processed_lines:
                        if line:  # 仅在行不为空时写入
                            f.write(line + '\n')


print("文件处理完成。")