def split_file(input_file, parts=5, prefix='urls_part'):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.strip()]  # 跳过空行

    total = len(lines)
    chunk_size = (total + parts - 1) // parts  # 向上取整

    for i in range(parts):
        start = i * chunk_size
        end = min(start + chunk_size, total)
        part_lines = lines[start:end]
        out_file = f"{prefix}{i+1}.txt"
        with open(out_file, 'w', encoding='utf-8') as f_out:
            f_out.writelines(part_lines)
        print(f"写入 {out_file}，共 {len(part_lines)} 行")

if __name__ == "__main__":
    split_file('urls.txt', parts=5)