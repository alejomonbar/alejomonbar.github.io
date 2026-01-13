#!/usr/bin/env python3

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple


BIB_PATH = "_bibliography/papers.bib"
OPENALEX_WORKS_ENDPOINT = "https://api.openalex.org/works/"
SEMANTIC_SCHOLAR_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/"
USER_AGENT = "alejomonbar.github.io citation updater (Semantic Scholar + OpenAlex)"
OPENALEX_MAILTO_ENV = "OPENALEX_MAILTO"


@dataclass(frozen=True)
class Identifiers:
    doi: Optional[str]
    arxiv: Optional[str]


def _http_get_json(url: str, timeout_s: int = 30) -> dict:
    import ssl
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        method="GET",
    )
    # SSL context - try default, fall back to unverified for local testing
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except ssl.SSLError:
        # Fall back to unverified context (local testing only)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)


def _normalize_doi(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^https?://(dx\.)?doi\.org/", "", raw, flags=re.IGNORECASE)
    return raw


def _normalize_arxiv(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^https?://arxiv\.org/(abs|pdf)/", "", raw, flags=re.IGNORECASE)
    raw = raw.replace(".pdf", "")
    return raw


def _extract_identifiers(entry_text: str) -> Identifiers:
    doi_match = re.search(r"\bdoi\s*=\s*\{([^}]+)\}", entry_text, flags=re.IGNORECASE)
    eprint_match = re.search(r"\beprint\s*=\s*\{([^}]+)\}", entry_text, flags=re.IGNORECASE)
    arxiv_id_match = re.search(r"\barxivId\s*=\s*\{([^}]+)\}", entry_text, flags=re.IGNORECASE)
    url_match = re.search(r"\burl\s*=\s*\{([^}]+)\}", entry_text, flags=re.IGNORECASE)

    doi = _normalize_doi(doi_match.group(1)) if doi_match else None

    arxiv_raw = None
    # Prefer explicit arxivId, then eprint if it looks like an arXiv id, then URL.
    if arxiv_id_match:
        arxiv_raw = arxiv_id_match.group(1)
    elif eprint_match:
        candidate = eprint_match.group(1).strip()
        # arXiv ids look like 2405.09169 or hep-th/...
        if re.match(r"^(\d{4}\.\d{4,5})(v\d+)?$", candidate) or re.match(
            r"^[a-z-]+(\.[A-Z]{2})?/\d{7}(v\d+)?$", candidate, flags=re.IGNORECASE
        ):
            arxiv_raw = candidate
    elif url_match and "arxiv.org" in url_match.group(1).lower():
        arxiv_raw = url_match.group(1)

    arxiv = _normalize_arxiv(arxiv_raw) if arxiv_raw else None
    return Identifiers(doi=doi, arxiv=arxiv)


def _openalex_work_url(ids: Identifiers) -> Optional[str]:
    mailto = None
    try:
        import os

        mailto = os.environ.get(OPENALEX_MAILTO_ENV) or None
    except Exception:
        mailto = None

    query = ""
    if mailto:
        query = "?" + urllib.parse.urlencode({"mailto": mailto})

    if ids.doi:
        identifier = "https://doi.org/" + ids.doi
        return OPENALEX_WORKS_ENDPOINT + urllib.parse.quote(identifier, safe="") + query
    if ids.arxiv:
        identifier = "https://arxiv.org/abs/" + ids.arxiv
        return OPENALEX_WORKS_ENDPOINT + urllib.parse.quote(identifier, safe="") + query
    return None


def _fetch_citations_semantic_scholar(ids: Identifiers) -> Optional[int]:
    """Try Semantic Scholar first (often closer to Google Scholar)."""
    if not ids.doi and not ids.arxiv:
        return None
    
    # Build Semantic Scholar URL
    if ids.doi:
        identifier = "DOI:" + ids.doi
    elif ids.arxiv:
        identifier = "ARXIV:" + ids.arxiv
    else:
        return None
    
    url = SEMANTIC_SCHOLAR_ENDPOINT + urllib.parse.quote(identifier, safe="") + "?fields=citationCount"
    
    try:
        payload = _http_get_json(url)
        count = payload.get("citationCount")
        if isinstance(count, int):
            return count
    except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
        # Any error, try OpenAlex instead
        pass
    
    return None


def _fetch_citations_openalex(ids: Identifiers) -> Optional[int]:
    """Fall back to OpenAlex if Semantic Scholar doesn't have it."""
    url = _openalex_work_url(ids)
    if not url:
        return None
    try:
        payload = _http_get_json(url)
        count = payload.get("cited_by_count")
        if isinstance(count, int):
            return count
    except (urllib.error.HTTPError, urllib.error.URLError, Exception):
        pass
    return None


def _fetch_citations_count(ids: Identifiers) -> Optional[int]:
    """Try Semantic Scholar first, then OpenAlex."""
    # Try Semantic Scholar (often closer to Google Scholar counts)
    count = _fetch_citations_semantic_scholar(ids)
    if count is not None:
        return count
    
    # Fall back to OpenAlex
    return _fetch_citations_openalex(ids)


def _split_front_matter(text: str) -> Tuple[str, str]:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return "---" + parts[1] + "---", parts[2]
    return "", text


def _iter_bib_entries(body: str) -> Iterable[Tuple[int, int, str]]:
    # Yields (start, end, entry_text) for each @...{...} block.
    matches = list(re.finditer(r"(?m)^@\w+\s*\{", body))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        yield start, end, body[start:end]


def _update_citations_field(entry_text: str, citations: int) -> str:
    # Replace existing citations field if present.
    if re.search(r"\bcitations\s*=\s*\{\d+\}\s*,?", entry_text, flags=re.IGNORECASE):
        return re.sub(
            r"\bcitations\s*=\s*\{\d+\}\s*,?",
            f"citations={{{citations}}},",
            entry_text,
            flags=re.IGNORECASE,
        )

    # Otherwise insert before the closing brace, ensuring the previous field ends with a comma.
    lines = entry_text.splitlines(True)
    closing_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "}":
            closing_idx = i
            break
    if closing_idx is None:
        return entry_text

    # Find the last meaningful line before the closing brace.
    prev_idx = closing_idx - 1
    while prev_idx >= 0 and lines[prev_idx].strip() == "":
        prev_idx -= 1

    if prev_idx >= 0 and not lines[prev_idx].rstrip().endswith(","):
        lines[prev_idx] = lines[prev_idx].rstrip("\n") + ",\n"

    lines.insert(closing_idx, f"citations={{{citations}}}\n")
    return "".join(lines)


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else BIB_PATH
    raw = open(path, "r", encoding="utf-8").read()
    fm, body = _split_front_matter(raw)

    updated_body = body
    # We do in-place slicing updates; build progressively.
    out_parts = []
    last_end = 0

    updated = 0
    skipped = 0
    unresolved = 0

    for start, end, entry in _iter_bib_entries(body):
        out_parts.append(body[last_end:start])

        ids = _extract_identifiers(entry)
        count = _fetch_citations_count(ids)

        if count is None:
            out_parts.append(entry)
            if ids.doi or ids.arxiv:
                unresolved += 1
            else:
                skipped += 1
        else:
            out_parts.append(_update_citations_field(entry, count))
            updated += 1

        last_end = end

        # Be polite to the API.
        time.sleep(0.25)

    out_parts.append(body[last_end:])
    new_body = "".join(out_parts)

    new_raw = (fm + new_body) if fm else new_body

    if new_raw != raw:
        open(path, "w", encoding="utf-8").write(new_raw)

    print(f"Updated citations for {updated} entries; unresolved={unresolved}; skipped={skipped}")
    print(f"Citation sources: Semantic Scholar (primary) + OpenAlex (fallback)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
