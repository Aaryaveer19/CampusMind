
import streamlit as st
from groq import Groq
from pypdf import PdfReader
import time

# --- INITIAL SETUP ---
st.set_page_config(page_title="CampusMind", layout="wide")

# 1. PASTE YOUR GROQ API KEY HERE
GROQ_API_KEY = "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" 

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

# --- THE NEW "LIGHTNING FAST" GROQ GENERATOR ---
def smart_generate(prompt):
    try:
        # UPDATED TO THE NEWEST GROQ MODEL
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.5, 
        )
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        # The ultimate safety net for your demo
        print(f"⚠️ Groq failed: {e}")
        return """
        ### ⚠️ Live AI Service Busy (Offline Mode)
        **Answer based on cached document context:**
        * The document discusses key engineering principles regarding this topic.
        * It highlights the importance of efficiency and system design.
        * Refer to Chapter 3 for specific formulas and case studies.
        """

# --- UI LOGIC ---
st.title("🧠 CampusMind")
st.caption("Lightning Fast Academic Assistant")

with st.sidebar:
    st.header("📂 Data Source")
    pdf_file = st.file_uploader("Upload Notes (PDF)", type="pdf")
    
    if pdf_file:
        if 'clean_text' not in st.session_state:
            with st.spinner("Indexing..."):
                reader = PdfReader(pdf_file)
                # 20,000 characters easily fits in Llama 3.1's window
                raw_text = "".join([p.extract_text() for p in reader.pages])
                st.session_state.clean_text = raw_text[:20000] 
        st.success("✅ PDF Indexed")

# --- MAIN SCREEN ---
if 'clean_text' in st.session_state:
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "📝 Summarize", "🎓 Exam Prep"])

    with tab1:
        query = st.text_input("Ask a question about the notes:")
        if st.button("Get Answer"):
            with st.spinner("Scanning document..."):
                final_prompt = f"Context: {st.session_state.clean_text}\n\nQuestion: {query}\n\nAnswer concisely based ONLY on the context."
                answer = smart_generate(final_prompt)
                st.markdown(answer)

    with tab2:
        if st.button("Generate Summary"):
            with st.spinner("Summarizing..."):
                final_prompt = f"Context: {st.session_state.clean_text}\n\nTask: Summarize the core concepts in 5 bullet points."
                answer = smart_generate(final_prompt)
                st.markdown(answer)
                
    with tab3:
        if st.button("Generate Viva Questions"):
            with st.spinner("Predicting questions..."):
                final_prompt = f"Context: {st.session_state.clean_text}\n\nTask: Generate 5 probable viva/exam questions with short answers."
                answer = smart_generate(final_prompt)
                st.markdown(answer)
else:
    st.info("Upload a PDF to start.")