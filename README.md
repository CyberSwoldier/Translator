# 🎣 Phishing Sim HTML Translator

A Streamlit app that translates phishing simulation HTML files into Nordic, Baltic, and Polish languages — preserving all HTML tags, structure, URLs, and placeholders.

## Supported Languages
- 🇳🇴 Norwegian (Bokmål)
- 🇸🇪 Swedish
- 🇩🇰 Danish
- 🇫🇮 Finnish
- 🇪🇪 Estonian
- 🇱🇻 Latvian
- 🇱🇹 Lithuanian
- 🇵🇱 Polish

---

## Project Structure

```
phishing_translator/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── language_rules/           # Grammar & translation rule files
    ├── norwegian_bokmal.md
    ├── swedish.md
    ├── danish.md
    ├── finnish.md
    ├── estonian.md
    ├── latvian.md
    ├── lithuanian.md
    └── polish.md
```

---

## Running Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Use the app
1. Enter your Anthropic API key in the sidebar
2. Select one or more target languages
3. Paste your English HTML source
4. Click **Translate**
5. Copy or download each translated HTML

---

## Deploying to Streamlit Cloud

1. Push this entire folder to a **GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in.
3. Click **New app**.
4. Select your GitHub repo and set:
   - **Main file path**: `app.py`
5. Under **Advanced settings → Secrets**, add your API key:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
   Then update `app.py` to use `st.secrets["ANTHROPIC_API_KEY"]` as a default.
6. Click **Deploy**.

---

## How It Works

1. **HTML Parsing**: BeautifulSoup extracts all visible text nodes, skipping `<script>`, `<style>`, `<head>`, and other non-visible tags.
2. **Batch Translation**: All text nodes are numbered and sent to Claude in a single API call with the language grammar rules as context.
3. **Reinsertion**: Translations are mapped back by index and reinserted into the original HTML structure.
4. **Grammar rules**: Each language has a dedicated `.md` file with detailed grammar rules, register guidance, and common pitfall warnings that Claude uses as a translation reference.

---

## Customizing Language Rules

The `language_rules/*.md` files contain grammar rules, register guidance, and translation pitfalls for each language. You can edit these files to add:
- Client-specific glossary terms
- Brand name handling rules
- Industry-specific terminology
- Additional pitfalls you've discovered

---

## Notes

- **Preserved elements**: HTML tags, attributes, CSS classes, URLs, email addresses, variable placeholders (`{{name}}`, `%email%`, `[Company]`), and numbers are NOT translated.
- **API key**: Never stored or logged — only used in-session for the API call.
- **Large files**: The app chunks text nodes into batches of 150 to avoid token limits.
- **Model**: Uses `claude-opus-4-6` for maximum translation quality.
