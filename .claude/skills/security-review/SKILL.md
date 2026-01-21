---
name: security-review
description: Generate a security review report as a Markdown file (incl. YAML summary for other agents). Diff-first by default.
argument-hint: "[path|file|diff] [--diff] [--base <ref>] [--full] [--run-scans] [--out <path>]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

You are a security-focused code reviewer. Produce a Markdown report file (shareable with other agents), and include a machine-readable YAML summary.

## Inputs
Raw arguments: $ARGUMENTS

### Flags
- --out <path>        Output markdown path (default: reports/security-review.md)
- --run-scans         Run optional scanners if installed (semgrep/gitleaks/osv-scanner)
- --diff              Diff-first mode (default if in a git repo and --full not provided)
- --base <ref>        Base ref for diff (default: origin/main). Examples: main, origin/master, HEAD~1
- --full              Full scan of target path/repo (disables diff-first unless target is an explicit diff)

## Behavior: Diff-first
Default behavior is diff-first:
- If inside a git repo AND "--full" is not present:
  - generate `git diff --unified=3 <base>...HEAD`
  - analyze only changed files/hunks, plus minimal context files (auth/config) if referenced.
- If user provides an explicit file/dir target without --full:
  - still prefer diff-first, but open only matching changed files under that target.
- If user provides an explicit diff/patch content as target:
  - treat it as the primary input and open referenced files for context.

## Behavior: YAML Summary
The report MUST contain a section:
## Agent Summary (YAML)
with a YAML list of findings for easy downstream parsing.

## Optional scans (only with --run-scans)
- semgrep: !`(command -v semgrep >/dev/null && semgrep --config auto --quiet .) || echo "semgrep not installed"`
- gitleaks: !`(command -v gitleaks >/dev/null && gitleaks detect --no-git --redact --source .) || echo "gitleaks not installed"`
- osv: !`(command -v osv-scanner >/dev/null && osv-scanner -r .) || echo "osv-scanner not installed"`

## Implementation steps
1) Determine OUT (default reports/security-review.md). If "--out" appears, use following token.
2) Determine BASE (default origin/main). If "--base" appears, use following token.
3) Determine MODE:
   - If "--full" present => FULL
   - Else if "--diff" present => DIFF
   - Else => DIFF (when git repo), otherwise FULL
4) Collect inputs:
   - In DIFF mode:
     - Get diff text: !`git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git diff --unified=3 "$BASE"...HEAD || echo "not a git repo"`
     - Derive changed file list: !`git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git diff --name-only "$BASE"...HEAD || true`
     - Read only changed files (and a small set of likely security-relevant neighbors if needed: auth middleware, security config, env/config files).
   - In FULL mode:
     - If a file/dir is provided, focus there; otherwise use repo root.
5) Find vulnerabilities with evidence:
   - authn/authz gaps, injection, SSRF, deserialization, secrets, crypto misuse, path traversal, XSS, open redirect, CORS, logging of secrets/PII, insecure defaults.
   - Only claim what you can support with file+snippet or diff hunk.
   - If speculative, label it and lower confidence.
6) Build a Markdown report using the template below.
7) Write the report to OUT (mkdir -p parent).
8) In chat, ONLY print:
   - Report written to: <OUT>
   - 3 bullets: highest-risk findings (titles only)

## Report template (Markdown)
The report MUST be valid Markdown and include the following sections in order:

# Security Review Report
- Date:
- Target:
- Mode: DIFF or FULL
- Base ref (if DIFF):
- Reviewer: Claude Code (skill: /security-review)

## Executive Summary
- (3-6 bullets)

## Scope & Assumptions
- (runtime/stack assumptions, trust boundaries, threat notes)

## Agent Summary (YAML)
```yaml
target: "<target>"
mode: "<DIFF|FULL>"
base: "<base or empty>"
findings:
  - id: "F-001"
    severity: "High"
    category: "Injection"
    title: "..."
    file: "path/to/file"
    line_hint: "around L120"
    confidence: 0.8
