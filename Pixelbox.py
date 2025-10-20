# -*- coding: utf-8 -*-
import os
import math
import numpy as np
from PIL import Image, ImageOps

# 输入和输出路径
input_folder = '/home/mm/projects/3dmem/utils/test_photo/image_origin'
output_folder = '/home/mm/projects/3dmem/utils/test_photo/image_compress'
os.makedirs(output_folder, exist_ok=True)

# 目标分辨率
TARGET_W, TARGET_H = 1280, 720

# 支持的图片格式
valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')

def pixel_subsample_keep_shape(img, target_w, target_h):
    """
    等比例像素间隔采样：
    - 使用统一 stride（x、y 相同）做子采样，防止形变。
    - 仅当原图至少在一个维度大于目标时才下采样；否则不缩放。
    - 结果不强行变成目标分辨率；由外层进行信箱式填充或（可选）裁剪。
    """
    # 处理 EXIF 方向
    img = ImageOps.exif_transpose(img)

    w, h = img.size
    # 若尺寸均不小于目标，计算 stride（取两维的 floor 比例中较小的）
    if w >= target_w or h >= target_h:
        # 至少一个维度需要缩小，确保 stride >= 1
        stride_w = max(1, w // target_w) if w > target_w else 1
        stride_h = max(1, h // target_h) if h > target_h else 1
        stride = max(1, min(stride_w, stride_h))  # 统一步长，防止形变

        if stride > 1:
            # 用最近邻的整数倍下采样，相当于每 stride 个像素取一个
            # 转 numpy 做“隔行隔列采样”，严格满足“像素间隔采样”
            arr = np.array(img)
            # 处理 L/LA/调色板等模式到 RGBA，避免通道数不一致
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')
                arr = np.array(img)
            subsampled = arr[::stride, ::stride, ...] if arr.ndim == 3 else arr[::stride, ::stride]
            img = Image.fromarray(subsampled)
        # stride==1 时不变
    # 若尺寸都小于目标，不缩放，保持清晰度与形状

    return img

def letterbox_to_target(img, target_w, target_h, bg_color=(0, 0, 0)):
    """
    信箱式填充到目标分辨率，不做上采样，形状不变。
    - 若图像超过目标（极少见于不规则输入），可中心裁剪到目标（仍不变形）。
    """
    w, h = img.size
    # 如果任一维超过目标，中心裁剪（不变形）
    if w > target_w or h > target_h:
        left = max(0, (w - target_w) // 2)
        top = max(0, (h - target_h) // 2)
        right = min(w, left + target_w)
        bottom = min(h, top + target_h)
        img = img.crop((left, top, right, bottom))
        w, h = img.size

    # 居中贴到目标画布（不放大，仅填充）
    # 处理透明图：先贴到不透明背景
    if img.mode == 'RGBA':
        base = Image.new('RGB', (target_w, target_h), bg_color)
        paste_x = (target_w - w) // 2
        paste_y = (target_h - h) // 2
        base.paste(img.convert('RGBA'), (paste_x, paste_y), mask=img.split()[-1])
        return base
    else:
        base = Image.new('RGB', (target_w, target_h), bg_color)
        paste_x = (target_w - w) // 2
        paste_y = (target_h - h) // 2
        base.paste(img, (paste_x, paste_y))
        return base

for filename in os.listdir(input_folder):
    if not filename.lower().endswith(valid_exts):
        continue

    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(output_folder, filename)

    try:
        with Image.open(input_path) as img:
            # 1) 等比例像素间隔采样（仅向下）
            img_ss = pixel_subsample_keep_shape(img, TARGET_W, TARGET_H)
            # 2) 信箱式填充到 1280×720（不放大原内容）
            out_img = letterbox_to_target(img_ss, TARGET_W, TARGET_H, bg_color=(0, 0, 0))

            # 统一保存为 RGB/jpg 或保持原扩展名均可；这里沿用原扩展名
            ext = os.path.splitext(filename)[1].lower()
            if ext in ('.png', '.webp', '.tiff'):
                # 无损格式尽量保留；PNG 如存在透明已在上一步合成到黑底
                out_img.save(output_path)
            else:
                # JPEG 设置较高质量
                out_img.save(output_path, quality=95)

            print("已处理:", filename)
    except Exception as e:
        print("处理 {} 时出错: {}".format(filename, e))

print("全部图片已按像素间隔采样并输出到:", output_folder)
