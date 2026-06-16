from __future__ import annotations

import argparse
import sys
from typing import Optional

from .config import RefinerConfig
from .core import refine_prompt


def _read_draft(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            return fh.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="refine",
        description="Refine a draft prompt into a token-efficient prompt via Gemini.",
    )
    p.add_argument("prompt", nargs="?", help="Draft prompt text. Omit to read --file or stdin.")
    p.add_argument("-f", "--file", help="Read the draft prompt from a file.")
    p.add_argument("-m", "--model", default=None, help="Gemini model id (default: gemini-2.5-flash).")
    p.add_argument("--no-research", dest="research", action="store_false", default=None,
                   help="Disable Google Search grounding (faster, cheaper).")
    p.add_argument("--research", dest="research", action="store_true", default=None,
                   help="Force-enable Google Search grounding.")
    p.add_argument("-t", "--temperature", type=float, default=None)
    p.add_argument("--max-tokens", dest="max_output_tokens", type=int, default=None)
    p.add_argument("--thinking", dest="thinking_budget", type=int, default=None,
                   help="Thinking token budget (0 = off, fastest).")
    p.add_argument("-l", "--language", dest="output_language", default=None,
                   help="Output language (default: pt-BR).")
    p.add_argument("--api-key", default=None, help="Override the GEMINI_API_KEY env var.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    args = build_parser().parse_args(argv)
    draft = _read_draft(args)
    if not draft.strip():
        print("Error: no draft prompt provided (positional arg, --file, or stdin).",
              file=sys.stderr)
        return 2
    try:
        config = RefinerConfig.from_env(
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            thinking_budget=args.thinking_budget,
            research=args.research,
            output_language=args.output_language,
        )
        refined = refine_prompt(draft, config)
    except Exception as exc:  # surface a clean one-line error to stderr
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(refined)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
