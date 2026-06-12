"""
One-off validation test against all the ACRA files on my machine. Not reproducible.
"""

import sys
from pathlib import Path

# ruff: noqa: E402
# ruff: noqa: S112

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.pdf_processing import process_pdf
from tqdm import tqdm
import config
import io

directory = Path(config.PDF_TESTING_PATH)

fail = 0
failed = []
for filepath in tqdm(list(directory.iterdir()), desc="Processing PDFs"):
    try:
        pdf = io.BytesIO(filepath.read_bytes())
        individuals = process_pdf(pdf)
        if not individuals:
            fail += 1
            failed.append(filepath)
    except Exception:
        continue
print(f"Total failures: {fail}/{len(list(directory.iterdir()))}\n")
print(f"Failed files: {failed}")
