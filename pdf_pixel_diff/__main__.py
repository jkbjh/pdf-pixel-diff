#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image


def convert_pdf_to_png(pdf_file, png_file):
    subprocess.check_call(["convert", "-density", "75", "-define", "png:color-type=6", pdf_file, png_file])


def compare_images(image1, image2):
    img1 = np.array(Image.open(image1))
    img2 = np.array(Image.open(image2))

    if img1.shape != img2.shape:
        return False

    pixel_diff = np.sum(img1 != img2)

    if pixel_diff == 0:
        return True
    else:
        diff = np.abs(img1 - img2)
        diff_img = Image.fromarray(diff.astype(np.uint8))
        diff_img.save("diff.png")
        return False


def main():
    parser = argparse.ArgumentParser(description="Custom PDF diff tool for Git")
    parser.add_argument("pdf1", help="Path to the first PDF file")
    parser.add_argument("pdf2", help="Path to the second PDF file")
    args = parser.parse_args()

    if not os.path.exists(args.pdf1):
        raise FileNotFoundError(f"Input PDF file '{args.pdf1}' not found.")
    if not os.path.exists(args.pdf2):
        raise FileNotFoundError(f"Input PDF file '{args.pdf2}' not found.")

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp_png1, tempfile.NamedTemporaryFile(suffix=".png") as tmp_png2:
        convert_pdf_to_png(args.pdf1, tmp_png1.name)
        convert_pdf_to_png(args.pdf2, tmp_png2.name)

        if compare_images(tmp_png1.name, tmp_png2.name):
            exit(0)  # Signal to Git that files are the same
        else:
            exit(1)  # Signal to Git that files are different


if __name__ == "__main__":
    main()
