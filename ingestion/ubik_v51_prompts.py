"""Frozen v5.1 prompts: read verbatim from prompts/v5.1 and verify SHA-256 before any paid call."""
import hashlib
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts" / "v5.1"
FROZEN = {
    "extraction": ("extraction.txt", "22a63958b94064356077432f080c49fa5f15834fa8597e76154c67fde106290a"),
    "pair_judge": ("pair_judge.txt", "703e308ae07b5e1c500674b6238dbe0248a5cdef0598921cd7beb8a5299d686f"),
}


def load_prompt(name):
    """Return the exact frozen text; abort if the file differs by a single byte."""
    filename, expected = FROZEN[name]
    raw = (PROMPT_DIR / filename).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise RuntimeError(f"Frozen prompt {filename} hash mismatch: {actual} != {expected}")
    return raw.decode("utf-8"), actual
