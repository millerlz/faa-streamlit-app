import streamlit as st
from openai import OpenAI
from io import StringIO
import os

# Load the FAA Bill
@st.cache_data
def load_document():
    with open("faa_bill.txt", "r", encoding="utf-8") as file:
        return file.read()

# Load base bill
base_text = load_document()

# --- File Upload ---
uploaded_file = st.file_uploader("📁 Upload a document to include in the analysis", type=["txt", "pdf"])

extra_text = ""
if uploaded_file:
    try:
        if uploaded_file.type == "application/pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            extra_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        else:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            extra_text = stringio.read()
    except Exception as e:
        st.error(f"Could not process uploaded file: {e}")

# Combine original bill with uploaded content
document = base_text + "\n\n" + extra_text

# --- Streamlit App Title ---
st.title("FAA Reauthorization Bill Analysis Tool")
st.markdown("Search the FAA Reauthorization Bill and any uploaded documents using keyword and GPT-powered semantic search.")

# --- Keyword Search ---
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

    # Chunk the document into paragraphs
    paragraphs = document.split("\n\n")
    relevant_chunks = [p for p in paragraphs if any(word in p.lower() for word in user_question.lower().split())]

    top_context = "\n\n".join(relevant_chunks[:5])[:3000]  # limit token count

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
