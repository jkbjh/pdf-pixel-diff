import subprocess
import sys


def test_main():
    result11 = subprocess.run([sys.executable, "-m", "pdf_pixel_diff", "tests/version1.pdf", "tests/version1.pdf"])
    assert result11.returncode == 0
    result12 = subprocess.run([sys.executable, "-m", "pdf_pixel_diff", "tests/version1.pdf", "tests/version2.pdf"])
    assert result12.returncode == 1
    result22 = subprocess.run([sys.executable, "-m", "pdf_pixel_diff", "tests/version1.pdf", "tests/version1.pdf"])
    assert result22.returncode == 0
