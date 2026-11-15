"""CLI: python main.py --query 'Tech Sector Q3 Analysis' [--offline]"""
import argparse
import os
import sys
from pathlib import Path


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Multi-agent market research & report generator")
    p.add_argument("--query", default="Tech Sector Q3 Analysis", help="Research topic")
    p.add_argument("--output-dir", default=os.getenv("OUTPUT_DIR", "output"))
    p.add_argument("--offline", action="store_true",
                   help="Run the pipeline on bundled sample data with no LLM/API keys (demo only)")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    os.environ["OUTPUT_DIR"] = args.output_dir
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    from crew.analysis import summarize_csv, summary_markdown
    from crew.benchmarks import BenchmarkLogger
    from crew.pdf_report import build_pdf

    bench = BenchmarkLogger(args.query, out / "benchmarks.json")
    bench.start()

    if args.offline:
        from crew.demo import run_offline
        report_md = run_offline(args.query, out, bench)
    else:
        if not os.getenv("OPENAI_API_KEY"):
            sys.exit("OPENAI_API_KEY is missing. Copy .env.example to .env, or use --offline.")
        from crew.crew import build_crew
        result = build_crew(args.query, bench).kickoff()
        report_md = getattr(result, "raw", None) or str(result)

    csv_path = out / "metrics.csv"
    summary_df = summarize_csv(str(csv_path)) if csv_path.exists() else None

    md = report_md
    if csv_path.exists():
        md += "\n\n## Appendix: Statistical Summary\n\n" + summary_markdown(str(csv_path)) + "\n"
    (out / "market_report.md").write_text(md)

    with bench.timed("PDF compilation", "report compiler"):
        pdf = build_pdf(report_md, out / "market_report.pdf", f"Market Report: {args.query}",
                        args.query, summary_df)
    run = bench.finish()
    print(f"Markdown: {out / 'market_report.md'}\nPDF: {pdf}\nBenchmarks: {out / 'benchmarks.json'} "
          f"({run['total_seconds']}s total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
