"""PDF Layout Test: the compiler must write a valid, paginated PDF without styling errors."""
import pandas as pd
from pypdf import PdfReader

from crew.pdf_report import build_pdf

MD = """# Tech Sector Q3
## Overview
Revenue grew **strongly**; margins were *stable* \u2192 positive outlook. Unicode \u2265 ok \u2603.
- Point one
- Point two
1. First
## Table
| Company | Growth |
|---|---|
| A | 10 |
| B | 12 |
"""


def _df():
    return pd.DataFrame({"revenue": [10, 20, 30], "margin": [0.1, 0.2, 0.3]}).describe()


def test_pdf_is_valid_and_has_banner_table_and_page_numbers(tmp_path):
    out = build_pdf(MD, tmp_path / "r.pdf", "Market Report", "Tech Sector Q3", _df())
    assert out.exists() and out.read_bytes().startswith(b"%PDF")
    reader = PdfReader(str(out))
    text = "\n".join(p.extract_text() for p in reader.pages)
    assert "Market Report" in text and "Tech Sector Q3" in text
    assert "Statistical Summary" in text and "mean" in text
    assert f"Page 1 of {len(reader.pages)}" in text
    assert reader.metadata.title == "Market Report"


def test_long_report_is_multi_page_with_correct_numbering(tmp_path):
    long_md = "# Big\n" + "\n\n".join(f"## S{i}\n" + ("Lorem ipsum dolor sit amet. " * 40) for i in range(25))
    out = build_pdf(long_md, tmp_path / "long.pdf", "Long", "q")
    reader = PdfReader(str(out))
    n = len(reader.pages)
    assert n > 1
    assert f"Page {n} of {n}" in reader.pages[-1].extract_text()


def test_markup_characters_do_not_raise(tmp_path):
    out = build_pdf("Cost < 5 & > 3 <b>unclosed", tmp_path / "x.pdf", "T & <T>", "a<b")
    assert out.exists()
