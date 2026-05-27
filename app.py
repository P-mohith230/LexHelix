"""
Smart Judicial Case Timeline Analyzer
Single-page Streamlit application with all modules as horizontal tabs.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import uuid
import json
from datetime import datetime, date

st.set_page_config(
    page_title="Smart Judicial Case Timeline Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import database as db
from modules.ocr_extractor import extract_text, is_tesseract_available, get_supported_formats
from modules.nlp_summarizer import summarize_judgment, get_available_methods, extract_key_points
from modules.case_flow import (
    generate_timeline_from_text, determine_case_stage,
    events_to_vis_timeline, CASE_STAGES, EVENT_TYPE_COLORS,
    compute_case_statistics
)
from modules.three_visualizations import get_3d_dashboard_hero, get_3d_bar_chart, get_3d_timeline_helix, get_3d_pie_chart

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Load Stats ──────────────────────────────────────────────
stats = db.get_case_stats()

# ── Plotly Custom Dark-Neon Style Helper ────────────────────
def style_plotly_figure(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="'Space Grotesk', sans-serif",
        font_color='#cbd5e1',
        title_font_family="'Space Grotesk', sans-serif",
        title_font_color='#FFD700',
        legend_font_family="'Plus Jakarta Sans', sans-serif",
        xaxis=dict(
            gridcolor='rgba(0, 240, 255, 0.05)',
            linecolor='rgba(0, 240, 255, 0.1)',
            zerolinecolor='rgba(0, 240, 255, 0.1)'
        ),
        yaxis=dict(
            gridcolor='rgba(0, 240, 255, 0.05)',
            linecolor='rgba(0, 240, 255, 0.1)',
            zerolinecolor='rgba(0, 240, 255, 0.1)'
        )
    )
    return fig

# ══════════════════════════════════════════════════════════
#  GLOBAL STYLES
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Global Font Assignments */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e2e8f0;
}
h1, h2, h3, h4, h5, h6, .section-header {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Background Cyber Grid with Neon Glow Spots */
.stApp {
    background-color: #03050c !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(0, 240, 255, 0.05) 0px, transparent 50%),
        radial-gradient(at 50% 0%, rgba(255, 215, 0, 0.04) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(255, 0, 127, 0.05) 0px, transparent 50%),
        linear-gradient(rgba(255, 255, 255, 0.005) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.005) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 100% 100%, 30px 30px, 30px 30px;
}

/* Hide Sidebar & Header */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.stApp > header { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Premium Futuristic HUD Header */
.main-header {
    background: linear-gradient(135deg, rgba(13, 17, 28, 0.75) 0%, rgba(6, 8, 20, 0.9) 100%);
    padding: 1.8rem 2.2rem; border-radius: 16px; margin-bottom: 2rem;
    border: 1px solid rgba(0, 240, 255, 0.15);
    box-shadow: 0 20px 50px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.05);
    position: relative; overflow: hidden;
    display: flex; justify-content: space-between; align-items: center;
}
.main-header::before {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(0,240,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.main-header h1 {
    color: #ffffff; font-size: 1.8rem; font-weight: 700; margin: 0;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #ffffff, #FFD700, #00f0ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(0,240,255,0.1);
}
.main-header p { color: #94a3b8; font-size: 0.88rem; margin: 0.4rem 0 0 0; letter-spacing: 0.5px; }

/* Premium Glassmorphism Metric Cards */
.metric-card {
    background: rgba(13, 17, 28, 0.55);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 240, 255, 0.12); border-radius: 16px;
    padding: 1.2rem 0.8rem; text-align: center;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03);
    position: relative; overflow: hidden;
}
.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0, 240, 255, 0.15), inset 0 1px 0 rgba(255,255,255,0.08);
    border-color: rgba(0, 240, 255, 0.35);
}
.metric-card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, transparent, #00f0ff, #FFD700, transparent);
    opacity: 0; transition: opacity 0.3s;
}
.metric-card:hover::after { opacity: 1; }
.metric-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; line-height: 1.1; }
.metric-label { font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0.5rem; font-weight: 600; }
.metric-icon { font-size: 1.4rem; margin-bottom: 0.3rem; filter: drop-shadow(0 0 5px rgba(0,240,255,0.4)); }

/* Sleek Sections */
.section-header {
    color: #f8fafc; font-size: 1.1rem; font-weight: 600;
    margin: 1.8rem 0 1.2rem 0; padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0, 240, 255, 0.15); letter-spacing: 0.5px;
    text-transform: uppercase; display: flex; align-items: center; gap: 8px;
}
.section-header::before {
    content: ''; display: inline-block; width: 4px; height: 12px; background: #FFD700; border-radius: 2px;
}

/* Glassmorphic Summary Box */
.summary-box {
    background: rgba(13, 17, 28, 0.65); backdrop-filter: blur(8px);
    border: 1px solid rgba(34, 197, 94, 0.25); border-left: 4px solid #22c55e;
    border-radius: 12px; padding: 1.5rem; margin: 1rem 0;
    color: #cbd5e1; line-height: 1.7; font-size: 0.9rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

/* Key Point Tags */
.key-point-tag {
    display: inline-block; background: rgba(0, 240, 255, 0.08); color: #00f0ff;
    padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem;
    margin: 0.2rem; border: 1px solid rgba(0, 240, 255, 0.25); font-weight: 500;
    transition: all 0.2s;
}
.key-point-tag:hover {
    background: rgba(0, 240, 255, 0.15);
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
    transform: scale(1.05);
}

/* Stage Indicators (Pill docking style) */
.stage-indicator {
    display: inline-flex; align-items: center; justify-content: center;
    flex-direction: column; gap: 0.4rem;
    background: rgba(13, 17, 28, 0.5); backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 14px;
    padding: 0.8rem 0.6rem; font-size: 0.7rem; color: #64748b;
    text-align: center; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); min-width: 90px;
}
.stage-active {
    border-color: #FFD700 !important; background: rgba(255, 215, 0, 0.08) !important;
    color: #FFD700 !important; font-weight: 700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    transform: scale(1.05);
}
.stage-past { border-color: rgba(34, 197, 94, 0.3); color: #22c55e; }

/* Custom Streamlit Tabs styling (Dock system) */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: rgba(13, 17, 28, 0.65) !important;
    backdrop-filter: blur(16px);
    border-radius: 16px; padding: 0.35rem;
    border: 1px solid rgba(0, 240, 255, 0.12);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
    justify-content: center;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px; padding: 0.65rem 1.5rem; font-weight: 600;
    font-size: 0.85rem; white-space: nowrap; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); color: #94a3b8;
}
.stTabs [data-baseweb="tab"]:hover { background: rgba(0, 240, 255, 0.05); color: #00f0ff; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(255, 0, 127, 0.08)) !important;
    color: #00f0ff !important; box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
    border: 1px solid rgba(0, 240, 255, 0.25) !important;
}
.stTabs [data-baseweb="tab-highlight"] { background-color: #00f0ff !important; height: 3px; border-radius: 3px; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* High-end Styled Inputs, Selectboxes & Textareas */
[data-baseweb="select"], [data-baseweb="input"], textarea, input {
    background-color: rgba(6, 8, 20, 0.8) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    color: #cbd5e1 !important;
    border-radius: 10px !important;
    transition: all 0.25s ease !important;
}
textarea:focus, input:focus, [data-baseweb="select"]:focus-within {
    border-color: #00f0ff !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.35) !important;
}

/* Glowing Streamlit Primary Buttons */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #00f0ff 0%, #00b4d8 50%, #ff007f 100%) !important;
    color: #ffffff !important; border: none !important; border-radius: 10px !important;
    padding: 0.6rem 1.6rem !important; font-weight: 600 !important;
    letter-spacing: 0.5px !important; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 5px 15px rgba(0,240,255,0.2) !important;
}
.stButton button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(0,240,255,0.4), 0 0 15px rgba(255,0,127,0.3) !important;
}

/* Glassmorphic Dataframes */
[data-testid="stDataFrame"] {
    background: rgba(13, 17, 28, 0.45) !important;
    border: 1px solid rgba(0, 240, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

/* Futuristic Scanning Laser Loader */
.scanner-container {
    position: relative; width: 100%; height: 180px;
    background: linear-gradient(180deg, rgba(6, 8, 20, 0.8) 0%, rgba(13, 17, 28, 0.5) 100%);
    border: 1px solid rgba(0, 240, 255, 0.25);
    border-radius: 12px; overflow: hidden; margin: 1rem 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.scanner-title {
    font-size: 12px; text-transform: uppercase; color: #00f0ff; letter-spacing: 2px;
    z-index: 5; font-weight: 600; text-shadow: 0 0 10px rgba(0,240,255,0.5);
    animation: scannerPulse 1.5s infinite alternate;
}
.scanner-laser {
    position: absolute; top: 0; left: 0; width: 100%; height: 3px;
    background: linear-gradient(90deg, transparent, #00f0ff, transparent);
    box-shadow: 0 0 10px #00f0ff, 0 0 20px #00f0ff;
    animation: laserSweep 2s ease-in-out infinite; z-index: 2;
}
@keyframes laserSweep {
    0% { top: 0%; }
    50% { top: 100%; }
    100% { top: 0%; }
}
@keyframes scannerPulse {
    0% { opacity: 0.5; }
    100% { opacity: 1.0; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <div>
        <h1>⚖️ Smart Judicial Case Timeline Analyzer</h1>
        <p>AI-Powered Legal Document Processing &bull; NLP Judgment Summarization &bull; Interactive Case Timelines</p>
    </div>
    <div style="background: rgba(0, 240, 255, 0.1); border: 1px solid #00f0ff; color: #00f0ff; border-radius: 30px; padding: 4px 14px; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
        JUDICIAL OS V3.5
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════════
tab_dashboard, tab_ocr, tab_cases, tab_nlp, tab_timeline, tab_analytics = st.tabs([
    "Dashboard",
    "OCR Extractor",
    "Case Manager",
    "NLP Summarizer",
    "Timeline Analyzer",
    "Analytics"
])


# ══════════════════════════════════════════════════════════
#  TAB 1: DASHBOARD
# ══════════════════════════════════════════════════════════
with tab_dashboard:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    metrics = [
        ("📂", "Total Cases", stats["total_cases"], col1),
        ("⌛", "Pending", stats["pending"], col2),
        ("🏛️", "Hearing", stats["hearing"], col3),
        ("✅", "Disposed", stats["disposed"], col4),
        ("📄", "Documents", stats["total_documents"], col5),
        ("📝", "Summaries", stats["total_summaries"], col6),
    ]
    for icon, label, value, col in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <p class="metric-value">{value}</p>
                <p class="metric-label">{label}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Premium Split Grid Layout
    hero_col, chart_col = st.columns([1.1, 1.3])
    
    with hero_col:
        st.markdown('<p class="section-header">Judicial AI Knowledge Graph</p>', unsafe_allow_html=True)
        st.components.v1.html(get_3d_dashboard_hero(), height=380)
        
    with chart_col:
        st.markdown('<p class="section-header">Case Analytics Topology</p>', unsafe_allow_html=True)
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            status_data = db.get_status_distribution()
            if status_data:
                df_status = pd.DataFrame(status_data)
                html_donut = get_3d_pie_chart(df_status['status'].tolist(), df_status['count'].tolist(), "Status Breakdown Topology", height=350)
                st.components.v1.html(html_donut, height=350)
            else:
                st.info("No case data yet.")
        with sub_c2:
            type_data = db.get_case_type_distribution()
            if type_data:
                df_type = pd.DataFrame(type_data)
                html_bars = get_3d_bar_chart(df_type['case_type'].tolist(), df_type['count'].tolist(), "Case Type Distribution Matrix", height=350)
                st.components.v1.html(html_bars, height=350)
            else:
                st.info("No case data yet.")

    st.markdown('<p class="section-header">Monthly Filing Trend</p>', unsafe_allow_html=True)
    monthly_data = db.get_monthly_filings()
    if monthly_data:
        df_monthly = pd.DataFrame(monthly_data)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_monthly['month'], y=df_monthly['count'],
            mode='lines+markers', line=dict(color='#FFD700', width=3),
            marker=dict(size=10, color='#FFD700', line=dict(width=2, color='#1a1a2e')),
            fill='tozeroy', fillcolor='rgba(255,215,0,0.08)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#e2e8f0', height=280, margin=dict(t=20,b=20,l=40,r=20),
                        xaxis=dict(title="Month", gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(title="Cases Filed", gridcolor='rgba(255,255,255,0.05)'))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-header">Recent Cases</p>', unsafe_allow_html=True)
    cases = db.get_all_cases()
    if cases:
        df = pd.DataFrame(cases[:10])
        display_cols = ['case_number','title','court','case_type','status','filing_date']
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], use_container_width=True, hide_index=True)
    else:
        st.info("No cases yet. Use the Case Manager tab to add cases or run setup_kaggle.py.")


# ══════════════════════════════════════════════════════════
#  TAB 2: OCR EXTRACTOR
# ══════════════════════════════════════════════════════════
with tab_ocr:
    st.markdown('<p class="section-header">OCR Image Text Extraction</p>', unsafe_allow_html=True)
    ocr_col1, ocr_col2 = st.columns(2)
    with ocr_col1:
        if is_tesseract_available():
            st.success("Tesseract OCR is available and ready.")
        else:
            st.error("Tesseract OCR not installed. [Install Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)")
    with ocr_col2:
        st.info(f"Supported formats: {', '.join(sorted(get_supported_formats()))}")

    upload_col, settings_col = st.columns([2, 1])
    with settings_col:
        st.markdown("**Settings**")
        all_cases = db.get_all_cases()
        case_opts = {"(No case linked)": None}
        case_opts.update({f"{c['case_number']} — {c['title']}": c['case_id'] for c in all_cases})
        selected_case_ocr = st.selectbox("Link to Case", list(case_opts.keys()), key="ocr_case")
        ocr_case_id = case_opts[selected_case_ocr]
    with upload_col:
        uploaded_file = st.file_uploader("Choose a scanned document image",
            type=['png','jpg','jpeg','tiff','tif','bmp','webp'], key="ocr_upload")
        if uploaded_file:
            st.image(uploaded_file, caption=uploaded_file.name, width=400)

    if uploaded_file:
        if st.button("Extract Text (Run OCR)", type="primary", use_container_width=True, key="run_ocr"):
            file_ext = os.path.splitext(uploaded_file.name)[1]
            unique_name = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Laser holographic scanner load sweep
            scan_placeholder = st.empty()
            scan_placeholder.markdown("""
            <div class="scanner-container">
                <div class="scanner-title">Scanning Scanned Document Matrix...</div>
                <div class="scanner-laser"></div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Running OCR..."):
                progress = st.progress(0, text="Preprocessing...")
                progress.progress(30, text="Running OCR engine...")
                result = extract_text(file_path)
                progress.progress(100, text="Done!")
                
            scan_placeholder.empty()
            if result["success"]:
                st.success(f"OCR completed using {result['method']}")
                m1, m2, m3 = st.columns(3)
                with m1: st.metric("Words", result["word_count"])
                with m2: st.metric("Confidence", f"{result['confidence']}%")
                with m3: st.metric("Method", result["method"])
                edited_text = st.text_area("Extracted Text (editable):", result["text"], height=350, key="ocr_txt")
                save_col, dl_col = st.columns(2)
                with save_col:
                    if st.button("Save to Database", key="save_ocr"):
                        doc_id = db.save_document(ocr_case_id, unique_name, uploaded_file.name,
                                                  file_ext, edited_text, result["confidence"], result["word_count"])
                        st.success(f"Saved! (Doc ID: {doc_id})")
                with dl_col:
                    st.download_button("Download TXT", edited_text,
                                      file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ocr.txt")
            else:
                st.error(f"OCR failed: {result['error']}")

    st.markdown("---")
    st.markdown('<p class="section-header">Previously Uploaded Documents</p>', unsafe_allow_html=True)
    all_docs = db.get_all_documents()
    if all_docs:
        for doc in all_docs[:8]:
            case_info = f"Case: {doc.get('case_number', 'N/A')}" if doc.get('case_number') else "Unlinked"
            with st.expander(f"{doc.get('original_name', doc['filename'])} | {case_info} | {doc.get('upload_date','')}"):
                dc1, dc2, dc3 = st.columns(3)
                with dc1: st.metric("Words", doc.get("word_count", 0))
                with dc2: st.metric("Confidence", f"{doc.get('ocr_confidence', 0)}%")
                with dc3: st.metric("Type", doc.get("file_type", "N/A"))
                if doc.get("extracted_text"):
                    st.text_area("Text", doc["extracted_text"][:2000], height=150,
                                key=f"pdoc_{doc['doc_id']}", disabled=True)
    else:
        st.info("No documents uploaded yet.")


# ══════════════════════════════════════════════════════════
#  TAB 3: CASE MANAGER
# ══════════════════════════════════════════════════════════
with tab_cases:
    case_sub1, case_sub2, case_sub3 = st.tabs(["Case List", "Create Case", "Case Detail"])

    with case_sub1:
        cases = db.get_all_cases()
        f1, f2, f3 = st.columns(3)
        with f1: status_f = st.selectbox("Status", ["All","Pending","Hearing","Disposed","Reserved"], key="cf_st")
        with f2: type_f = st.selectbox("Type", ["All","Civil","Criminal","Environmental","Intellectual Property","Labour","Family"], key="cf_ty")
        with f3: search_f = st.text_input("Search", placeholder="Case number or title...", key="cf_sr")
        filtered = cases
        if status_f != "All": filtered = [c for c in filtered if c.get("status") == status_f]
        if type_f != "All": filtered = [c for c in filtered if c.get("case_type") == type_f]
        if search_f:
            sl = search_f.lower()
            filtered = [c for c in filtered if sl in c.get("case_number","").lower() or sl in c.get("title","").lower()]
        st.markdown(f"**{len(filtered)}** cases found")
        if filtered:
            df = pd.DataFrame(filtered)
            cols = ['case_id','case_number','title','court','case_type','status','priority','filing_date']
            avail = [c for c in cols if c in df.columns]
            st.dataframe(df[avail], use_container_width=True, hide_index=True)
            st.markdown("#### Quick Status Update")
            qs1, qs2, qs3 = st.columns(3)
            with qs1: upd_id = st.selectbox("Case ID", [c["case_id"] for c in filtered], key="qs_id")
            with qs2: new_st = st.selectbox("New Status", ["Pending","Hearing","Arguments","Evidence","Reserved","Disposed"], key="qs_st")
            with qs3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update", type="primary", key="qs_btn"):
                    db.update_case_status(upd_id, new_st)
                    st.success(f"Updated to {new_st}")
                    st.rerun()
        else:
            st.info("No cases found. Create one in the Create Case tab.")

    with case_sub2:
        with st.form("create_case_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                case_num = st.text_input("Case Number *", placeholder="SCI/2024/001")
                title = st.text_input("Case Title *", placeholder="State vs. Defendant")
                court = st.selectbox("Court", ["Supreme Court of India","High Court of Delhi",
                    "High Court of Bombay","High Court of Madras","High Court of Calcutta",
                    "High Court of Karnataka","District Court","Sessions Court","Other"])
                judge = st.text_input("Presiding Judge", placeholder="Hon. Justice Name")
            with fc2:
                petitioner = st.text_input("Petitioner")
                respondent = st.text_input("Respondent")
                case_type = st.selectbox("Case Type", ["Civil","Criminal","Environmental",
                    "Intellectual Property","Labour","Family","Constitutional","Tax","Other"])
                filing_dt = st.date_input("Filing Date", value=date.today())
                priority = st.selectbox("Priority", ["Normal","High","Urgent"])
            if st.form_submit_button("Create Case", type="primary", use_container_width=True):
                if not case_num or not title:
                    st.error("Case Number and Title are required!")
                else:
                    try:
                        cid = db.create_case(case_num, title, court, judge, petitioner, respondent,
                                            case_type, filing_dt.strftime("%Y-%m-%d"), "Pending", priority)
                        db.add_timeline_event(cid, filing_dt.strftime("%Y-%m-%d"), "Filing",
                                            "Case Filed", f"Case {case_num} filed at {court}")
                        st.success(f"Case created! (ID: {cid})")
                        st.balloons()
                    except Exception as e:
                        st.error(str(e))

    with case_sub3:
        cases = db.get_all_cases()
        if cases:
            copts = {f"{c['case_number']} — {c['title']}": c['case_id'] for c in cases}
            sel = st.selectbox("Select Case", list(copts.keys()), key="cd_sel")
            case = db.get_case(copts[sel])
            if case:
                ic = st.columns(4)
                for i, (l, v) in enumerate([("Status", case.get("status")),
                    ("Type", case.get("case_type")), ("Court", case.get("court")),
                    ("Priority", case.get("priority"))]):
                    with ic[i]: st.metric(l, v or "N/A")
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown(f"**Judge:** {case.get('judge','N/A')}")
                    st.markdown(f"**Petitioner:** {case.get('petitioner','N/A')}")
                with d2:
                    st.markdown(f"**Respondent:** {case.get('respondent','N/A')}")
                    st.markdown(f"**Filed:** {case.get('filing_date','N/A')}")
                docs = db.get_documents_by_case(case['case_id'])
                if docs:
                    st.markdown("**Documents:**")
                    for d in docs:
                        st.markdown(f"- {d.get('original_name', d['filename'])} | Words: {d.get('word_count',0)} | Conf: {d.get('ocr_confidence',0)}%")
                events = db.get_timeline_events(case['case_id'])
                if events:
                    st.markdown("**Timeline:**")
                    for e in events:
                        st.markdown(f"- **{e['event_date']}** [{e['event_type']}] {e['title']}")
                with st.expander("Danger Zone"):
                    if st.button("Delete Case", key="del_case"):
                        db.delete_case(case['case_id'])
                        st.success("Deleted.")
                        st.rerun()
        else:
            st.info("No cases available.")


# ══════════════════════════════════════════════════════════
#  TAB 4: NLP SUMMARIZER
# ══════════════════════════════════════════════════════════
with tab_nlp:
    st.markdown('<p class="section-header">NLP Judgment Summarizer</p>', unsafe_allow_html=True)
    nlp_src1, nlp_src2 = st.tabs(["From Case Document", "Paste Text"])

    with nlp_src1:
        cases = db.get_all_cases()
        if cases:
            nlp_copts = {f"{c['case_number']} — {c['title']}": c['case_id'] for c in cases}
            nlp_sel = st.selectbox("Select Case", list(nlp_copts.keys()), key="nlp_case")
            nlp_cid = nlp_copts[nlp_sel]
            docs = db.get_documents_by_case(nlp_cid)
            if docs:
                doc_opts = {f"{d.get('original_name', d['filename'])} (ID: {d['doc_id']})": d for d in docs}
                nlp_doc_sel = st.selectbox("Select Document", list(doc_opts.keys()), key="nlp_doc")
                doc = doc_opts[nlp_doc_sel]
                text = doc.get("extracted_text", "")
                if text:
                    with st.expander("View Full Text", expanded=False):
                        st.text_area("Text", text, height=250, disabled=True, key="nlp_ft")
                    nc1, nc2 = st.columns(2)
                    with nc1: method = st.selectbox("Method", get_available_methods(), key="nlp_m")
                    with nc2: n_sent = st.slider("Summary Sentences", 3, 10, 5, key="nlp_s")
                    if st.button("Generate Summary", type="primary", use_container_width=True, key="nlp_gen"):
                        with st.spinner("Analyzing with NLP..."):
                            result = summarize_judgment(text, method=method, num_sentences=n_sent)
                        if result["success"]:
                            st.success(f"Summary via {result['method']}")
                            st.markdown(f'<div class="summary-box">{result["summary"]}</div>', unsafe_allow_html=True)
                            kp = result["key_points"]
                            kc1, kc2 = st.columns(2)
                            with kc1:
                                for key in ["case_numbers","judges","court_names"]:
                                    if kp.get(key):
                                        st.markdown(f"**{key.replace('_',' ').title()}:**")
                                        for v in kp[key]: st.markdown(f"- {v}")
                            with kc2:
                                for key in ["dates","statutes"]:
                                    if kp.get(key):
                                        st.markdown(f"**{key.title()}:**")
                                        for v in kp[key][:10]: st.markdown(f"- {v}")
                                if kp.get("legal_terms"):
                                    st.markdown("**Legal Terms:**")
                                    tags = ''.join(f'<span class="key-point-tag">{t}</span>' for t in kp["legal_terms"])
                                    st.markdown(tags, unsafe_allow_html=True)
                            if st.button("Save Summary", key="nlp_save"):
                                db.save_summary(doc["doc_id"], nlp_cid, result["summary"],
                                               result["key_points"], result["method"])
                                st.success("Saved!")
                        else:
                            st.error(result['error'])
                else:
                    st.warning("No text in document. Run OCR first.")
            else:
                st.info("No documents for this case. Upload via OCR Extractor tab.")
        else:
            st.info("No cases. Create one in Case Manager tab.")

    with nlp_src2:
        pasted = st.text_area("Paste judgment text:", height=300, key="nlp_paste",
                             placeholder="Paste legal judgment text here for analysis...")
        if pasted:
            pc1, pc2 = st.columns(2)
            with pc1: pm = st.selectbox("Method", get_available_methods(), key="pm")
            with pc2: ps = st.slider("Sentences", 3, 10, 5, key="ps")
            if st.button("Summarize", type="primary", use_container_width=True, key="nlp_paste_btn"):
                with st.spinner("Processing..."):
                    r = summarize_judgment(pasted, method=pm, num_sentences=ps)
                if r["success"]:
                    st.success(r['method'])
                    st.markdown(f'<div class="summary-box">{r["summary"]}</div>', unsafe_allow_html=True)
                    kp = r["key_points"]
                    for key, lbl in [("dates","Dates"), ("statutes","Statutes"), ("legal_terms","Legal Terms")]:
                        if kp.get(key):
                            st.markdown(f"**{lbl}:** {', '.join(str(v) for v in kp[key])}")
                else:
                    st.error(r['error'])


# ══════════════════════════════════════════════════════════
#  TAB 5: TIMELINE ANALYZER
# ══════════════════════════════════════════════════════════
with tab_timeline:
    st.markdown('<p class="section-header">Case Timeline Analyzer</p>', unsafe_allow_html=True)
    cases = db.get_all_cases()
    if not cases:
        st.info("No cases. Create one in Case Manager tab.")
    else:
        tl_copts = {f"{c['case_number']} — {c['title']}": c['case_id'] for c in cases}
        tl_sel = st.selectbox("Select Case", list(tl_copts.keys()), key="tl_case")
        tl_cid = tl_copts[tl_sel]
        tl_case = db.get_case(tl_cid)
        tl_events = db.get_timeline_events(tl_cid)

        st.markdown("#### Case Flow Progress")
        current_stage = determine_case_stage(tl_events)
        stage_cols = st.columns(len(CASE_STAGES))
        for i, stage in enumerate(CASE_STAGES):
            with stage_cols[i]:
                is_active = stage["stage"] == current_stage["stage"]
                is_past = i < CASE_STAGES.index(current_stage)
                css = "stage-active" if is_active else ("stage-past" if is_past else "")
                opa = "1" if (is_active or is_past) else "0.35"
                st.markdown(f'<div class="stage-indicator {css}" style="opacity:{opa}">'
                           f'{stage["icon"]}<br>{stage["stage"]}</div>', unsafe_allow_html=True)

        tl_t1, tl_t2, tl_t3 = st.tabs(["Interactive Timeline", "Add Event", "Auto-Generate"])

        with tl_t1:
            if tl_events:
                st.markdown(f"**{len(tl_events)}** events for **{tl_case.get('case_number','')}**")
                
                # Dynamic 3D Helix Timeline substitution
                st.components.v1.html(
                    get_3d_timeline_helix(tl_events, f"Timeline double Helix: {tl_case.get('case_number','')}", height=450),
                    height=450
                )
                
                evt_df = pd.DataFrame(tl_events)
                st.dataframe(evt_df[['event_date','event_type','title','description']],
                            use_container_width=True, hide_index=True)
            else:
                st.info("No events yet. Add events or use Auto-Generate.")

        with tl_t2:
            with st.form("add_event"):
                ae1, ae2 = st.columns(2)
                with ae1:
                    ev_date = st.date_input("Date", value=date.today(), key="ae_dt")
                    ev_type = st.selectbox("Type", list(EVENT_TYPE_COLORS.keys()), key="ae_ty")
                    ev_title = st.text_input("Title", placeholder="e.g., First Hearing", key="ae_ti")
                with ae2:
                    ev_desc = st.text_area("Description", height=120, key="ae_ds")
                if st.form_submit_button("Add Event", type="primary", use_container_width=True):
                    if ev_title:
                        db.add_timeline_event(tl_cid, ev_date.strftime("%Y-%m-%d"), ev_type, ev_title, ev_desc)
                        st.success("Event added!")
                        st.rerun()
                    else:
                        st.error("Title required!")

        with tl_t3:
            docs = db.get_documents_by_case(tl_cid)
            text_docs = [d for d in docs if d.get("extracted_text")] if docs else []
            if text_docs:
                ag_opts = {f"{d.get('original_name', d['filename'])}": d for d in text_docs}
                ag_sel = st.selectbox("Document", list(ag_opts.keys()), key="ag_doc")
                if st.button("Analyze and Generate", type="primary", use_container_width=True, key="ag_btn"):
                    with st.spinner("Analyzing..."):
                        gen = generate_timeline_from_text(ag_opts[ag_sel]["extracted_text"], tl_case)
                    if gen:
                        st.success(f"Found {len(gen)} events!")
                        for ev in gen:
                            with st.expander(f"{ev['event_date']} - {ev['title']}"):
                                st.write(f"Type: {ev['event_type']} | {ev.get('description','')}")
                                if st.button("Add This Event", key=f"ag_{ev['event_date']}_{ev['title']}"):
                                    db.add_timeline_event(tl_cid, ev["event_date"], ev["event_type"],
                                                        ev["title"], ev.get("description",""))
                                    st.rerun()
                    else:
                        st.warning("No datable events found.")
            else:
                st.info("No documents with text. Upload and OCR first.")


# ══════════════════════════════════════════════════════════
#  TAB 6: ANALYTICS
# ══════════════════════════════════════════════════════════
with tab_analytics:
    st.markdown('<p class="section-header">Court Analytics Dashboard</p>', unsafe_allow_html=True)
    cases = db.get_all_cases()
    a_stats = compute_case_statistics(cases)
    if not cases:
        st.info("No data. Add cases first.")
    else:
        ak = st.columns(5)
        analytics_kpis = [
            ("&#128193;", "Total Cases", a_stats["total_cases"]),
            ("&#9203;", "Pending", a_stats["status_distribution"].get("Pending",0)),
            ("&#9989;", "Disposed", a_stats["status_distribution"].get("Disposed",0)),
            ("&#128197;", "Avg Duration", f"{a_stats['avg_duration_days']}d"),
            ("&#128202;", "Case Types", len(a_stats["type_distribution"]))
        ]
        for i, (ic, lb, vl) in enumerate(analytics_kpis):
            with ak[i]:
                st.markdown(f'<div class="metric-card"><div class="metric-icon">{ic}</div>'
                           f'<p class="metric-value">{vl}</p>'
                           f'<p class="metric-label">{lb}</p></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        ac1, ac2 = st.columns(2)
        with ac1:
            st.markdown("#### Status Breakdown")
            if a_stats["status_distribution"]:
                sdf = pd.DataFrame(list(a_stats["status_distribution"].items()), columns=["Status","Count"])
                html_donut = get_3d_pie_chart(sdf['Status'].tolist(), sdf['Count'].tolist(), "Case Status Breakdown Topology", height=380)
                st.components.v1.html(html_donut, height=380)
        with ac2:
            st.markdown("#### Case Types")
            if a_stats["type_distribution"]:
                tdf = pd.DataFrame(list(a_stats["type_distribution"].items()), columns=["Type","Count"])
                html_bars = get_3d_bar_chart(tdf['Type'].tolist(), tdf['Count'].tolist(), "Case Type Distribution Grid", height=380)
                st.components.v1.html(html_bars, height=380)

        ac3, ac4 = st.columns(2)
        with ac3:
            st.markdown("#### Court Distribution")
            if a_stats["court_distribution"]:
                cdf = pd.DataFrame(list(a_stats["court_distribution"].items()), columns=["Court","Count"])
                fig = px.bar(cdf, x='Count', y='Court', orientation='h', color='Count',
                            color_continuous_scale=['#00f0ff','#FFD700'])
                fig = style_plotly_figure(fig)
                fig.update_layout(height=380, margin=dict(t=30,b=30), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with ac4:
            st.markdown("#### Priority")
            if a_stats["priority_distribution"]:
                pdf = pd.DataFrame(list(a_stats["priority_distribution"].items()), columns=["Priority","Count"])
                html_donut = get_3d_pie_chart(pdf['Priority'].tolist(), pdf['Count'].tolist(), "Case Priority Distribution Index", height=380)
                st.components.v1.html(html_donut, height=380)

        st.markdown("#### Monthly Filing Trend")
        if a_stats["monthly_trend"]:
            mdf = pd.DataFrame(list(a_stats["monthly_trend"].items()), columns=["Month","Filings"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=mdf['Month'], y=mdf['Filings'], mode='lines+markers+text',
                line=dict(color='#00f0ff', width=3, shape='spline'),
                marker=dict(size=12, color='#FFD700', line=dict(width=2, color='#03050c')),
                fill='tozeroy', fillcolor='rgba(0, 240, 255, 0.05)',
                text=mdf['Filings'], textposition="top center", textfont=dict(color='#FFD700')))
            fig = style_plotly_figure(fig)
            fig.update_layout(height=320, margin=dict(t=20,b=30,l=50,r=30))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Full Data Table")
        df = pd.DataFrame(cases)
        cols = ['case_number','title','court','case_type','status','priority','judge','filing_date']
        avail = [c for c in cols if c in df.columns]
        st.dataframe(df[avail], use_container_width=True, hide_index=True)
        csv = df[avail].to_csv(index=False)
        st.download_button("Export CSV", csv, file_name="judicial_analytics.csv", mime="text/csv")
