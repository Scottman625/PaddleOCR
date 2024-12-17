import json

# 输入 JSON 文件路径
input_json_path = "train_data\\test\\det\\labels.json"  # 替换为您的 JSON 文件路径

# 输出文本文件路径
output_txt_path = "train_data\\test\\det\labels_format.json"

def convert_json_to_label(input_json_path, output_txt_path):
    # 读取 JSON 数据
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 用于存储转换后的结果
    results = []

    # 遍历 JSON 数据
    for image_name, annotations in data.items():
        formatted_annotations = []
        for idx, annotation in enumerate(annotations, start=1):
            formatted_annotations.append({
                "transcription": annotation.get("transcription", ""),
                "label": "other",  # 可以根据需要修改
                "points": annotation.get("points", []),
                "id": idx,
                "linking": []
            })

        # 将图像名称与格式化的标注信息组合
        result = f"{image_name}\t{json.dumps(formatted_annotations, ensure_ascii=False)}"
        results.append(result)

    # 写入输出文件
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"转换完成！结果已保存到 {output_txt_path}")

# 调用转换函数
convert_json_to_label(input_json_path, output_txt_path)
