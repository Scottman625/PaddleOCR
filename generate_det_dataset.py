from PIL import Image, ImageDraw, ImageFont
import os
import random
import json
import logging
from datetime import datetime

# 設置日誌
def setup_logger(output_dir):
    """設置日誌配置"""
    log_dir = os.path.join(output_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 設置日誌文件名（包含時間戳）
    log_file = os.path.join(log_dir, f'generation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # 配置日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 同時輸出到控制台
        ]
    )
    return logging.getLogger(__name__)

def check_font_support(font, text):
    """檢查字體是否完全支援所有字符，並確保不是顯示為方框"""
    try:
        for char in text:
            if font.getbbox(char) is None:
                return False
            test_img = Image.new('RGB', (50, 50), color='white')
            test_draw = ImageDraw.Draw(test_img)
            test_draw.text((10, 10), char, font=font, fill='black')
            pixels = test_img.load()
            black_pixels = []
            for x in range(test_img.width):
                for y in range(test_img.height):
                    if pixels[x, y] != (255, 255, 255):
                        black_pixels.append((x, y))
            if len(black_pixels) == 0:
                return False
            if black_pixels:
                min_x = min(x for x, y in black_pixels)
                max_x = max(x for x, y in black_pixels)
                min_y = min(y for x, y in black_pixels)
                max_y = max(y for x, y in black_pixels)
                width = max_x - min_x + 1
                height = max_y - min_y + 1
                if abs(width - height) < 3:
                    return False
                edge_pixels = set()
                for x, y in black_pixels:
                    if (x in (min_x, max_x) or y in (min_y, max_y)):
                        edge_pixels.add((x, y))
                if len(edge_pixels) > (width + height) * 0.9:
                    return False
                filled_area = len(black_pixels)
                total_area = width * height
                if filled_area / total_area > 0.9:
                    return False
        return True
    except Exception as e:
        print(f"Font check error for char '{char}': {str(e)}")
        return False

def calculate_text_size(text, font):
    """計算文字的總寬度和高度"""
    total_width = 0
    max_height = 0
    for char in text:
        bbox = font.getbbox(char)
        total_width += bbox[2]
        max_height = max(max_height, bbox[3])
    return total_width, max_height

def is_overlapping(new_bbox, existing_bboxes):
    """檢查新的文字邊界框是否與現有邊界框重疊"""
    for bbox in existing_bboxes:
        if not (new_bbox[2] < bbox[0] or new_bbox[0] > bbox[2] or new_bbox[3] < bbox[1] or new_bbox[1] > bbox[3]):
            return True
    return False

def generate_images_and_labels_with_coordinates(ch_dict_path, output_dir, font_folder, num_samples):
    logger = setup_logger(output_dir)
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    label_file = os.path.join(output_dir, "labels.json")
    labels = {}

    if os.path.exists(label_file):
        try:
            with open(label_file, 'r', encoding='utf-8') as f:
                labels = json.load(f)
        except Exception as e:
            logger.warning(f"無法讀取現有的標籤文件: {e}")
            labels = {}
    existing_images = set(os.listdir(images_dir))
    for image_name in list(labels.keys()):
        if image_name not in existing_images:
            del labels[image_name]
            logger.info(f"刪除缺失圖片的標籤: {image_name}")

    font_files = [os.path.join(font_folder, f) for f in os.listdir(font_folder) if f.endswith(('.ttf', '.otf'))]
    if not font_files:
        logger.error("字體文件夾中沒有找到有效的字體文件！")
        raise ValueError("字體文件夾中沒有找到有效的字體文件！")

    with open(ch_dict_path, 'r', encoding='utf-8') as f:
        characters = [line.strip() for line in f if line.strip()]

    successful_count = 0
    attempt_count = 0
    max_attempts = num_samples * 2

    while successful_count < num_samples and attempt_count < max_attempts:
        attempt_count += 1
        image_name = f"img_{len(labels) + 1}.jpg"
        img_width = 400
        img_height = 200
        margin = 10
        img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        existing_bboxes = []
        text_annotations = []
        text_count = random.randint(2, 6)
        for _ in range(text_count):
            font_path = random.choice(font_files)
            try:
                font_size = random.randint(20, 40)
                # 尋找支援所有字符的字體和文字組合
                valid_font = None
                valid_text = None
                max_text_attempts = 10

                for text_attempt in range(max_text_attempts):
                    text = ''.join(random.choices(characters, k=random.randint(2, 10)))
                    
                    font_files_copy = font_files.copy()
                    while font_files_copy:
                        font_path = random.choice(font_files_copy)
                        font_files_copy.remove(font_path)
                        try:
                            test_font = ImageFont.truetype(font_path, random.randint(20, 40))
                            if check_font_support(test_font, text):
                                valid_font = test_font
                                valid_text = text
                                break
                        except Exception as e:
                            logger.debug(f"字體載入失敗 {font_path}: {e}")
                            continue
                    
                    if valid_font is not None:
                        break

                if valid_font is None:
                    logger.warning(f"第 {successful_count + 1} 張圖片在多次嘗試後仍找不到合適的字體和文字組合，跳過")
                    continue

                text = valid_text
                # font = ImageFont.truetype(font_path, font_size)
                # text = ''.join(random.choices(characters, k=random.randint(2, 6)))
                bbox = draw.textbbox((0, 0), text, font=valid_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                for attempt in range(10):
                    x1 = random.randint(margin, img_width - text_width - margin)
                    y1 = random.randint(margin, img_height - text_height - margin)
                    x2, y2 = x1 + text_width, y1 + text_height
                    new_bbox = (x1, y1, x2, y2)
                    if not is_overlapping(new_bbox, existing_bboxes):
                        draw.text((x1, y1), text, font=valid_font, fill=(0, 0, 0))
                        existing_bboxes.append(new_bbox)
                        text_annotations.append({
                            "transcription": text,
                            "points": [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
                            "illegibility": False
                        })
                        break
            except Exception as e:
                logger.error(f"文字生成失敗: {e}")
                continue
        if not text_annotations:
            continue
        img_path = os.path.join(images_dir, image_name)
        img.save(img_path)
        labels[image_name] = text_annotations
        successful_count += 1
        logger.info(f"成功生成圖片: {image_name}, 包含 {len(text_annotations)} 個文字區域")
        if successful_count % 100 == 0:
            with open(label_file, 'w', encoding='utf-8') as f:
                json.dump(labels, f, ensure_ascii=False, indent=4)
            logger.info(f"已完成 {successful_count} 張圖片的生成")

    with open(label_file, 'w', encoding='utf-8') as f:
        json.dump(labels, f, ensure_ascii=False, indent=4)
    logger.info(f"生成完成！成功生成 {successful_count} 張圖片")
    logger.info(f"圖片保存在: {images_dir}")
    logger.info(f"標注文件保存在: {label_file}")

if __name__ == "__main__":
    ch_dict_path = 'ppocr/utils/ppocr_ch_dict.txt'
    output_dir = 'train_data/train/det'
    font_folder = '字體/字體'
    num_samples = 2500
    generate_images_and_labels_with_coordinates(ch_dict_path, output_dir, font_folder, num_samples)
