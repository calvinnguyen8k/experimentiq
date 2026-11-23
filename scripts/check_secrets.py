"""Small, offline repository secret check. Reports locations, never secret values."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?im)^[ \t]*OPENAI_API_KEY[ \t]*=[ \t]*['\"]?[^\s'\"#]{8,}"),
]


def findings(text):
    return sorted(
        {
            text.count("\n", 0, match.start()) + 1
            for pattern in PATTERNS
            for match in pattern.finditer(text)
        }
    )


def main():
    # Includes tracked files and untracked nonignored work; forced tracked .env is caught.
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    failed = False
    count = 0
    for name in sorted(set(result.stdout.decode().split("\0")) - {""}):
        path = ROOT / name
        if not path.is_file():
            continue
        count += 1
        if path.name.startswith(".env") and path.name != ".env.example":
            print(f"Forbidden environment file: {name}")
            failed = True
        text = path.read_text(errors="replace")
        for line in findings(text):
            print(f"Potential secret: {name}:{line}")
            failed = True
    print(
        f"Secret pattern check: {'FAILED' if failed else 'passed'} ({count} files checked)."
    )
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
