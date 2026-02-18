import streamlit as st
from groq import Groq
from pypdf import PdfReader
import os
from dotenv import load_dotenv  # 👈 1. Import the reader

# --- INITIAL SETUP ---
st.set_page_config(page_title="CampusMind AI", page_icon="🧠", layout="wide")

load_dotenv()  # 👈 2. Tell Python to read the .env file!

# Now os.getenv will actually find your key!
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

# ... (The rest of your code stays exactly the same!) ...

# --- CUSTOM UI CSS (The "Startup" Look) ---
st.markdown("""
    <style>
    /* Main Background & Text */
    .stApp { background-color: #0B0F19; color: #E5E7EB; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 700 !important; }
    
    /* Sleek Input Fields */
    .stTextInput>div>div>input { 
        background-color: #1F2937; 
        color: white; 
        border-radius: 8px; 
        border: 1px solid #374151; 
        padding: 10px;
    }
    
    /* Gradient Buttons with Hover Effects */
    .stButton>button { 
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white; 
        border-radius: 8px; 
        border: none;
        height: 2.8em;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4); 
        color: white;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1F2937; }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { color: #A78BFA !important; border-bottom: 2px solid #A78BFA !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INIT SESSION STATES (Prevents answers from disappearing) ---
if 'chat_answer' not in st.session_state: st.session_state.chat_answer = ""
if 'summary_answer' not in st.session_state: st.session_state.summary_answer = ""
if 'exam_answer' not in st.session_state: st.session_state.exam_answer = ""

# --- API SETUP ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

# --- GROQ GENERATOR ---
def smart_generate(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            temperature=0.5, 
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Groq failed: {e}")
        return "⚠️ **Offline Mode Active:** The live AI is currently overwhelmed by hackathon traffic. Please refer to the cached context."

# --- SIDEBAR LOGIC ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4185/4185848.png", width=60) # Small brain icon
    st.title("CampusMind Data")
    st.markdown("Upload your institutional resources to train the digital brain.")
    
    pdf_file = st.file_uploader("Drop PDF here", type="pdf")
    
    if pdf_file:
        if 'clean_text' not in st.session_state:
            with st.spinner("🧠 Absorbing knowledge..."):
                reader = PdfReader(pdf_file)
                raw_text = "".join([p.extract_text() for p in reader.pages])
                st.session_state.clean_text = raw_text[:20000] 
        st.success("✅ Knowledge Base Active")

# --- MAIN SCREEN LOGIC ---
st.title("🧠 CampusMind")
st.markdown("#### *Your AI-Powered Academic Copilot*")
st.divider()

if 'clean_text' in st.session_state:
    # App is active
    tab1, tab2, tab3 = st.tabs(["🔍 Semantic Search", "📝 Auto-Notes", "🎓 Exam Simulator"])

    # TAB 1
    with tab1:
        st.markdown("### Ask your Study Material")
        query = st.text_input("Enter your question:", placeholder="e.g., What are the main causes of...")
        if st.button("Search Knowledge Base"):
            with st.spinner("Scanning documents..."):
                prompt = f"Context: {st.session_state.clean_text}\n\nQuestion: {query}\n\nAnswer concisely based ONLY on the context."
                st.session_state.chat_answer = smart_generate(prompt)
        
        if st.session_state.chat_answer:
            st.info("💡 **Answer:**")
            st.markdown(st.session_state.chat_answer)

    # TAB 2
    with tab2:
        st.markdown("### Instant Revision Notes")
        if st.button("✨ Generate Smart Summary"):
            with st.spinner("Synthesizing notes..."):
                prompt = f"Context: {st.session_state.clean_text}\n\nTask: Summarize the core concepts in 5 bullet points."
                st.session_state.summary_answer = smart_generate(prompt)
        
        if st.session_state.summary_answer:
            st.success("📝 **Study Summary:**")
            st.markdown(st.session_state.summary_answer)
                
# TAB 3
    with tab3:
        st.markdown("### Predict Viva & Exam Questions")
        
        # 1. Add the interactive slider
        num_questions = st.slider("How many questions do you want to generate?", min_value=1, max_value=15, value=5)
        
        # 2. Add the button
        if st.button("🎯 Generate Practice Test"):
            with st.spinner(f"Analyzing past patterns to generate {num_questions} questions..."):
                # 3. Inject the slider value directly into the prompt!
                prompt = f"Context: {st.session_state.clean_text}\n\nTask: Generate {num_questions} probable viva/exam questions with short answers."
                st.session_state.exam_answer = smart_generate(prompt)
        
        # 4. Display the results
        if st.session_state.exam_answer:
            st.warning(f"🎓 **Your {num_questions} Practice Questions:**")
            st.markdown(st.session_state.exam_answer)

else:
    # The "Empty State" - What users see before uploading
    st.markdown("""
    ### Welcome to the Future of Learning 🚀
    Engineering colleges generate massive amounts of data, but finding the right answer at 2 AM before an exam is impossible. 
    **CampusMind fixes this.**
    
    👈 **Upload a Syllabus, PPT, or Notes PDF in the sidebar to begin.**
    
    ### What it can do:
    * **🔍 Semantic Search:** Ask natural questions, get exact answers.
    * **📝 Auto-Notes:** Turn 50 pages of reading into a 5-bullet summary.
    * **🎓 Exam Simulator:** Predict what the professor will ask tomorrow.
    """)