# -*- coding: utf-8 -*-
# 生成桌面图标：陶土橙圆角方块 + 白色 C（Claude 风格强调色）
from PIL import Image, ImageDraw, ImageFont

size = 256
img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
# 陶土橙圆角方块
d.rounded_rectangle([10, 10, size - 10, size - 10], radius=52, fill=(201, 100, 66, 255))
# 白色 C 字母
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 155)
except Exception:
    font = ImageFont.load_default()
d.text((size // 2, size // 2 + 6), "C", font=font, fill=(250, 249, 245, 255), anchor="mm")

img.save("D:/C-Learning/CStudy-GUI/icon.ico", format="ICO",
         sizes=[(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)])
print("icon.ico 生成成功")
