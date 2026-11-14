"""Policy file names and the procedure strings the tools accept."""

from __future__ import annotations

import re
from pathlib import Path

from tools.patients import project_root


def policies_dir() -> Path:
    return project_root() / "data" / "policies"


def parse_front_matter(text: str) -> tuple[dict[str, str | list[str]], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end]
    body = text[end + 4 :]
    meta: dict[str, str | list[str]] = {}
    aliases: list[str] = []
    collecting_aliases = False
    for line in raw.splitlines():
        if line.startswith("also_known_as:"):
            collecting_aliases = True
            continue
        if collecting_aliases and line.startswith("  - "):
            aliases.append(line[4:].strip())
            continue
        collecting_aliases = False
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    if aliases:
        meta["also_known_as"] = aliases
    return meta, body.lstrip("\n")


def policy_catalog() -> list[dict[str, str | list[str]]]:
    catalog = []
    for path in sorted(policies_dir().glob("*.md")):
        meta, _body = parse_front_matter(path.read_text(encoding="utf-8"))
        meta["path"] = str(path)
        catalog.append(meta)
    return catalog


def resolve_procedure(procedure: str) -> str | None:
    """Map a user phrase to the canonical procedure name, or None."""
    wanted = re.sub(r"\s+", " ", procedure.strip().lower())
    if not wanted:
        return None
    for meta in policy_catalog():
        names = [str(meta.get("procedure", ""))]
        names.extend(meta.get("also_known_as") or [])
        if any(wanted == name.lower() for name in names):
            return str(meta["procedure"])
    return None
