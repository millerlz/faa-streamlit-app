
import streamlit as st

# Load the FAA Bill
@st.cache_data
def load_document():
    with open("faa_bill.txt", "r", encoding="utf-8") as file:
        return file.read()

document = load_document()

# Streamlit UI
st.title("FAA Reauthorization Bill Search Tool")

# Keyword Search
search_query = st.text_input("🔍 Keyword Search", placeholder="e.g., union, NATCA, bargaining unit")

if search_query:
    st.write("### Matching Sections")
    matches = []
    lines = document.split('\n')
    for i, line in enumerate(lines):
        if search_query.lower() in line.lower():
            context = "\n".join(lines[max(0, i-2):i+3])
            matches.append(context)
if matches:
    selected_match = st.selectbox("Select a matching section to preview:", matches)
    st.text_area("Preview", selected_match, height=300)
else:
    st.info("No matches found.")

    else:
        st.info("No matches found.")
import openai
import os

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.markdown("---")
st.header("🤖 AI-Powered Semantic Search")

user_question = st.text_input("Ask a question about the bill", placeholder="e.g. Where does the bill involve NATCA?")

if user_question:
    st.write("Thinking...")
    # Chunk the document into paragraphs
    paragraphs = document.split("\\n\\n")
    relevant_chunks = [p for p in paragraphs if any(word in p.lower() for word in user_question.lower().split())]

    top_context = "\\n\\n".join(relevant_chunks[:5])[:3000]  # keep GPT input short
    prompt = f"""You are a legal assistant analyzing FAA legislation.
Given this excerpt from a reauthorization bill:
\"\"\"
{top_context}
\"\"\"

Answer this question based only on the text above:
\"{user_question}\"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        answer = response["choices"][0]["message"]["content"]
        st.success("AI Response:")
        st.write(answer)
    except Exception as e:
        st.error(f"Error from OpenAI: {e}")
