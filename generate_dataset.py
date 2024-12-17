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
            # 檢查是否有字形資訊
            if font.getbbox(char) is None:
                return False
            
            # 創建一個臨時圖像來測試字符渲染
            test_img = Image.new('RGB', (50, 50), color='white')
            test_draw = ImageDraw.Draw(test_img)
            test_draw.text((10, 10), char, font=font, fill='black')
            
            # 檢查是否為純矩形（可能是未支援字符的替代顯示）
            pixels = test_img.load()
            black_pixels = []
            for x in range(test_img.width):
                for y in range(test_img.height):
                    if pixels[x, y] != (255, 255, 255):  # 如果不是白色
                        black_pixels.append((x, y))
            
            if len(black_pixels) == 0:  # 完全沒有渲染
                return False
            
            # 檢查是否為完全矩形（通常表示替代字符）
            if black_pixels:
                min_x = min(x for x, y in black_pixels)
                max_x = max(x for x, y in black_pixels)
                min_y = min(y for x, y in black_pixels)
                max_y = max(y for x, y in black_pixels)
                
                # 計算邊界框的寬度和高度
                width = max_x - min_x + 1
                height = max_y - min_y + 1
                
                # 檢查是否為正方形或接近正方形
                if abs(width - height) < 3:  # 如果寬高差異很小
                    return False
                
                # 檢查邊界的規則性
                edge_pixels = set()
                for x, y in black_pixels:
                    if (x in (min_x, max_x) or y in (min_y, max_y)):
                        edge_pixels.add((x, y))
                
                # 如果邊界像素太規則（形成完美的矩形），可能是替代字符
                if len(edge_pixels) > (width + height) * 0.9:
                    return False
                
                # 檢查填充的均勻性
                filled_area = len(black_pixels)
                total_area = width * height
                if filled_area / total_area > 0.9:  # 如果填充過於均勻
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
        total_width += bbox[2]  # bbox[2] 是字符寬度
        max_height = max(max_height, bbox[3])  # bbox[3] 是字符高度
    return total_width, max_height

def generate_images_and_labels_with_coordinates(ch_dict_path, output_dir, font_folder, num_samples):
    # 設置日誌
    logger = setup_logger(output_dir)
    
    # 創建輸出目錄
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    label_file = os.path.join(output_dir, "labels.json")
    labels = {}

    # 檢查現有的圖片和標籤
    if os.path.exists(label_file):
        try:
            with open(label_file, 'r', encoding='utf-8') as f:
                labels = json.load(f)
        except Exception as e:
            logger.warning(f"無法讀取現有的標籤文件: {e}")
            labels = {}

    # 檢查圖片目錄中的現有圖片
    existing_images = set(os.listdir(images_dir))
    
    # 清理不一致的數據
    for image_name in list(labels.keys()):
        if image_name not in existing_images:
            del labels[image_name]
            logger.info(f"刪除缺失圖片的標籤: {image_name}")
    
    # 獲取字體文件列表
    font_files = [os.path.join(font_folder, f) for f in os.listdir(font_folder) if f.endswith(('.ttf', '.otf'))]
    if not font_files:
        logger.error("字體文件夾中沒有找到有效的字體文件！")
        raise ValueError("字體文件夾中沒有找到有效的字體文件！")

    # 讀取字符字典
    with open(ch_dict_path, 'r', encoding='utf-8') as f:
        characters = [line.strip() for line in f if line.strip()]

    successful_count = 0
    attempt_count = 0
    max_attempts = num_samples * 2

    while successful_count < num_samples and attempt_count < max_attempts:
        attempt_count += 1
        
        image_name = f"img_{len(labels) + 1}.jpg"
        
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
        try:
            # 計算文字大小
            text_width, text_height = calculate_text_size(text, valid_font)
            
            # 設定邊距和圖片大小
            margin = 20
            img_width = text_width + margin * 2
            img_height = text_height + margin * 2
            img_width = max(200, min(400, img_width))
            img_height = max(100, min(200, img_height))

            # 創建圖片
            img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            # 計算文字位置
            x1 = margin
            y1 = (img_height - text_height) // 2
            
            # 獲取實際的文字邊界框
            bbox = draw.textbbox((x1, y1), text, font=valid_font)
            x1, y1, x2, y2 = bbox

            # 繪制文字
            draw.text((margin, (img_height - text_height) // 2), text, font=valid_font, fill=(0, 0, 0))

            # 保存圖片
            img_path = os.path.join(images_dir, image_name)
            img.save(img_path)

            # 更新標籤
            labels[image_name] = [{
                "transcription": text,
                "points": [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
                "illegibility": False
            }]

            # 定期保存標籤文件
            if successful_count % 100 == 0:
                with open(label_file, 'w', encoding='utf-8') as f:
                    json.dump(labels, f, ensure_ascii=False, indent=4)
                logger.info(f"已完成 {successful_count} 張圖片的生成")

            successful_count += 1
            logger.debug(f"成功生成圖片: {image_name}")

        except Exception as e:
            logger.error(f"生成圖片 {image_name} 時發生錯誤: {str(e)}")
            if os.path.exists(os.path.join(images_dir, image_name)):
                os.remove(os.path.join(images_dir, image_name))
            continue

    # 最後保存標籤文件
    with open(label_file, 'w', encoding='utf-8') as f:
        json.dump(labels, f, ensure_ascii=False, indent=4)

    logger.info(f"生成完成！成功生成 {successful_count} 張圖片")
    logger.info(f"圖片保存在: {images_dir}")
    logger.info(f"標注文件保存在: {label_file}")

# 使用示例
if __name__ == "__main__":
    ch_dict_path = 'ppocr/utils/ppocr_ch_dict.txt'
    output_dir = 'train_data/test/images_v2'
    font_folder = '字體/字體'
    num_samples = 30000

    generate_images_and_labels_with_coordinates(ch_dict_path, output_dir, font_folder, num_samples)