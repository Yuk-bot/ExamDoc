import streamlit as st
import requests
import os, json

SUMMARY_DIR = "storage/summary"
def load_summary():
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





uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Upload to backend"):
        files = []
    
        
        for file in uploaded_files:
            files.append(
                ("files", (file.name, file.getvalue(), "application/pdf"))
            )

        with st.spinner("Uploading and processing..."):
            response = requests.post(
                "http://127.0.0.1:8000/upload-files",
                files=files
            )

        if response.status_code == 200:
            st.success("Upload successful")
            st.badge("Success")
            st.sidebar.title("Upload files")
            st.sidebar.subheader("The summary for the pdf is as follows")
            summary=load_summary()
            if not summary:
                st.sidebar.markdown("Summary not avaliable")
            st.sidebar.write(summary)
            st.markdown("Open the sidebar to get summary")
        else:
            st.error(f"Upload failed: {response.text}")

st.divider()
query= "http://127.0.0.1:8000/query"

st.title("Examdoc")
st.divider()

if "messages" not in st.session_state:  
    #session state is the session state object that lets you execute your requests 
    #a session is every active run of the streamlit app u see on the broweser evry time u refresher or start you app you get a new session and state is what is happening inside your particular session- what is being done 
    st.session_state.messages = []

# Show chat history
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
