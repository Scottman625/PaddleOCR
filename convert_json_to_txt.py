import json

# 输入 JSON 文件路径
input_json_path = "train_data\\train\\images_v2\\labels.json"

# 输出 TXT 文件路径
output_txt_path = "train_data\\train\\images_v2\\labels.txt"

with open(input_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 转换为识别模型所需的格式
with open(output_txt_path, "w", encoding="utf-8") as f:
    for image_name, annotations in data.items():
        for annotation in annotations:
            transcription = annotation["transcription"]
            f.write(f"{image_name}\t{transcription}\n")

print(f"识别模型的标签已生成：{output_txt_path}")
