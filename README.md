# Anki卡片 AI 图像生成器

这个 Python 脚本可以自动为 Anki 卡片生成配图。它从 CSV 文件中读取词汇，使用 OpenAI 的 DALL-E 3 模型生成相应的图片，并将这些图片添加到 Anki 卡片中。

## 功能

- 从 CSV 文件读取词汇列表
- 使用 DALL-E 3 生成每个词汇的插图
- 将生成的图片保存到本地文件夹
- 更新 CSV 文件，添加图片引用
- 将图片复制到 Anki 媒体文件夹
- 支持 API 密钥的安全存储和使用

## 安装

1. 克隆此仓库：
   ```
   git clone https://github.com/victor-defi/ankicards_ai_image.git
   ```

2. 安装所需的 Python 库：
   ```
   pip install openai requests pypinyin
   ```

## 使用方法

1. 运行脚本：
   ```
   python anki_card.py
   ```

2. 按照提示输入您的 OpenAI Key

3. prompt = f"日本动漫风格的插图，展现'{*word*}'的概念，画面清晰可爱，具有典型的日本动画特征"。即默认 prompt，可以自行修改，生成结果取决于 openai

4. anki_media_folder = '/Users/farmer/Library/Application Support/Anki2/账户 1/collection.media' ，该行代码的目的是为了将图片复制到 anki 媒体文件夹下，**请各位自行填写，否则会写入失败**