#!/usr/bin/env python3
import argparse
import os
import tempfile

import numpy as np
from PIL import Image

from . import convert_pdf_to_png
from . import create_pixel_diff_image
from . import pad_images_to_same_size
from . import to_ascii_art


def main():
    parser = argparse.ArgumentParser(description="Custom PDF diff tool for Git")
    parser.add_argument("pdf1", help="Path to the first PDF file")
    parser.add_argument("pdf2", help="Path to the second PDF file")
    parser.add_argument("--asciiart", action="store_true", help="Convert diff image to ASCII art and print to console")
    parser.add_argument("--exit0", action="store_true", help="Output exit code 0 even when files are different")
    parser.add_argument("--storediff", type=str, help="Store the diff image to a given path")
    args = parser.parse_args()

    if not os.path.exists(args.pdf1):
        raise FileNotFoundError(f"Input PDF file '{args.pdf1}' not found.")
    if not os.path.exists(args.pdf2):
        raise FileNotFoundError(f"Input PDF file '{args.pdf2}' not found.")

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp_png1, tempfile.NamedTemporaryFile(
        suffix=".png"
    ) as tmp_png2, tempfile.NamedTemporaryFile(suffix=".png") as tmp_diff:
        convert_pdf_to_png(args.pdf1, tmp_png1.name)
        convert_pdf_to_png(args.pdf2, tmp_png2.name)

        img1 = Image.open(tmp_png1.name)
        img2 = Image.open(tmp_png2.name)

        # ensure that the saved images are the same size
        img1, img2 = pad_images_to_same_size(img1, img2)
        img1.save(tmp_png1.name)
        img2.save(tmp_png2.name)

        pixel_diff = np.sum(np.array(img1) != np.array(img2))

        if pixel_diff == 0:
            exit(0)  # Signal to Git that files are the same
        else:
            if args.storediff:
                diff_image = args.storediff
            else:
                diff_image = tmp_diff.name
            # apply_image_magick_operations(diff_image)
            print(f"Changed: {args.pdf1}")
            if args.asciiart:
                create_pixel_diff_image(tmp_png1.name, tmp_png2.name, diff_image)
                with tempfile.NamedTemporaryFile(suffix=".txt") as tmp_diff_txt:
                    to_ascii_art(diff_image, tmp_diff_txt.name)
                    with open(tmp_diff_txt.name, "rt") as fobj:
                        print()
                        print(fobj.read())

            if not args.exit0:
                exit(1)  # Signal to Git that files are different


if __name__ == "__main__":
    main()
