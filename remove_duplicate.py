# 定义函数读取文件内容
import os

def read_file(file_path):
    """读取文件并返回集合形式的内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(line.strip() for line in file if line.strip())

def write_union_to_file(file1, file2, output_file):
    """计算两个文件的联集并写入到输出文件"""
    # 读取两个文件内容
    set1 = read_file(file1)
    set2 = read_file(file2)

    # 计算联集
    union_set = set1 | set2  # 使用 | 计算集合联集

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write("\n".join(sorted(union_set)))

    print(f"联集已保存到文件: {output_file}")

# 示例用法
file1_path = 'ppocr/utils/ppocr_ch_dict.txt'  # 替换为第一个文件路径
file2_path = 'ppocr/utils/ppocr_keys_v1.txt'  # 替换为第二个文件路径
output_path = 'ppocr/utils/combine_keys_dict.txt'  # 替换为输出文件路径

write_union_to_file(file1_path, file2_path, output_path)
