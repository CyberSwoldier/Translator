import streamlit as st
import json
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
LANGUAGE_CONFIG = {
    "Norwegian (Bokmål)": {"code": "nb", "file": "norwegian_bokmal.md", "flag": "🇳🇴"},
    "Swedish":            {"code": "sv", "file": "swedish.md",           "flag": "🇸🇪"},
    "Danish":             {"code": "da", "file": "danish.md",            "flag": "🇩🇰"},
    "Finnish":            {"code": "fi", "file": "finnish.md",           "flag": "🇫🇮"},
    "Estonian":           {"code": "et", "file": "estonian.md",          "flag": "🇪🇪"},
    "Latvian":            {"code": "lv", "file": "latvian.md",           "flag": "🇱🇻"},
    "Lithuanian":         {"code": "lt", "file": "lithuanian.md",        "flag": "🇱🇹"},
    "Polish":             {"code": "pl", "file": "polish.md",            "flag": "🇵🇱"},
}

RULES_DIR  = Path(__file__).parent / "language_rules"
SKIP_TAGS  = {"script", "style", "code", "pre", "head", "meta", "link", "noscript"}
CHUNK_SIZE = 150
CLAUDE_MODEL = "claude-opus-4-6"
OPENAI_MODEL = "gpt-4o"


# ─────────────────────────────────────────────
# SECRETS LOADING
# ─────────────────────────────────────────────
def get_secret(key: str) -> str:
    """Read from st.secrets first, then environment variables."""
    try:
        val = st.secrets.get(key, "")
        return val if val else ""
    except Exception:
        return os.environ.get(key, "")


# ─────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────
def extract_text_nodes(html: str) -> tuple[dict, object]:
    soup = BeautifulSoup(html, "html.parser")
    mapping = {}
    idx = 0

    def walk(node):
        nonlocal idx
        if isinstance(node, Comment):
            return
        if isinstance(node, NavigableString):
            parent_tag = node.parent.name if node.parent else None
            text = str(node)
            if parent_tag in SKIP_TAGS or not text.strip():
                return
            mapping[idx] = text
            node.replace_with(f"[[TX_{idx}]]")
            idx += 1
        else:
            for child in list(node.children):
                walk(child)

    walk(soup)
    return mapping, soup


def reinsert_translations(soup_str: str, translations: dict) -> str:
    result = soup_str
    for idx, translated_text in translations.items():
        result = result.replace(f"[[TX_{idx}]]", translated_text)
    return result


def load_language_rules(filename: str) -> str:
    path = RULES_DIR / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_prompt(mapping: dict, target_language: str, rules: str) -> str:
    numbered = "\n".join(
        f'{i}: {json.dumps(t, ensure_ascii=False)}' for i, t in mapping.items()
    )
    return f"""You are a professional translator specialising in security awareness and phishing simulation content. Translate the strings below from English to {target_language}.

LANGUAGE RULES:
{rules}

INSTRUCTIONS:
1. Translate ONLY text — leave brand names, URLs, email addresses, and placeholders ({{{{name}}}}, %name%, [Name], etc.) untouched.
2. Use the correct formal register for this language (formal "you" form).
3. Apply all grammar rules strictly: case endings, gender agreement, special characters.
4. Preserve leading/trailing whitespace and HTML entities (&amp;, &nbsp;, etc.) exactly.
5. If a string is a symbol, number, or already in the target language, return it unchanged.
6. Return ONLY a valid JSON object — no explanation, no markdown fences.

STRINGS (index: "text"):
{numbered}

Return format: {{"0": "translation", "1": "translation", ...}}"""


# ─────────────────────────────────────────────
# TRANSLATION BACKENDS
# ─────────────────────────────────────────────
def translate_chunk_claude(mapping: dict, target_language: str, rules: str, api_key: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8096,
        messages=[{"role": "user", "content": build_prompt(mapping, target_language, rules)}],
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return {int(k): v for k, v in json.loads(raw).items()}


def translate_chunk_openai(mapping: dict, target_language: str, rules: str, api_key: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": build_prompt(mapping, target_language, rules)}],
        response_format={"type": "json_object"},
        max_tokens=8096,
    )
    raw = response.choices[0].message.content.strip()
    return {int(k): v for k, v in json.loads(raw).items()}


def translate_html(html: str, target_language: str, lang_config: dict,
                   backend: str, api_key: str) -> str:
    rules   = load_language_rules(lang_config["file"])
    mapping, soup = extract_text_nodes(html)
    if not mapping:
        return html

    all_translations = {}
    indices = list(mapping.keys())

    for i in range(0, len(indices), CHUNK_SIZE):
        chunk = {idx: mapping[idx] for idx in indices[i:i + CHUNK_SIZE]}
        if backend == "Claude (Anthropic)":
            result = translate_chunk_claude(chunk, target_language, rules, api_key)
        else:
            result = translate_chunk_openai(chunk, target_language, rules, api_key)
        all_translations.update(result)

    return reinsert_translations(str(soup), all_translations)


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Phishing Sim Translator",
        page_icon="🎣",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Sidebar ──────────────────────────────
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")

        # Backend selector
        st.markdown("### 🤖 Translation Backend")
        backend = st.radio(
            "backend",
            ["Claude (Anthropic)", "OpenAI (GPT-4o)"],
            label_visibility="collapsed",
        )

        # API key — auto-load from secrets.toml
        st.markdown("### 🔑 API Key")
        secret_key_name = "ANTHROPIC_API_KEY" if backend == "Claude (Anthropic)" else "OPENAI_API_KEY"
        placeholder     = "sk-ant-..." if backend == "Claude (Anthropic)" else "sk-..."
        loaded_key      = get_secret(secret_key_name)
        is_loaded       = bool(loaded_key and loaded_key not in ("sk-ant-...", "sk-..."))

        if is_loaded:
            st.success(f"✅ Key loaded from `secrets.toml`")
            api_key = loaded_key
            override = st.text_input(
                "Override key (optional)",
                type="password",
                placeholder=placeholder,
                help=f"Leave blank to use the key from secrets.toml",
            )
            if override.strip():
                api_key = override.strip()
        else:
            st.info(f"💡 Tip: add `{secret_key_name}` to `.streamlit/secrets.toml` to skip this step.")
            api_key = st.text_input(
                "Paste your API key",
                type="password",
                placeholder=placeholder,
            )

        st.markdown("---")

        # Language selector
        st.markdown("### 🌍 Target Languages")
        select_all = st.checkbox("Select all", value=False)
        selected_languages = []
        for lang_name, config in LANGUAGE_CONFIG.items():
            if st.checkbox(f"{config['flag']} {lang_name}", value=select_all, key=f"lang_{lang_name}"):
                selected_languages.append(lang_name)

        st.markdown("---")
        st.caption(
            "Translates phishing simulation HTML into Nordic, Baltic & Polish. "
            "Tags, URLs, and placeholders are always preserved. "
            "Grammar rules are injected per language for natural output."
        )

    # ── Main area ────────────────────────────
    st.title("🎣 Phishing Sim HTML Translator")
    st.markdown(
        "Paste your **English HTML** below, pick languages in the sidebar, and click **Translate**. "
        "All HTML structure, tags, URLs, and `{{placeholders}}` are untouched."
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📄 English Source HTML")
        source_html = st.text_area(
            "source",
            height=500,
            placeholder="<html>\n  <body>\n    <h1>Urgent: Verify Your Account</h1>\n    ...\n  </body>\n</html>",
            label_visibility="collapsed",
        )
        if source_html.strip():
            preview_soup = BeautifulSoup(source_html, "html.parser")
            count = len([t for t in preview_soup.find_all(string=True) if t.strip()])
            st.caption(f"📊 ~{count} text nodes detected")

    with col2:
        st.markdown("### 👁️ Source Preview")
        if source_html.strip():
            with st.expander("Render preview", expanded=False):
                st.components.v1.html(source_html, height=400, scrolling=True)
        else:
            st.info("Paste HTML on the left to preview it here.")

    st.markdown("---")

    # Validation messages
    key_missing = not api_key or api_key in ("sk-ant-...", "sk-...")
    if key_missing:
        st.warning("⚠️ Add your API key in the sidebar (or set it in `.streamlit/secrets.toml`).")
    elif not source_html.strip():
        st.warning("⚠️ Paste your HTML source above.")
    elif not selected_languages:
        st.warning("⚠️ Select at least one target language in the sidebar.")

    ready = not key_missing and source_html.strip() and selected_languages
    translate_btn = st.button("🚀 Translate", type="primary", use_container_width=True, disabled=not ready)

    # ── Translation + results ─────────────────
    if translate_btn:
        results = {}
        bar    = st.progress(0)
        status = st.empty()

        for i, lang_name in enumerate(selected_languages):
            config = LANGUAGE_CONFIG[lang_name]
            status.text(f"Translating → {config['flag']} {lang_name}…")
            try:
                translated = translate_html(source_html, lang_name, config, backend, api_key)
                results[lang_name] = {"html": translated, "error": None}
            except Exception as e:
                err = str(e)
                if "auth" in err.lower() or "401" in err:
                    err = "Invalid API key — please check your key."
                elif "rate" in err.lower() or "429" in err:
                    err = "Rate limit reached — wait a moment and try again. (Free tier has low limits.)"
                results[lang_name] = {"html": None, "error": err}

            bar.progress((i + 1) / len(selected_languages))

        bar.empty()
        status.success("✅ All done!")

        st.markdown("## 📦 Results")
        for lang_name, result in results.items():
            config = LANGUAGE_CONFIG[lang_name]
            with st.expander(f"{config['flag']} {lang_name}  ({config['code']})", expanded=True):
                if result["error"]:
                    st.error(f"❌ {result['error']}")
                else:
                    tab_code, tab_preview = st.tabs(["📋 HTML Code", "👁️ Rendered Preview"])
                    with tab_code:
                        st.code(result["html"], language="html")
                        st.download_button(
                            label=f"⬇️ Download {lang_name} HTML",
                            data=result["html"].encode("utf-8"),
                            file_name=f"phishing_sim_{config['code']}.html",
                            mime="text/html",
                            key=f"dl_{lang_name}",
                        )
                    with tab_preview:
                        st.components.v1.html(result["html"], height=500, scrolling=True)


if __name__ == "__main__":
    main()
