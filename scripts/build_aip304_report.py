#!/usr/bin/env python3
"""Build and check the AIP304 CW2 report; Python's standard library only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "report"
MAX_PAGES = 5
LANGUAGES = ("en", "zh")
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b|待填写|待补充|占位", re.I)
FONTS = ("Latin Modern Roman", "Latin Modern Sans", "Latin Modern Mono",
         "Noto Serif CJK SC", "Noto Sans CJK SC")


class BuildError(Exception):
    """An actionable report or toolchain error."""


def command(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    result = subprocess.run(args, text=True, encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=300, **kwargs)
    if result.returncode:
        raise BuildError(f"Command failed ({result.returncode}): {' '.join(args)}\n{result.stdout[-6000:]}")
    return result


def require_text(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"{field} must contain non-empty text.")
    return value.strip()


def read_config(path: Path, languages: tuple[str, ...], mode: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"Cannot read report configuration {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BuildError("Report configuration must be a JSON object.")
    if type(data.get("option")) is not int or data["option"] not in (1, 2):
        raise BuildError("option must be the integer 1 or 2.")
    authors = data.get("authors")
    if not isinstance(authors, list) or not 1 <= len(authors) <= 3:
        raise BuildError("authors must contain 1-3 students, each with name and id.")
    fields = []
    for i, author in enumerate(authors):
        if not isinstance(author, dict):
            raise BuildError(f"authors[{i}] must be an object with name and id.")
        for key in ("name", "id"):
            name = f"authors[{i}].{key}"
            author[key] = require_text(author.get(key), name)
            fields.append((name, author[key]))
    if len({a["id"].casefold() for a in authors}) != len(authors):
        raise BuildError("Each author must have a distinct student ID.")
    for field in ("title", "ai_disclosure", "contributions"):
        if not isinstance(data.get(field), dict):
            raise BuildError(f"{field} must have language keys en and/or zh.")
        for language in languages:
            name = f"{field}.{language}"
            data[field][language] = require_text(data[field].get(language), name)
            fields.append((name, data[field][language]))
    if mode == "submission":
        remaining = [name for name, value in fields if PLACEHOLDER.search(value)]
        if remaining:
            raise BuildError("Submission blocked: replace placeholder metadata in " + ", ".join(remaining))
    return data


def escape_tex(value: str) -> str:
    # Metadata is plain text, never executable TeX or shell code.
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                    "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
                    "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(c, " " if c in "\r\n" else c) for c in value)


def metadata_tex(data: dict, language: str, mode: str) -> str:
    values = {
        "ReportOption": str(data["option"]),
        "ReportTitle": escape_tex(data["title"][language]),
        "ReportAuthors": r" \quad | \quad ".join(
            escape_tex(a["name"]) + " (" + escape_tex(a["id"]) + ")" for a in data["authors"]),
        "ReportAIDisclosure": escape_tex(data["ai_disclosure"][language]),
        "ReportContributions": escape_tex(data["contributions"][language]),
    }
    flags = ("\\ReportChinese" + ("true" if language == "zh" else "false") + "\n"
             "\\ReportSubmission" + ("true" if mode == "submission" else "false") + "\n")
    return flags + "".join("\\newcommand{\\" + key + "}{" + value + "}\n" for key, value in values.items())


def check_source_structure() -> None:
    # A helpful source guard, not a semantic proof of coursework compliance.
    forbidden = re.compile(r"\\(?:appendix\b|tableofcontents\b|begin\s*\{titlepage\})")
    for path in sorted(SOURCE.rglob("*.tex")):
        text = re.sub(r"(?<!\\)%[^\n]*", "", path.read_text(encoding="utf-8"))
        if forbidden.search(text):
            raise BuildError(f"Remove the cover/contents/appendix command in {path.relative_to(ROOT)}. "
                             "CW2 has one PDF, at most five pages, with no separate cover or appendix.")


def check_toolchain() -> dict:
    required = ("latexmk", "xelatex", "bibtex", "kpsewhich", "pdfinfo", "pdffonts", "pdftotext", "fc-match")
    missing = [name for name in required if not shutil.which(name)]
    if missing:
        raise BuildError("Missing tools: " + ", ".join(missing) + ". See report/README.md.")
    for package in ("fontspec.sty", "xeCJK.sty", "natbib.sty", "geometry.sty",
                    "tabularx.sty", "titlesec.sty", "caption.sty", "fancyhdr.sty", "xurl.sty"):
        command(["kpsewhich", package])
    for family in FONTS:
        match = command(["fc-match", "--format=%{family}", family]).stdout
        if family.casefold() not in match.casefold():
            raise BuildError(f"Font {family!r} is unavailable; fontconfig substituted {match!r}. "
                             "Install fonts-lmodern and fonts-noto-cjk.")
    return {name: command([name, "--version"]).stdout.splitlines()[0]
            for name in ("xelatex", "bibtex")}


def check_log(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = (
        r"Missing character:", r"There were undefined (?:references|citations)",
        r"(?:Citation|Reference) [^\n]* undefined", r"multiply[ -]defined",
        r"Rerun to get cross-references right",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            raise BuildError(f"Unresolved typesetting issue in {path.name}: {match.group(0)}")
    for match in re.finditer(r"Overfull \\[hv]box \(([0-9.]+)pt too (?:wide|high)\)", text):
        if float(match.group(1)) > 2:
            raise BuildError(f"Content overflows its box in {path.name}: {match.group(0)}. "
                             "Shorten/reflow the text, table or figure; do not reduce readability to fit.")


def inspect_pdf(pdf: Path, language: str, mode: str) -> dict:
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise BuildError(f"Expected PDF is missing or empty: {pdf}")
    info = command(["pdfinfo", str(pdf)]).stdout
    match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.M)
    if not match:
        raise BuildError(f"Cannot determine total page count for {pdf.name}.")
    pages = int(match.group(1))
    if not 1 <= pages <= MAX_PAGES:
        raise BuildError(f"{pdf.name} has {pages} pages; CW2 allows 1-{MAX_PAGES} total, "
                         "including references, AI disclosure and contributions. Edit the content and rebuild.")
    font_rows = command(["pdffonts", str(pdf)]).stdout.splitlines()[2:]
    fonts = []
    for row in font_rows:
        parts = row.split()
        if len(parts) < 8:
            continue
        if parts[-5] != "yes":
            raise BuildError(f"Font is not embedded in {pdf.name}: {parts[0]}")
        fonts.append(parts[0])
    if not fonts:
        raise BuildError(f"No embedded text fonts found in {pdf.name}.")
    text = command(["pdftotext", "-enc", "UTF-8", str(pdf), "-"]).stdout
    if "AIP304" not in text or "\ufffd" in text:
        raise BuildError(f"Unexpected or unreadable extracted text in {pdf.name}.")
    if language == "zh" and not re.search(r"[\u3400-\u9fff]", text):
        raise BuildError("The Chinese PDF has no extractable Chinese text.")
    if mode == "submission" and PLACEHOLDER.search(text):
        raise BuildError(f"Submission blocked: a placeholder remains in the rendered {language} PDF.")
    return {"file": pdf.name, "language": language, "mode": mode, "pages": pages,
            "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "fonts": fonts}


def build_one(data: dict, language: str, mode: str) -> tuple[Path, dict]:
    name = f"AIP304-CW2-{language}-{mode}"
    work = ROOT / "build" / "aip304-cw2" / mode / language
    # This fixed directory contains only generated files from this script.
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (work / "metadata.tex").write_text(metadata_tex(data, language, mode), encoding="utf-8")
    env = os.environ.copy()
    env["TEXINPUTS"] = str(work) + os.pathsep + str(SOURCE) + os.pathsep + env.get("TEXINPUTS", "")
    env["BIBINPUTS"] = str(SOURCE) + os.pathsep + env.get("BIBINPUTS", "")
    args = ["latexmk", "-norc", "-xelatex", "-bibtex", "-interaction=nonstopmode",
            "-halt-on-error", "-file-line-error", "-no-shell-escape",
            "-outdir=" + str(work), "-jobname=" + name, "main.tex"]
    print(f"Building {language} ({mode}) with XeLaTeX...", flush=True)
    with (work / "console.log").open("w", encoding="utf-8") as stream:
        result = subprocess.run(args, cwd=SOURCE, env=env, stdout=stream,
                                stderr=subprocess.STDOUT, timeout=300)
    if result.returncode:
        tail = (work / "console.log").read_text(encoding="utf-8", errors="replace")[-6000:]
        raise BuildError(f"XeLaTeX failed for {language}. See {work / 'console.log'}\n{tail}")
    check_log(work / (name + ".log"))
    pdf = work / (name + ".pdf")
    details = inspect_pdf(pdf, language, mode)
    print(f"PASS: {pdf.name} - {details['pages']}/{MAX_PAGES} pages, embedded fonts, resolved references.")
    return pdf, details


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("all", *LANGUAGES), default="all")
    parser.add_argument("--mode", choices=("preview", "submission"), default="preview")
    parser.add_argument("--config", type=Path, default=SOURCE / "report.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "aip304-cw2")
    args = parser.parse_args(argv)
    languages = LANGUAGES if args.language == "all" else (args.language,)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Never leave a stale success artifact after a failed build in the same directory.
    for lang in LANGUAGES:
        for mode in ("preview", "submission"):
            (output / f"AIP304-CW2-{lang}-{mode}.pdf").unlink(missing_ok=True)
    (output / "manifest.json").unlink(missing_ok=True)
    (ROOT / "build" / "aip304-cw2" / "failure.log").unlink(missing_ok=True)
    try:
        data = read_config(args.config, languages, args.mode)
        check_source_structure()
        versions = check_toolchain()
        builds = [build_one(data, lang, args.mode) for lang in languages]
        manifest = {"option": data["option"], "mode": args.mode, "max_pages": MAX_PAGES,
                    "source_commit": os.environ.get("GITHUB_SHA", "local-working-tree"),
                    "toolchain": versions, "reports": [details for _, details in builds],
                    "notice": "Build checks do not certify experimental validity or submission completeness."}
        # Publish only after every requested language has passed all checks.
        for pdf, _ in builds:
            shutil.copyfile(pdf, output / pdf.name)
        (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary = "## AIP304 CW2 PDF\n\n| Language | Mode | Pages | PDF |\n|---|---|---:|---|\n"
        for _, result in builds:
            summary += f"| {result['language']} | {result['mode']} | {result['pages']}/5 | {result['file']} |\n"
        summary += "\nThe final coursework submission contains **one** report PDF. "
        summary += "Preview PDFs contain drafting prompts and are not submission reports.\n"
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as stream:
                stream.write(summary)
        print(f"Checked PDFs and manifest: {output}")
        return 0
    except (BuildError, OSError, subprocess.TimeoutExpired) as exc:
        diagnostics = ROOT / "build" / "aip304-cw2"
        diagnostics.mkdir(parents=True, exist_ok=True)
        (diagnostics / "failure.log").write_text(str(exc) + "\n", encoding="utf-8")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
