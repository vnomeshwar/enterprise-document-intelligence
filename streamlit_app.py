import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide"
)


st.title("📄 Enterprise Document Intelligence")
st.write("Upload a document and ask questions about its content.")


# -------------------------
# Document Upload
# -------------------------

st.header("Upload Document")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)


if uploaded_file is not None:

    if st.button("Process Document"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }

        response = requests.post(
            f"{API_URL}/upload",
            files=files
        )

        if response.status_code == 200:

            result = response.json()

            st.success(result["message"])

            st.write(
                f"**Pages:** {result['pages_extracted']}"
            )

            st.write(
                f"**Chunks:** {result['chunks_created']}"
            )

            st.write(
                f"**Embedding dimension:** "
                f"{result['embedding_dimension']}"
            )

        else:
            st.error("Document processing failed.")


# -------------------------
# Question Answering
# -------------------------

st.header("Ask a Question")

question = st.text_input(
    "Enter your question"
)


if st.button("Ask"):

    if not question:
        st.warning("Please enter a question.")

    else:

        response = requests.post(
            f"{API_URL}/ask",
            json={
                "question": question
            }
        )

        if response.status_code == 200:

            result = response.json()

            st.subheader("Answer")

            st.write(result["answer"])


            st.subheader("Sources")

            for source in result["sources"]:

                st.write(
                    f"📄 **{source['document']}** — "
                    f"Page {source['page']} "
                    f"(similarity: {source['similarity']})"
                )

        else:
            st.error("Failed to get an answer.")