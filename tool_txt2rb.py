import os
import re

# 定义
jp_script_base = 'story_ns/umi'
cn_script_base = 'story_umipro_cn/umi'
start_line = 18467

SPACE_pattern = r"([ﾟﾞ♪☆](@[a-z|\[\]](\.)?)*)@"
SPACE_replace = r"{text}@"
HALFWIDTH = "｢｣ｧｨｩｪｫｬｭｮｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝｰｯ—､ﾟﾞ･｡`"
HALFWIDTH_REPLACE = "「」ぁぃぅぇぉゃゅょあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんーっ―、？！…。　'"
trans_table = str.maketrans(HALFWIDTH_REPLACE, HALFWIDTH)

# 读取并处理rb文件
with open('main.rb', 'r', encoding='utf-8') as f:
    target_script = f.read().splitlines()

# 输出的初始部分
output = '\n'.join(target_script[:start_line]) + '\n'
target_script = target_script[start_line:]

# 处理每个EP和章节
for ep in range(1, 9):
    print(f'Processing Episode {ep}')
    for chapter in range(101):
        script_jp = f'{jp_script_base}{ep}_{chapter}.txt'
        script_cn = f'{cn_script_base}{ep}_{chapter}.txt'
        if not os.path.exists(script_jp):
            break

        # 读取日文和中文的txt文件
        with open(script_jp, 'r', encoding='utf-8') as f:
            lines_jp = f.read().splitlines()
        with open(script_cn, 'r', encoding='utf-8') as f:
            lines_cn = f.read().splitlines()

        # 在 target_script 中查找章节的开始
        chapter_script = target_script[:]
        line_idx = next((i for i, x in enumerate(chapter_script) if x.startswith('s.ins 0xa0, byte(1), ')), -1) + 1
        chapter_script = chapter_script[:line_idx]
        chapter_script = '\n'.join(chapter_script)
        chapter_script = re.sub(SPACE_pattern, lambda m: SPACE_replace.format(text=m.group(1)), chapter_script)

        # 遍历日文txt的每一行
        for i in range(len(lines_jp)):
            if i < len(lines_cn) and lines_cn[i]:
                lines_jp[i] = lines_jp[i].translate(trans_table)
                lines_cn[i] = lines_cn[i].translate(trans_table)

                # 保存所有匹配方式的结果及其位置
                matches = []

                for fun in [lambda x: x + '@', lambda x: x + "'", lambda x: x.strip() + '@', lambda x: x.strip() + "'"]:
                    match = fun(lines_jp[i])
                    pos = chapter_script.find(match)
                    if pos != -1:
                        matches.append((pos, match, fun(lines_cn[i])))

                # 替换最早出现的匹配项
                if matches:
                    matches.sort()  # 按匹配项在脚本中的位置排序
                    match0 = matches[0]
                    chapter_script = chapter_script.replace(match0[1], match0[2], 1)

        output += chapter_script + '\n'
        target_script = target_script[line_idx:]

# 将处理后的内容写回.rb文件
with open('main_tr.rb', 'w', encoding='utf-8') as f:
    f.write(output + '\n' + '\n'.join(target_script))