import os
import streamlit as st
from rag import get_user_docs, process_pdf

import re
st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

if 'indexed' not in st.session_state:
    st.session_state.indexed = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Chat"

if 'email_verified' not in st.session_state:
    st.session_state.email_verified = False

if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Email validation function
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# EMAIL VERIFICATION PAGE
if not st.session_state.email_verified:
    # Hide sidebar
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the email form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Header
        st.markdown("<h1 style='text-align: center;'>🤖 RAG Chat Assistant</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Your Personal Document Q&A System</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Email input card
        with st.container():
            st.markdown("### Welcome! 👋")
            st.markdown("Please enter your email to continue")
            
            email_input = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                key="email_input",
                label_visibility="collapsed"
            )
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit_button = st.button("Continue →", type="primary", use_container_width=True)
            
            if submit_button:
                if not email_input:
                    st.error("⚠️ Please enter your email address")
                elif not is_valid_email(email_input):
                    st.error("⚠️ Please enter a valid email address")
                else:
                    st.session_state.email_verified = True
                    st.session_state.user_email = email_input
                    st.success("✅ Email verified! Redirecting...")
                    st.rerun()
            

    st.stop()

# Sidebar Navigation
with st.sidebar:
    st.title("AI Chat Assistant")
    
    # Show user email
    st.caption(f"👤 {st.session_state.user_email}")
    
    st.divider()
    
    # Page selection
    page = st.radio(
        "Navigate to:",
        ["💬 Chat", "📚 Data Management"],
        key="navigation"
    )
    
    st.session_state.current_page = page
    
    st.divider()
    
    # System Status
    st.subheader("System Status")
    if st.session_state.indexed:
        st.success("🟢 Ready")
        st.info(f"📄 {len(st.session_state.uploaded_files)} documents indexed")
    else:
        st.warning("⚠️ No documents indexed")
    
    # Quick stats
    if st.session_state.messages:
        st.metric("Chat Messages", len(st.session_state.messages))
    
    # Logout button
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.email_verified = False
        st.session_state.user_email = ""
        st.session_state.messages = []
        st.rerun()

# CHAT PAGE
if st.session_state.current_page == "💬 Chat":
    st.title("💬 Chat Assistant")
    st.caption("Ask questions about your uploaded documents")
    
    # Check if system is ready
    if not st.session_state.indexed:
        st.warning("⚠️ Please go to 'Data Management' to upload and index documents first!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question...", disabled=not st.session_state.indexed):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO: Add RAG logic here
                import time
                time.sleep(1)  # Simulate processing
                
                # Placeholder response
                response = f"This is a placeholder response to: '{prompt}'. RAG logic will be implemented here."
                st.markdown(response)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear chat button at bottom
    if st.session_state.messages:
        st.divider()
        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

# DATA MANAGEMENT PAGE
elif st.session_state.current_page == "📚 Data Management":
    st.title("📚 Data Management")
    st.caption("Upload and index your PDF documents")
    
    st.subheader("Upload Documents")
    # if st.session_state.user_email:
        # existing_files = get_user_docs(st.session_state.user_email).list_documents()
        # if existing_files:
        #     st.info(f"📂 You have already indexed {len(existing_files)} documents. Upload more to add to your collection.")
    uploaded_files = st.file_uploader(
        "Choose PDF files (Maximum 10 files)",
        type=['pdf'],
        accept_multiple_files=True,
        key="pdf_uploader",
        help="Upload PDF documents that you want to query"
    )
    
    # Check if max files exceeded
    if uploaded_files and len(uploaded_files) > 10:
        st.error("⚠️ Maximum 10 files allowed!")
        uploaded_files = uploaded_files[:10]
    
    # Update session state
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")

        
        # Index button
        col1, col2, col3 = st.columns([2, 2, 2])
        with col2:
            if st.button("🔄 Index Documents", type="primary", use_container_width=True):
                with st.spinner("Indexing documents... This may take a moment."):
                    # TODO: Add indexing logic here
                    save_path = f"./uploads/{st.session_state.user_email}/"
                    os.makedirs(save_path, exist_ok=True)
                    pdf_path = os.path.join(save_path, uploaded_files[0].name)
                    with open(pdf_path, "wb") as f:
                        f.write( uploaded_files[0].getbuffer())
                    vectordb = process_pdf(pdf_path, st.session_state.user_email)
                    import time
                    time.sleep(2)  # Simulate processing
                    st.session_state.indexed = True
                    st.success("✅ Documents indexed successfully!")
                    st.balloons()
                    time.sleep(1)
    else:
        st.info("👆 Upload PDF files to get started")
    
    # Indexing status
    st.divider()
    st.subheader("Indexing Status")
    
    if st.session_state.indexed:
        st.success("✅ Documents are indexed and ready for querying")
      
    else:
        st.info("📋 Upload documents and click 'Index Documents' to begin")