import os
import difflib

folder_a = 'story_ns'
folder_b = 'story_umipro'
files_to_exclude = {'umi8_9.txt'}  # 排除的文件名

# 获取文件夹A和B中的文件名列表，并按字母、数字顺序排序
files_a = sorted(os.listdir(folder_a))
files_b = sorted(os.listdir(folder_b))

# 找到两个文件夹中都有的文件
common_files = sorted(set(files_a).intersection(files_b))
common_files = [file for file in common_files if file not in files_to_exclude]

# 打开diff.txt文件，如果没有则创建
with open('diff.txt', 'w', encoding='utf-8') as diff_file:
    for file_name in common_files:
        file_a_path = os.path.join(folder_a, file_name)
        file_b_path = os.path.join(folder_b, file_name)

        with open(file_a_path, 'r', encoding='utf-8') as file_a, open(file_b_path, 'r', encoding='utf-8') as file_b:
            content_a = file_a.readlines()
            content_b = file_b.readlines()

            # 对比两边文件的总行数是否一致，如果不一致则写入diff.txt
            if len(content_a) != len(content_b):
                diff_file.write(f'LINES in {file_name}:\n')
                diff_file.write(f'{file_name} (A) has {len(content_a)} lines\n')
                diff_file.write(f'{file_name} (B) has {len(content_b)} lines\n')
                diff_file.write('\n' + '='*40 + '\n\n')

        # 比较两个文件的内容
        diff = list(difflib.unified_diff(content_a, content_b, fromfile=file_name + ' (A)', tofile=file_name + ' (B)'))

        buffer = []
        added_lines = 0
        removed_lines = 0
        in_diff_block = False

        for line in diff:
            if line.startswith('@@'):
                # 在遇到新的 diff 块时，判断并写入之前的不一致部分
                if in_diff_block: # if in_diff_block and added_lines != removed_lines:
                    diff_file.write(f'Differences in {file_name}:\n')
                    for buf_line in buffer:
                        if buf_line.startswith(('+', '-')):
                            diff_file.write(buf_line)
                    diff_file.write('\n' + '='*40 + '\n\n')

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
                # 当遇到没有前缀的行时，判断前面的累积部分是否需要写入
                if buffer: # if buffer and added_lines != removed_lines:
                    diff_file.write(f'{file_name}:\n')
                    for buf_line in buffer:
                        if buf_line.startswith(('+', '-')):
                            diff_file.write(buf_line)
                    diff_file.write('\n' + '='*40 + '\n\n')

                # 重置状态
                buffer = []
                added_lines = 0
                removed_lines = 0
                in_diff_block = False

        # 最后一段不一致的块
        if in_diff_block: # if in_diff_block and added_lines != removed_lines:
            diff_file.write(f'{file_name}:\n')
            for buf_line in buffer:
                if buf_line.startswith(('+', '-')):
                    diff_file.write(buf_line)
            diff_file.write('\n' + '='*40 + '\n\n')