import csv
import os
import requests
import time
from openai import OpenAI
import base64
import shutil
from pypinyin import lazy_pinyin

# 加密的API密钥文件路径
ENCRYPTED_API_KEY_FILE = 'encrypted_api_key.txt'

def encrypt_api_key(api_key):
    return base64.b64encode(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key):
    return base64.b64decode(encrypted_api_key.encode()).decode()

def get_api_key():
    if os.path.exists(ENCRYPTED_API_KEY_FILE):
        with open(ENCRYPTED_API_KEY_FILE, 'r') as file:
            encrypted_api_key = file.read().strip()
            return decrypt_api_key(encrypted_api_key)
    else:
        api_key = input("请输入您的OpenAI API密钥: ")
        encrypted_api_key = encrypt_api_key(api_key)
        with open(ENCRYPTED_API_KEY_FILE, 'w') as file:
            file.write(encrypted_api_key)
        return api_key

def get_csv_file_path():
    while True:
        csv_file_path = input("请输入CSV文件的路径: ").strip()
        # 移除可能的引号
        csv_file_path = csv_file_path.strip("'\"")
        if os.path.exists(csv_file_path) and csv_file_path.lower().endswith('.csv'):
            return csv_file_path
        else:
            print(f"文件 '{csv_file_path}' 不存在或不是CSV文件,请重新输入。")
            print("请确保输入的是完整的文件路径,包括文件名和.csv扩展名。")

def convert_to_pinyin(word):
    return '_'.join(lazy_pinyin(word))

def generate_image_for_word(client, word, output_folder, index):
    prompt = f"日本动漫风格的插图，展现'{word}'的概念，画面清晰可爱，具有典型的日本动画特征"
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # 下载图片
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            temp_filename = f"{index:03d}_{word}.png"
            image_path = os.path.join(output_folder, temp_filename)
            with open(image_path, 'wb') as image_file:
                image_file.write(image_response.content)
            print(f"已生成并保存图片: {word} ({temp_filename})")
            return True
        else:
            print(f"下载图片失败: {word}")
            return False
    except Exception as e:
        print(f"生成图片时出错 {word}: {str(e)}")
        return False

def rename_images_to_pinyin(output_folder):
    for filename in os.listdir(output_folder):
        if filename.endswith('.png'):
            index, word = filename.split('_', 1)
            word = word[:-4]  # 移除 .png 扩展名
            pinyin_word = convert_to_pinyin(word)
            new_filename = f"{index}_{pinyin_word}.png"
            old_path = os.path.join(output_folder, filename)
            new_path = os.path.join(output_folder, new_filename)
            os.rename(old_path, new_path)
            print(f"重命名文件: {filename} -> {new_filename}")

def update_csv_with_images(csv_path, image_column):
    temp_csv_path = csv_path + '.temp'
    with open(csv_path, 'r', encoding='utf-8') as input_file, \
         open(temp_csv_path, 'w', newline='', encoding='utf-8') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)
        
        for index, row in enumerate(reader, start=1):
            while len(row) <= image_column:
                row.append('')  # 确保行有足够的列
            word = row[0]
            pinyin_word = convert_to_pinyin(word)
            image_reference = f'<img src="{index:03d}_{pinyin_word}.png">'
            row[image_column] = image_reference
            writer.writerow(row)
    
    os.replace(temp_csv_path, csv_path)
    print(f"CSV文件已更新，图片引用已添加到第{image_column + 1}列")

def copy_images_to_anki(source_folder):
    anki_media_folder = '/Users/farmer/Library/Application Support/Anki2/账户 1/collection.media'
    if not os.path.exists(anki_media_folder):
        print(f"Anki媒体文件夹不存在: {anki_media_folder}")
        return False

    for filename in os.listdir(source_folder):
        if filename.endswith('.png'):
            source_path = os.path.join(source_folder, filename)
            dest_path = os.path.join(anki_media_folder, filename)
            try:
                shutil.copy2(source_path, dest_path)
                print(f"已复制 {filename} 到Anki媒体文件夹")
            except Exception as e:
                print(f"复制 {filename} 时出错: {str(e)}")

    print("所有图片已复制到Anki媒体文件夹")
    return True

def generate_images_from_csv(client, csv_file_path):
    csv_directory = os.path.dirname(csv_file_path)
    csv_filename = os.path.basename(csv_file_path)
    
    output_folder_name = os.path.splitext(csv_filename)[0]
    output_folder = os.path.join(csv_directory, output_folder_name)
    os.makedirs(output_folder, exist_ok=True)

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        words = [row[0] for row in reader]

    for index, word in enumerate(words, start=1):
        success = generate_image_for_word(client, word, output_folder, index)
        if not success:
            print(f"跳过 {word} 并继续下一个")
        time.sleep(1)

    # 在所有图片生成后重命名文件
    rename_images_to_pinyin(output_folder)

    new_csv_path = os.path.join(output_folder, csv_filename)
    try:
        shutil.copy(csv_file_path, new_csv_path)
        print(f"CSV文件已成功复制到 {new_csv_path}")
    except Exception as e:
        print(f"复制CSV文件时出错: {str(e)}")
        return

    # 询问用户想要将图片添加到哪一列
    while True:
        try:
            image_column = int(input("请输入要添加图片引用的列号（0为第一列）: "))
            if image_column >= 0:
                break
            else:
                print("请输入非负整数。")
        except ValueError:
            print("请输入有效的整数。")

    # 更新CSV文件，添加图片引用
    update_csv_with_images(new_csv_path, image_column)

    # 复制图片到Anki媒体文件夹
    if copy_images_to_anki(output_folder):
        print("图片已成功复制到Anki媒体文件夹")
    else:
        print("复制图片到Anki媒体文件夹失败")

    print(f"\n处理完成！")
    print(f"生成的图片和更新后的CSV文件位于: {output_folder}")
    print(f"图片已复制到Anki媒体文件夹: /Users/farmer/Library/Application Support/Anki2/账户 1/collection.media")

if __name__ == "__main__":
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)
    
    csv_file_path = get_csv_file_path()
    generate_images_from_csv(client, csv_file_path)
