import streamlit as st
import requests
import os, json
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(layout="wide")


if 'pdf_ref' not in st.session_state:
    st.session_state.pdf_ref=None 

SUMMARY_DIR = "storage/summary"
def load_summary(retries=5, delay=0.5):
    latest_path = os.path.join(SUMMARY_DIR, "latest.json")
    if not os.path.exists(latest_path):
        return None

    with open(latest_path, "r", encoding="utf-8") as f:
        doc_id = json.load(f)["doc_id"]

    summary_path = os.path.join(SUMMARY_DIR, f"{doc_id}.json")
    if not os.path.exists(summary_path):
        return None

    with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)




st.sidebar.title("Upload files")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF, DOCX, or TXT files",
    type=["pdf", "docx", "txt"],
    key='upload_files',  #creating new key for session_state for the uploaded file variable
    accept_multiple_files=True
)



if uploaded_files:
    if st.sidebar.button("Upload to backend"):
        files = []
    
        
        for file in uploaded_files:
            ext = os.path.splitext(file.name)[1].lower()
            mime_type = "application/pdf"
            if ext == ".docx":
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == ".txt":
                mime_type = "text/plain"
            files.append(
                ("files", (file.name, file.getvalue(), mime_type))
            )

        with st.spinner("Uploading and processing..."):
            response = requests.post(
                "http://127.0.0.1:8000/upload-files",
                files=files
            )

        if response.status_code == 200:
            data=response.json() #get the json part of the reponse returned by the /upload endpoint

            #create a new varibale function by state_session like basically create a new state and use it only after file uplaoad
            st.session_state.summary=data[-1]["summary"]
            st.session_state.uploaded_file = uploaded_files[-1]
            st.session_state.uploaded_file_ext = os.path.splitext(uploaded_files[-1].name)[1].lower()
            if "summary" in st.session_state:
                st.sidebar.subheader("Summary")
                st.sidebar.markdown(st.session_state.summary)
            
        else:
            st.sidebar.error(f"Upload failed: {response.text}")
            st.error(f"Upload failed: {response.text}")


query= "http://127.0.0.1:8000/query"

st.title("Examdoc")
st.subheader("Open the sidebar to upload a document :))")
st.divider()
main_col, right_panel = st.columns([3, 2])

with right_panel:
    st.subheader("Hello! How may I help you")

    if "messages" not in st.session_state:  
        #session state is the session state object that lets you execute your requests 
        #a session is every active run of the streamlit app u see on the broweser evry time u refresher or start you app you get a new session and state is what is happening inside your particular session- what is being done 
        st.session_state.messages = []

# Show chat history
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    prompt = st.chat_input("Ask a question")

    if prompt:
   
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
    )
        with st.chat_message("user"):
            st.markdown(prompt)

        data_to_backend = {
            "query": prompt,
            "k_top": 5
    }

        try:
            response = requests.post(query, json=data_to_backend)

            if response.status_code == 200:
                answer = response.json()["answer"]
            else:
                answer = f"Backend error {response.status_code}\n\n{response.text}"

        except requests.exceptions.RequestException as e:
            answer = f"Could not connect to backend:\n\n{e}"

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        st.rerun()

with main_col:
    st.subheader("Document")

    with st.container(border=True):
        if st.session_state.get("uploaded_file"):
            if st.session_state.get("uploaded_file_ext") == ".pdf":
                binary_data = st.session_state.uploaded_file.getvalue()
                pdf_viewer(input=binary_data, width=550)
            else:
                st.markdown(f"Uploaded file: **{st.session_state.uploaded_file.name}**")
                if st.session_state.uploaded_file_ext == ".txt":
                    st.code(st.session_state.uploaded_file.getvalue().decode("utf-8", errors="ignore"), language="text")
        else:
            st.caption("No document loaded")
