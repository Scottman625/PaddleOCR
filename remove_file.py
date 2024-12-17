import os
image_dir = "train_data\\test\\images_v2\\images"
for num in range(5001, 6715):
    image_name = f"img_{num}.jpg"
    image_path = os.path.join(image_dir, image_name)
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"已刪除圖片: {image_name}")
    else:
        print(f"圖片不存在: {image_path}")