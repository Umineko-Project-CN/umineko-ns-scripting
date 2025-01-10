import os
import re

# 定义
jp_script_base = 'story_ns/'
cn_script_base = 'story_cn/'
ep_list = [
    *(("umi" + str(i), list(range(0, 31))) for i in range(1, 9)),
    ("tsubasa", list(range(1, 16)) + [20]),
    ("hane", list(range(1, 3))),
    ("saku", list(range(1, 4))),
    ("tsubasa", list(range(16, 20)))
]
start_line = 18467

SPACE_pattern = r"((@[a-z|\[\]](\.)?)*)@"
SPACE_replace = r"{text}@"

HALFWIDTH = "｢｣ｧｨｩｪｫｬｭｮｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝｰｯ—､ﾟﾞ･｡`ゞ"
HALFWIDTH_REPLACE = "「」ぁぃぅぇぉゃゅょあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんーっ―、？！…。　'，"
trans_table = str.maketrans(HALFWIDTH_REPLACE, HALFWIDTH)

# 人名映射表
name_map = {
    'ベルフェゴール': '贝露菲格露',
    'ウィラード・Ｈ・ライト': '威拉德·H·莱特',
    'ウィッチハンター三神': '魔女猎人三神',
    '右代宮　霧江': '右代宫　雾江',
    '南條　雅行': '南条　雅行',
    '右代宮　秀吉': '右代宫　秀吉',
    '右代宮　金蔵': '右代宫　金藏',
    '郷田　俊朗': '乡田　俊朗',
    'シエスタ４５': '谢丝塔 45',
    'マモン': '马蒙',
    'ガァプ': '噶普',
    'サタン': '撒旦',
    'エンジェ・ベアトリーチェ': '安琪·贝阿朵莉切',
    '右代宮　縁寿': '右代宫　缘寿',
    'フェザリーヌ': '菲泽莉努',
    'アスモデウス': '阿丝磨德乌丝',
    '右代宮　楼座': '右代宫　楼座',
    'ウェルギリアス': '维尔吉利亚斯',
    '右代宮　戦人': '右代宫　战人',
    '右代宮　朱志香': '右代宫　朱志香',
    'シエスタ００': '谢丝塔 00',
    'レヴィアタン': '雷维阿坦',
    '熊沢　チヨ': '熊泽　千代',
    '右代宮　蔵臼': '右代宫　藏臼',
    '黒き戦人': '黑战人',
    'ガートルード': '格德鲁特',
    '右代宮　理御': '右代宫　理御',
    '右代宮　譲治': '右代宫　让治',
    '右代宮　夏妃': '右代宫　夏妃',
    'シエスタ５５６': '谢丝塔 556',
    'ピース': '匹伊丝',
    '熊沢　鯖吉': '熊泽　鲭吉',
    'ワルギリア': '瓦尔基莉亚',
    'ベルゼブブ': '贝露赛布布',
    'コーネリア': '柯内莉亚',
    '右代宮　絵羽': '右代宫　绘羽',
    'サク': '咲',
    '古戸　ヱリカ': '古户　绘梨花',
    '紗音': '纱音',
    '須磨寺　霞': '須磨寺　霞',
    '山羊の従者': '山羊仆从',
    '川畑船長': '川畑船长',
    '右代宮　留弗夫': '右代宫　留弗夫',
    'ドラノール': '德拉诺尔',
    '姉ベアトリーチェ': '姐姐贝阿朵莉切',
    '寿ゆかり': '寿　由香里',
    'ロノウェ': '罗诺威',
    '南條　輝正': '南条　辉正',
    'ゼパル': '赛帕尔',
    '小此木　鉄郎': '小次木　铁郎',
    '呂ノ上　源次': '吕之上　源次',
    'フラウロス': '弗拉乌罗斯',
    '八城　幾子': '八城　几子',
    'ベアトリーチェ': '贝阿朵莉切',
    'ラムダデルタ': '拉姆达戴露塔',
    '右代宮　真里亞': '右代宫　真里亚',
    'ルシファー': '路西法',
    'クレル': '克蕾尔',
    'シエスタ４１０': '谢丝塔 410',
    'フルフル': '芙尔芙尔',
    'エヴァ・ベアトリーチェ': '夏娃·贝阿朵莉切',
    'さくたろう': '樱太郎',
    'ベルンカステル': '贝伦卡斯泰露'
}


# 读取并处理rb文件
with open('main.rb', 'r', encoding='utf-8') as f:
    target_script = f.read().splitlines()

# 输出的初始部分
output = '\n'.join(target_script[:start_line]) + '\n'
target_script = target_script[start_line:]

# 处理每个EP和章节
for ep, chapters in ep_list:
    for chapter in chapters:
        print(f'Processing Episode {ep} Chapter {chapter}')
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
        line_idx = next((i for i, x in enumerate(chapter_script) if x.startswith('s.ins 0xa0, byte(1), ')), len(chapter_script)) + 1
        chapter_script = chapter_script[:line_idx]
        chapter_script = '\n'.join(chapter_script)

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
        # 删多余空格
        chapter_script = re.sub(SPACE_pattern, lambda m: SPACE_replace.format(text=m.group(1)), chapter_script)
        output += chapter_script + '\n'
        target_script = target_script[line_idx:]

# 修改人名名称
for name_jp, name_cn in name_map.items():
    output = re.sub(rf"'{re.escape(name_jp)}\s?@", f"'{name_cn}@", output)

# 修改章节标题、tip和人物介绍
output = re.sub('\'うみねこのなく頃に','\'海猫鸣泣之时',output)
with open('chapters.txt', 'r', encoding='utf-8') as rf:
    chapter_lines = [line.strip() for line in rf.readlines()]
with open('tips.txt', 'r', encoding='utf-8') as rf:
    tips_lines = [line.strip() for line in rf.readlines()]
with open('characters.txt', 'r', encoding='utf-8') as rf:
    characters_lines = [line.strip() for line in rf.readlines()]

# 解析tips和characters
tips_pairs = []
for i, line in enumerate(tips_lines, start=1):
    parts = line.split(',')
    tip1 = parts[0].strip().strip("'")
    tip2 = parts[1].strip().strip("'")
    tips_pairs.append((tip1, tip2))
characters_pairs = []
for i, line in enumerate(characters_lines, start=1):
    parts = line.split(',')
    character1 = parts[0].strip().strip("'")
    character2 = parts[1].strip().strip("'")
    characters_pairs.append((character1, character2))

# 替换计数器
chapter_index = 0
tip_index = 0
character_index = 0
updated_lines = []

tip_pattern = re.compile(
    r"^(snr\.tip\s+([0-6]),\s+([0-9]|1[0-9]|2[0-6]),\s*)'([^']*)',\s*'([^']*)'(.*)$")
character_pattern = re.compile(
        r"^(segments\s*<<\s*\[\d+,\s*)'([^']*)',\s*'([^']*)'\s*(.*)$")
for line in output.splitlines():
    match_chapter = re.match(r'(s\.ins 0xa0, byte\(1\), )(.*)', line)
    match_tip = tip_pattern.match(line)
    match_char = character_pattern.match(line)
    # 替换章节
    if match_chapter and chapter_index < len(chapter_lines):
        updated_lines.append(f"{match_chapter.group(1)}'{chapter_lines[chapter_index]}'\n")
        chapter_index += 1
    #替换tip
    elif match_tip and tip_index < len(tips_pairs) :
        prefix = match_tip.group(1)
        suffix = match_tip.group(6)
        new1, new2 = tips_pairs[tip_index]
        tip_index += 1
        new_line = f"{prefix}'{new1}', '{new2}'{suffix}\n"
        updated_lines.append(new_line)
    # 替换人物介绍
    elif match_char and character_index < len(characters_pairs):
        prefix = match_char.group(1)
        suffix = match_char.group(4)
        new1, new2 = characters_pairs[character_index]
        character_index += 1
        new_line = f"{prefix}'{new1}', '{new2}'{suffix}\n"
        updated_lines.append(new_line)
    else:
        updated_lines.append(line + '\n')
output = ''.join(updated_lines)

# 将处理后的内容写回.rb文件
with open('catbox\script.rb', 'w', encoding='utf-8') as f:
    f.write(output + '\n' + '\n'.join(target_script))