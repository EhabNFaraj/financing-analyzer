import argparse
from .ingest import load_raw
from .analyze import kpis, save_excel_summary
from .viz import build_charts

parser = argparse.ArgumentParser(description="Toro Auto Financing Analyzer")
sub = parser.add_subparsers(dest="cmd")

sub.add_parser("ingest")
sub.add_parser("analyze")
sub.add_parser("run-weekly")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.cmd == "ingest":
        load_raw()
        print("Ingest complete.")
    elif args.cmd == "analyze":
        k = kpis(); p = save_excel_summary(k)
        print(f"Saved {p}")
    elif args.cmd == "run-weekly":
        load_raw(); k = kpis(); p = save_excel_summary(k); build_charts()
        print(f"Weekly package ready: {p}")
    else:
        parser.print_help()
