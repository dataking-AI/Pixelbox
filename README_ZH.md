# Pixelbox — README

一键将目录内的图片做“像素间隔下采样 + 信箱式填充”，在不拉伸、不上采样的前提下，统一输出为 1280×720 分辨率。

## 功能简介

* 等比例像素间隔下采样：通过统一 stride（x、y 相同）进行整数倍采样，避免形变与模糊。
* EXIF 方向自动纠正：避免相机旋转信息导致的横竖颠倒。
* 信箱式填充到目标分辨率：不放大原始内容，余量以纯色背景填充至 1280×720。
* 透明图处理：将 RGBA 合成到指定背景色后输出。
* 批量处理：遍历目录内常见格式图片（jpg/jpeg/png/bmp/webp/tiff）。

## 处理流程

1. 读取原图并应用 `ImageOps.exif_transpose` 纠正方向。
2. 若宽或高超过目标分辨率，则计算统一 stride，执行“像素间隔采样”进行整数倍下采样；否则不缩放。
3. 将下采样后的图像居中贴到 1280×720 画布上（信箱式填充）；若仍有超过目标尺寸的边界，居中裁剪而不变形。
4. 按原扩展名保存；JPEG 以较高质量写出。

## 目录结构与默认路径

```text
input_folder  = /home/mm/projects/3dmem/utils/test_photo/image_origin
output_folder = /home/mm/projects/3dmem/utils/test_photo/image_compress
```

> 如需修改，请在脚本顶部更改 `input_folder` 与 `output_folder`。

## 依赖环境

* Python 3.8+
* Pillow
* NumPy

安装依赖：

```bash
pip install pillow numpy
```

## 使用方法

1. 将待处理图片放入 `input_folder`。
2. 运行脚本：

   ```bash
   python3 Pixelbox.py
   ```
3. 处理完成的文件输出到 `output_folder`，终端会打印处理进度与结果路径。

## 参数与可配置项

* 目标分辨率：在脚本顶部修改

  ```python
  TARGET_W, TARGET_H = 1280, 720
  ```
* 背景色（信箱填充颜色）：

  ```python
  letterbox_to_target(..., bg_color=(0, 0, 0))  # 默认为黑色
  ```
* 支持的扩展名：

  ```python
  valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
  ```

## 关键设计说明

### 1) `pixel_subsample_keep_shape(img, target_w, target_h)`

* 仅当原图在任一维度大于目标尺寸时才执行下采样。
* stride 取 `min(floor(w/target_w), floor(h/target_h))` 的下界再限制为 ≥1，且对 x/y 统一，避免比例失衡。
* 使用 NumPy 的步进切片 `arr[::stride, ::stride]` 实现“像素间隔采样”，等价于最近邻整数倍下采样，锐度可控、速度快。

### 2) `letterbox_to_target(img, target_w, target_h, bg_color)`

* 不对小图做上采样，保持清晰度与纹理。
* 若仍有超过目标画布的边界（少见），进行中心裁剪以匹配目标分辨率。
* 对 RGBA 图像，先与背景色合成，避免透明边导致的保存异常。

## 输出规则

* PNG/WebP/TIFF：直接保存（保留无损特性；透明已在上一步合成到背景）。
* JPEG/JPG：以 `quality=95` 写出，质量与体积平衡。

## 常见问题

1. 处理后图片四周有黑边
   说明原图宽高比与 16:9 不一致，信箱式填充会保留原比例，留出填充边。可在 `bg_color` 处自定义背景色。

2. 想“填满画面”而不是留边
   目前实现是信箱式填充以避免放大或裁剪。如需“等比裁剪填充满画面”，可在 `letterbox_to_target` 中将逻辑改为：

   * 先按比例等比缩放至“至少一边等于目标尺寸，另一边大于等于目标尺寸”，再中心裁剪到目标分辨率。

3. 透明 PNG 输出成黑底
   透明通道会被合成到 `bg_color` 指定的底色。希望保留透明的话，需要改写逻辑：让目标画布为 RGBA，并以 PNG 输出。

4. 性能优化
   大量图片时，可考虑开启多进程处理，或在 HDD 上分批次运行以减少随机读写压力。

## 示例日志

```text
已处理: 001.jpg
已处理: 002.png
已处理: 003.webp
全部图片已按像素间隔采样并输出到: /home/mm/projects/3dmem/utils/test_photo/image_compress
```

