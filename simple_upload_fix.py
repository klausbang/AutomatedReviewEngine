def _render_legacy_upload_interface(self):
    """Legacy upload interface fallback"""
    st.info("🔧 Using simplified upload interface")
    
    try:
        # Upload interface
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
                # Simple file acceptance without complex validation
                st.success("✅ File uploaded successfully")
                
                if st.button("Add to Review Queue", key="add_to_queue"):
                    # Initialize uploaded_files if it doesn't exist
                    if 'uploaded_files' not in st.session_state:
                        st.session_state.uploaded_files = []
                    
                    st.session_state.uploaded_files.append({
                        'name': uploaded_file.name,
                        'size': uploaded_file.size,
                        'type': uploaded_file.type,
                        'upload_time': datetime.now()
                    })
                    st.success(f"Added {uploaded_file.name} to review queue")
                    
    except Exception as e:
        st.error(f"Upload error: {e}")
        st.info("Please try refreshing the page or contact support if the issue persists.")
