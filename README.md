# Pixelbox

**Pixelbox** performs adaptive pixel subsampling and letterbox padding to standardize images without distortion or upscaling.
It ensures consistent 1280×720 outputs while preserving original proportions, texture detail, and visual fidelity.

---

## Overview

Pixelbox is a lightweight image preprocessing tool designed for datasets, vision pipelines, and general media preparation.
It automatically reduces image resolution by integer pixel strides and pads the result to the target frame using a letterbox (non-scaling) method.

### Key Features

* **Pixel-interval subsampling:** Uses integer stride sampling to downscale without aliasing or geometric distortion.
* **EXIF orientation correction:** Automatically adjusts image orientation from camera metadata.
* **Letterbox padding:** Centers the image on a fixed-size canvas (default 1280×720) with configurable background color.
* **Transparency handling:** Merges RGBA images onto the background color.
* **Batch processing:** Iterates through supported formats in a folder automatically.

---

## Processing Pipeline

1. Load and transpose the image according to EXIF data.
2. If the image exceeds the target size in either dimension, compute a uniform stride and perform pixel-interval subsampling.
3. Center the result on a target canvas (letterbox padding).
4. Save the processed image with the same extension as the input.

---

## Default Paths

```text
Input:  /home/mm/projects/3dmem/utils/test_photo/image_origin
Output: /home/mm/projects/3dmem/utils/test_photo/image_compress
```

Modify `input_folder` and `output_folder` at the top of the script as needed.

---

## Requirements

* Python 3.8 or newer
* Pillow
* NumPy

Install dependencies:

```bash
pip install pillow numpy
```

---

## Usage

1. Place your source images into the input folder.
2. Run:

   ```bash
   python Pixelbox.py
   ```
3. Processed images will be written to the output folder, with progress printed in the terminal.

---

## Configurable Parameters

* **Target resolution:**

  ```python
  TARGET_W, TARGET_H = 1280, 720
  ```
* **Background color:**

  ```python
  letterbox_to_target(..., bg_color=(0, 0, 0))
  ```
* **Supported extensions:**

  ```python
  valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
  ```

---

## Core Design

### pixel_subsample_keep_shape

* Executes integer-stride pixel sampling to reduce resolution uniformly along both axes.
* Prevents aspect distortion by using the smaller stride of the two dimensions.
* Avoids any scaling operation; pure sampling ensures crisp edges and accurate pixel ratios.

### letterbox_to_target

* Pads smaller images to the target size without scaling.
* For oversized images, performs center cropping while maintaining proportions.
* Handles transparent images by merging onto a solid background before output.

---

## Output Policy

* **Lossless formats (PNG/WebP/TIFF):** Saved directly.
* **JPEG formats:** Saved at `quality=95` for a balance between compression and detail.

---

## Example Console Output

```text
Processed: img_001.jpg
Processed: img_002.png
Processed: img_003.webp
All images processed and saved to: /home/mm/projects/3dmem/utils/test_photo/image_compress
```

---

## Notes

* Black borders appear when the original aspect ratio differs from 16:9. Change `bg_color` to match your preference.
* To fill the frame instead of padding, modify `letterbox_to_target` to perform proportional scaling followed by central cropping.
* For transparent PNGs, transparency is flattened against the specified background color.

