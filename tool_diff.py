import os
import difflib

folder_a = 'story_ns'
folder_b = 'story_umipro'
files_to_exclude = {'umi8_9.txt'}  # 排除的文件名

# 获取文件夹A和B中的文件名列表

# 获取文件夹A和B中的文件名列表，并按字母、数字顺序排序
files_a = sorted(os.listdir(folder_a))
files_b = sorted(os.listdir(folder_b))

# 找到两个文件夹中都有的文件
common_files = sorted(set(files_a).intersection(files_b))
common_files = [file for file in common_files if file not in files_to_exclude]

for file_name in common_files:
    file_a_path = os.path.join(folder_a, file_name)
    file_b_path = os.path.join(folder_b, file_name)

    with open(file_a_path, 'r', encoding='utf-8') as file_a, open(file_b_path, 'r', encoding='utf-8') as file_b:
        content_a = file_a.readlines()
        content_b = file_b.readlines()

        # 对比两边文件的总行数是否一致，如果不一致则打印
        if len(content_a) != len(content_b):
            print(f'LINES in {file_name}:')
            print(f'{file_name} (A) has {len(content_a)} lines')
            print(f'{file_name} (B) has {len(content_b)} lines')
            print('\n' + '='*40 + '\n')

    # 比较两个文件的内容
    diff = list(difflib.unified_diff(content_a, content_b, fromfile=file_name + ' (A)', tofile=file_name + ' (B)'))

    buffer = []
    added_lines = 0
    removed_lines = 0
    in_diff_block = False

    for line in diff:
        if line.startswith('@@'):
            # 在遇到新的 diff 块时，判断并输出之前的不一致部分
            if in_diff_block and added_lines != removed_lines:
                print(f'Differences in {file_name}:')
                for buf_line in buffer:
                    if buf_line.startswith(('+', '-')):
                        print(buf_line, end='')
                print('\n' + '='*40 + '\n')
            
            # 重置状态
            buffer = []
            added_lines = 0
            removed_lines = 0
            in_diff_block = True

        elif line.startswith('+'):
            added_lines += 1
            buffer.append(line)
        elif line.startswith('-'):
            removed_lines += 1
            buffer.append(line)
        else:
            # 当遇到没有前缀的行时，判断前面的累积部分是否需要打印
            if added_lines != removed_lines:
                if buffer:
                    print(f'{file_name}:')
                    for buf_line in buffer:
                        if buf_line.startswith(('+', '-')):
                            print(buf_line, end='')
                    print('\n' + '='*40 + '\n')
            # 重置状态
            buffer = []
            added_lines = 0
            removed_lines = 0
            in_diff_block = False

    # 最后一段不一致的块
    if in_diff_block and added_lines != removed_lines:
        print(f'{file_name}:')
        for buf_line in buffer:
            if buf_line.startswith(('+', '-')):
                print(buf_line, end='')
        print('\n' + '='*40 + '\n')