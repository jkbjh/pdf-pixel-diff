#!/usr/bin/env python3
import shutil
import subprocess

import img2unicode  # slow import.
import numpy as np
from PIL import Image


def pad_images_to_same_size(image1, image2):
    width1, height1 = image1.size
    width2, height2 = image2.size
    max_width = max(width1, width2)
    max_height = max(height1, height2)
    padded_image1 = Image.new("RGB", (max_width, max_height), (255, 255, 255))  # White background
    padded_image2 = Image.new("RGB", (max_width, max_height), (255, 255, 255))  # White background
    left_padding1 = (max_width - width1) // 2
    top_padding1 = (max_height - height1) // 2
    left_padding2 = (max_width - width2) // 2
    top_padding2 = (max_height - height2) // 2
    padded_image1.paste(image1, (left_padding1, top_padding1))
    padded_image2.paste(image2, (left_padding2, top_padding2))
    return padded_image1, padded_image2


def get_terminal_size():
    return shutil.get_terminal_size(fallback=(120, 50))


def scale_image_to_fit(image_path, output_path):
    cols, rows = get_terminal_size()
    pixel_multiplier = 8
    width, height = cols * pixel_multiplier, rows * pixel_multiplier
    img = Image.open(image_path)
    ratio = np.minimum(width / img.width, height / img.height)
    new_width, new_height = (int(img.width * ratio), int(img.height * ratio))
    resized_img = img.resize((new_width, new_height))
    resized_img.save(output_path)


def to_ascii_art(in_png, out_txt):
    # Use Unicode Block Elements
    cols, rows = get_terminal_size()
    scale_image_to_fit(in_png, "diff.scaled.png")
    optimizer = img2unicode.FastQuadDualOptimizer()
    renderer = img2unicode.Renderer(default_optimizer=optimizer, max_h=rows, max_w=cols)
    renderer.render_terminal("diff.scaled.png", out_txt)


def convert_pdf_to_png(pdf_file, png_file):
    subprocess.check_call(["convert", "-density", "75", "-define", "png:color-type=6", pdf_file, png_file])


def create_pixel_diff_image(image1, image2, diff_image):
    # subprocess.run(["compare", "-metric", "AE", "-fuzz", "5%", image1, image2, diff_image])
    # subprocess.run(["compare", "-metric", "AE", "-fuzz", "5%", image1, image2, diff_image])
    # subprocess.run(["compare", "-density", "300", image1, image2, "-compose", "src", diff_image])# diff.jpeg
    subprocess.run(
        "convert '(' " + image1 + " -flatten -grayscale Rec709Luminance ')' "
        "'(' " + image2 + " -flatten -grayscale Rec709Luminance ')' "
        "'(' -clone 0-1 -compose darken -composite ')' "
        "-channel RGB -combine " + diff_image,
        shell=True,
    )


def apply_image_magick_operations(image_path):
    subprocess.check_call(["convert", image_path, "-blur", "0x3", "-contrast-stretch", "10%", image_path])
