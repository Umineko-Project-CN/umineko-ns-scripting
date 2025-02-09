import os
import re
import copy

# # # # # # # # # # # # # # #
# 1. 定义
# # # # # # # # # # # # # # #

# 1.0. 路径定义
jp_script_base = 'story_ns/'
cn_script_base = 'story_cn/'

# 1.1. 文本修改部分定义
# EP列表
ep_list = [
    *(("umi" + str(i), list(range(0, 31))) for i in range(1, 9)),
    ("tsubasa", list(range(1, 16)) + [20]),
    ("hane", list(range(1, 3))),
    ("saku", list(range(1, 4))),
    ("tsubasa", list(range(16, 20)))
]
# 开始行
start_line = 18467
# 空格替换
SPACE_pattern = r"((@[a-z|\[\]](\.)?)*)@"
SPACE_replace = r"{text}@"
# 匹配章节标题、Tips、Characters
CHAPTER_pattern = r'(s\.ins 0xa0, byte\(1\), )(.*)'
TIP_pattern = r"^(snr\.tip\s+([0-6]),\s+([0-9]|1[0-9]|2[0-6]),\s*)'([^']*)',\s*'([^']*)'(.*)$"
CHAR_pattern = r"^(segments\s*<<\s*\[\d+,\s*)'([^']*)',\s*'([^']*)'\s*(.*)$"
# 字符替换
HALFWIDTH = "—｢｣ｧｨｩｪｫｬｭｮｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝｰｯ､ﾟﾞ･｡`ゞ"
HALFWIDTH_REPLACE = "―「」ぁぃぅぇぉゃゅょあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんーっ、？！…。　'，"
trans_table_jp = str.maketrans(HALFWIDTH_REPLACE[:-1], HALFWIDTH[:-1])
trans_table_cn = str.maketrans(HALFWIDTH_REPLACE[1:], HALFWIDTH[1:])
# Chapters字符替換
CHAPTER_hans = "è东两为义乡书亚亲仪们伙伞传伦侦关则剧动劳厅另唤围圣场备复实宫宾对尔岁岛崭师帕带开忆恶戏战户择时朵杀杂检樱橱步每滩炼烦爱狱猎现电盘种笼类紧红终结绘缘节苏获萨蓝观规议记访证诞语误说请谁谈谜谢贝贵赛轩轻辑达还这迟选逻释钥锅错门问队难项预题风馆验骗黑"
CHAPTER_hans_REPLACE = "轜辧辷迚迯逎逓逧逹遖邉邨醗釖釛釟釡釶釼鈎鈩鈬銹鋲錺錻鍄鎭鎹鏥鐚鐡鑁鑓鑚鑛閇閊閖閙閠閧陦隲靤靫靱靹鞆鞐韈韮韲頚頴頽顋颪飃飜飮餝餠饂馼駈駲騨髞髢髴鬪鮃鮖鮗鮟鮴鯏鯑鯒鯣鯱鯲鯵鰄鰊鰌鰐鰕鰛鰮鰯鰰鰺鱇鱚鱶鳫鳬鳰鴎鴪鴫鴬鵄鵆鵈鵐鵞鵤鵺鶫鷄鷆麁麕麪麹麿鼈鼡龝"
trans_table_chapter = str.maketrans(CHAPTER_hans, CHAPTER_hans_REPLACE)
# 选项、人名替换
name_map = {
    # 选项等
    '選択肢':'选项',
    'ルシファー\000レヴィアタン\000サタン\000ベルフェゴール\000マモン\000ベルゼブブ\000アスモデウス\000':'路西法\000雷维阿坦\000撒旦\000贝露菲格露\000马蒙\000贝露赛布布\000阿斯磨德乌丝\000',
    'シエスタ００\000シエスタ４１０\000シエスタ４５\000シエスタ５５６\000':'谢丝塔 00\000谢丝塔 410\000谢丝塔 45\000谢丝塔 556\000',
    'ドラノール\000コーネリア\000ガートルード\000':'德拉诺尔\000柯内莉亚\000格德鲁特\000',
    'ゼパル\000フルフル\000':'赛帕尔\000芙尔芙尔\000',
    '汝は、猫を殺すか、否か':'汝是否要将猫杀死',
    '殺す\000否\000':'杀\000否\000',
    # 人名
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

# 1.2. 代码修改部分定义
# 新图片
insert_bgs = [
    "end_all00_01 = snr.bg 'end_all00_01', 65535",
    "end_all00_02 = snr.bg 'end_all00_02', 65535"
]
target_bgs = 'snr.write_bgs'

# 图片调用：end_all00
target_lines_endall00 = [
    "s.ins 0xcb",
    "s.ins 0xc1, 3, byte(2), 0, byte(1), 2402",
    "s.ins 0xc3, 3, 5, byte(1), -3",
]
insert_lines_endall00 = [
    "s.ins 0xc1, 19, byte(1), 0, byte(0), end_all00_01",
    "s.ins 0xc3, 19, 6, byte(1), 0", # 初始透明
    "s.ins 0xc3, 19, 6, byte(1), 255, 30", # 淡入
    "s.ins 0x83, byte(0), 60", # 等待
    "s.ins 0xc3, 19, 6, byte(1), 0, 30", # 淡出
    "s.ins 0xc2, 19, byte(0) ", # 隐藏

    "s.ins 0xc1, 19, byte(1), 0, byte(0), end_all00_02",
    "s.ins 0xc3, 19, 6, byte(1), 0", # 初始透明
    "s.ins 0xc3, 19, 6, byte(1), 255, 30", # 淡入
    "s.ins 0x83, byte(0), 60", # 等待
    "s.ins 0xc3, 19, 6, byte(1), 0, 30", # 淡出
    "s.ins 0xc2, 19, byte(0) ", # 隐藏
]

# # # # # # # # # # # # # # #
# 2. 函数
# # # # # # # # # # # # # # #

# 2.1 读取文本
def parse(file_path):
    with open(file_path, 'r', encoding='utf-8') as rf:
        return [line.strip() for line in rf.readlines()]
    
# 2.2 替换文本
def main_text(target_script, chapter_lines, tips_lines, characters_lines):
    # 2.2.1 替换正文
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
                # 翼1特殊处理
                if ep == "tsubasa" and chapter == 1:
                    lines_jp_nc = copy.deepcopy(lines_jp)
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
                    lines_jp[i] = lines_jp[i].translate(trans_table_jp)
                    lines_cn[i] = lines_cn[i].translate(trans_table_cn)

                    # 保存所有匹配方式的结果及其位置
                    matches = []

                    for fun in [lambda x: x + '@', lambda x: x + "'", lambda x: x.strip() + '@', lambda x: x.strip() + "'"]:
                        match = fun(lines_jp[i])
                        match_nc = fun(lines_jp_nc[i]) if ep == "tsubasa" and chapter == 1 else None # 翼1特殊处理
                        pos = chapter_script.find(match)
                        pos_nc = chapter_script.find(match_nc) if match_nc else -1 # 翼1特殊处理

                        if pos != -1:
                            matches.append((pos, match, fun(lines_cn[i])))
                        elif pos_nc != -1:
                            matches.append((pos_nc, match_nc, fun(lines_cn[i]))) # 翼1特殊处理

                    # 替换最早出现的匹配项
                    if matches:
                        matches.sort()  # 按匹配项在脚本中的位置排序
                        match0 = matches[0]
                        chapter_script = chapter_script.replace(match0[1], match0[2], 1)
            # 删多余空格
            chapter_script = re.sub(SPACE_pattern, lambda m: SPACE_replace.format(text=m.group(1)), chapter_script)
            output += chapter_script + '\n'
            target_script = target_script[line_idx:]

    # 2.2.2 替换章节标题、Tips和Characters
    output = re.sub('\'うみねこのなく頃に','\'海猫鸣泣之时',output)

    # 解析Tips和Characters
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
    chapter_i = 0
    tip_i = 0
    character_i = 0
    updated_lines = []

    for line in output.splitlines():
        match_chapter = re.match(CHAPTER_pattern, line)
        match_tip = re.match(TIP_pattern, line)
        match_char = re.match(CHAR_pattern, line)
        # 替换章节标题
        if match_chapter and chapter_i < len(chapter_lines):
            chapter_line = chapter_lines[chapter_i].translate(trans_table_chapter) # 替换章节标题字符
            updated_lines.append(f"{match_chapter.group(1)}'{chapter_line}'\n")
            chapter_i += 1
        #替换Tips
        elif match_tip and tip_i < len(tips_pairs) :
            prefix = match_tip.group(1)
            suffix = match_tip.group(6)
            new1, new2 = tips_pairs[tip_i]
            tip_i += 1
            new_line = f"{prefix}'{new1}', '{new2}'{suffix}\n"
            updated_lines.append(new_line)
        # 替换Characters
        elif match_char and character_i < len(characters_pairs):
            prefix = match_char.group(1)
            suffix = match_char.group(4)
            new1, new2 = characters_pairs[character_i]
            character_i += 1
            new_line = f"{prefix}'{new1}', '{new2}'{suffix}\n"
            updated_lines.append(new_line)
        else:
            updated_lines.append(line + '\n')
    output = ''.join(updated_lines)

    # 2.2.3 替换人名
    for name_jp, name_cn in name_map.items():
        output = re.sub(rf"'{re.escape(name_jp)}\s?", f"'{name_cn}", output)

    return output, target_script

# 2.3 增加代码
def main_code(script_lines):
    # 新图片
    for i, line in enumerate(script_lines):
        if target_bgs in line:
            script_lines[i:i] = insert_bgs
            break

    # 图片调用：end_all00
    for i in range(len(script_lines) - len(target_lines_endall00) + 1):
        if script_lines[i:i + len(target_lines_endall00)] == target_lines_endall00:
            # 把新内容增加到这一行之后
            script_lines[i + len(target_lines_endall00):i + len(target_lines_endall00)] = insert_lines_endall00
            break

    return script_lines

# # # # # # # # # # # # # # #
# 3. 读取与保存
# # # # # # # # # # # # # # #

# 3.1 读取
target_script = parse('main.rb')
chapter_lines = parse('chapters.txt')
tips_lines = parse('tips.txt')
characters_lines = parse('characters.txt')

# 3.2 替换文本
output, trans_target_script = main_text(target_script, chapter_lines, tips_lines, characters_lines)
script_lines = (output + '\n' + '\n'.join(trans_target_script)).splitlines()

# 3.3 增加代码
# script_lines = main_code(script_lines)

# 3.4 将修改后的内容写回script.rb文件
with open('catbox\script.rb', 'w', encoding='utf-8') as f:
    f.writelines('\n'.join(script_lines))