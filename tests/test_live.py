import os
import pytest
from refiner.config import RefinerConfig
from refiner.core import refine_prompt


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="no GEMINI_API_KEY set")
def test_live_refine_returns_text():
    cfg = RefinerConfig.from_env(research=False)  # cheap/fast: no grounding
    out = refine_prompt(
        "Quero que me ajudes a escrever um email simpatico para um cliente novo",
        cfg,
    )
    assert isinstance(out, str) and len(out) > 0
