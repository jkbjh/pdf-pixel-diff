#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile

import ascii_magic
import numpy as np
from PIL import Image


def convert_pdf_to_png(pdf_file, png_file):
    subprocess.check_call(["convert", "-density", "75", "-define", "png:color-type=6", pdf_file, png_file])


def create_pixel_diff_image(image1, image2, diff_image):
    subprocess.run(["compare", "-metric", "AE", "-fuzz", "5%", image1, image2, diff_image])
    subprocess.run(["convert", diff_image, "-blur", "0x3", diff_image])  # Apply a blur filter


def main():
    parser = argparse.ArgumentParser(description="Custom PDF diff tool for Git")
    parser.add_argument("pdf1", help="Path to the first PDF file")
    parser.add_argument("pdf2", help="Path to the second PDF file")
    parser.add_argument("--asciiart", action="store_true", help="Convert diff image to ASCII art and print to console")
    args = parser.parse_args()

    if not os.path.exists(args.pdf1):
        raise FileNotFoundError(f"Input PDF file '{args.pdf1}' not found.")
    if not os.path.exists(args.pdf2):
        raise FileNotFoundError(f"Input PDF file '{args.pdf2}' not found.")

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp_png1, tempfile.NamedTemporaryFile(suffix=".png") as tmp_png2:
        convert_pdf_to_png(args.pdf1, tmp_png1.name)
        convert_pdf_to_png(args.pdf2, tmp_png2.name)

        pixel_diff = np.sum(np.array(Image.open(tmp_png1.name)) != np.array(Image.open(tmp_png2.name)))

        if pixel_diff == 0:
            exit(0)  # Signal to Git that files are the same
        else:
            diff_image = "diff.png"
            create_pixel_diff_image(tmp_png1.name, tmp_png2.name, diff_image)

            if args.asciiart:
                ascii_art = ascii_magic.from_image(diff_image)
                ascii_art.to_terminal()
            else:
                print("Files are different, use --asciiart flag to view ASCII art representation.")

            exit(1)  # Signal to Git that files are different


if __name__ == "__main__":
    main()
