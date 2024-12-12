import os

with open("train/train_data/outPart60DictLabel20.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

missing_files = []
for line in lines:
    image_path = line.split(" ")[0]
    if not os.path.exists(image_path):
        missing_files.append(image_path)

if missing_files:
    print("Missing files:")
    print("\n".join(missing_files))
else:
    print("All files are present.")
