"""CLI entry point: `python -m retail_scraper`."""
from __future__ import annotations

import argparse
import sys

from .config import ScraperConfig
from .runner import run


def _parse_args(argv):
    p = argparse.ArgumentParser(
        prog="retail_scraper",
        description="Scrape off-market retail property leads from public sources.",
    )
    p.add_argument("--states", nargs="+", default=None,
                   help="Two-letter state codes to target (e.g. CA TX FL).")
    p.add_argument("--max-sqft", type=float, default=None,
                   help="Hard cap on total square feet (default 20000).")
    p.add_argument("--target", type=int, default=None,
                   help="Target number of valid properties (default 50).")
    p.add_argument("--out-csv", default=None)
    p.add_argument("--out-json", default=None)
    p.add_argument("--out-rejected", default=None)
    p.add_argument("--out-summary", default=None)
    p.add_argument("--log-level", default=None,
                   choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    p.add_argument("--disable", nargs="*", default=[],
                   help="Adapter names to disable, e.g. --disable fdic_ore sba_oreo")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    cfg = ScraperConfig()
    if args.states:
        cfg.states = [s.upper() for s in args.states]
    if args.max_sqft is not None:
        cfg.max_total_sqft = args.max_sqft
    if args.target is not None:
        cfg.target_count = args.target
    if args.out_csv:
        cfg.output_csv = args.out_csv
    if args.out_json:
        cfg.output_json = args.out_json
    if args.out_rejected:
        cfg.output_rejected_csv = args.out_rejected
    if args.out_summary:
        cfg.output_summary_md = args.out_summary
    if args.log_level:
        cfg.log_level = args.log_level
    for name in args.disable:
        attr = f"enable_{name}"
        if hasattr(cfg, attr):
            setattr(cfg, attr, False)
    return run(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
