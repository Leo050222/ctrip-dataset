with open('input.txt', 'r', encoding='utf-8') as f:  # 指定编码为 UTF-8
    urls = f.readlines()

total = len(urls)
per_file = total // 14
remainder = total % 14

start = 0
for i in range(14):
    end = start + per_file + (1 if i < remainder else 0)
    with open(f'urls_part{i+1}.txt', 'w', encoding='utf-8') as f_out:  # 输出文件也指定编码
        f_out.writelines(urls[start:end])
    start = end