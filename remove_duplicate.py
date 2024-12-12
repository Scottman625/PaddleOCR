with open("ppocr/utils/ppocr_keys_v1.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

unique_chars = set()
cleaned_lines = []
for line in lines:
    char = line.strip()
    if char not in unique_chars:
        unique_chars.add(char)
        cleaned_lines.append(char + "\n")

with open("ppocr/utils/ppocr_keys_v1.txt", "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print("重複字符已移除")
