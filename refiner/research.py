from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from google.genai import types

from .config import RefinerConfig
from .system_prompt import build_research_prompt


@dataclass
class Source:
    title: str
    uri: str


@dataclass
class ResearchDigest:
    topic_slug: str
    digest: str
    queries: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    model: str = ""
    created_at: str = ""


def slugify(text: str) -> str:
    # transliterate accents (avião -> aviao) so filenames stay ASCII-clean
    norm = unicodedata.normalize("NFKD", text.lower())
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    words = re.sub(r"[^a-z0-9\s-]", "", norm).split()
    return "-".join(words[:7])[:50] or "research"


def _extract_grounding(response) -> tuple[list[str], list[Source]]:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return [], []
    gm = getattr(candidates[0], "grounding_metadata", None)
    if gm is None:
        return [], []
    queries = list(getattr(gm, "web_search_queries", None) or [])
    sources: list[Source] = []
    for chunk in getattr(gm, "grounding_chunks", None) or []:
        web = getattr(chunk, "web", None)
        if web is None:
            continue
        uri = getattr(web, "uri", None)
        if not uri:
            continue
        sources.append(Source(title=getattr(web, "title", None) or uri, uri=uri))
    return queries, sources


def run_research(draft: str, config: RefinerConfig, client) -> ResearchDigest:
    cfg = types.GenerateContentConfig(
        system_instruction=build_research_prompt(config.output_language),
        temperature=config.temperature,
        max_output_tokens=config.max_output_tokens,
        thinking_config=types.ThinkingConfig(thinking_budget=config.thinking_budget),
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )
    response = client.models.generate_content(
        model=config.model,
        contents=f"INPUT A REFINAR:\n\n{draft}",
        config=cfg,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Research pass returned empty output.")
    queries, sources = _extract_grounding(response)
    return ResearchDigest(
        topic_slug=slugify(draft),
        digest=text,
        queries=queries,
        sources=sources,
        model=config.model,
        created_at=date.today().isoformat(),
    )


def format_digest_for_prompt(digest: ResearchDigest) -> str:
    return f"<pesquisa_de_dominio>\n{digest.digest}\n</pesquisa_de_dominio>"


def render_markdown(digest: ResearchDigest) -> str:
    queries = "\n".join(f"- {q}" for q in digest.queries) or "- (nenhuma registrada)"
    sources = "\n".join(f"- [{s.title}]({s.uri})" for s in digest.sources) or "- (nenhuma registrada)"
    return (
        f"# Research digest — {digest.topic_slug}\n\n"
        f"- Data: {digest.created_at}\n"
        f"- Modelo: {digest.model}\n\n"
        f"## Queries executadas\n{queries}\n\n"
        f"## Fontes\n{sources}\n\n"
        f"## Digest\n{digest.digest}\n"
    )


def save_digest(digest: ResearchDigest, research_dir: str) -> Path:
    out_dir = Path(research_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    path = out_dir / f"{stamp}-{digest.topic_slug}.md"
    path.write_text(render_markdown(digest), encoding="utf-8")
    return path
