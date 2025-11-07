"""
🌾 AI Crop Doctor - Farmer-Friendly Agricultural Assistant
Beautiful, clean design for Indian farmers
"""

import streamlit as st
from datetime import datetime
from PIL import Image
import io
import time
from config import *
from utils import *

# Page Configuration
st.set_page_config(
    page_title="🌾 AI Crop Doctor - Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit defaults
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    section[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Load Custom CSS
with open('styles.css', 'r', encoding='utf-8') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize Session State
def init_session():
    defaults = {
        'page': 'home',
        'language': 'en',
        'voice_mode': False,
        'analysis_complete': False,
        'report': None,
        'voice_text': None,
        'disease_info': None,
        'audio_report_path': None,
        'detected_language': 'en',
        'selected_district': 'Select District',
        'current_step': 1,
        'report_language': 'en',
        'final_report_language': 'en'
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# Check API Status
api_status = check_api_configuration()

# ============================================
# NAVIGATION BAR
# ============================================
st.markdown("""
<nav class="top-navbar">
    <div class="nav-container">
        <div class="nav-brand">
            <span class="brand-icon">🌾</span>
            <span class="brand-name">AI Crop Doctor</span>
        </div>
    </div>
</nav>
""", unsafe_allow_html=True)

# Navigation Buttons
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns([1, 1, 1, 1, 1, 1])

with nav_col1:
    if st.button("🏠 Home", key="nav_home", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()

with nav_col2:
    if st.button("🌿 Diagnose", key="nav_diagnose", use_container_width=True):
        st.session_state.page = 'diagnose'
        st.rerun()

with nav_col3:
    if st.button("📊 Reports", key="nav_reports", use_container_width=True):
        st.session_state.page = 'reports'
        st.rerun()

with nav_col4:
    if st.button("❓ Help", key="nav_help", use_container_width=True):
        st.session_state.page = 'help'
        st.rerun()

with nav_col5:
    if st.button("ℹ️ About Us", key="nav_about", use_container_width=True):
        st.session_state.page = 'about'
        st.rerun()

with nav_col6:
    if st.button("🌐 ਪੰਜਾਬੀ", key="nav_language", use_container_width=True):
        st.session_state.language = 'pa' if st.session_state.language == 'en' else 'en'

# API Configuration Check
if not api_status['all_configured']:
    st.markdown(f"""
    <div class="alert-box alert-warning">
        <div class="alert-icon">⚠️</div>
        <div class="alert-content">
            <h3>Configuration Needed</h3>
            <p>Please add these API keys to your .env file:</p>
            <ul>
                {''.join(f'<li>{key}</li>' for key in api_status['missing'])}
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Main Content Wrapper
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# ============================================
# HOME PAGE
# ============================================
if st.session_state.page == 'home':
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">Detect Crop Diseases Instantly</h1>
            <h2 class="hero-subtitle">With Your Voice or a Photo!</h2>
            <p class="hero-description">
                Empowering farmers with AI for healthy harvests 🌾
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    st.markdown('<div class="action-section">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="action-card card-voice">
            <div class="action-icon">🗣️</div>
            <h3 class="action-title">Voice Diagnosis</h3>
            <p class="action-text">Speak in your language to describe the problem</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Voice Diagnosis", key="home_voice", use_container_width=True, type="primary"):
            st.session_state.page = 'diagnose'
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="action-card card-image">
            <div class="action-icon">📷</div>
            <h3 class="action-title">Upload Image</h3>
            <p class="action-text">Take a photo of your plant's affected area</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upload Plant Image", key="home_image", use_container_width=True, type="primary"):
            st.session_state.page = 'diagnose'
            st.session_state.current_step = 2
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="action-card card-location">
            <div class="action-icon">📍</div>
            <h3 class="action-title">Location</h3>
            <p class="action-text">Get weather-based pest alerts for your area</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Share My Location", key="home_location", use_container_width=True, type="primary"):
            st.session_state.page = 'diagnose'
            st.session_state.current_step = 3
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Info Section
    st.markdown("""
    <div class="info-banner">
        <p class="info-text">
            💡 <strong>How it works:</strong> Speak or upload to get instant disease report and treatment plan
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("""
    <div class="features-section">
        <h2 class="section-title">Why Farmers Trust AI Crop Doctor</h2>
    </div>
    """, unsafe_allow_html=True)
    
    feat1, feat2, feat3, feat4 = st.columns(4)
    
    with feat1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🎤</div>
            <h4>Voice Support</h4>
            <p>Speak in Hindi, Punjabi, or English</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🤖</div>
            <h4>AI Powered</h4>
            <p>Advanced disease detection technology</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📱</div>
            <h4>Mobile Friendly</h4>
            <p>Works on any smartphone</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat4:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🆓</div>
            <h4>100% Free</h4>
            <p>No charges, no hidden fees</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# DIAGNOSE PAGE
# ============================================
elif st.session_state.page == 'diagnose':
    
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">🌿 Crop Disease Diagnosis</h1>
        <p class="page-subtitle">Follow the simple 4-step process</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress Steps
    st.markdown(f"""
    <div class="progress-steps">
        <div class="step {'active' if st.session_state.current_step >= 1 else ''}">
            <div class="step-circle">1</div>
            <div class="step-label">Your Problem</div>
        </div>
        <div class="step-line"></div>
        <div class="step {'active' if st.session_state.current_step >= 2 else ''}">
            <div class="step-circle">2</div>
            <div class="step-label">Upload Image</div>
        </div>
        <div class="step-line"></div>
        <div class="step {'active' if st.session_state.current_step >= 3 else ''}">
            <div class="step-circle">3</div>
            <div class="step-circle">3</div>
            <div class="step-label">Location</div>
        </div>
        <div class="step-line"></div>
        <div class="step {'active' if st.session_state.current_step >= 4 else ''}">
            <div class="step-circle">4</div>
            <div class="step-label">Language</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 1: Voice/Text Input
    st.markdown("""
    <div class="input-card">
        <div class="card-header">
            <div class="card-icon">🗣️</div>
            <h3 class="card-title">Step 1: Tell Us Your Crop Problem</h3>
        </div>
        <p class="card-description">
            Speak in Punjabi or Hindi. Example: "My wheat leaves are turning yellow"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    audio_file = st.file_uploader(
        "📤 Upload Audio File",
        type=['wav', 'mp3', 'm4a', 'ogg', 'webm', 'aac', 'flac'],
        help="Record and upload your voice describing the problem",
        key="audio_input"
    )
    
    if audio_file:
        st.markdown('<div class="upload-preview">', unsafe_allow_html=True)
        st.audio(audio_file, format='audio/wav')
        st.markdown("""
        <div class="success-badge">
            <span class="badge-icon">✓</span>
            <span class="badge-text">Audio uploaded successfully!</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.current_step < 2:
            st.session_state.current_step = 2
    
    # Step 2: Image Upload
    st.markdown("""
    <div class="input-card">
        <div class="card-header">
            <div class="card-icon">📷</div>
            <h3 class="card-title">Step 2: Upload or Capture Plant Photo</h3>
        </div>
        <p class="card-description">
            Click or drag your leaf image here. Make sure the affected area is clearly visible.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    image_file = st.file_uploader(
        "📤 Upload Plant Image",
        type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
        help="Upload a clear photo of the affected plant",
        key="image_input"
    )
    
    if image_file:
        st.markdown('<div class="upload-preview">', unsafe_allow_html=True)
        image = Image.open(image_file)
        st.image(image, caption="Your Plant Image", use_column_width=True)
        st.markdown("""
        <div class="success-badge">
            <span class="badge-icon">✓</span>
            <span class="badge-text">Image uploaded successfully!</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.current_step < 3:
            st.session_state.current_step = 3
    
    # Step 3: Location
    st.markdown("""
    <div class="input-card">
        <div class="card-header">
            <div class="card-icon">📍</div>
            <h3 class="card-title">Step 3: Confirm Your Farm Location</h3>
        </div>
        <p class="card-description">
            Used to check weather and pest risk in your area
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    district = st.selectbox(
        "🗺️ Select Your District",
        options=PUNJAB_DISTRICTS,
        index=0,
        key="district_input"
    )
    st.session_state.selected_district = district
    
    if district != "Select District":
        st.markdown(f"""
        <div class="location-badge">
            <span class="location-icon">📍</span>
            <span class="location-text">{district}, Punjab, India</span>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.current_step < 4:
            st.session_state.current_step = 4
    
    # Step 4: Language Selection for Report
    st.markdown("""
    <div class="input-card">
        <div class="card-header">
            <div class="card-icon">🌐</div>
            <h3 class="card-title">Step 4: Select Report Language</h3>
        </div>
        <p class="card-description">
            Choose the language for your diagnosis report and audio
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Language options with clear mapping
    language_display = {
        'English': 'en',
        'हिंदी (Hindi)': 'hi',
        'ਪੰਜਾਬੀ (Punjabi)': 'pa',
        'اردو (Urdu)': 'ur'
    }
    
    selected_language_display = st.selectbox(
        "🗣️ Report Language",
        options=list(language_display.keys()),
        index=0,
        key="report_language_select"
    )
    
    # Store the language code in session state
    st.session_state.report_language = language_display[selected_language_display]
    
    st.markdown(f"""
    <div class="language-selection-badge">
        <span class="language-icon">🌐</span>
        <span class="language-text">Report will be generated in: <strong>{selected_language_display}</strong></span>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate Report Button
    st.markdown('<div class="generate-section">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🌾 Generate My AI Report", key="generate_btn", use_container_width=True, type="primary"):
            
            is_valid, error_msg = validate_inputs(audio_file, image_file, district)
            
            if not is_valid:
                st.markdown(f"""
                <div class="alert-box alert-warning">
                    <div class="alert-icon">⚠️</div>
                    <div class="alert-content">
                        <h4>Missing Information</h4>
                        <p>{error_msg}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Processing Animation
                st.markdown("""
                <div class="processing-box">
                    <div class="spinner"></div>
                    <h3 class="processing-title">Analyzing your data...</h3>
                    <p class="processing-text">Checking image, voice, and weather data</p>
                </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Audio Processing
                    status_text.markdown("🎯 **Processing voice input...**")
                    progress_bar.progress(25)
                    time.sleep(0.5)
                    
                    audio_processor = AudioProcessor()
                    voice_text, detected_lang, error = audio_processor.transcribe_audio(audio_file)
                    
                    if error:
                        st.error(f"Voice processing error: {error}")
                        st.stop()
                    
                    st.session_state.voice_text = voice_text
                    st.session_state.detected_language = detected_lang
                    
                    # Step 2: Disease Detection
                    status_text.markdown("🔬 **Analyzing plant health...**")
                    progress_bar.progress(50)
                    time.sleep(0.5)
                    
                    detector = EnhancedPlantDiseaseDetector()
                    disease_info, error = detector.detect_disease_advanced(image_file)
                    
                    if error:
                        st.warning(f"Using backup analysis: {error}")
                        disease_info = create_fallback_disease_info()
                    
                    st.session_state.disease_info = disease_info
                    
                    # Step 3: AI Analysis - USE SELECTED LANGUAGE
                    status_text.markdown("🤖 **Generating treatment plan...**")
                    progress_bar.progress(75)
                    time.sleep(0.5)
                    
                    # CRITICAL: Use user-selected language from dropdown
                    selected_report_language = st.session_state.report_language
                    
                    analyzer = AIAnalyzer()
                    report, error = analyzer.analyze_problem(
                        voice_text, 
                        disease_info, 
                        district, 
                        selected_report_language  # Use selected language, not detected
                    )
                    
                    if error:
                        st.error(f"AI analysis error: {error}")
                        st.stop()
                    
                    st.session_state.report = report
                    st.session_state.final_report_language = selected_report_language
                    
                    # Step 4: Audio Report in Selected Language
                    status_text.markdown(f"🔊 **Creating audio report in {selected_language_display}...**")
                    progress_bar.progress(90)
                    time.sleep(0.5)
                    
                    audio_path, _ = audio_processor.text_to_speech(report, selected_report_language)
                    st.session_state.audio_report_path = audio_path
                    
                    # Complete
                    progress_bar.progress(100)
                    status_text.markdown("✅ **Analysis complete!**")
                    st.session_state.analysis_complete = True
                    
                    time.sleep(1)
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Results
    if st.session_state.analysis_complete and st.session_state.report:
        
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        
        # Results Header
        st.markdown("""
        <div class="results-header">
            <h2 class="results-title">📄 Your AI Diagnosis Report</h2>
            <p class="results-subtitle">Complete analysis and treatment recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Summary Card
        if st.session_state.disease_info:
            disease_name = st.session_state.disease_info.get('disease_name', 'Unknown')
            confidence = st.session_state.disease_info.get('confidence', 0) * 100
            is_healthy = st.session_state.disease_info.get('is_healthy', False)
            
            status_icon = "✅" if is_healthy else "⚠️" if confidence > 50 else "❌"
            status_text = "Healthy" if is_healthy else "At Risk" if confidence > 50 else "Infected"
            status_class = "status-healthy" if is_healthy else "status-risk" if confidence > 50 else "status-infected"
            
            st.markdown(f"""
            <div class="diagnosis-summary">
                <div class="summary-header">
                    <span class="summary-icon">{status_icon}</span>
                    <h3 class="summary-title">{disease_name}</h3>
                </div>
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-label">Status</div>
                        <div class="stat-value {status_class}">{status_text}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Confidence</div>
                        <div class="stat-value">{confidence:.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Location</div>
                        <div class="stat-value">{st.session_state.selected_district}</div>
                    </div>
                </div>
                <div class="severity-bar">
                    <div class="severity-fill" style="width: {confidence}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Voice Transcription
        st.markdown("""
        <div class="report-section">
            <h3 class="section-title">🎤 Your Problem Description</h3>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="transcription-text">{st.session_state.voice_text}</div>', unsafe_allow_html=True)
        
        # Show detected voice language
        detected_lang_name = LANGUAGES.get(st.session_state.detected_language, {}).get('name', 'English')
        st.markdown(f'<p style="margin-top: 0.5rem; color: #666; font-size: 0.9rem;">Voice detected in: {detected_lang_name}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Treatment Plan
        st.markdown("""
        <div class="report-section">
            <h3 class="section-title">💊 Your Treatment Plan</h3>
        """, unsafe_allow_html=True)
        
        # Show report language
        final_lang = st.session_state.get('final_report_language', 'en')
        report_lang_name = LANGUAGES.get(final_lang, {}).get('name', 'English')
        st.markdown(f'<p style="margin-bottom: 1rem; color: #666; font-size: 0.9rem;">Report generated in: {report_lang_name}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display AI Report
        st.markdown(st.session_state.report)
        
        # Audio Player
        if st.session_state.audio_report_path:
            st.markdown("""
            <div class="audio-section">
                <h3 class="section-title">🔊 Listen to Your Report</h3>
                <p class="section-subtitle">Audio version in your selected language</p>
            </div>
            """, unsafe_allow_html=True)
            with open(st.session_state.audio_report_path, 'rb') as audio:
                st.audio(audio.read(), format='audio/mp3')
        
        # Action Buttons
        st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            final_lang = st.session_state.get('final_report_language', 'en')
            language_name = LANGUAGES.get(final_lang, {}).get('name', 'English')
            
            report_text = generate_text_report(
                st.session_state.voice_text,
                st.session_state.disease_info,
                st.session_state.report,
                st.session_state.selected_district,
                language_name
            )
            st.download_button(
                "📥 Download Report",
                data=report_text,
                file_name=f"Crop_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            if st.session_state.audio_report_path:
                with open(st.session_state.audio_report_path, 'rb') as audio:
                    st.download_button(
                        "🎵 Download Audio",
                        data=audio.read(),
                        file_name=f"Crop_Audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
        
        with col3:
            if st.button("🔄 New Diagnosis", use_container_width=True):
                st.session_state.analysis_complete = False
                st.session_state.report = None
                st.session_state.voice_text = None
                st.session_state.disease_info = None
                st.session_state.current_step = 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# REPORTS PAGE
# ============================================
elif st.session_state.page == 'reports':
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">📊 My Diagnosis Reports</h1>
        <p class="page-subtitle">View your analysis history</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.analysis_complete and st.session_state.report:
        st.markdown("""
        <div class="report-card">
            <h3 class="card-title">Latest Report</h3>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.report)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <h3 class="empty-title">No Reports Yet</h3>
            <p class="empty-text">Complete a diagnosis to see your reports here</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# HELP PAGE
# ============================================
elif st.session_state.page == 'help':
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">❓ Help & Support</h1>
        <p class="page-subtitle">Get assistance for farming issues</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="help-card">
            <h3 class="help-title">📞 Emergency Contacts</h3>
            <div class="contact-box">
                <strong>Punjab Agricultural University</strong>
                <p>📞 Kisan Call Center: <a href="tel:18001801551">1800-180-1551</a></p>
                <p>📧 Email: info@pau.edu</p>
            </div>
            <div class="contact-box">
                <strong>Agriculture Department Punjab</strong>
                <p>📞 Helpline: <a href="tel:01722296032">0172-2296032</a></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="help-card">
            <h3 class="help-title">🏢 Visit KVK Centers</h3>
            <p>Your nearest Krishi Vigyan Kendra provides:</p>
            <ul class="help-list">
                <li>Free soil testing</li>
                <li>Expert consultation</li>
                <li>Training programs</li>
                <li>Subsidized inputs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# ABOUT PAGE
# ============================================
elif st.session_state.page == 'about':
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">ℹ️ About AI Crop Doctor</h1>
        <p class="page-subtitle">Technology for farmers, by farmers</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="about-section">
        <h2 class="about-title">Our Mission</h2>
        <p class="about-text">
            AI Crop Doctor is dedicated to helping Indian farmers detect and treat crop diseases 
            using advanced artificial intelligence. We provide free, easy-to-use tools that work 
            in multiple languages and on any device.
        </p>
    </div>
    
    <div class="about-section">
        <h2 class="about-title">How It Works</h2>
        <div class="tech-grid">
            <div class="tech-box">
                <div class="tech-icon">🎤</div>
                <h4>Voice Recognition</h4>
                <p>AssemblyAI powered speech-to-text</p>
            </div>
            <div class="tech-box">
                <div class="tech-icon">🔬</div>
                <h4>Disease Detection</h4>
                <p>Plant.id professional API</p>
            </div>
            <div class="tech-box">
                <div class="tech-icon">🤖</div>
                <h4>AI Analysis</h4>
                <p>OpenRouter LLaMA 3.2</p>
            </div>
            <div class="tech-box">
                <div class="tech-icon">🔊</div>
                <h4>Audio Reports</h4>
                <p>Google Text-to-Speech</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main-wrapper

# Footer
st.markdown(f"""
<footer class="app-footer">
    <div class="footer-content">
        <div class="footer-section">
            <h4>AI Crop Doctor</h4>
            <p>Empowering farmers with AI technology</p>
        </div>
        <div class="footer-section">
            <h4>Quick Links</h4>
            <p><a href="#">Privacy Policy</a></p>
            <p><a href="#">Terms of Service</a></p>
        </div>
        <div class="footer-section">
            <h4>Contact</h4>
            <p>Email: support@aicropdoctor.com</p>
            <p>Phone: 1800-180-1551</p>
        </div>
    </div>
    <div class="footer-bottom">
        <p>Made with ❤️ for Farmers of India | © 2024 AI Crop Doctor v{APP_VERSION}</p>
    </div>
</footer>
""", unsafe_allow_html=True)
