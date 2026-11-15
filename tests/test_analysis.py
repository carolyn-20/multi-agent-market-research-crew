"""Pandas Analysis Test: the parser must compute correct statistics on a mock CSV."""
import pytest

from crew.analysis import summarize_csv, summary_markdown
from crew.tools import calculate_financial_metrics


@pytest.fixture
def mock_csv(tmp_path):
    p = tmp_path / "metrics.csv"
    p.write_text("company,revenue,margin\nA,10,0.1\nB,20,0.2\nC,30,0.3\nD,40,0.4\n")
    return str(p)


def test_summary_statistics_are_correct(mock_csv):
    df = summarize_csv(mock_csv)
    assert df.loc["mean", "revenue"] == pytest.approx(25.0)
    assert df.loc["min", "revenue"] == 10
    assert df.loc["max", "revenue"] == 40
    assert df.loc["std", "revenue"] == pytest.approx(12.9099, abs=1e-3)  # sample std
    assert df.loc["mean", "margin"] == pytest.approx(0.25)
    assert "company" not in df.columns  # non-numeric column excluded


def test_markdown_table_shape(mock_csv):
    md = summary_markdown(mock_csv)
    lines = md.splitlines()
    assert lines[0].startswith("|") and "revenue" in lines[0] and "margin" in lines[0]
    assert set(lines[1].replace("|", "").strip()) <= set("-: ")
    assert any(l.startswith("| mean") for l in lines)


def test_no_numeric_columns_raises(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("a,b\nx,y\n")
    with pytest.raises(ValueError):
        summarize_csv(str(p))


def _run(t, **kw):
    return t.run(**kw) if hasattr(t, "run") else t(**kw)


def test_tool_wrapper_returns_markdown(mock_csv):
    out = _run(calculate_financial_metrics, csv_path=mock_csv)
    assert "| mean" in out and "revenue" in out


def test_tool_wrapper_handles_missing_file():
    out = _run(calculate_financial_metrics, csv_path="/nope/missing.csv")
    assert out.startswith("Could not analyse")
