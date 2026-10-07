"""
genz.cli
--------
Command-line entry point.

    python3 -m genz.cli build hello.gz -o dist/
    python3 -m genz.cli build hello.gz -o dist/ --watch
"""

import argparse
import os
import sys
import time

from . import compile_source
from .lexer import LexError
from .parser import ParseError


def _build_once(src_path: str, out_dir: str) -> bool:
    try:
        with open(src_path, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"genz: cannot read {src_path}: {e}", file=sys.stderr)
        return False

    try:
        html, css, js = compile_source(source)
    except (LexError, ParseError) as e:
        print(f"genz: {src_path}: {e}", file=sys.stderr)
        return False

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(out_dir, "style.css"), "w", encoding="utf-8") as f:
        f.write(css)
    with open(os.path.join(out_dir, "script.js"), "w", encoding="utf-8") as f:
        f.write(js)

    print(f"genz: built {src_path} -> {out_dir}/ (index.html, style.css, script.js)")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(prog="genz", description="CodeGenZ compiler")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="compile a .gz file to HTML/CSS/JS")
    build.add_argument("source", help="path to a .gz source file")
    build.add_argument("-o", "--out", default="dist", help="output directory (default: dist)")
    build.add_argument("--watch", action="store_true", help="rebuild on file change")

    args = parser.parse_args(argv)

    if args.command == "build":
        ok = _build_once(args.source, args.out)
        if not args.watch:
            sys.exit(0 if ok else 1)

        print("genz: watching for changes (ctrl+c to stop)...")
        last_mtime = os.path.getmtime(args.source) if os.path.exists(args.source) else 0
        try:
            while True:
                time.sleep(0.5)
                if not os.path.exists(args.source):
                    continue
                mtime = os.path.getmtime(args.source)
                if mtime != last_mtime:
                    last_mtime = mtime
                    _build_once(args.source, args.out)
        except KeyboardInterrupt:
            print("\ngenz: stopped watching")


if __name__ == "__main__":
    main()
