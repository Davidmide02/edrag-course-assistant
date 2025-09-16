# from tqdm import tqdm

# # Text extraction
# from PyPDF2 import PdfReader
# from pathlib import Path
# from typing import List, Dict, Tuple, Optional

# def extract_text_from_pdf(path: str) -> List[Tuple[str, Optional[int]]]:
#     """Return list of (text, page_number) for each page."""
#     reader = PdfReader(path)
#     pages = []
#     print(f"PDF has {len(reader.pages)} pages")
#     for i, page in tqdm(enumerate(reader.pages)):
#         try:
#             text = page.extract_text() or ""
#         except Exception:
#             text = ""
#         pages.append((text, i + 1))
#     open(f"{extract_text_from_pdf}.txt", "w").write(pages)
#     return pages


# extract_text_from_pdf("./data/lecture1.pdf")


from typing import List, Tuple, Optional
from PyPDF2 import PdfReader
from tqdm import tqdm
import os

def extract_text_from_pdf(path: str) -> List[Tuple[str, Optional[int]]]:
    """Return list of (text, page_number) for each page."""
    reader = PdfReader(path)
    pages = []
    print(f"PDF has {len(reader.pages)} pages")

    for i, page in tqdm(enumerate(reader.pages), total=len(reader.pages), desc="Extracting"):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append((text, i + 1))

    # Save to a .txt file
    output_path = os.path.splitext(path)[0] + ".txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for text, page_num in pages:
            f.write(f"--- Page {page_num} ---\n{text}\n\n")

    return pages

# Example usage
extract_text_from_pdf("./data/simultaneous_equ.pdf")