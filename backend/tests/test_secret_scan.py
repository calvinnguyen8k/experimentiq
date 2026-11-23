import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "secret_scan", Path(__file__).resolve().parents[2] / "scripts" / "check_secrets.py"
)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


def test_empty_key_placeholder_does_not_match_next_line():
    assert scanner.findings("OPENAI_API_KEY=\nOPENAI_MODEL=gpt-4.1-mini\n") == []


def test_key_assignment_and_private_key_are_detected_without_outputting_values():
    assert scanner.findings("OPENAI_API_KEY=" + "x" * 30) == [1]
    assert scanner.findings("line one\n" + "sk-" + "a" * 40) == [2]
    assert scanner.findings("-----BEGIN " + "PRIVATE KEY-----") == [1]
