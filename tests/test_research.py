from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from refiner.config import RefinerConfig
from refiner.research import (
    ResearchDigest,
    Source,
    _extract_grounding,
    format_digest_for_prompt,
    render_markdown,
    run_research,
    save_digest,
    slugify,
)


def _cfg(**kw):
    return RefinerConfig.from_env(api_key="x", **kw)


def _grounding_response(text, queries, sources):
    chunks = [SimpleNamespace(web=SimpleNamespace(title=t, uri=u)) for t, u in sources]
    gm = SimpleNamespace(web_search_queries=list(queries), grounding_chunks=chunks)
    return SimpleNamespace(text=text, candidates=[SimpleNamespace(grounding_metadata=gm)])


def test_slugify_basic():
    assert slugify("Pesquise mochilas para artigo pessoal de avião!") == "pesquise-mochilas-para-artigo-pessoal-de-aviao"


def test_extract_grounding_reads_queries_and_sources():
    resp = _grounding_response("d", ["q1", "q2"], [("LATAM", "https://latam.com")])
    queries, sources = _extract_grounding(resp)
    assert queries == ["q1", "q2"]
    assert sources == [Source(title="LATAM", uri="https://latam.com")]


def test_extract_grounding_defensive_when_missing():
    assert _extract_grounding(SimpleNamespace(candidates=None)) == ([], [])
    assert _extract_grounding(SimpleNamespace(candidates=[SimpleNamespace(grounding_metadata=None)])) == ([], [])


def test_run_research_returns_digest_and_uses_search_tool():
    client = Mock()
    client.models.generate_content.return_value = _grounding_response(
        "## Vocabulário\n- artigo pessoal", ["q1"], [("T", "U")]
    )
    digest = run_research("pesquise mochilas", _cfg(research=True), client=client)
    assert "artigo pessoal" in digest.digest
    assert digest.queries == ["q1"]
    assert digest.sources[0].uri == "U"
    assert digest.topic_slug  # non-empty
    cfg = client.models.generate_content.call_args.kwargs["config"]
    assert cfg.tools  # Pass 1 MUST have the google_search tool


def test_run_research_raises_on_empty_text():
    client = Mock()
    client.models.generate_content.return_value = _grounding_response("", [], [])
    try:
        run_research("draft", _cfg(research=True), client=client)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_format_digest_for_prompt_wraps_in_tags():
    d = ResearchDigest("slug", "FATOS", ["q"], [Source("T", "U")], "m", "2026-06-25")
    out = format_digest_for_prompt(d)
    assert out.startswith("<pesquisa_de_dominio>")
    assert out.rstrip().endswith("</pesquisa_de_dominio>")
    assert "FATOS" in out


def test_render_markdown_has_all_sections():
    d = ResearchDigest("slug", "FATOS", ["q1"], [Source("LATAM", "https://latam.com")], "gemini-2.5-flash", "2026-06-25")
    md = render_markdown(d)
    assert "# Research digest" in md
    assert "2026-06-25" in md
    assert "q1" in md
    assert "[LATAM](https://latam.com)" in md
    assert "FATOS" in md


def test_save_digest_writes_file(tmp_path):
    d = ResearchDigest("mochilas", "FATOS", ["q1"], [Source("T", "U")], "m", "2026-06-25")
    path = save_digest(d, str(tmp_path))
    assert path.exists()
    assert path.suffix == ".md"
    assert "mochilas" in path.name
    assert "FATOS" in path.read_text(encoding="utf-8")
