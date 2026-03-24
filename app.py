"""
GenAI Notes — Pure Streamlit App
• All data saved to notes.json (same folder as app.py)
• Notes + attachments (images/code) per topic
• AI Revision via Anthropic API
• Practice tab with 18 hands-on projects
• NO iframes, NO GitHub token, NO CORS issues
"""
import streamlit as st
import json, os, base64, requests, urllib.parse
from pathlib import Path

BASE       = Path(__file__).parent
NOTES_FILE = BASE / "notes.json"
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")

st.set_page_config(
    page_title="🧠 GenAI Notes",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

#MainMenu,header,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"]{display:none!important}

html,body,.stApp,[data-testid="stAppViewContainer"]{
  background:#0d0f14!important; color:#e8eaf0!important;
  font-family:'DM Sans',sans-serif!important;
}
[data-testid="stMain"]{background:#0d0f14!important}
.block-container{padding:1.2rem 1.8rem 3rem!important; max-width:100%!important}

/* sidebar */
[data-testid="stSidebar"]{
  background:#13161d!important;
  border-right:1px solid #ffffff12!important;
  min-width:260px!important; max-width:260px!important;
}
[data-testid="stSidebar"]>div:first-child{padding-top:0!important}

/* sidebar buttons */
/* sidebar — only the non-nav parts still use st.button (tab switcher + search) */

/* ── sidebar nav (pure HTML anchors) ── */
.sb-nav a,.sb-topic{
  display:block; width:100%; padding:5px 14px 5px 30px;
  font-size:12px; color:#9298ab;
  font-family:'DM Sans',sans-serif;
  text-decoration:none !important; cursor:pointer;
  border-left:3px solid transparent;
  transition:background .1s,color .1s; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis; box-sizing:border-box;
}
.sb-nav a:hover,.sb-topic:hover{background:#1a1d26!important;color:#e8eaf0!important}
.sb-nav a.active,.sb-topic.active{
  background:#7c6ef710!important;color:#7c6ef7!important;
  border-left-color:#7c6ef7!important;
}
.sb-phase-hdr{
  display:flex;align-items:center;gap:6px;
  padding:9px 14px 3px;
  font-size:10px;font-weight:700;color:#5c6275;
  text-transform:uppercase;letter-spacing:.08em;
  font-family:'DM Mono',monospace;
}
.sb-pdot{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}
.sb-pcnt{margin-left:auto;font-size:10px;color:#5c6275}
.sb-prog{padding:0 14px 4px}
.sb-prog-track{height:2px;background:#ffffff10;border-radius:1px;overflow:hidden}
.sb-prog-fill{height:100%;border-radius:1px}
.sb-sec-lbl{
  padding:5px 14px 2px 28px;
  font-size:9px;color:#5c6275;
  font-family:'DM Mono',monospace;
  text-transform:uppercase;letter-spacing:.06em;
}
.sb-noted-dot{
  display:inline-block;width:5px;height:5px;border-radius:50%;
  background:#3dd68c;margin-right:5px;vertical-align:middle;
}

/* main content area */
[data-testid="stVerticalBlock"]{gap:0!important}

/* text area */
.stTextArea>div>div>textarea{
  background:#1a1d26!important; border:1px solid #ffffff12!important;
  border-radius:10px!important; color:#e8eaf0!important;
  font-family:'DM Mono',monospace!important; font-size:13px!important;
  line-height:1.7!important; caret-color:#7c6ef7!important;
}
.stTextArea>div>div>textarea:focus{
  border-color:#7c6ef7!important;
  box-shadow:0 0 0 2px #7c6ef740!important; outline:none!important;
}
.stTextArea>div>div>textarea::placeholder{color:#5c6275!important}
.stTextArea label{color:#5c6275!important; font-size:11px!important;
  font-family:'DM Mono',monospace!important; text-transform:uppercase!important;
  letter-spacing:.05em!important}

/* text input */
.stTextInput>div>div>input{
  background:#1a1d26!important; border:1px solid #ffffff12!important;
  border-radius:8px!important; color:#e8eaf0!important;
  font-family:'DM Sans',sans-serif!important; font-size:13px!important;
  padding:8px 12px!important; caret-color:#7c6ef7!important;
}
.stTextInput>div>div>input:focus{
  border-color:#7c6ef7!important; box-shadow:0 0 0 2px #7c6ef740!important;
}
.stTextInput label{color:#5c6275!important; font-size:11px!important; font-family:'DM Mono',monospace!important}

/* buttons */
.stButton button{
  background:#5b4fd4!important; color:#fff!important;
  border:none!important; border-radius:8px!important;
  font-family:'Syne',sans-serif!important; font-weight:600!important;
  font-size:12px!important; padding:7px 14px!important;
  box-shadow:none!important; transition:opacity .15s!important;
}
.stButton button:hover{opacity:.85!important; transform:none!important}
.stButton button:focus{box-shadow:none!important; outline:none!important}

/* save button */
.save-btn .stButton button{background:#3dd68c!important; color:#000!important}
/* revise button */
.revise-btn .stButton button{
  background:linear-gradient(135deg,#7c6ef7,#38bdf8)!important; color:#fff!important}
/* clear button */
.clear-btn .stButton button{
  background:#1a1d26!important; color:#9298ab!important;
  border:1px solid #ffffff20!important}
.clear-btn .stButton button:hover{color:#ef4444!important; border-color:#ef4444!important; opacity:1!important}
/* done button */
.done-btn .stButton button{background:#f59e0b!important; color:#000!important}
/* tab button */
.tab-notes-btn .stButton button,
.tab-practice-btn .stButton button{
  background:#1a1d26!important; color:#9298ab!important;
  border:1px solid #ffffff15!important; border-radius:8px!important;
  font-size:12px!important; padding:7px 18px!important; width:100%!important;
  justify-content:center!important; text-align:center!important;
}
.tab-active .stButton button{
  background:#7c6ef720!important; color:#7c6ef7!important;
  border-color:#7c6ef740!important;
}

/* file uploader */
[data-testid="stFileUploader"]{
  background:#1a1d26!important; border:1px dashed #ffffff20!important;
  border-radius:10px!important; padding:8px!important;
}
[data-testid="stFileUploader"] label{
  color:#9298ab!important; font-size:12px!important;
  font-family:'DM Mono',monospace!important;
}
[data-testid="stFileUploaderDropzone"]{
  background:#1a1d26!important; border:1px dashed #ffffff20!important;
  border-radius:8px!important;
}
[data-testid="stFileUploaderDropzone"] *{color:#9298ab!important}

/* expander */
[data-testid="stExpander"]{
  border:1px solid #ffffff12!important; border-radius:10px!important;
  background:#13161d!important; margin-bottom:5px!important;
}
[data-testid="stExpander"] summary{
  color:#e8eaf0!important; font-size:13px!important;
  font-family:'DM Sans',sans-serif!important; padding:10px 14px!important;
}
[data-testid="stExpander"] summary:hover{color:#7c6ef7!important}

/* progress bar */
.stProgress>div>div{background:#7c6ef7!important}
.stProgress>div{background:#1a1d26!important; border-radius:4px!important}

/* selectbox */
[data-testid="stSelectbox"]>div>div{
  background:#1a1d26!important; border:1px solid #ffffff12!important;
  border-radius:8px!important; color:#e8eaf0!important;
}

/* success / error */
[data-testid="stAlert"]{border-radius:8px!important; font-size:13px!important}

/* tabs (for practice) */
[data-testid="stTabs"] [role="tab"]{
  font-family:'Syne',sans-serif!important; font-size:12px!important;
  font-weight:600!important; color:#9298ab!important;
  background:transparent!important; border-bottom:2px solid transparent!important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{
  color:#7c6ef7!important; border-bottom-color:#7c6ef7!important;
}
[data-testid="stTabs"] [data-testid="stTabsBar"]{
  background:#13161d!important; border-bottom:1px solid #ffffff12!important;
}

/* divider */
hr{border-color:#ffffff12!important; margin:8px 0!important}

/* scrollbar */
::-webkit-scrollbar{width:4px!important}
::-webkit-scrollbar-thumb{background:#ffffff20!important; border-radius:99px!important}

/* images in notes */
.note-img{
  border-radius:8px; border:1px solid #ffffff15;
  max-width:100%; margin:4px 0; display:block;
}
/* code preview */
.code-preview{
  background:#1a1d26; border:1px solid #ffffff12;
  border-radius:8px; padding:10px 12px;
  font-family:'DM Mono',monospace; font-size:11px;
  color:#38bdf8; line-height:1.6; overflow-x:auto;
  white-space:pre; max-height:200px; overflow-y:auto;
}

/* metric */
[data-testid="stMetric"]{
  background:#13161d!important; border:1px solid #ffffff12!important;
  border-radius:10px!important; padding:12px 16px!important;
}
[data-testid="stMetricValue"]{
  color:#7c6ef7!important; font-family:'Syne',sans-serif!important;
  font-weight:800!important;
}
[data-testid="stMetricLabel"]{color:#5c6275!important; font-size:11px!important}

/* chip / tag helper */
.chip{
  display:inline-block; font-size:10px;
  font-family:'DM Mono',monospace; padding:2px 8px;
  border-radius:12px; margin:2px 2px 2px 0;
}
.chip-skill{background:#7c6ef720;color:#9b8ef9;border:1px solid #7c6ef730}
.chip-tool{background:#38bdf820;color:#67d8f7;border:1px solid #38bdf830}
.chip-easy{background:#3dd68c20;color:#3dd68c;border:1px solid #3dd68c30}
.chip-med{background:#f59e0b20;color:#f59e0b;border:1px solid #f59e0b30}
.chip-hard{background:#ef444420;color:#ef4444;border:1px solid #ef444430}
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_notes() -> dict:
    if NOTES_FILE.exists():
        try:
            return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_notes(data: dict):
    NOTES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ── Session state init ────────────────────────────────────────────────────────
if "notes"         not in st.session_state: st.session_state.notes         = load_notes()
if "done_practice" not in st.session_state: st.session_state.done_practice = st.session_state.notes.get("__done_practice__", {})
if "tab"           not in st.session_state: st.session_state.tab           = "notes"
if "current_key"   not in st.session_state: st.session_state.current_key   = None
if "current_phase" not in st.session_state: st.session_state.current_phase = None
if "current_pid"   not in st.session_state: st.session_state.current_pid   = None
if "revision_text" not in st.session_state: st.session_state.revision_text = ""
if "revision_mode" not in st.session_state: st.session_state.revision_mode = None

notes         = st.session_state.notes
done_practice = st.session_state.done_practice

def persist():
    """Save everything to notes.json"""
    payload = dict(notes)
    payload["__done_practice__"] = done_practice
    save_notes(payload)

# ── Handle query-param navigation (sidebar HTML links) ───────────────────────
import urllib.parse
_qp = st.query_params
if "tab" in _qp:
    _tab = _qp["tab"]
    if _tab in ("notes","practice") and st.session_state.tab != _tab:
        st.session_state.tab = _tab
        st.session_state.current_key = None
        st.session_state.current_pid = None
        st.session_state.revision_text = ""
        st.query_params.clear()
        st.rerun()

if "nav" in _qp:
    _nav = _qp["nav"]
    _tab = _qp.get("tab", st.session_state.tab)
    st.session_state.tab = _tab
    if _tab == "notes":
        st.session_state.current_key  = _nav
        st.session_state.current_pid  = None
        if "::" in _nav:
            st.session_state.current_phase = _nav.split("::")[0]
    else:
        st.session_state.current_pid  = _nav
        st.session_state.current_key  = None
    st.session_state.revision_text = ""
    st.session_state.revision_mode = None
    st.query_params.clear()
    st.rerun()

# ── Topic / Phase data ────────────────────────────────────────────────────────
PHASES = [
  {"id":"p1","label":"Phase 1","title":"Math & ML Foundations","color":"#7c6ef7","sections":[
    {"title":"Linear Algebra","topics":["Vectors & matrices","Matrix multiplication","Eigenvalues & eigenvectors","SVD","Dot products","Norms & distances"]},
    {"title":"Calculus","topics":["Derivatives & gradients","Chain rule","Partial derivatives","Jacobians","Taylor series"]},
    {"title":"Probability & Statistics","topics":["Probability distributions","Bayes theorem","MLE & MAP","KL divergence","Entropy & information theory","Gaussian processes"]},
    {"title":"Classical ML","topics":["Linear / logistic regression","Decision trees & ensembles","SVMs","Dimensionality reduction (PCA, t-SNE)","Clustering (K-means, DBSCAN)","Bias-variance tradeoff","Cross-validation"]},
  ]},
  {"id":"p2","label":"Phase 2","title":"Deep Learning Core","color":"#38bdf8","sections":[
    {"title":"Neural Network Basics","topics":["Perceptrons & MLPs","Activation functions","Forward & backpropagation","Loss functions","Weight initialization","Batch normalization","Dropout & regularization"]},
    {"title":"Optimizers","topics":["SGD & momentum","Adam / AdamW","Learning rate schedules","Gradient clipping","Mixed precision training"]},
    {"title":"CNNs","topics":["Convolution operations","Pooling layers","ResNet / VGG / EfficientNet","Object detection (YOLO, RCNN)","Image segmentation"]},
    {"title":"RNNs & Sequence Models","topics":["Vanilla RNNs","LSTMs & GRUs","Vanishing gradient problem","Bidirectional RNNs","Sequence-to-sequence models","Attention (pre-transformer)"]},
    {"title":"Frameworks","topics":["PyTorch (must-have)","TensorFlow / Keras","JAX","Hugging Face ecosystem"]},
  ]},
  {"id":"p3","label":"Phase 3","title":"Generative Architectures","color":"#3dd68c","sections":[
    {"title":"Transformers","topics":["Self-attention mechanism","Multi-head attention","Positional encoding","Encoder-decoder architecture","Masked attention (causal)","KV-cache","Flash attention","Sparse attention","Rotary position embeddings (RoPE)"]},
    {"title":"Autoencoders & VAEs","topics":["Undercomplete autoencoders","Denoising autoencoders","Variational inference","ELBO loss","Latent space navigation","VQ-VAE"]},
    {"title":"GANs","topics":["Generator & discriminator","GAN training dynamics","Mode collapse & mitigation","Wasserstein GAN","Progressive GAN","StyleGAN 2/3","Conditional GANs","CycleGAN"]},
    {"title":"Diffusion Models","topics":["Forward diffusion process","Reverse diffusion (DDPM)","DDIM sampling","Score matching","CFG (classifier-free guidance)","Stable Diffusion architecture","SDXL & SD3","Consistency models","Flow matching"]},
    {"title":"State Space Models","topics":["Mamba / SSM basics","S4 model","H3 model","Selective state spaces","SSM vs Transformer comparison"]},
  ]},
  {"id":"p4","label":"Phase 4","title":"Large Language Models","color":"#f59e0b","sections":[
    {"title":"LLM Fundamentals","topics":["Tokenization (BPE, WordPiece, SentencePiece)","Embedding layers","Next-token prediction","Perplexity metric","Scaling laws","Context window mechanics","Temperature & sampling strategies"]},
    {"title":"Pre-training","topics":["Causal language modeling","Masked language modeling (BERT-style)","Data curation & preprocessing","Distributed pre-training","Checkpointing strategies","Emergent capabilities"]},
    {"title":"Key LLM Families","topics":["GPT-2 / GPT-3 / GPT-4","LLaMA 1/2/3","Mistral & Mixtral (MoE)","Gemma","Claude architecture","Gemini","Phi series (small LLMs)","Qwen / DeepSeek"]},
    {"title":"Architecture Variants","topics":["Encoder-only (BERT, RoBERTa)","Decoder-only (GPT)","Encoder-decoder (T5, BART)","Mixture of Experts (MoE)","Sparse transformers","Long-context models (Gemini 1.5)"]},
  ]},
  {"id":"p5","label":"Phase 5","title":"Training & Fine-Tuning","color":"#ef6c47","sections":[
    {"title":"Fine-Tuning Methods","topics":["Full fine-tuning","LoRA (Low-Rank Adaptation)","QLoRA","Prefix tuning","Prompt tuning","Adapter layers","PEFT library usage"]},
    {"title":"Instruction Tuning","topics":["Instruction datasets (Alpaca, FLAN)","Chat templates","System prompt design","Multi-turn fine-tuning","Self-instruct method"]},
    {"title":"RLHF & Alignment","topics":["Reward model training","Proximal Policy Optimization (PPO)","Direct Preference Optimization (DPO)","Constitutional AI","RLAIF","GRPO (DeepSeek-R1 style)","RLHF vs DPO tradeoffs"]},
    {"title":"Distributed Training","topics":["Data parallelism","Model parallelism","Pipeline parallelism","Tensor parallelism","Zero Redundancy Optimizer (ZeRO)","DeepSpeed","FSDP (PyTorch)","Megatron-LM"]},
    {"title":"Efficiency","topics":["Quantization (INT8, INT4, GPTQ)","Pruning & sparsity","Knowledge distillation","Flash attention 2","Gradient checkpointing","Mixed precision (BF16, FP16)"]},
  ]},
  {"id":"p6","label":"Phase 6","title":"Multimodal & Specialized","color":"#e879f9","sections":[
    {"title":"Vision-Language Models","topics":["CLIP (contrastive learning)","ALIGN","LLaVA","Flamingo / IDEFICS","GPT-4V","Gemini Vision","PaLI-X","InstructBLIP"]},
    {"title":"Text-to-Image","topics":["Stable Diffusion (deep dive)","DALL·E 3","Midjourney internals","ControlNet","IP-Adapter","DreamBooth fine-tuning","Textual inversion"]},
    {"title":"Video Generation","topics":["Sora architecture overview","Video diffusion models","AnimateDiff","CogVideoX","Temporal consistency","Motion conditioning"]},
    {"title":"Audio & Speech","topics":["Text-to-speech (TTS) models","Whisper (ASR)","MusicGen","AudioCraft","Voice cloning","Neural codec language models (VALL-E)"]},
    {"title":"Code Models","topics":["Codex / GitHub Copilot","StarCoder","Code Llama","DeepSeek-Coder","Fill-in-the-middle (FIM)","Unit test generation"]},
  ]},
  {"id":"p7","label":"Phase 7","title":"Prompting & RAG","color":"#fb7185","sections":[
    {"title":"Prompt Engineering","topics":["Zero-shot prompting","Few-shot prompting","Chain-of-thought (CoT)","Tree-of-thought (ToT)","Self-consistency","Least-to-most prompting","ReAct prompting","Structured output prompting"]},
    {"title":"Embeddings & Vector Search","topics":["Embedding models (text-embedding-3, E5, BGE)","Cosine similarity","FAISS","Pinecone","Weaviate","Chroma","Qdrant","ANN algorithms (HNSW, IVF)"]},
    {"title":"RAG","topics":["Naive RAG","Chunking strategies","Hybrid search (BM25 + dense)","Re-ranking (Cohere, Colbert)","Advanced RAG (query expansion, HyDE)","Self-RAG","GraphRAG","Contextual retrieval"]},
    {"title":"Structured Generation","topics":["JSON mode","Function calling / tool use","Instructor library","Outlines library","Constrained decoding (grammar-based)"]},
  ]},
  {"id":"p8","label":"Phase 8","title":"Agents & Agentic Systems","color":"#a3e635","sections":[
    {"title":"Agent Fundamentals","topics":["ReAct framework","Tool use & function calling","Planning & reasoning loops","Memory types (episodic, semantic, procedural)","Agent evaluation"]},
    {"title":"Frameworks","topics":["LangChain (chains, agents)","LlamaIndex (data agents)","AutoGen","CrewAI","LangGraph (stateful agents)","Pydantic AI","Smolagents"]},
    {"title":"Memory Systems","topics":["Short-term (context window)","Long-term (vector DB, knowledge graphs)","Working memory patterns","Memory compression","MemGPT architecture"]},
    {"title":"Multi-Agent Systems","topics":["Agent orchestration","Supervisor pattern","Swarm architecture","Task decomposition","Inter-agent communication","Hierarchical agents"]},
    {"title":"Agentic Patterns","topics":["Map-reduce agent","Reflection pattern","Plan-and-execute","Self-debugging agents","Human-in-the-loop","Computer use / browser agents"]},
  ]},
  {"id":"p9","label":"Phase 9","title":"Deployment & MLOps","color":"#94a3b8","sections":[
    {"title":"Inference & Serving","topics":["vLLM (PagedAttention)","TGI (Text Generation Inference)","Triton Inference Server","ONNX Runtime","TensorRT-LLM","OpenAI API-compatible serving","Batching strategies"]},
    {"title":"Optimization for Inference","topics":["KV cache management","Speculative decoding","Continuous batching","Prefix caching","AWQ quantization","GPTQ quantization","ExLlamaV2"]},
    {"title":"Evaluation","topics":["BLEU & ROUGE","BERTScore","FID (image generation)","MMLU / HellaSwag / ARC benchmarks","LLM-as-judge","RAGAS (RAG eval)","Human eval","Red-teaming"]},
    {"title":"MLOps for GenAI","topics":["Weights & Biases","MLflow","Experiment tracking","Model versioning","Data versioning (DVC)","CI/CD for ML","A/B testing LLMs","Prompt versioning"]},
    {"title":"Cloud & Infrastructure","topics":["AWS SageMaker","GCP Vertex AI","Azure ML","Lambda Labs / RunPod","Kubernetes for ML","Cost optimization"]},
  ]},
  {"id":"p10","label":"Phase 10","title":"Safety & Frontier Research","color":"#f97316","sections":[
    {"title":"Safety & Alignment","topics":["Hallucination types & mitigation","Factuality & grounding","Jailbreaking & prompt injection","Constitutional AI","RLHF alignment","Scalable oversight","Mechanistic interpretability","Activation patching"]},
    {"title":"Bias & Fairness","topics":["Representation bias in training data","Toxicity detection","Fairness metrics","Counterfactual fairness","Debiasing techniques","Red-teaming for bias"]},
    {"title":"Frontier Research Areas","topics":["Test-time compute scaling","Chain-of-thought reasoning models (o1, R1)","World models","Neurosymbolic AI","Continual learning","Federated learning for LLMs","Long-context scaling","AI agents in the wild"]},
    {"title":"Responsible AI","topics":["Data privacy & copyright","Model watermarking","Audit & governance","EU AI Act basics","NIST AI RMF","Synthetic data ethics"]},
  ]},
]

PRACTICE_CATS = [
  {"id":"cat-python","label":"Python Foundations","color":"#38bdf8","projects":[
    {"id":"py1","title":"NumPy Neural Net from Scratch","difficulty":"medium","time":"4–6 hrs","skills":["NumPy","Backprop","Linear Algebra"],"tools":["Python","NumPy","Matplotlib"],"desc":"Build a 2-layer neural network from pure NumPy — no PyTorch, no Keras. Implement forward pass, loss, backpropagation, and gradient descent by hand.","steps":["Implement matrix multiply & sigmoid/ReLU","Build a forward pass computing activations layer by layer","Implement MSE and cross-entropy loss from scratch","Derive and code backprop using chain rule","Run gradient descent on XOR and MNIST","Add mini-batch support and LR decay","Visualise decision boundaries with Matplotlib"],"concepts":["Chain rule","Jacobian","Gradient flow","Weight matrices","Loss landscape"],"outcomes":["Deep backprop intuition no framework gives","Confidence to debug gradient issues","Solid NumPy vectorisation skill"],"challenge":"Add a 3rd hidden layer and batch normalisation — purely in NumPy."},
    {"id":"py2","title":"Async LLM Batch Caller","difficulty":"medium","time":"3–4 hrs","skills":["asyncio","Concurrency","Python"],"tools":["Python","asyncio","httpx"],"desc":"Build a concurrent LLM batch caller with rate limiting, exponential backoff, and SSE streaming. Foundation of every production AI pipeline.","steps":["Understand the event loop, coroutines, async/await","Build async LLM caller with httpx","Fan out 50 prompts with asyncio.gather()","Add semaphore to cap concurrency","Implement exponential backoff for 429 errors","Stream SSE responses via async generators","Benchmark serial vs parallel"],"concepts":["Event loop","Coroutines","Semaphore","Backpressure","SSE streaming"],"outcomes":["Fast LLM batch pipelines","Handle rate limits gracefully","Understand async patterns in AI frameworks"],"challenge":"Add live progress bar with rich that updates per response."},
    {"id":"py3","title":"ML Utility Decorators","difficulty":"easy","time":"2 hrs","skills":["Python","Decorators","Profiling"],"tools":["Python","functools","contextlib"],"desc":"Write production-quality Python utilities: timing decorators, retry wrappers, GPU memory trackers — patterns from PyTorch/HuggingFace source.","steps":["Build @timer decorator","Build @retry with exponential backoff","Create no_grad context manager wrapper","Write ExperimentContext setting seeds","Implement @cache_to_disk","Combine into ml_utils.py with tests"],"concepts":["First-class functions","Closures","functools.wraps","Context managers"],"outcomes":["Clean reusable ML utility code","Understand HuggingFace/LangChain internals","Debug production ML pipelines faster"],"challenge":"Make @retry work with both sync and async functions."},
  ]},
  {"id":"cat-pytorch","label":"PyTorch & Training","color":"#f59e0b","projects":[
    {"id":"pt1","title":"Train a Mini-GPT on Custom Text","difficulty":"hard","time":"1–2 days","skills":["PyTorch","Transformers","LLM Pre-training"],"tools":["PyTorch","tiktoken","W&B","Colab/RunPod"],"desc":"Implement mini-GPT from scratch — multi-head causal attention, transformer blocks, BPE tokenizer — then train on domain-specific text.","steps":["Implement multi-head causal self-attention","Build transformer block: attention + MLP + LayerNorm","Stack N blocks with token + positional embeddings","Write data loader with BPE tokenization via tiktoken","Training loop with gradient accumulation + cosine LR","Log to W&B: loss, grad norms, sample generations","Replace learned positions with RoPE","Train on 100MB of text on free Colab T4","Generate text and measure perplexity"],"concepts":["Causal masking","RoPE","Gradient accumulation","LR warmup","Perplexity"],"outcomes":["Deep understanding of every LLM component","Ability to modify any open-source LLM","Real GPU training experience"],"challenge":"Implement KV-caching and measure tokens/sec speedup."},
    {"id":"pt2","title":"Fine-tune LLaMA with QLoRA","difficulty":"hard","time":"4–6 hrs","skills":["QLoRA","PEFT","Fine-tuning","HuggingFace"],"tools":["transformers","peft","trl","bitsandbytes"],"desc":"Fine-tune a 7B model on your own instruction dataset using QLoRA — industry standard for consumer-hardware fine-tuning.","steps":["Prepare 500–1000 row instruction dataset","Load 7B model in 4-bit NF4 with bitsandbytes","Configure LoRA: r, alpha, target modules","Set up SFTTrainer with packing and chat template","Train 1–3 epochs, monitor with W&B","Merge LoRA weights back into base model","Compare fine-tuned vs base on 20 test prompts","Push to Hugging Face Hub"],"concepts":["LoRA rank & alpha","NF4 quantization","Chat templates","Adapter merging","VRAM budgeting"],"outcomes":["Domain-specific LLM fine-tuning","PEFT internals understanding","Real fine-tuned model on HF Hub"],"challenge":"Quantize to GGUF and benchmark with llama.cpp."},
    {"id":"pt3","title":"DDPM Diffusion from Scratch","difficulty":"hard","time":"1 day","skills":["Diffusion Models","PyTorch","DDPM","UNet"],"tools":["PyTorch","torchvision","matplotlib","tqdm"],"desc":"Implement DDPM end-to-end on MNIST/CIFAR-10 — noise scheduler, UNet, training loop, reverse sampler — then extend with DDIM.","steps":["Implement forward process with cosine schedule","Build UNet with sinusoidal timestep embeddings","Implement DDPM training: predict noise epsilon","Write reverse diffusion sampling loop","Train on MNIST for ~50 epochs on Colab","Visualise the denoising process","Implement DDIM for 10x faster sampling","Add class conditioning for digit-specific generation"],"concepts":["Markov chain","ELBO","Score matching","DDIM","CFG"],"outcomes":["Intuition for how Stable Diffusion works","Ability to implement diffusion papers","UNet architecture mastery"],"challenge":"Condition on CLIP text embeddings for tiny text-to-image."},
  ]},
  {"id":"cat-llmapps","label":"LLM Apps & APIs","color":"#3dd68c","projects":[
    {"id":"llm1","title":"Production Streaming Chatbot","difficulty":"medium","time":"4–5 hrs","skills":["LLM APIs","Streaming","Memory"],"tools":["Anthropic SDK","FastAPI","Redis"],"desc":"Build a production chatbot backend with SSE streaming, Redis conversation memory, token counting, and auto-summarisation when context fills.","steps":["FastAPI with POST /chat/stream","SSE streaming with Anthropic SDK","Redis conversation history with TTL","Sliding window: keep last N tokens","Token counting with tiktoken","Conversation summarisation when context full","Minimal HTML/JS SSE frontend","Per-user rate limiting with slowapi"],"concepts":["SSE streaming","Context management","Token counting","Session state","Rate limiting"],"outcomes":["Backend skills to ship real chatbot","Context management in production","Streaming API integration"],"challenge":"Add tool use with full tool-call/tool-result loop."},
    {"id":"llm2","title":"Structured Data Extraction","difficulty":"medium","time":"3–4 hrs","skills":["Pydantic","Structured Output","Data Engineering"],"tools":["instructor","Pydantic","Anthropic/OpenAI","pandas"],"desc":"Extract typed, validated JSON from unstructured text at scale using Pydantic + Instructor with auto-retry on validation failure.","steps":["Define Pydantic model with nested types","Patch client with instructor library","Extract from 10 sample documents","Add field validators for enums, dates, ranges","Async batch for 1000 docs with rate limiting","Handle partial extractions gracefully","Export to pandas DataFrame","Build eval: sample 50, measure accuracy"],"concepts":["JSON Schema","Pydantic validation","Retry-on-validation-error","Async batching"],"outcomes":["Build any extraction pipeline quickly","Pydantic expert skill","Production LLM pipeline architecture"],"challenge":"Second-pass validator: run each extraction twice, flag disagreements."},
    {"id":"llm3","title":"LLM Evaluation Framework","difficulty":"medium","time":"4–5 hrs","skills":["LLM Evaluation","LLM-as-Judge","Benchmarking"],"tools":["Python","Anthropic API","pandas","plotly"],"desc":"Build your own LLM eval harness with LLM-as-judge, pairwise comparison, and factual consistency — benchmark two models head-to-head.","steps":["Create 50–100 row test set","ROUGE and exact-match baselines","LLM-as-judge with rubric-based scoring","Pairwise comparison: A vs B","Factual consistency checker","Run Claude vs GPT-4o on your test set","Aggregate scores with confidence intervals","Visualise per-category with plotly","Write findings summary"],"concepts":["Evaluation metrics","Judge bias","Position bias","Benchmark leakage","Calibration"],"outcomes":["Reliable AI product evaluation","Catch regressions before users do","LLM benchmark design expertise"],"challenge":"Add judge calibration with golden examples and Spearman correlation."},
  ]},
  {"id":"cat-rag","label":"RAG & Vector Search","color":"#fb7185","projects":[
    {"id":"rag1","title":"Advanced RAG Pipeline","difficulty":"medium","time":"6–8 hrs","skills":["RAG","Vector DBs","Embeddings","Retrieval"],"tools":["LangChain","ChromaDB","Anthropic API","RAGAS"],"desc":"Production RAG beyond naive retrieval: hybrid search, HyDE query expansion, cross-encoder re-ranking, citation generation, RAGAS eval.","steps":["Ingest 100+ page PDF: parse, clean, chunk","Embed with BGE-M3 or text-embedding-3-large","Store in ChromaDB with rich metadata","Naive RAG baseline, measure accuracy","BM25 + dense hybrid search with RRF","HyDE: embed hypothetical answer, retrieve","Cross-encoder re-ranker on top-20","Citation generator grounding answers","RAGAS eval: faithfulness, relevancy, precision","FastAPI endpoint + chat UI"],"concepts":["Semantic chunking","RRF fusion","HyDE","Cross-encoder re-ranking","RAGAS"],"outcomes":["Build any enterprise RAG system","Deep retrieval quality knowledge","Full-stack RAG deployment"],"challenge":"Add self-RAG: verify each claim is supported by retrieved context."},
    {"id":"rag2","title":"GraphRAG with Neo4j","difficulty":"hard","time":"1 day","skills":["GraphRAG","Knowledge Graphs","Neo4j"],"tools":["Neo4j","LangChain","Anthropic API","spaCy"],"desc":"Combine knowledge graph traversal with vector retrieval. Extract entities/relationships from docs, store in Neo4j, answer multi-hop questions.","steps":["Extract (s,r,o) triplets with spaCy + LLM","Store in Neo4j","Link chunks in vector store to KG nodes","Query: extract entities, traverse KG","Combine graph + vector context","Answer multi-hop questions","Compare vs naive RAG on 20 questions","Visualise KG with pyvis"],"concepts":["Knowledge graphs","Entity extraction","Graph traversal","Multi-hop reasoning"],"outcomes":["RAG for complex multi-document reasoning","Neo4j skills","When GraphRAG beats naive RAG"],"challenge":"Add temporal reasoning: tag relationships with time periods."},
  ]},
  {"id":"cat-agents","label":"AI Agents & Agentic Systems","color":"#a3e635","projects":[
    {"id":"ag1","title":"ReAct Agent from Scratch","difficulty":"medium","time":"5–6 hrs","skills":["ReAct","Tool Use","Agents"],"tools":["Anthropic API","Python"],"desc":"Build a ReAct agent from scratch — no LangChain. Implement the think→tool-call→observe→think loop using Anthropic tool-use API with 5 real tools.","steps":["Define 5 tools: web_search, calculator, code_executor, file_read, wikipedia","Implement real Python functions for each","Agent loop: call LLM → parse tool_use → execute → feed result","Multi-turn with accumulated messages + tool_result blocks","Max steps limit and stopping condition","Chain-of-thought scratchpad before each action","Test on 10 multi-step tasks","Add streaming to watch agent think","Log tool calls, build success rate report"],"concepts":["Tool use","ReAct loop","Message accumulation","Tool result formatting","Stopping criteria"],"outcomes":["Build any custom agent without framework","Understand LangChain agent internals","Tool design expertise"],"challenge":"Add memory: persist observations to vector store across sessions."},
    {"id":"ag2","title":"Multi-Agent Research with LangGraph","difficulty":"hard","time":"1 day","skills":["LangGraph","Multi-agent","Orchestration"],"tools":["LangGraph","LangChain","Anthropic API","Tavily"],"desc":"Planner → Researcher×3 (parallel) → Critic → Writer pipeline with conditional loops, human-in-the-loop approval, and streaming execution.","steps":["Design graph: Planner, Researcher×3, Critic, Writer","Define shared state with TypedDict","Planner: decompose question into sub-queries","Researcher: web search + RAG per sub-query","Fan out Researchers with Send() API","Critic: review for gaps and contradictions","Conditional edge: if unsatisfied, loop back","Writer: synthesise report with citations","Human-in-the-loop before final write","Stream graph execution live"],"concepts":["Graph state","Conditional edges","Fan-out/fan-in","Human-in-the-loop","Checkpointing"],"outcomes":["Production multi-agent pipelines","LangGraph expert skill","When multi-agent beats single-agent"],"challenge":"Add memory: reuse cached results if question was researched before."},
    {"id":"ag3","title":"Self-Debugging Coding Agent","difficulty":"hard","time":"1 day","skills":["Code Generation","Self-debugging","Agents"],"tools":["Anthropic API","Python","subprocess","pytest","Docker"],"desc":"Agent that writes, runs, tests, and self-debugs Python code. Gets a task, writes code, executes in sandbox, reads errors, fixes, iterates.","steps":["Set up Docker sandbox for safe execution","code_exec tool: runs Python, returns stdout/stderr","write_file, read_file, run_tests tools","Agent loop: write → test → debug → repeat","10 LeetCode-style challenges","Measure: solve rate within 5 iterations","Code review step: suggest improvements","Log iterations, compute pass@k"],"concepts":["Sandboxed execution","Self-debugging loops","Pass@k","Test-driven generation"],"outcomes":["Build Devin-style coding assistant","Code agent design expertise","Docker sandboxing skills"],"challenge":"TDD agent: write tests first, then implement to pass them."},
    {"id":"ag4","title":"Voice AI Assistant — End to End","difficulty":"hard","time":"1 day","skills":["STT","TTS","LLM","Real-time Audio"],"tools":["Whisper","ElevenLabs","Anthropic API","FastAPI","WebSocket"],"desc":"Full voice AI: mic → Whisper STT → Claude with tools → ElevenLabs TTS → speaker. Full duplex, real-time streaming, live transcript UI.","steps":["Record mic with PyAudio + VAD","Transcribe with Whisper","Send to Claude with tools (calendar, weather, search)","Stream response to TTS per sentence","Play TTS output in real time","WebSocket server in FastAPI","React/HTML frontend: audio level, transcript, tool calls","Wake-word detection","Measure end-to-end latency"],"concepts":["VAD","Streaming TTS","WebSocket full-duplex","Latency optimization","Wake-word"],"outcomes":["Build any voice AI product","Real-time audio pipeline mastery","End-to-end full-stack AI"],"challenge":"Emotion detection from voice tone, adjust response style."},
  ]},
  {"id":"cat-mlops","label":"MLOps & Deployment","color":"#94a3b8","projects":[
    {"id":"ops1","title":"Deploy LLM with vLLM + Docker","difficulty":"medium","time":"5–6 hrs","skills":["vLLM","Docker","FastAPI","LLM Serving"],"tools":["vLLM","Docker","FastAPI","Nginx","Prometheus"],"desc":"Deploy Mistral 7B as a production OpenAI-compatible API using vLLM. Add auth, rate limiting, Prometheus monitoring, Grafana dashboards.","steps":["Set up vLLM with 7B model, test with OpenAI SDK","FastAPI wrapper: API key auth + rate limiting","Dockerfile + docker-compose with CUDA passthrough","Prometheus metrics: requests, latency p50/p95/p99","Grafana dashboard with LLM panels","Nginx load balancing across 2 vLLM instances","Load test with locust","Request/response logging to PostgreSQL","Deploy to RunPod or Lambda Labs"],"concepts":["Continuous batching","PagedAttention","GPU memory management","OpenAI API compat","Horizontal scaling"],"outcomes":["Ship production LLM APIs","ML infrastructure skills","Deep vLLM internals"],"challenge":"Speculative decoding with TinyLlama draft model."},
    {"id":"ops2","title":"LLM Observability System","difficulty":"medium","time":"4–5 hrs","skills":["LLM Observability","Tracing","Analytics"],"tools":["Langfuse","OpenTelemetry","PostgreSQL","Grafana"],"desc":"Full observability: trace every call, measure latency per step, track costs, detect quality regressions, build dashboard.","steps":["Instrument with OpenTelemetry spans","Store traces in PostgreSQL: prompt, response, latency, cost","Cost calculator: tokens × pricing","Add Langfuse for LLM-specific tracing","Anomaly detection: flag topic drift","Daily reports: latency, cost, error rate","Grafana p99 latency alerts","A/B testing: 10% traffic to new model","User feedback loop: thumbs up/down"],"concepts":["Distributed tracing","LLM cost accounting","Semantic drift","A/B testing","Feedback loops"],"outcomes":["Production LLM monitoring","Cost control for AI products","Data-driven prompt iteration"],"challenge":"Automatic regression detector comparing weekly quality scores."},
  ]},
  {"id":"cat-capstone","label":"Capstone Projects","color":"#e879f9","projects":[
    {"id":"cap1","title":"AI Research Assistant — Full Stack","difficulty":"hard","time":"1–2 weeks","skills":["Full Stack","RAG","Agents","Fine-tuning","Deployment"],"tools":["Next.js","FastAPI","PostgreSQL","Redis","ChromaDB","Anthropic"],"desc":"Build and ship a complete AI research assistant: ingest papers/docs/web, RAG Q&A, insight saving, literature review generation. Your portfolio centrepiece.","steps":["FastAPI + PostgreSQL + Redis + ChromaDB backend","URL scraper, PDF parser, arXiv API connector","Semantic chunking + hybrid search + re-ranking + citations","ResearchAgent: autonomously searches arXiv and summarises","Next.js: streaming chat, document viewer, insight board","JWT auth, per-user document collections","Deploy: Docker on Railway/Render, Vercel for frontend","Fine-tune small model on your interaction data","RAGAS eval + Langfuse usage tracking","Landing page, README, demo video"],"concepts":["Full-stack architecture","Multi-tenant design","Vector DB at scale","Streaming UX","Production deployment"],"outcomes":["Shipped real product to show employers","Full-stack AI engineering portfolio","End-to-end system design experience"],"challenge":"Weekly digest: agent emails you new papers on tracked topics every Sunday."},
    {"id":"cap2","title":"Open Source LLM Contribution","difficulty":"hard","time":"Ongoing","skills":["Open Source","PyTorch","LLM internals","Research Engineering"],"tools":["GitHub","PyTorch","transformers","vLLM or llama.cpp"],"desc":"Contribute to vLLM, HuggingFace transformers, llama.cpp, or LangGraph. Study codebase, find a good first issue, ship a real merged PR.","steps":["Pick: vLLM, transformers, llama.cpp, LangGraph, or LlamaIndex","Read architecture docs, explore codebase for a week","Run all tests locally, make trivial change to verify setup","Find 'good first issue' or 'help wanted' labels","Pick issue related to something you've studied","Read relevant papers before writing code","Write implementation with tests following style guide","Open draft PR early, get maintainer feedback","Iterate until merged","Write blog post explaining what you built"],"concepts":["Codebase navigation","TDD","Git workflow","Code review","Technical writing"],"outcomes":["Proof of expert-level skill","Maintainer network in AI field","Deep codebase understanding"],"challenge":"Write a Twitter/LinkedIn thread after your first merged PR."},
  ]},
]

# ── AI call ───────────────────────────────────────────────────────────────────
def call_anthropic(prompt: str) -> str:
    if not ANTHROPIC_KEY:
        return "⚠️ Set ANTHROPIC_API_KEY in Streamlit secrets."
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 700,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"]
        return f"API error {r.status_code}: {r.json().get('error',{}).get('message','')}"
    except Exception as e:
        return f"Error: {e}"

# ── Helper: note key ──────────────────────────────────────────────────────────
def nkey(phase_id, topic): return f"{phase_id}::{topic}"
def akey(phase_id, topic): return f"__att__{phase_id}::{topic}"

def get_note(k):    return notes.get(k, "")
def get_attach(k):  return notes.get(akey(*k.split("::")) if "::" in k else k, [])

# ── Stats ─────────────────────────────────────────────────────────────────────
all_topics   = [nkey(p["id"], t) for p in PHASES for s in p["sections"] for t in s["topics"]]
noted_count  = sum(1 for k in all_topics if notes.get(k, "").strip())
all_projects = [pr for c in PRACTICE_CATS for pr in c["projects"]]
done_count   = sum(1 for pr in all_projects if done_practice.get(pr["id"]))

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:14px 14px 10px;border-bottom:1px solid #ffffff12">
      <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:800;
                  background:linear-gradient(135deg,#7c6ef7,#38bdf8);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        🧠 GenAI Notes
      </div>
      <div style="font-size:10px;color:#5c6275;margin-top:2px;font-family:'DM Mono',monospace">
        // expert knowledge base + practice lab
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tab switcher (only 2 real buttons — fine) ─────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        notes_active = st.session_state.tab == "notes"
        nb_style = "background:#7c6ef720;color:#7c6ef7;border:1px solid #7c6ef740;" if notes_active else "background:#1a1d26;color:#9298ab;border:1px solid #ffffff15;"
        st.markdown(f'<button onclick="window.location.href=\'?tab=notes\'" style="{nb_style}width:100%;padding:7px 4px;border-radius:8px;font-family:Syne,sans-serif;font-weight:600;font-size:11px;cursor:pointer;transition:all .15s">📚 NOTES</button>', unsafe_allow_html=True)
    with c2:
        prac_active = st.session_state.tab == "practice"
        pb_style = "background:#7c6ef720;color:#7c6ef7;border:1px solid #7c6ef740;" if prac_active else "background:#1a1d26;color:#9298ab;border:1px solid #ffffff15;"
        st.markdown(f'<button onclick="window.location.href=\'?tab=practice\'" style="{pb_style}width:100%;padding:7px 4px;border-radius:8px;font-family:Syne,sans-serif;font-weight:600;font-size:11px;cursor:pointer;transition:all .15s">⚡ PRACTICE</button>', unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Search ────────────────────────────────────────────────────────────────
    search = st.text_input("search", placeholder="🔍  Search topics…",
                           label_visibility="collapsed", key="search_input")
    fl = search.strip().lower()

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    # ── Build nav HTML in one shot ────────────────────────────────────────────
    ck_now  = st.session_state.current_key
    pid_now = st.session_state.current_pid
    cur_tab = st.session_state.tab

    nav_html = '<div class="sb-nav">'

    if cur_tab == "notes":
        for phase in PHASES:
            all_t   = [t for s in phase["sections"] for t in s["topics"]]
            vis_t   = [t for t in all_t if fl in t.lower()] if fl else all_t
            if not vis_t: continue
            noted_p = sum(1 for t in all_t if notes.get(nkey(phase["id"], t), "").strip())
            pct     = int(noted_p / len(all_t) * 100) if all_t else 0

            nav_html += f'''
            <div class="sb-phase-hdr">
              <span class="sb-pdot" style="background:{phase["color"]}"></span>
              <span style="flex:1">{phase["label"]}: {phase["title"]}</span>
              <span class="sb-pcnt">{noted_p}/{len(all_t)}</span>
            </div>
            <div class="sb-prog">
              <div class="sb-prog-track">
                <div class="sb-prog-fill" style="width:{pct}%;background:{phase["color"]}"></div>
              </div>
            </div>'''

            for section in phase["sections"]:
                s_vis = [t for t in section["topics"] if fl in t.lower()] if fl else section["topics"]
                if not s_vis: continue
                nav_html += f'<div class="sb-sec-lbl">{section["title"]}</div>'
                for topic in s_vis:
                    k        = nkey(phase["id"], topic)
                    has_note = bool(notes.get(k, "").strip())
                    is_act   = ck_now == k
                    dot      = '<span class="sb-noted-dot"></span>' if has_note else ''
                    act_cls  = " active" if is_act else ""
                    href = f"?nav={urllib.parse.quote(k)}&tab=notes"
                    nav_html += f'<a class="sb-topic{act_cls}" href="{href}" title="{topic}">{dot}{topic}</a>'

    else:  # practice tab
        for cat in PRACTICE_CATS:
            vis_p  = [p for p in cat["projects"] if fl in p["title"].lower() or any(fl in s.lower() for s in p["skills"])] if fl else cat["projects"]
            if not vis_p: continue
            done_c = sum(1 for p in cat["projects"] if done_practice.get(p["id"]))
            nav_html += f'''
            <div class="sb-phase-hdr">
              <span class="sb-pdot" style="background:{cat["color"]}"></span>
              <span style="flex:1">{cat["label"]}</span>
              <span class="sb-pcnt">{done_c}/{len(cat["projects"])}</span>
            </div>'''
            for proj in vis_p:
                is_act    = pid_now == proj["id"]
                is_done   = done_practice.get(proj["id"], False)
                diff_col  = {"easy":"#3dd68c","medium":"#f59e0b","hard":"#ef4444"}.get(proj["difficulty"],"#94a3b8")
                status    = f'<span style="color:{diff_col};font-size:8px;margin-right:4px">{"✓" if is_done else "●"}</span>'
                act_cls   = " active" if is_act else ""
                href      = f"?nav={urllib.parse.quote(proj['id'])}&tab=practice"
                nav_html += f'<a class="sb-topic{act_cls}" href="{href}" title="{proj["title"]}">{status}{proj["title"]}</a>'

    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
ck  = st.session_state.current_key
pid = st.session_state.current_pid

# Welcome screen
if not ck and not pid:
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Topics", len(all_topics))
    c2.metric("Noted",  noted_count)
    c3.metric("Projects", len(all_projects))
    c4.metric("Done",   done_count)
    st.markdown("""
    <div style="text-align:center;padding:48px 0 20px">
      <div style="font-size:48px;opacity:.2">⚡</div>
      <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                  color:#9298ab;margin:12px 0 8px">Pick a topic to begin</div>
      <div style="font-size:13px;color:#5c6275;max-width:360px;margin:0 auto;line-height:1.6">
        Use <strong style="color:#e8eaf0">Notes</strong> tab to write & AI-revise theory.<br>
        Use <strong style="color:#e8eaf0">Practice</strong> tab for hands-on projects.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── NOTES topic view ──────────────────────────────────────────────────────────
elif ck:
    phase_id, topic = ck.split("::", 1)
    phase = next((p for p in PHASES if p["id"] == phase_id), {})

    # Header
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 12px;
                border-bottom:1px solid #ffffff12;margin-bottom:14px">
      <span style="background:{phase.get('color','#7c6ef7')}20;color:{phase.get('color','#7c6ef7')};
                   border:1px solid {phase.get('color','#7c6ef7')}40;
                   font-size:10px;padding:3px 9px;border-radius:20px;
                   font-family:'DM Mono',monospace;white-space:nowrap">
        {phase.get('label','')}: {phase.get('title','')}
      </span>
      <span style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;
                   color:#e8eaf0">{topic}</span>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout: editor | revision
    col_edit, col_rev = st.columns([3, 2], gap="medium")

    with col_edit:
        # Notes textarea
        current_text = notes.get(ck, "")
        new_text = st.text_area(
            "📝 YOUR NOTES — markdown supported",
            value=current_text,
            height=320,
            placeholder="Write notes here…\n\n• Explain it in your own words\n• Add code snippets and examples\n• Note gotchas and common mistakes\n• Then click ✦ AI Revise for a sharp summary",
            key=f"editor_{ck}"
        )

        # Save / Clear buttons
        b1, b2, b3 = st.columns([2, 2, 2])
        with b1:
            st.markdown('<div class="revise-btn">', unsafe_allow_html=True)
            if st.button("✦ AI Revise", key=f"revise_{ck}", use_container_width=True):
                with st.spinner("Generating revision…"):
                    prompt = f"""You are a concise GenAI teacher. The student is studying: **{topic}**

Their notes:
{new_text or '(no notes yet)'}

Generate a sharp, exam-ready revision summary with:
1. Core concept in one sentence
2. Key points (5–8 bullets, each ≤ 15 words)
3. Common gotcha / tricky part
4. One analogy that makes it click

Keep it tight — max 250 words. Use markdown."""
                    st.session_state.revision_text = call_anthropic(prompt)
                    st.session_state.revision_mode = "revision"
            st.markdown("</div>", unsafe_allow_html=True)
        with b2:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            if st.button("💾 Save Note", key=f"save_{ck}", use_container_width=True):
                if new_text.strip():
                    notes[ck] = new_text
                else:
                    notes.pop(ck, None)
                persist()
                st.success("✓ Saved!", icon="✅")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with b3:
            st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
            if st.button("✕ Clear", key=f"clear_{ck}", use_container_width=True):
                notes.pop(ck, None)
                persist()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Attachments ───────────────────────────────────────────────────────
        st.markdown("""
        <div style="margin-top:16px;padding-top:12px;border-top:1px solid #ffffff12">
          <div style="font-size:10px;font-family:'DM Mono',monospace;color:#5c6275;
                      text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">
            📎 Attachments
          </div>
        </div>
        """, unsafe_allow_html=True)

        att_key = f"__att__{ck}"
        attachments = notes.get(att_key, [])

        ua1, ua2 = st.columns(2)
        with ua1:
            img_files = st.file_uploader("🖼 Add Images", type=["png","jpg","jpeg","gif","webp"],
                                          accept_multiple_files=True, key=f"img_{ck}",
                                          label_visibility="collapsed")
            if img_files:
                for f in img_files:
                    if f.size > 4 * 1024 * 1024:
                        st.warning(f"{f.name} too large (max 4MB)")
                        continue
                    b64 = base64.b64encode(f.read()).decode()
                    mime = f.type or "image/png"
                    data_url = f"data:{mime};base64,{b64}"
                    # Avoid duplicates
                    if not any(a.get("name") == f.name and a.get("type") == "image" for a in attachments):
                        attachments.append({"type":"image","name":f.name,"data":data_url})
                notes[att_key] = attachments
                persist()
                st.rerun()
            st.markdown('<div style="font-size:10px;color:#5c6275;font-family:DM Mono,monospace;margin-top:-8px">🖼 Images</div>', unsafe_allow_html=True)

        with ua2:
            code_files = st.file_uploader(
                "📄 Add Code",
                type=["py","js","ts","jsx","tsx","json","yaml","yml","txt","md","sh","cpp","c","java","rs","go","sql","html","css"],
                accept_multiple_files=True,
                key=f"code_{ck}",
                label_visibility="collapsed"
            )
            if code_files:
                for f in code_files:
                    if f.size > 500 * 1024:
                        st.warning(f"{f.name} too large (max 500KB)")
                        continue
                    content = f.read().decode("utf-8", errors="replace")
                    ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else "txt"
                    if not any(a.get("name") == f.name and a.get("type") == "code" for a in attachments):
                        attachments.append({"type":"code","name":f.name,"data":content,"lang":ext})
                notes[att_key] = attachments
                persist()
                st.rerun()
            st.markdown('<div style="font-size:10px;color:#5c6275;font-family:DM Mono,monospace;margin-top:-8px">📄 Code files</div>', unsafe_allow_html=True)

        # Show existing attachments
        if attachments:
            imgs  = [a for a in attachments if a["type"] == "image"]
            codes = [a for a in attachments if a["type"] == "code"]

            if imgs:
                st.markdown(f'<div style="font-size:10px;color:#5c6275;font-family:DM Mono,monospace;text-transform:uppercase;letter-spacing:.04em;margin:10px 0 6px">Images ({len(imgs)})</div>', unsafe_allow_html=True)
                img_cols = st.columns(min(len(imgs), 4))
                for i, att in enumerate(imgs):
                    with img_cols[i % 4]:
                        st.image(att["data"], caption=att["name"], use_container_width=True)
                        if st.button("✕ Remove", key=f"del_img_{ck}_{i}"):
                            attachments.remove(att)
                            notes[att_key] = attachments
                            persist()
                            st.rerun()

            if codes:
                st.markdown(f'<div style="font-size:10px;color:#5c6275;font-family:DM Mono,monospace;text-transform:uppercase;letter-spacing:.04em;margin:10px 0 6px">Code files ({len(codes)})</div>', unsafe_allow_html=True)
                for i, att in enumerate(codes):
                    lang_icon = {"py":"🐍","js":"🟨","ts":"🔷","jsx":"⚛","tsx":"⚛","json":"{}","yaml":"📋","yml":"📋","sh":"🖥","cpp":"⚙","c":"⚙","java":"☕","rs":"🦀","go":"🐹","sql":"🗃","html":"🌐","css":"🎨","md":"📝"}.get(att.get("lang",""),"📄")
                    with st.expander(f"{lang_icon} {att['name']}  ·  {att.get('lang','').upper()}", expanded=False):
                        st.code(att["data"][:3000] + ("…" if len(att["data"]) > 3000 else ""), language=att.get("lang","text"))
                        if st.button("✕ Remove file", key=f"del_code_{ck}_{i}"):
                            attachments.remove(att)
                            notes[att_key] = attachments
                            persist()
                            st.rerun()

    with col_rev:
        st.markdown('<div style="font-size:10px;font-family:DM Mono,monospace;color:#5c6275;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">✦ AI Revision Summary</div>', unsafe_allow_html=True)
        if st.session_state.revision_text:
            st.markdown(st.session_state.revision_text)
        else:
            st.markdown('<div style="color:#5c6275;font-style:italic;font-size:13px;padding-top:20px;text-align:center">Click ✦ AI Revise to generate<br>a revision summary from your notes.</div>', unsafe_allow_html=True)

# ── PRACTICE project view ──────────────────────────────────────────────────────
elif pid:
    proj = next((p for c in PRACTICE_CATS for p in c["projects"] if p["id"] == pid), None)
    cat  = next((c for c in PRACTICE_CATS for p in c["projects"] if p["id"] == pid), None)
    if not proj or not cat:
        st.error("Project not found")
    else:
        diff_color = {"easy":"#3dd68c","medium":"#f59e0b","hard":"#ef4444"}.get(proj["difficulty"],"#94a3b8")
        diff_label = {"easy":"Easy","medium":"Medium","hard":"Hard"}.get(proj["difficulty"],"")

        # Header
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:4px 0 12px;
                    border-bottom:1px solid #ffffff12;margin-bottom:14px;flex-wrap:wrap">
          <span style="background:{cat['color']}20;color:{cat['color']};
                       border:1px solid {cat['color']}40;
                       font-size:10px;padding:3px 9px;border-radius:20px;
                       font-family:'DM Mono',monospace">{cat['label']}</span>
          <span style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;
                       color:#e8eaf0;flex:1">{proj['title']}</span>
          <span class="chip chip-{proj['difficulty']}">{diff_label}</span>
          <span style="font-size:11px;color:#5c6275;font-family:'DM Mono',monospace">⏱ {proj['time']}</span>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_r = st.columns([3, 2], gap="medium")

        with col_l:
            # Tags
            skills_html = "".join(f'<span class="chip chip-skill">{s}</span>' for s in proj["skills"])
            tools_html  = "".join(f'<span class="chip chip-tool">{t}</span>'  for t in proj["tools"])
            st.markdown(f'<div style="margin-bottom:10px">{skills_html}{tools_html}</div>', unsafe_allow_html=True)

            # Description
            st.markdown(f'<p style="font-size:13px;color:#9298ab;line-height:1.7;margin-bottom:16px">{proj["desc"]}</p>', unsafe_allow_html=True)

            # What you'll gain
            st.markdown('<div style="font-size:11px;font-family:DM Mono,monospace;color:#5c6275;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px">🎯 What you\'ll gain</div>', unsafe_allow_html=True)
            for o in proj["outcomes"]:
                st.markdown(f'<div style="display:flex;gap:7px;padding:3px 0;font-size:12.5px;color:#9298ab"><span style="color:#3dd68c;flex-shrink:0">✓</span>{o}</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            # Steps
            st.markdown('<div style="font-size:11px;font-family:DM Mono,monospace;color:#5c6275;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px">📋 Step-by-step guide</div>', unsafe_allow_html=True)
            for i, step in enumerate(proj["steps"], 1):
                st.markdown(f'<div style="display:flex;gap:10px;padding:6px 0;border-bottom:1px solid #ffffff08;font-size:12.5px;color:#9298ab"><span style="width:18px;height:18px;border-radius:50%;background:#5b4fd4;color:#fff;font-size:9px;font-family:DM Mono,monospace;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px">{i}</span>{step}</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            # Concepts
            st.markdown('<div style="font-size:11px;font-family:DM Mono,monospace;color:#5c6275;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px">🧠 Concepts you\'ll master</div>', unsafe_allow_html=True)
            chips = "".join(f'<span style="display:inline-block;background:#1a1d26;border:1px solid #ffffff12;border-radius:6px;padding:3px 9px;font-size:11px;color:#9298ab;margin:2px;font-family:DM Mono,monospace">{c}</span>' for c in proj["concepts"])
            st.markdown(f'<div style="margin-bottom:12px">{chips}</div>', unsafe_allow_html=True)

            # Challenge box
            st.markdown(f"""
            <div style="background:#7c6ef710;border:1px solid #7c6ef730;border-radius:10px;
                        padding:10px 14px;margin-top:4px;font-size:12.5px;color:#9298ab;line-height:1.6">
              <strong style="color:#7c6ef7">🔥 Stretch Challenge:</strong> {proj['challenge']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            # Mark done button
            is_done = done_practice.get(pid, False)
            d1, d2 = st.columns([2, 3])
            with d1:
                done_cls = "clear-btn" if is_done else "done-btn"
                st.markdown(f'<div class="{done_cls}">', unsafe_allow_html=True)
                if st.button("↩ Mark Undone" if is_done else "✓ Mark Done", key=f"done_{pid}", use_container_width=True):
                    done_practice[pid] = not is_done
                    persist()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        with col_r:
            # AI Help
            st.markdown('<div style="font-size:10px;font-family:DM Mono,monospace;color:#5c6275;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">✦ AI Project Help</div>', unsafe_allow_html=True)

            ha, hb, hc = st.columns(3)
            with ha:
                st.markdown('<div class="revise-btn">', unsafe_allow_html=True)
                if st.button("✦ Concepts", key=f"ai_explain_{pid}", use_container_width=True):
                    with st.spinner("Generating…"):
                        st.session_state.revision_text = call_anthropic(f"Explain the core concepts for this GenAI project intuitively (200 words max):\n\nProject: {proj['title']}\nConcepts: {', '.join(proj['concepts'])}\n\nBullet points, focus on intuition not math.")
                        st.session_state.revision_mode = "explain"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with hb:
                st.markdown('<div class="revise-btn">', unsafe_allow_html=True)
                if st.button("💡 Hint", key=f"ai_hint_{pid}", use_container_width=True):
                    with st.spinner("Generating…"):
                        st.session_state.revision_text = call_anthropic(f"Give 3 specific implementation hints (not solutions) for this project:\n\nProject: {proj['title']}\nTools: {', '.join(proj['tools'])}\nFirst steps: {'; '.join(proj['steps'][:4])}\n\nNudge without spoiling.")
                        st.session_state.revision_mode = "hint"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with hc:
                st.markdown('<div class="revise-btn">', unsafe_allow_html=True)
                if st.button("⚠ Pitfalls", key=f"ai_pitfalls_{pid}", use_container_width=True):
                    with st.spinner("Generating…"):
                        st.session_state.revision_text = call_anthropic(f"List the top 5 pitfalls and debugging tips for this project:\n\nProject: {proj['title']}\n\nNumbered list with brief explanations.")
                        st.session_state.revision_mode = "pitfalls"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.revision_text:
                st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
                st.markdown(st.session_state.revision_text)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#5c6275;font-style:italic;font-size:12px;padding-top:16px;text-align:center">Click a button above<br>to get AI help on this project.</div>', unsafe_allow_html=True)
