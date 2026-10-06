"""Copy this file to config.py (gitignored) and fill in your keys.

    copy config.example.py config.py

A key left empty here falls back to the matching environment variable
(ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, DEEPSEEK_API_KEY).
"""

ANTHROPIC_API_KEY = ""
OPENAI_API_KEY = ""
GEMINI_API_KEY = ""
OPENROUTER_API_KEY = ""
DEEPSEEK_API_KEY = ""
# Only if your Anthropic key is not scoped to a workspace (the API says so): wrkspc_...
ANTHROPIC_WORKSPACE_ID = ""
# Google Cloud Vision (vision_test.py only): an API key from a project with the Cloud Vision API enabled.
GOOGLE_VISION_API_KEY = ""

# Models to benchmark. The key is the name used on the command line and in
# report filenames; "model" is the provider's own model id.
#
#   provider: anthropic | openai | gemini | openrouter | deepseek
#   effort:   Anthropic only — low | medium | high | xhigh | max.
#             Claude Opus 5.5 always thinks; effort sets how much (API default: medium).
#   reasoning_effort: OpenAI only - none (no thinking) | low | medium | high | xhigh.
#   thinking: Anthropic only - "between_tools" turns thinking off on Claude Sonnet 5.5
#             (effort high or below). Omit to leave the model's default (adaptive).
MODELS = {
    "claude-opus-5-5": {"provider": "anthropic", "model": "claude-opus-5-5", "effort": "medium"},
    # "claude-opus-5-5-high": {"provider": "anthropic", "model": "claude-opus-5-5", "effort": "high"},
    "deepseek-flash": {"provider": "deepseek", "model": "deepseek-flash"},
    # OpenAI and Google models through OpenRouter (one key, real cost reported per call):
    "gpt-6.1-sol": {"provider": "openrouter", "model": "openai/gpt-6.1-sol"},
    "gemini-3.8-flash": {"provider": "openrouter", "model": "google/gemini-3.8-flash"},

    # More candidates — uncomment to include:
    # "claude-sonnet-5-5": {"provider": "anthropic", "model": "claude-sonnet-5-5", "effort": "medium"},
    # "claude-sonnet-5-5-nothink": {"provider": "anthropic", "model": "claude-sonnet-5-5",
    #                               "thinking": "between_tools", "effort": "high"},
    # "claude-haiku-4-5": {"provider": "anthropic", "model": "claude-haiku-4-5"},
    # "grok-4.7": {"provider": "openrouter", "model": "x-ai/grok-4.7"},
    # "qwen3.8-max-prime": {"provider": "openrouter", "model": "qwen/qwen3.8-max-prime"},
    # Direct OpenAI / Gemini (need their own keys and a dated entry in pricing.py):
    # "gpt-6.1-sol-direct": {"provider": "openai", "model": "gpt-6.1-sol"},
    # "gpt-6.1-sol-low": {"provider": "openai", "model": "gpt-6.1-sol", "reasoning_effort": "low"},
    # "gpt-6-luna": {"provider": "openai", "model": "gpt-6-luna"},
    # "gpt-6-luna-nothink": {"provider": "openai", "model": "gpt-6-luna", "reasoning_effort": "none"},
    # "gpt-6-luna-xhigh": {"provider": "openai", "model": "gpt-6-luna", "reasoning_effort": "xhigh"},
    # "gemini-3.8-flash-direct": {"provider": "gemini", "model": "gemini-3.8-flash"},
}

MAX_OUTPUT_TOKENS = 16000   # room for thinking/reasoning tokens plus the JSON answer
REQUEST_TIMEOUT_S = 180
DEFAULT_CONCURRENCY = 4

# The one prompt every model receives, word for word. Changing it makes new
# results incomparable with earlier runs (the run metadata records its hash).
PROMPT = """You are identifying a wristwatch from a single photo, to pre-fill a listing on a luxury watch resale marketplace.

Report:
- brand: one of Rolex, Omega, Patek Philippe, Audemars Piguet, Tag Heuer, Breitling, Cartier, IWC, Jaeger-LeCoultre, Vacheron Constantin — or "unknown".
- model_family: the collection and model name the brand uses.
- reference_number: the manufacturer's exact reference number for this specific version of the watch (including dial, material and strap/bracelet variant where the brand encodes them), written in the brand's own official format — keep its dots, slashes and letters. Always give your single best guess; do not answer "unknown" here.
- movement: automatic, manual, quartz, solar, hybrid, or "unknown".
- case_material: stainless-steel, gold, platinum, titanium, ceramic, bronze, or "unknown".
- bracelet_material: leather, metal, rubber, fabric, nylon, or "unknown".
- confidence: a number from 0.0 to 1.0 — how sure you are that reference_number is exactly right.

Answer as JSON."""
