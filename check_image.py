import os
import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def visualize_json_annotations(image_dir, json_path, output_dir=None):
    """
    读取JSON标注文件，将检测框和文本可视化并展示或保存结果。
    
    Args:
        image_dir (str): 存储图像的目录路径。
        json_path (str): JSON标注文件的路径。
        output_dir (str, optional): 可选，保存可视化结果的目录路径。如果为 None，则只展示图像。
    """
    # 检查输出目录是否存在
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        annotations = json.load(f)
    
    # 遍历每个图像和其对应的标注
    for image_name, bboxes in annotations.items():
        image_path = os.path.join(image_dir, image_name)
        
        # 检查图像文件是否存在
        if not os.path.exists(image_path):
            print(f"图像文件 {image_path} 不存在，跳过...")
            continue
        
        # 打开图像
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        
        # 设置字体（使用系统默认字体）
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except:
            font = ImageFont.load_default()
        
        # 遍历当前图像的所有标注框
        for box in bboxes:
            transcription = box.get("transcription", "")
            points = box.get("points", [])
            
            # 绘制边界框
            if len(points) == 4:
                int_points = [(int(x), int(y)) for x, y in points]
                draw.polygon(int_points, outline="red", width=2)
                
                # 计算文本位置（左上角）
                x, y = points[0]
                draw.text((x, y - 10), transcription, fill="blue", font=font)
        
        # 显示图像
        plt.imshow(image)
        plt.axis('off')
        plt.title(image_name)
        plt.show()
        
        # 保存结果（可选）
        if output_dir:
            output_path = os.path.join(output_dir, image_name)
            image.save(output_path)
            print(f"保存可视化结果至: {output_path}")

# 示例使用
if __name__ == "__main__":
    # 输入目录和文件路径
    image_directory = "train_data/test/det/images"  # 图片目录
    json_file_path = "train_data/test/det/labels.json"  # 标注文件
    output_directory = "visualized_results"  # 可选，保存可视化结果的目录

    # 执行可视化
    visualize_json_annotations(image_directory, json_file_path, output_directory)
