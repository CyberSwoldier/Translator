import streamlit as st
import anthropic
import json
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment
import copy

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
LANGUAGE_CONFIG = {
    "Norwegian (Bokmål)": {"code": "nb", "file": "norwegian_bokmal.md", "flag": "🇳🇴"},
    "Swedish": {"code": "sv", "file": "swedish.md", "flag": "🇸🇪"},
    "Danish": {"code": "da", "file": "danish.md", "flag": "🇩🇰"},
    "Finnish": {"code": "fi", "file": "finnish.md", "flag": "🇫🇮"},
    "Estonian": {"code": "et", "file": "estonian.md", "flag": "🇪🇪"},
    "Latvian": {"code": "lv", "file": "latvian.md", "flag": "🇱🇻"},
    "Lithuanian": {"code": "lt", "file": "lithuanian.md", "flag": "🇱🇹"},
    "Polish": {"code": "pl", "file": "polish.md", "flag": "🇵🇱"},
}

RULES_DIR = Path(__file__).parent / "language_rules"

# Tags whose text should NOT be translated
SKIP_TAGS = {"script", "style", "code", "pre", "head", "meta", "link", "noscript"}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def load_language_rules(filename: str) -> str:
    """Load grammar rules from markdown file."""
    rules_path = RULES_DIR / filename
    if rules_path.exists():
        return rules_path.read_text(encoding="utf-8")
    return ""


def extract_text_nodes(html: str) -> tuple[dict, list]:
    """
    Extract all translatable text nodes from HTML.
    Returns:
        - mapping: {index: original_text}
        - soup: parsed BeautifulSoup object
    """
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
            # Skip if parent tag is in skip list or text is whitespace-only
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
    """Replace [[TX_N]] placeholders with translated text."""
    result = soup_str
    for idx, translated_text in translations.items():
        placeholder = f"[[TX_{idx}]]"
        result = result.replace(placeholder, translated_text)
    return result


def build_translation_prompt(mapping: dict, target_language: str, rules: str) -> str:
    """Build the prompt to send to Claude for batch translation."""
    numbered_texts = "\n".join(
        f'{idx}: {json.dumps(text, ensure_ascii=False)}'
        for idx, text in mapping.items()
    )

    prompt = f"""You are a professional translator and proofreader specializing in security awareness and phishing simulation content. Your task is to translate the following text strings from English to {target_language}.

LANGUAGE RULES & GRAMMAR REFERENCE:
{rules}

TRANSLATION INSTRUCTIONS:
1. Translate ONLY the text content — do NOT translate brand names, URLs, email addresses, variable placeholders like {{{{name}}}}, {{{{company}}}}, %name%, [Name], etc.
2. Maintain the same urgency, tone, and register as the original phishing simulation (professional-looking, authoritative).
3. Apply the grammar rules above strictly — pay special attention to: correct case endings, gender agreement, formal address form (use the formal "you" form appropriate for this language), and special characters.
4. Preserve any HTML entities (&amp;, &nbsp;, etc.) as-is.
5. Preserve leading and trailing whitespace exactly as in the source.
6. If a string is already in the target language or is a symbol/number only, return it unchanged.
7. Do NOT add any explanation or commentary — return ONLY valid JSON.

STRINGS TO TRANSLATE (format: index: "text"):
{numbered_texts}

Return a JSON object mapping each index (as a string) to its translation. Example format:
{{"0": "translated text 0", "1": "translated text 1"}}

Return ONLY the JSON object, nothing else."""

    return prompt


def translate_with_claude(mapping: dict, target_language: str, rules: str, api_key: str) -> dict:
    """Send batch translation request to Claude API."""
    client = anthropic.Anthropic(api_key=api_key)

    prompt = build_translation_prompt(mapping, target_language, rules)

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8096,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()

    # Strip markdown code blocks if present
    if response_text.startswith("```"):
        response_text = re.sub(r"^```[a-z]*\n?", "", response_text)
        response_text = re.sub(r"\n?```$", "", response_text)

    translations_raw = json.loads(response_text)
    # Convert string keys to int keys
    return {int(k): v for k, v in translations_raw.items()}


def translate_html(html: str, target_language: str, lang_config: dict, api_key: str) -> str:
    """Full pipeline: extract → translate → reinsert."""
    rules = load_language_rules(lang_config["file"])
    mapping, soup = extract_text_nodes(html)

    if not mapping:
        return html  # Nothing translatable found

    # Split into chunks to stay within token limits (max ~200 strings per call)
    CHUNK_SIZE = 150
    all_translations = {}

    indices = list(mapping.keys())
    for i in range(0, len(indices), CHUNK_SIZE):
        chunk_indices = indices[i : i + CHUNK_SIZE]
        chunk_mapping = {idx: mapping[idx] for idx in chunk_indices}
        chunk_translations = translate_with_claude(chunk_mapping, target_language, rules, api_key)
        all_translations.update(chunk_translations)

    soup_str = str(soup)
    translated_html = reinsert_translations(soup_str, all_translations)
    return translated_html


# ─────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Phishing Sim Translator",
        page_icon="🎣",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Sidebar ──
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")

        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Your Anthropic API key. Never shared or stored.",
        )

        st.markdown("---")
        st.markdown("### 🌍 Target Languages")
        selected_languages = []
        for lang_name, config in LANGUAGE_CONFIG.items():
            if st.checkbox(f"{config['flag']} {lang_name}", key=f"lang_{lang_name}"):
                selected_languages.append(lang_name)

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown(
            """
            This tool translates phishing simulation HTML files 
            into Nordic, Baltic, and Polish languages while 
            preserving all HTML structure and tags.
            
            Grammar rules files are loaded automatically 
            for each language to ensure high-quality, 
            natural-sounding translations.
            """
        )

    # ── Main content ──
    st.title("🎣 Phishing Sim HTML Translator")
    st.markdown(
        "Paste your English HTML below, select target languages, and click **Translate**. "
        "HTML tags, attributes, URLs, and placeholders are preserved."
    )

    # Input area
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📄 English Source HTML")
        source_html = st.text_area(
            label="Paste your HTML here",
            height=500,
            placeholder="<html>\n  <body>\n    <h1>Urgent: Verify Your Account</h1>\n    ...\n  </body>\n</html>",
            label_visibility="collapsed",
        )

        # Quick stats
        if source_html.strip():
            soup_preview = BeautifulSoup(source_html, "html.parser")
            text_count = len([t for t in soup_preview.find_all(string=True) if t.strip()])
            st.caption(f"📊 ~{text_count} text nodes detected")

    with col2:
        st.markdown("### 👁️ Preview")
        if source_html.strip():
            with st.expander("Render HTML Preview", expanded=False):
                st.components.v1.html(source_html, height=400, scrolling=True)
        else:
            st.info("Paste HTML on the left to see a preview here.")

    st.markdown("---")

    # Translate button
    translate_btn = st.button(
        "🚀 Translate",
        type="primary",
        use_container_width=True,
        disabled=not (api_key and source_html.strip() and selected_languages),
    )

    if not api_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar.")
    elif not source_html.strip():
        st.warning("⚠️ Please paste your HTML source.")
    elif not selected_languages:
        st.warning("⚠️ Please select at least one target language.")

    # ── Translation results ──
    if translate_btn:
        results = {}
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, lang_name in enumerate(selected_languages):
            config = LANGUAGE_CONFIG[lang_name]
            status_text.text(f"Translating to {config['flag']} {lang_name}...")

            try:
                translated = translate_html(source_html, lang_name, config, api_key)
                results[lang_name] = {"html": translated, "error": None}
            except json.JSONDecodeError as e:
                results[lang_name] = {"html": None, "error": f"JSON parse error: {e}"}
            except anthropic.AuthenticationError:
                results[lang_name] = {"html": None, "error": "Invalid API key. Please check your key."}
            except anthropic.RateLimitError:
                results[lang_name] = {"html": None, "error": "Rate limit reached. Please wait and try again."}
            except Exception as e:
                results[lang_name] = {"html": None, "error": str(e)}

            progress_bar.progress((i + 1) / len(selected_languages))

        status_text.text("✅ Translation complete!")
        progress_bar.empty()

        # ── Display results ──
        st.markdown("## 📦 Translation Results")

        for lang_name, result in results.items():
            config = LANGUAGE_CONFIG[lang_name]
            with st.expander(
                f"{config['flag']} {lang_name} ({config['code']})",
                expanded=True,
            ):
                if result["error"]:
                    st.error(f"❌ Error: {result['error']}")
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
