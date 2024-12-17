import os

# 输入和输出文件路径
input_file = r"D:\code\Python\PaddleOCR\PaddleOCR\train\eval_data\label.txt"
output_file = r"D:\code\Python\PaddleOCR\PaddleOCR\train\eval_data\clean_label.txt"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        # 去除多余的换行符并分割
        parts = line.strip().split(' ', 1)
        if len(parts) != 2:  # 如果分割后长度不为 2，则打印错误行并跳过
            print(f"Invalid line skipped: {line.strip()}")
            continue

        img_path, label = parts

        # 检查路径是否为有效文件路径
        if not os.path.exists(img_path):
            print(f"Missing image file: {img_path}")
            continue

        # 写入修复后的标签文件
        outfile.write(f"{img_path}\t{label}\n")

print(f"Cleaned label file saved to: {output_file}")
