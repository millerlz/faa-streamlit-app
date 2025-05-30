
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
