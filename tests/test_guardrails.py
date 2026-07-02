"""A-008 out-of-scope guard: forbidden strings must not appear in src/.

Scripted version of the blueprint's grep check: the strings
``create_order_instruction``, ``ib_insync``, and ``mcp__`` must not appear
anywhere under ``src/`` (D-013, D-014).
"""

from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"

# Assembled to avoid the literals appearing verbatim in grep output noise;
# the joined values are exactly the blueprint's forbidden strings.
FORBIDDEN = [
    "create_order" + "_instruction",
    "ib_" + "insync",
    "mcp" + "__",
]


def test_forbidden_strings_absent_from_src():
    offenders = []
    for path in SRC.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for needle in FORBIDDEN:
            if needle in text:
                offenders.append(f"{path}: contains {needle!r}")
    assert not offenders, "\n".join(offenders)


def test_no_network_or_broker_imports_in_src():
    """Belt-and-braces: no sockets, HTTP clients, or broker libs in src/."""
    banned_imports = ("socket", "requests", "urllib", "http.client", "ibapi")
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for mod in banned_imports:
            if f"import {mod}" in text or f"from {mod}" in text:
                offenders.append(f"{path}: imports {mod}")
    assert not offenders, "\n".join(offenders)


def test_guardrail_scan_covers_sprint_003_modules():
    """A-008: the greps above must actually be scanning the ledger modules.

    Guards against src-layout drift silently exempting new code."""
    scanned = {p.name for p in SRC.rglob("*.py")}
    expected = {
        "risk_math.py", "snapshot.py", "cli.py",  # Sprint 002
        "registry.py", "trades.py", "ledger.py", "cli_ledger.py",  # Sprint 003
    }
    missing = expected - scanned
    assert not missing, f"guardrail scan is missing modules: {sorted(missing)}"
