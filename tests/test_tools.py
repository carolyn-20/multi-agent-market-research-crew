import pytest

from crew import tools


def test_extract_text_strips_scripts_and_nav():
    html = "<html><nav>menu</nav><script>x=1</script><body><p>Revenue  rose</p><p>10%</p></body></html>"
    assert tools.extract_text(html) == "Revenue rose 10%"


def test_search_requires_api_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        tools.search_web("x")


def test_tavily_search_and_scrape_with_fallback(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "k")

    class Resp:
        def raise_for_status(self): pass
        def json(self):
            return {"results": [{"title": "T1", "url": "http://a", "content": "snippet A"},
                                {"title": "T2", "url": "http://b", "content": "snippet B"}]}

    monkeypatch.setattr(tools.requests, "post", lambda *a, **k: Resp())
    monkeypatch.setattr(tools, "scrape_url",
                        lambda url, **k: "page text" if url == "http://a" else (_ for _ in ()).throw(OSError()))
    out = tools.search_and_scrape("q")
    assert "### T1" in out and "page text" in out
    assert "snippet B" in out  # scrape failure falls back to snippet


def test_write_metrics_csv_validates(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))
    path = tools.write_metrics_csv("company,rev\nA,1\nB,2")
    assert path.endswith("metrics.csv") and (tmp_path / "metrics.csv").exists()
    with pytest.raises(ValueError):
        tools.write_metrics_csv("a,b\nx,y")
