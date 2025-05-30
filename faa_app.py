
import streamlit as st
from openai import OpenAI
from io import StringIO, BytesIO
import requests
import os

# Deployment marker
st.caption("🛠 Updated version deployed on May 30")

# Load the FAA Bill
@st.cache_data
def load_document():
    with open("faa_bill.txt", "r", encoding="utf-8") as file:
        return file.read()

base_text = load_document()

# --- App Title ---
st.title("FAA Reauthorization Bill Analysis Tool")
st.markdown("Search the FAA Reauthorization Bill and supporting documents using keyword and AI-powered semantic search.")

# --- Google Drive File Link Input ---
st.markdown("### 🌐 Load File from Google Drive")

drive_url = st.text_input("Paste a shareable Google Drive file link (TXT or PDF)")

def extract_drive_file_id(url):
    if "id=" in url:
        return url.split("id=")[1].split("&")[0]
    elif "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    return None

extra_drive_text = ""

if drive_url:
    try:
        file_id = extract_drive_file_id(drive_url)
        if file_id:
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            response = requests.get(download_url)

            if response.ok:
                if drive_url.endswith(".txt") or "text/plain" in response.headers.get("Content-Type", ""):
                    extra_drive_text = response.text
                elif "pdf" in response.headers.get("Content-Type", ""):
                    from PyPDF2 import PdfReader
                    reader = PdfReader(BytesIO(response.content))
                    extra_drive_text = "\n".join([page.extract_text() or "" for page in reader.pages])
                else:
                    st.warning("Unsupported file type. Use TXT or PDF.")
            else:
                st.error("Failed to download file from Google Drive.")
        else:
            st.warning("Could not extract file ID from the provided URL.")
    except Exception as e:
        st.error(f"Error loading Drive file: {e}")

extra_text = ""  # Placeholder for uploader text later

# Combine all text sources (uploader added at bottom)
document = base_text + "\n\n" + extra_drive_text

# --- Keyword Search ---
st.markdown("---")
st.header("🔍 Keyword Search")

search_query = st.text_input("Enter a keyword", placeholder="e.g., union, NATCA, bargaining unit")

matches = []
if search_query:
    lines = document.split('\n')
    for i, line in enumerate(lines):
        if search_query.lower() in line.lower():
            context = "\n".join(lines[max(0, i-2):i+3])
            matches.append(context)

if matches:
    selected_match = st.selectbox("Select a matching section to preview:", matches)
    st.text_area("Preview", selected_match, height=300)
elif search_query:
    st.info("No matches found.")

# --- GPT Semantic Search ---
st.markdown("---")
st.header("🤖 AI-Powered Semantic Search")

user_question = st.text_input("Ask a question about the bill", placeholder="e.g. Where does the bill involve NATCA?")

if user_question:
    st.write("Thinking...")

    paragraphs = document.split("\n\n")
    relevant_chunks = [p for p in paragraphs if any(word in p.lower() for word in user_question.lower().split())]
    top_context = "\n\n".join(relevant_chunks[:5])[:3000]

    prompt = f"""You are a legal assistant analyzing FAA legislation.
Given this excerpt from legislative and supporting documents:
\"\"\"
{top_context}
\"\"\"

Answer this question based only on the text above:
\"{user_question}\"
"""

    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        answer = response.choices[0].message.content
        st.success("AI Response:")
        st.write(answer)
    except Exception as e:
        st.error(f"Error from OpenAI: {e}")

# --- File Upload Section (BOTTOM) ---
st.markdown("---")
st.header("📁 Upload a document (TXT or PDF) to include in your session")

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])

if uploaded_file:
    try:
        if uploaded_file.type == "application/pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            extra_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        else:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            extra_text = stringio.read()
        document += "\n\n" + extra_text
        st.success("Document successfully added to your session.")
    except Exception as e:
        st.error(f"Could not process uploaded file: {e}")
