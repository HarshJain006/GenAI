import streamlit as st
import streamlit.components.v1 as components
import json, base64, requests, os

st.set_page_config(
    page_title="GenAI Notes",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Hide Streamlit chrome ─────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Read secrets ──────────────────────────────────────────────────────────────
GITHUB_TOKEN  = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO   = st.secrets.get("GITHUB_REPO", "")
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")
NOTES_FILE    = "notes.json"
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")

gh_configured = bool(GITHUB_TOKEN and GITHUB_REPO)
ai_configured = bool(ANTHROPIC_KEY)

# ── Load existing notes from GitHub (server-side on page load) ───────────────
@st.cache_data(ttl=60, show_spinner=False)
def gh_load(token, repo, branch, notes_file):
    if not token or not repo:
        return {}, ""
    url = f"https://api.github.com/repos/{repo}/contents/{notes_file}?ref={branch}"
    try:
        r = requests.get(url, headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }, timeout=10)
        if r.status_code == 200:
            d = r.json()
            content = base64.b64decode(d["content"]).decode("utf-8")
            return json.loads(content), d["sha"]
    except Exception:
        pass
    return {}, ""

initial_notes, initial_sha = gh_load(
    GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH, NOTES_FILE
)

# ── Read HTML template ────────────────────────────────────────────────────────
html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# ── Inject runtime config ─────────────────────────────────────────────────────
# Strategy: inject credentials + initial data so the browser JS can call
# GitHub API and Anthropic API DIRECTLY — no Streamlit fetch proxy needed.
# This avoids all CORS / iframe / fetch issues entirely.
config_js = f"""<script>
window.APP_CONFIG = {{
  ghConfigured:  {"true" if gh_configured else "false"},
  aiConfigured:  {"true" if ai_configured else "false"},
  githubToken:   {json.dumps(GITHUB_TOKEN)},
  githubRepo:    {json.dumps(GITHUB_REPO)},
  githubBranch:  {json.dumps(GITHUB_BRANCH)},
  notesFile:     {json.dumps(NOTES_FILE)},
  anthropicKey:  {json.dumps(ANTHROPIC_KEY)},
  initialNotes:  {json.dumps(initial_notes)},
  initialSha:    {json.dumps(initial_sha)}
}};
</script>"""

html = html.replace("</head>", config_js + "\n</head>")

# ── Render the app ────────────────────────────────────────────────────────────
components.html(html, height=950, scrolling=False)
