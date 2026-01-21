#!/usr/bin/env python3
"""
Find missing documentation in Python files using pydocstyle.

This script identifies undocumented functions, classes, and modules,
and outputs the results in a format suitable for the documentation skill prompt.

Usage:
    python find_missing_docs.py <path> [--output json|text|prompt]
    python find_missing_docs.py backend/src --output prompt

Requirements:
    pip install pydocstyle
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocstringIssue:
    """Represents a missing or incomplete docstring issue."""

    file_path: str
    line: int
    code: str
    message: str
    context: str = ""


def run_pydocstyle(target_path: str) -> list[DocstringIssue]:
    """
    Run pydocstyle on the target path and parse the output.

    Args:
        target_path: File or directory path to analyze.

    Returns:
        List of DocstringIssue objects representing missing documentation.
    """
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pydocstyle",
                target_path,
                "--select=D100,D101,D102,D103,D104,D105,D106,D107",
            ],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("Error: pydocstyle not found. Install with: pip install pydocstyle")
        sys.exit(1)

    issues = []
    lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # pydocstyle output format: "path:line message" on one line
        # or "path:line in public function `name`" followed by error code
        if ":" in line and not line.startswith(" "):
            parts = line.split(":", 2)
            if len(parts) >= 2:
                file_path = parts[0]
                try:
                    line_num = int(parts[1].split()[0])
                except (ValueError, IndexError):
                    i += 1
                    continue

                context = parts[2].strip() if len(parts) > 2 else ""

                # Next line contains the error code and message
                if i + 1 < len(lines):
                    error_line = lines[i + 1].strip()
                    if error_line.startswith("D"):
                        code_parts = error_line.split(":", 1)
                        code = code_parts[0].strip()
                        message = code_parts[1].strip() if len(code_parts) > 1 else ""

                        issues.append(
                            DocstringIssue(
                                file_path=file_path,
                                line=line_num,
                                code=code,
                                message=message,
                                context=context,
                            )
                        )
                        i += 2
                        continue
        i += 1

    return issues


def extract_code_context(file_path: str, line: int, context_lines: int = 5) -> str:
    """
    Extract code context around the given line.

    Args:
        file_path: Path to the source file.
        line: Line number to extract context around.
        context_lines: Number of lines to include after the target line.

    Returns:
        Code snippet with context.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return ""

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start = max(0, line - 1)
        end = min(len(lines), line + context_lines)
        snippet = "".join(lines[start:end])
        return snippet.rstrip()
    except Exception:
        return ""


def format_as_text(issues: list[DocstringIssue]) -> str:
    """Format issues as human-readable text."""
    if not issues:
        return "No missing documentation found."

    output = [f"Found {len(issues)} documentation issue(s):\n"]

    for issue in issues:
        output.append(f"  {issue.file_path}:{issue.line}")
        output.append(f"    [{issue.code}] {issue.message}")
        if issue.context:
            output.append(f"    Context: {issue.context}")
        output.append("")

    return "\n".join(output)


def format_as_json(issues: list[DocstringIssue]) -> str:
    """Format issues as JSON."""
    return json.dumps(
        [
            {
                "file": issue.file_path,
                "line": issue.line,
                "code": issue.code,
                "message": issue.message,
                "context": issue.context,
            }
            for issue in issues
        ],
        indent=2,
    )


def format_as_prompt(issues: list[DocstringIssue], include_code: bool = True) -> str:
    """
    Format issues as input for the documentation skill prompt.

    Groups issues by file and includes code context for each undocumented element.
    """
    if not issues:
        return "No documentation needed - all elements are documented."

    # Group by file
    by_file: dict[str, list[DocstringIssue]] = {}
    for issue in issues:
        if issue.file_path not in by_file:
            by_file[issue.file_path] = []
        by_file[issue.file_path].append(issue)

    output = ["## Missing Documentation Report\n"]
    output.append(f"Total: {len(issues)} undocumented element(s) in {len(by_file)} file(s)\n")

    for file_path, file_issues in by_file.items():
        output.append(f"### File: `{file_path}`\n")

        for issue in file_issues:
            element_type = get_element_type(issue.code)
            output.append(f"**{element_type}** (line {issue.line})")

            if issue.context:
                # Extract name from context like "in public function `name`"
                output.append(f"- {issue.context}")

            if include_code:
                code_snippet = extract_code_context(file_path, issue.line)
                if code_snippet:
                    output.append(f"\n```python\n{code_snippet}\n```\n")
                else:
                    output.append("")
            else:
                output.append("")

    output.append("---\n")
    output.append("Please generate documentation for the elements listed above.")

    return "\n".join(output)


def get_element_type(code: str) -> str:
    """Map pydocstyle error code to element type."""
    mapping = {
        "D100": "Module",
        "D101": "Class",
        "D102": "Method",
        "D103": "Function",
        "D104": "Package (__init__.py)",
        "D105": "Magic method",
        "D106": "Nested class",
        "D107": "__init__ method",
    }
    return mapping.get(code, "Unknown")


def main():
    parser = argparse.ArgumentParser(
        description="Find missing documentation in Python files."
    )
    parser.add_argument(
        "path",
        help="File or directory to analyze",
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["text", "json", "prompt"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-code",
        action="store_true",
        help="Don't include code snippets in prompt output",
    )

    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)

    issues = run_pydocstyle(str(target_path))

    if args.output == "text":
        print(format_as_text(issues))
    elif args.output == "json":
        print(format_as_json(issues))
    elif args.output == "prompt":
        print(format_as_prompt(issues, include_code=not args.no_code))

    # Exit with non-zero if issues found
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
