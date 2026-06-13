"""
One-off validation test against all the ACRA files on my machine. Not reproducible.
"""

# pylint: skip-file
# ruff: noqa
import sys
from pathlib import Path
import io
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import config
from core.pdf_processing import process_pdf


def process_one_file(filepath: Path):
    try:
        pdf = io.BytesIO(filepath.read_bytes())
        individuals = process_pdf(pdf)
        return filepath, len(individuals) > 0  # (path, success)
    except Exception:
        return filepath, False


def main():
    directory = Path(config.PDF_TESTING_PATH)
    files = list(directory.iterdir())
    failed = []

    with ProcessPoolExecutor(max_workers=8) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(process_one_file, f): f for f in files}
        for future in tqdm(
            as_completed(future_to_file), total=len(files), desc="Processing PDFs"
        ):
            filepath, success = future.result()
            if not success:
                failed.append(filepath)

    print(f"Total failures: {len(failed)}/{len(files)}")
    if failed:
        print("Failed files:", failed)


if __name__ == "__main__":
    main()
