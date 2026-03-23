import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import requests
import os

st.set_page_config(
    page_title="GenAI Notes",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── GitHub Config ────────────────────────────────────────────────────────────
GITHUB_TOKEN  = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO   = st.secrets.get("GITHUB_REPO", "")        # e.g. "username/genai-notes"
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")
NOTES_FILE    = "notes.json"
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ─── GitHub helpers ───────────────────────────────────────────────────────────
def gh_get_file():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return None, None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{NOTES_FILE}?ref={GITHUB_BRANCH}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content), data["sha"]
    return {}, None

def gh_save_file(notes: dict, sha=None):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False, "GitHub not configured"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{NOTES_FILE}"
    content = base64.b64encode(json.dumps(notes, indent=2).encode()).decode()
    payload = {
        "message": "Update GenAI notes",
        "content": content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        return True, "Saved to GitHub ✓"
    return False, f"Error {r.status_code}: {r.text[:200]}"

# ─── Streamlit API endpoints via query params ──────────────────────────────────
qp = st.query_params

if "action" in qp:
    action = qp["action"]

    if action == "load":
        notes, sha = gh_get_file()
        st.json({"notes": notes or {}, "sha": sha or ""})
        st.stop()

    elif action == "save":
        body = st.session_state.get("_save_body", {})
        notes = body.get("notes", {})
        sha   = body.get("sha", None)
        ok, msg = gh_save_file(notes, sha)
        st.json({"ok": ok, "msg": msg})
        st.stop()

    elif action == "revise":
        topic = qp.get("topic", "this topic")
        note  = qp.get("note", "")
        if not ANTHROPIC_KEY:
            st.json({"text": "⚠️ ANTHROPIC_API_KEY not set in Streamlit secrets."})
            st.stop()
        prompt = f"""You are a concise GenAI teacher. The student is studying: **{topic}**

Their notes:
{note if note else "(no notes yet)"}

Generate a sharp, exam-ready revision summary with:
1. Core concept in one sentence
2. Key points (5–8 bullets, each ≤ 15 words)
3. Common gotcha / tricky part
4. One analogy that makes it click

Keep it tight — max 250 words. Use markdown."""

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 600, "messages": [{"role":"user","content": prompt}]}
        )
        if resp.status_code == 200:
            text = resp.json()["content"][0]["text"]
        else:
            text = f"API error {resp.status_code}"
        st.json({"text": text})
        st.stop()

# ─── Inject config into page for JS to use ────────────────────────────────────
gh_configured   = bool(GITHUB_TOKEN and GITHUB_REPO)
ai_configured   = bool(ANTHROPIC_KEY)

# ─── Read the HTML template ───────────────────────────────────────────────────
html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, "r") as f:
    html = f.read()

# Inject runtime config
config_js = f"""<script>
window.APP_CONFIG = {{
  ghConfigured: {'true' if gh_configured else 'false'},
  aiConfigured: {'true' if ai_configured else 'false'},
  streamlitBase: window.location.origin + window.location.pathname.replace(/\\/$/, '')
}};
</script>"""
html = html.replace("</head>", config_js + "\n</head>")

components.html(html, height=920, scrolling=True)

# ─── Save endpoint (POST via session_state trick) ─────────────────────────────
if "save_notes" in st.session_state:
    payload = st.session_state.pop("save_notes")
    notes, sha = payload["notes"], payload.get("sha")
    ok, msg = gh_save_file(notes, sha)
    st.toast(msg, icon="✅" if ok else "❌")
