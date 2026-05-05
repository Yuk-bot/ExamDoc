import streamlit as st
import requests
import os


st.set_page_config(
    page_title="ExamDoc AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = None

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
    st.session_state.uploaded_file_ext = None

#css
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=DM+Mono:wght@400;500&display=swap');

/* Reset */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f5f4f0; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1a1a18 !important;
    border-right: 1px solid #2c2c28;
    width: 400px !important;
}
[data-testid="stSidebar"] > div { padding: 2rem 1.4rem; }
[data-testid="stSidebar"] * { color: #a8a89e !important; }
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] strong { color: #f0efe8 !important; }

/* Brand */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 2rem;
}
.brand-dot {
    width: 28px; height: 28px;
    background: #e8e25a;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
}
.brand-name {
    font-size: 0.92rem;
    font-weight: 600;
    color: #f0efe8 !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* Labels */
.sidebar-label {
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #484840 !important;
    margin-bottom: 0.75rem;
    display: block;
}

/* Summary */
.summary-box {
    background: #242420;
    border-left: 3px solid #e8e25a;
    border-radius: 8px;
    padding: 1rem;
    font-size: 0.8rem;
}

/* Topbar */
.topbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1.4rem;
}
.status-badge {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 0.3rem 0.7rem;
    font-size: 0.7rem;
}

/* Panels */
.panel-header {
    padding: 0.9rem 1.2rem;
    border-bottom: 1px solid #ebebdf;
    background: #fafaf6;
    display: flex;
    justify-content: space-between;
}
.panel-title {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
}
.panel-badge {
    font-size: 0.68rem;
    font-family: monospace;
}

/* Chat */
.chat-empty {
    height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:

    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-dot"></div>
        <span class="brand-name">ExamDoc AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sidebar-label">Documents</span>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files and st.button("Analyse Document"):

        files = []
        for file in uploaded_files:
            ext = os.path.splitext(file.name)[1].lower()
            mime = "application/pdf"
            if ext == ".docx":
                mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == ".txt":
                mime = "text/plain"

            files.append(("files", (file.name, file.getvalue(), mime)))

        with st.spinner("Processing…"):
            try:
                res = requests.post("http://127.0.0.1:8000/upload-files", files=files)

                if res.status_code == 200:
                    data = res.json()
                    st.session_state.summary = data[-1]["summary"]
                    st.session_state.uploaded_file = uploaded_files[-1]
                    st.session_state.uploaded_file_ext = os.path.splitext(uploaded_files[-1].name)[1].lower()
                    st.success("Ready!")
                else:
                    st.error(res.text)

            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.summary:
        st.markdown("---")
        st.markdown('<span class="sidebar-label">Summary</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-box">{st.session_state.summary}</div>', unsafe_allow_html=True)


doc_loaded = st.session_state.uploaded_file is not None
doc_name = st.session_state.uploaded_file.name if doc_loaded else "Idle"

st.markdown(f"""
<div class="topbar">
    <span>Workspace</span>
    <span class="status-badge">{doc_name}</span>
</div>
""", unsafe_allow_html=True)


left_col, right_col = st.columns(2)

with left_col:

    st.markdown('<div class="panel-header"><span class="panel-title">Document</span><span class="panel-badge">Viewer</span></div>', unsafe_allow_html=True)

    with st.container(border=True):

        if not doc_loaded:
            st.markdown('<div class="chat-empty">Upload a document</div>', unsafe_allow_html=True)

        else:
            file = st.session_state.uploaded_file
            ext = st.session_state.uploaded_file_ext

            if ext == ".pdf":
                try:
                    from streamlit_pdf_viewer import pdf_viewer
                    pdf_viewer(file.getvalue(), height=600)
                except:
                    st.download_button("Download PDF", file.getvalue(), file.name)

            elif ext == ".txt":
                content = file.getvalue().decode("utf-8", errors="ignore")
                st.text_area("", content, height=600)

            else:
                st.download_button("Download file", file.getvalue(), file.name)


with right_col:

    st.markdown('<div class="panel-header"><span class="panel-title">Chat</span><span class="panel-badge">RAG</span></div>', unsafe_allow_html=True)

    with st.container(border=True):

        if not st.session_state.messages:
            st.markdown('<div class="chat-empty">Ask about your document</div>', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ask something...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            try:
                res = requests.post(
                    "http://127.0.0.1:8000/query",
                    json={"query": prompt}
                )
                answer = res.json()["answer"]
            except Exception as e:
                answer = f"Error: {e}"

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()