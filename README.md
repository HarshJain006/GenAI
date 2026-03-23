# 🧠 GenAI Notes — Your Expert Knowledge Base

A beautiful notes + AI revision app for all 200+ GenAI topics, hosted on Streamlit Cloud with notes saved to GitHub.

---

## ✨ Features

- 📝 **Per-topic notes** for all 200+ GenAI topics across 10 phases
- ✦ **AI Revision** — Claude generates a sharp revision summary from your notes
- 💾 **GitHub sync** — notes saved as `notes.json` in your repo
- 🔍 **Search** across all topics instantly
- 📊 **Progress tracking** per phase

---

## 🚀 Setup (5 minutes)

### Step 1 — Fork / clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### Step 2 — Push to your GitHub repo

```bash
git init
git add .
git commit -m "Initial GenAI Notes setup"
git remote add origin https://github.com/YOUR_USERNAME/genai-notes.git
git push -u origin main
```

### Step 3 — Create a GitHub Personal Access Token

1. Go to **GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name like `genai-notes`
4. Select scope: ✅ `repo` (full control of private repositories)
5. Copy the token — you'll need it next

### Step 4 — Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Connect your GitHub repo
4. Set **Main file path** → `app.py`
5. Click **Advanced settings → Secrets** and paste:

```toml
GITHUB_TOKEN      = "ghp_your_token_here"
GITHUB_REPO       = "your-username/genai-notes"
GITHUB_BRANCH     = "main"
ANTHROPIC_API_KEY = "sk-ant-your_key_here"
```

6. Click **Deploy!**

### Step 5 — Get your Anthropic API Key (for AI Revision)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key and paste it into the Streamlit secret above

---

## 📁 File Structure

```
genai-notes/
├── app.py              # Streamlit backend (GitHub sync + AI revision)
├── index.html          # Frontend (all topics, editor, revision pane)
├── requirements.txt    # Python deps
├── .gitignore
├── .streamlit/
│   └── secrets.toml    # LOCAL dev only (never commit with real values!)
└── notes.json          # Auto-created when you first save notes
```

---

## 🛠 Local Development

```bash
pip install streamlit requests
streamlit run app.py
```

Fill in `.streamlit/secrets.toml` with your real keys for local testing.

---

## 💡 How it works

1. **Frontend** (`index.html`) is served inside Streamlit via `components.html`
2. **Notes** are stored in the app's JS state and synced to `notes.json` in your GitHub repo via the GitHub Contents API
3. **AI Revision** calls the Anthropic API through the Streamlit backend, generating a summary from your notes
4. On load, notes are fetched from GitHub so they persist across sessions and devices
