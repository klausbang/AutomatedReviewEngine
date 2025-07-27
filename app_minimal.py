"""
Minimal Streamlit App - Emergency Fallback
Simple document upload interface for testing
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Automated Review Engine v1.0.0",
    page_icon="📋",
    layout="wide"
)

def main():
    """Main application"""
    st.title("📋 Automated Review Engine v1.0.0")
    st.sidebar.title("Navigation")
    
    # Initialize session state
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Navigation
    page = st.sidebar.radio(
        "Select Page:",
        ["🏠 Home", "📤 Upload Documents", "📋 Review Queue", "⚙️ Settings"]
    )
    
    if page == "🏠 Home":
        render_home()
    elif page == "📤 Upload Documents":
        render_upload()
    elif page == "📋 Review Queue":
        render_queue()
    elif page == "⚙️ Settings":
        render_settings()

def render_home():
    """Home page"""
    st.markdown("## 🏠 Welcome to Automated Review Engine")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", "✅ Ready")
    
    with col2:
        st.metric("Documents Uploaded", len(st.session_state.uploaded_files))
    
    with col3:
        st.metric("Version", "1.0.0")
    
    st.markdown("### Quick Start")
    st.markdown("1. **Upload Documents** - Go to Upload Documents page")
    st.markdown("2. **Review Queue** - Check uploaded files")
    st.markdown("3. **Execute Testing** - Use the UAT plan for validation")

def render_upload():
    """Upload page"""
    st.markdown("## 📤 Document Upload")
    st.markdown("### Upload Documents for Review")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a document to review",
        type=['pdf', 'docx', 'doc'],
        help="Upload PDF or Word documents for automated review"
    )
    
    if uploaded_file is not None:
        # File information
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**File Name:** {uploaded_file.name}")
            st.info(f"**File Size:** {uploaded_file.size:,} bytes")
            st.info(f"**File Type:** {uploaded_file.type}")
        
        with col2:
            st.success("✅ File uploaded successfully")
            
            if st.button("Add to Review Queue", key="add_to_queue"):
                st.session_state.uploaded_files.append({
                    'name': uploaded_file.name,
                    'size': uploaded_file.size,
                    'type': uploaded_file.type,
                    'upload_time': datetime.now()
                })
                st.success(f"Added {uploaded_file.name} to review queue")
                st.rerun()

def render_queue():
    """Review queue"""
    st.markdown("## 📋 Review Queue")
    
    if st.session_state.uploaded_files:
        st.markdown(f"### {len(st.session_state.uploaded_files)} Document(s) in Queue")
        
        for i, file_info in enumerate(st.session_state.uploaded_files):
            with st.expander(f"📄 {file_info['name']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Size:** {file_info['size']:,} bytes")
                    st.write(f"**Type:** {file_info['type']}")
                    st.write(f"**Uploaded:** {file_info['upload_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    if st.button(f"🔍 Process {file_info['name']}", key=f"process_{i}"):
                        st.info("🚧 Review processing will be implemented in Phase 4.2")
                    
                    if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.uploaded_files.pop(i)
                        st.rerun()
    else:
        st.info("📝 No documents in queue. Upload documents to get started.")

def render_settings():
    """Settings page"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### System Information")
    st.info("**Version:** 1.0.0 (Emergency Fallback Mode)")
    st.info("**Status:** Simplified interface active")
    st.info("**Mode:** User Acceptance Testing")
    
    st.markdown("### Performance")
    st.success("✅ System running smoothly")
    st.info("📊 Performance monitoring available in full version")

if __name__ == "__main__":
    main()
