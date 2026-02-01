import streamlit as st
import requests

s=st.sidebar.title("Upload files")
st.sidebar.markdown("The summary for the pdf is as follows")

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
        else:
            st.error(f"Upload failed: {response.text}")

st.divider()
query= "http://127.0.0.1:8000/query"

st.title("Examdoc")
st.divider()
st.markdown("Open the sidebar to get the pdf summary")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a question")

if prompt:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "query": prompt,  # MUST match FastAPI model
        "k_top": 5
    }

    try:
        response = requests.post(query, json=payload)

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
