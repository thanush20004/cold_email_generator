
import os
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from urllib.parse import quote

# Change to the project directory to ensure relative paths work
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# Custom CSS for modern dark-themed UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark theme background */
    .stApp {
        background: linear-gradient(135deg, #0a0f1c 0%, #1a1f3c 50%, #0d1421 100%);
        min-height: 100vh;
    }
    
    /* Glassmorphism card */
    .glass-card {
        background: rgba(30, 41, 70, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.05);
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #bfdbfe;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #60a5fa;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input field styling */
    .stTextInput > div > div {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #60a5fa !important;
        box-shadow: 0 0 20px rgba(96, 165, 250, 0.2) !important;
    }
    
    .stTextInput input {
        color: white !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(148, 163, 184, 0.5) !important;
    }
    
    /* Helper text */
    .helper-text {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    /* Label styling */
    label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
        color: #22c55e !important;
        border-radius: 0.5rem !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #ef4444 !important;
        border-radius: 0.5rem !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        color: #60a5fa !important;
        border-radius: 0.5rem !important;
    }
    
    /* Code block styling */
    .stCode {
        background: rgba(15, 23, 42, 0.8) !important;
        border-radius: 0.75rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 2rem 0 !important;
    }
    
    /* Gmail button styling */
    .gmail-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #ea4335 0%, #d93025 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 9999px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .gmail-button:hover {
        background: linear-gradient(135deg, #f87171 0%, #ea4335 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(234, 67, 53, 0.3);
    }
    
    /* Spinner customization */
    .stSpinner {
        color: #60a5fa !important;
    }
    
    /* Job card styling */
    .job-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .job-title {
        color: #60a5fa;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }
    
    .job-meta {
        color: #94a3b8;
        margin-top: 0.5rem;
    }
    
    /* Footer */
    .footer-text {
        color: #64748b;
        text-align: center;
        font-size: 0.875rem;
        margin-top: 2rem;
    }
    
    /* Column layout fix */
    .row-widget {
        margin-bottom: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)


def create_streamlit_app(llm, portfolio, clean_text):
    # Header with envelope icon
    st.markdown('''
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="display: inline-block; margin-bottom: 1rem; animation: float 3s ease-in-out infinite;">
                <svg style="width: 4rem; height: 4rem; filter: drop-shadow(0 0 10px rgba(96, 165, 250, 0.5));" fill="none" stroke="#60a5fa" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
            </div>
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #bfdbfe; margin-bottom: 0.5rem;">Job Application Email Generator</h1>
            <p style="color: #94a3b8; font-size: 1.1rem;">Generate personalized cold emails for your job applications</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Glassmorphism card container
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Your details section
    st.markdown('''
        <h2 style="font-size: 1.25rem; font-weight: 600; color: #60a5fa; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            Your Information
        </h2>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        your_name = st.text_input("Your Name:", value="Your Name", help="Your full name")
        your_email = st.text_input("Your Email:", value="your.email@example.com", help="Your contact email")
    with col2:
        recipient_name = st.text_input("Recipient Name (Optional):", value="", help="Leave blank for 'Dear Hiring Manager'")
        # Empty placeholder for layout
        st.text_input("Target Company:", value="", disabled=True, help="Company from the job posting will be used")
    
    # Helper text below inputs
    st.markdown('''
        <p class="helper-text">Your full name</p>
        <p class="helper-text">Your contact email</p>
        <p class="helper-text">Leave blank for generic greeting</p>
        <p class="helper-text">Auto-filled from job posting</p>
    ''', unsafe_allow_html=True)
    
    st.markdown('<hr>', unsafe_allow_html=True)
    
    # Job details section
    st.markdown('''
        <h2 style="font-size: 1.25rem; font-weight: 600; color: #60a5fa; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            Job Details
        </h2>
    ''', unsafe_allow_html=True)
    
    url_input = st.text_input("Job Posting URL:", value="https://jobs.nike.com/job/R-33460", help="Paste a direct job posting URL")
    st.markdown('<p class="helper-text">Paste a direct job posting URL (e.g., from LinkedIn, Indeed, or company career pages)</p>', unsafe_allow_html=True)
    
    # Submit button
    col_btn, col_spacer = st.columns([1, 3])
    with col_btn:
        submit_button = st.button("✨ Generate Email", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close glass-card
    
    st.markdown('<p class="footer-text">Made with ❤️ using Streamlit & LangChain</p>', unsafe_allow_html=True)
    
    if submit_button:
        try:
            with st.spinner('🔍 Scraping job posting...'):
                loader = WebBaseLoader([url_input])
                data = loader.load().pop().page_content
                
            with st.spinner('🧹 Cleaning text...'):
                cleaned_data = clean_text(data)
                
            if not cleaned_data.strip():
                st.error("❌ Could not extract text from the URL. The page might be blocking scrapers or requiring JavaScript.")
                st.info("💡 Try using a different job posting URL from companies like Nike, Microsoft, or Amazon.")
            else:
                with st.spinner('📝 Generating email...'):
                    portfolio.load_portfolio()
                    jobs = llm.extract_jobs(cleaned_data)
                
                if not jobs:
                    st.error("❌ Could not extract job details from the page.")
                    st.info("💡 Make sure you're using a direct job posting URL, not a search results page.")
                else:
                    st.success("✅ Email generated successfully!")
                    st.markdown("---")
                    
                    for job in jobs:
                        # Display job info - dark theme styling
                        st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                            <h4 style="margin: 0; color: #60a5fa;">📋 {job.get('role', 'Unknown Role')}</h4>
                            <p style="margin: 5px 0 0 0; color: #94a3b8;">💼 {job.get('experience', 'Experience not specified')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        skills = job.get('skills', [])
                        if skills:
                            st.markdown(f"""
                            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); padding: 10px 15px; border-radius: 8px; margin-bottom: 15px;">
                                <span style="color: #60a5fa; font-weight: 600;">🛠️ Skills:</span>
                                <span style="color: #cbd5e1; margin-left: 8px;">{", ".join(skills[:5])}{"..." if len(skills) > 5 else ""}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        links = portfolio.query_links(skills)
                        email = llm.write_mail(
                            job, 
                            links,
                            your_name=your_name,
                            your_email=your_email,
                            recipient_name=recipient_name
                        )
                        
                        st.markdown("### 📧 Generated Email")
                        
                        # Display email in a styled container
                        st.markdown(f'''
                        <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #3b82f6; border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                            <pre style="white-space: pre-wrap; font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #e2e8f0; margin: 0;">{email}</pre>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Add Gmail button
                        subject = quote(f"Job Application - {job.get('role', 'Position')}")
                        body = quote(email)
                        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&tf=1&su={subject}&body={body}"
                        
                        st.markdown(f'''
                            <center>
                                <a href="{gmail_url}" target="_blank" class="gmail-button">
                                    📧 Send to Gmail
                                </a>
                            </center>
                        ''', unsafe_allow_html=True)
                        st.markdown("---")
                        
        except Exception as e:
            st.error(f"❌ An Error Occurred: {str(e)}")
            st.info("💡 Try using a different job posting URL. Some websites block automated scrapers.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(
        layout="wide", 
        page_title="Job Application Email Generator", 
        page_icon="📧",
        initial_sidebar_state="expanded"
    )
    create_streamlit_app(chain, portfolio, clean_text)
