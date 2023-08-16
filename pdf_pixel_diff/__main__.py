#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image


def scale_image_to_fit(image_path, output_path):
    cols, rows = os.get_terminal_size()
    pixel_multiplier = 8
    width, height = cols * pixel_multiplier, rows * pixel_multiplier
    img = Image.open(image_path)
    ratio = np.minimum(width / img.width, height / img.height)
    new_width, new_height = (int(img.width * ratio), int(img.height * ratio))
    resized_img = img.resize((new_width, new_height))
    resized_img.save(output_path)


def to_ascii_art(in_png, out_txt):
    import img2unicode

    # Use Unicode Block Elements
    cols, rows = os.get_terminal_size()
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


def main():
    parser = argparse.ArgumentParser(description="Custom PDF diff tool for Git")
    parser.add_argument("pdf1", help="Path to the first PDF file")
    parser.add_argument("pdf2", help="Path to the second PDF file")
    parser.add_argument("--asciiart", action="store_true", help="Convert diff image to ASCII art and print to console")
    parser.add_argument("--exit0", action="store_true", help="Output exit code 0 even when files are different")
    args = parser.parse_args()

    if not os.path.exists(args.pdf1):
        raise FileNotFoundError(f"Input PDF file '{args.pdf1}' not found.")
    if not os.path.exists(args.pdf2):
        raise FileNotFoundError(f"Input PDF file '{args.pdf2}' not found.")

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp_png1, tempfile.NamedTemporaryFile(
        suffix=".png"
    ) as tmp_png2, tempfile.NamedTemporaryFile(suffix=".png") as tmp_diff:
        del tmp_diff
        convert_pdf_to_png(args.pdf1, tmp_png1.name)
        convert_pdf_to_png(args.pdf2, tmp_png2.name)

        pixel_diff = np.sum(np.array(Image.open(tmp_png1.name)) != np.array(Image.open(tmp_png2.name)))

        if pixel_diff == 0:
            exit(0)  # Signal to Git that files are the same
        else:
            diff_image = "diff.png"
            # apply_image_magick_operations(diff_image)
            if args.asciiart:
                create_pixel_diff_image(tmp_png1.name, tmp_png2.name, diff_image)
                to_ascii_art(diff_image, "diff.txt")
                with open("diff.txt", "rt") as fobj:
                    print()
                    print(fobj.read())
            else:
                print(f"Changed: {args.pdf1}")

            if not args.exit0:
                exit(1)  # Signal to Git that files are different


if __name__ == "__main__":
    main()
