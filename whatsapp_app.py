"""
Cyberbullying App WhatsApp - Real-Time AI Moderation Dashboard.
Sleek dark-mode WhatsApp Web Clone with glassmorphic stylings,
real-time message blurring, 10s auto-delete countdowns, and browser popup warnings.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime

import database as db
from modules.moderator_engine import classify_message
from modules.chat_simulator import get_dialogue_line, get_total_dialogue_count
from modules.three_visualizations import get_3d_dashboard_hero, get_3d_bar_chart, get_3d_timeline_helix

# Page Configurations
st.set_page_config(
    page_title="Cyberbullying App WhatsApp",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZER
# ══════════════════════════════════════════════════════════
if "active_contact" not in st.session_state:
    st.session_state.active_contact = 1  # Aarav Sharma by default
if "sim_index" not in st.session_state:
    st.session_state.sim_index = 0
if "active_countdown" not in st.session_state:
    st.session_state.active_countdown = None  # holds (message_id, start_time, original_text, sender_id, receiver_id)
if "trigger_detection_alert" not in st.session_state:
    st.session_state.trigger_detection_alert = False
if "trigger_deletion_alert" not in st.session_state:
    st.session_state.trigger_deletion_alert = False
if "show_profile_page" not in st.session_state:
    st.session_state.show_profile_page = False  # toggles profile detail page

# ══════════════════════════════════════════════════════════
#  GLOBAL HIGH-TECH STYLING (GLASSMORPHISM)
# ══════════════════════════════════════════════════════════
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* Global resets & typography */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #03050c !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e2e8f0;
}
h1, h2, h3, h4, h5, h6, .section-header {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700;
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

/* Glassmorphism Card styling */
.glass-panel {
    background: rgba(13, 20, 35, 0.45);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 240, 255, 0.12);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    margin-bottom: 1.2rem;
}

/* Cyber Alert Banner */
.cyberbullying-banner {
    background: linear-gradient(135deg, rgba(255, 0, 127, 0.25) 0%, rgba(20, 5, 15, 0.8) 100%);
    border: 1px solid #ff007f;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #ff007f;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    line-height: 1.5;
    box-shadow: 0 0 20px rgba(255, 0, 127, 0.25);
    margin-bottom: 1.2rem;
    animation: alertPulse 1.5s infinite alternate;
}

@keyframes alertPulse {
    0% { border-color: rgba(255, 0, 127, 0.5); }
    100% { border-color: rgba(255, 0, 127, 1); }
}

/* WhatsApp-Web Layout */
.whatsapp-container {
    display: flex;
    height: 75vh;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(0, 240, 255, 0.15);
    background: rgba(8, 12, 22, 0.8);
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6);
}

/* Chat Bubbles */
.chat-window {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    background: radial-gradient(circle at 50% 50%, #0d131f 0%, #05080f 100%);
}

.chat-bubble {
    max-width: 65%;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    font-size: 0.88rem;
    line-height: 1.45;
    position: relative;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.35);
}

.sender-bubble {
    align-self: flex-end;
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.15) 0%, rgba(0, 180, 216, 0.08) 100%);
    border: 1px solid rgba(0, 240, 255, 0.2);
    color: #e2e8f0;
    border-bottom-right-radius: 2px;
}

.receiver-bubble {
    align-self: flex-start;
    background: rgba(16, 24, 43, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: #e2e8f0;
    border-bottom-left-radius: 2px;
}

/* Bullying Blurring CSS Censors */
.toxic-blurred {
    filter: blur(7px);
    background: rgba(255, 0, 127, 0.12) !important;
    border: 1px solid #ff007f !important;
    color: #ff007f !important;
    cursor: help;
    transition: filter 0.35s ease;
}
.toxic-blurred:hover {
    filter: blur(0px);
}

.deleted-bubble {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px dashed rgba(255, 255, 255, 0.15) !important;
    color: #64748b !important;
    font-style: italic;
}

/* Profiles stats grid */
.profile-stats-card {
    background: rgba(13, 20, 35, 0.65);
    border: 1px solid rgba(255, 215, 0, 0.12);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.45);
}

/* Custom Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10, 15, 28, 0.85) !important;
    border-radius: 12px;
    padding: 0.3rem;
    border: 1px solid rgba(0, 240, 255, 0.15);
}
.stTabs [data-baseweb="tab"] {
    padding: 0.5rem 1.5rem;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: rgba(0, 240, 255, 0.15) !important;
    color: #00f0ff !important;
    border-radius: 10px;
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
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  NATIVE BROWSER ALERTS POPUPS
# ══════════════════════════════════════════════════════════
if st.session_state.trigger_detection_alert:
    st.components.v1.html('<script>alert("This is a cyber message");</script>', height=0)
    st.session_state.trigger_detection_alert = False

if st.session_state.trigger_deletion_alert:
    st.components.v1.html('<script>alert("Cyberbullying message has been automatically deleted after 10 seconds.");</script>', height=0)
    st.session_state.trigger_deletion_alert = False

# ══════════════════════════════════════════════════════════
#  LIVE COUNTDOWN SCHEDULER
# ══════════════════════════════════════════════════════════
if st.session_state.active_countdown:
    msg_id, start_time, raw_text, sender_id, receiver_id = st.session_state.active_countdown
    elapsed = (datetime.now() - start_time).total_seconds()
    
    if elapsed >= 10:
        db.flag_message_deleted(msg_id)
        # Update user profiles: increment statistics
        db.increment_contact_stats(sender_id, "sent")
        db.increment_contact_stats(receiver_id, "received")
        st.session_state.active_countdown = None
        st.session_state.trigger_deletion_alert = True
        st.rerun()
    else:
        sec_left = int(10 - elapsed)
        st.markdown(f"""
        <div class="cyberbullying-banner">
            🚨 <strong>Aegis Shield Warning:</strong> Cyberbullying text detected in your messaging feed! <br>
            Censoring, hiding, and blurring message bubble: <em>"{raw_text[:60]}"</em><br>
            <strong>Automatic permanent deletion & alert audit in: {sec_left} seconds</strong>
        </div>
        """, unsafe_allow_html=True)
        # Force redraw to handle live ticking
        time.sleep(0.9)
        st.rerun()

# ══════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,240,255,0.15); padding-bottom: 0.8rem; margin-bottom: 1.5rem;">
    <div>
        <h1 style="margin: 0; color: #e2e8f0; font-size: 1.7rem;">💬 Cyberbullying App WhatsApp</h1>
        <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #64748b;">
            Aegis AI Shield &bull; Real-Time CSS Blurring &bull; 10s Countdown Auto-Delete &bull; 3D WebGL Analytics
        </p>
    </div>
    <div style="background: rgba(0, 240, 255, 0.1); border: 1px solid #00f0ff; color: #00f0ff; border-radius: 30px; padding: 4px 14px; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
        Aegis OS V4.2
    </div>
</div>
""", unsafe_allow_html=True)


# Get details of the active contact
active_c = db.get_contact(st.session_state.active_contact)

# ══════════════════════════════════════════════════════════
#  PAGE 2: DEDICATED PROFILE BEHAVIOR VIEW
# ══════════════════════════════════════════════════════════
if st.session_state.show_profile_page:
    
    # Header bar with back button
    st.markdown('<div class="glass-panel" style="padding: 1rem;">', unsafe_allow_html=True)
    pb_col1, pb_col2 = st.columns([4, 1])
    with pb_col1:
        st.markdown(f"### 👤 {active_c['name']} — Behavior Safety Profile")
    with pb_col2:
        if st.button("← Back to Chat", type="primary", use_container_width=True, key="back_to_chat"):
            st.session_state.show_profile_page = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Core Stats Grid
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("#### Cumulative Behavioral Toxicity Ledger")
    
    grid1, grid2, grid3 = st.columns(3)
    with grid1:
        st.markdown(f"""
        <div class="profile-stats-card" style="border: 1px solid rgba(255, 0, 127, 0.35);">
            <span style="font-size: 3.5rem;">{active_c['avatar']}</span>
            <h3 style="margin-top: 0.8rem; color: #e2e8f0;">{active_c['name']}</h3>
            <span style="background: rgba(0, 240, 255, 0.1); border: 1px solid #00f0ff; color: #00f0ff; border-radius: 30px; padding: 3px 12px; font-size: 10px; font-weight: bold;">
                {'ONLINE' if active_c['is_online'] == 1 else 'OFFLINE'}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
    with grid2:
        st.markdown(f"""
        <div class="profile-stats-card" style="border: 1px solid rgba(255, 0, 127, 0.35); height: 100%;">
            <div style="font-size: 3rem; color: #ff007f; font-weight: bold; margin-top: 1rem;">{active_c['sent_bully_count']}</div>
            <div style="font-size: 0.95rem; color: #cbd5e1; margin-top: 0.5rem; font-weight: 600;">Sent Cyberbullying Warnings</div>
            <p style="font-size: 0.75rem; color: #64748b; margin-top: 0.8rem;">Total harmful or toxic messages dispatched by this contact across dialogue streams.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with grid3:
        st.markdown(f"""
        <div class="profile-stats-card" style="border: 1px solid rgba(255, 215, 0, 0.35); height: 100%;">
            <div style="font-size: 3rem; color: #ffd700; font-weight: bold; margin-top: 1rem;">{active_c['received_bully_count']}</div>
            <div style="font-size: 0.95rem; color: #cbd5e1; margin-top: 0.5rem; font-weight: 600;">Targeted Cyberbullying Count</div>
            <p style="font-size: 0.75rem; color: #64748b; margin-top: 0.8rem;">Total instances where this contact was the recipient of toxic speech or harassment.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"**Composite Toxicity Index:** {int(active_c['toxicity_score']*100)}%")
    st.progress(active_c["toxicity_score"])
    st.markdown("""
    <p style="font-size: 0.75rem; color: #64748b; line-height: 1.45; text-align: justify; margin-top: 0.5rem;">
        *Composite Safety scoring reflects cumulative cyberbullying indicators. Even when toxic dialogues are permanently deleted from chat threads, these counts are permanently logged in the profile ledger to audit personal behavior.*
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3D Visual Helix for Contact History
    st.markdown("---")
    st.markdown("#### Chronological Chat History Spline Tracker")
    history = db.get_chat_history(1, active_c["contact_id"])
    if history:
        st.components.v1.html(get_3d_timeline_helix(history, f"Chronological Spline curve: {active_c['name']}", height=450), height=450)
    else:
        st.info("No timeline events logged. Start a live dialogue stream to populate WebGL spline coordinates.")


# ══════════════════════════════════════════════════════════
#  PAGE 1: MAIN WHATSAPP DIALOGUE & MODERATION HUB
# ══════════════════════════════════════════════════════════
else:
    tab_chat, tab_analytics, tab_alerts = st.tabs([
        "💬 WhatsApp Web Shield",
        "📊 3D Graphics Analytics",
        "🛡️ Moderation Audit Ledger"
    ])

    # ──────────────────────────────────────────────────────────
    #  TAB 1: WHATSAPP WEB SHIELD
    # ──────────────────────────────────────────────────────────
    with tab_chat:
        all_contacts = db.get_all_contacts()
        
        # Unified WhatsApp Layout
        st.markdown('<div class="whatsapp-container">', unsafe_allow_html=True)
        ws_col1, ws_col2 = st.columns([1, 2.5])
        
        # Sidebar with active contacts
        with ws_col1:
            st.markdown('<div style="background: rgba(10,15,28,0.95); height: 74vh; border-right: 1px solid rgba(0,240,255,0.1); padding: 0.5rem;">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin: 0.5rem; color: #00f0ff;">Active Chats</h4>', unsafe_allow_html=True)
            
            for c in all_contacts:
                active_css = "active" if c["contact_id"] == st.session_state.active_contact else ""
                online_dot = "🟢" if c["is_online"] == 1 else "⚫"
                
                # Checkbox button to select contact
                if st.button(f"{c['avatar']} {c['name']} {online_dot}", key=f"btn_c_{c['contact_id']}", use_container_width=True):
                    st.session_state.active_contact = c["contact_id"]
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Active chat window
        with ws_col2:
            
            # Chat Header with creative button to launch Profile Page
            st.markdown('<div style="padding: 0.85rem; background: rgba(16, 24, 43, 0.95); border-bottom: 1px solid rgba(0,240,255,0.1); display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
            
            c_header_left, c_header_right = st.columns([3, 1])
            with c_header_left:
                st.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.3rem; margin-right: 0.5rem;">{active_c['avatar']}</span>
                    <strong style="font-size: 0.95rem; color: #e2e8f0; margin-right: 0.8rem;">{active_c['name']}</strong>
                    <span style="background: rgba(0, 240, 255, 0.1); border: 1px solid #00f0ff; color: #00f0ff; border-radius: 30px; padding: 1px 8px; font-size: 8px; font-weight: bold; text-transform: uppercase;">
                        {'ONLINE' if active_c['is_online'] == 1 else 'OFFLINE'}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
            with c_header_right:
                # CREATIVE PROFILE ACCESS BUTTON (Like WhatsApp live contact detail experience)
                if st.button("👤 View Profile Stats", type="primary", use_container_width=True, key="toggle_profile_stats"):
                    st.session_state.show_profile_page = True
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Message area
            history = db.get_chat_history(1, active_c["contact_id"]) # Aarav is user 1
            
            msg_container = st.container(height=350)
            with msg_container:
                for msg in history:
                    is_me = msg["sender_id"] == 1
                    bubble_class = "sender-bubble" if is_me else "receiver-bubble"
                    
                    if msg["is_deleted"] == 1:
                        st.markdown(f'<div class="chat-bubble {bubble_class} deleted-bubble">🚫 [Message deleted - flagged as cyberbullying]</div>', unsafe_allow_html=True)
                    elif msg["is_toxic"] == 1:
                        st.markdown(f'<div class="chat-bubble {bubble_class} toxic-blurred" title="Hover to view flagged content &bull; Aegis classification: {msg["classification_tag"]}">⚠️ [BLURRED TOXICITY - DELETING] {msg["message_text"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-bubble {bubble_class}">{msg["message_text"]}</div>', unsafe_allow_html=True)
            
            # Input Area
            with st.form("message_send_form", clear_on_submit=True):
                mc1, mc2 = st.columns([4, 1])
                with mc1:
                    user_msg = st.text_input("Type a message...", placeholder="Type message to send...", label_visibility="collapsed")
                with mc2:
                    send_btn = st.form_submit_button("Send 🚀", use_container_width=True)
                
                if send_btn and user_msg:
                    # Classify message in real-time
                    mod = classify_message(user_msg)
                    
                    if mod["is_toxic"]:
                        msg_id = db.save_message(
                            sender_id=1,
                            receiver_id=active_c["contact_id"],
                            message_text=user_msg,
                            original_text=user_msg,
                            is_toxic=1,
                            toxicity_probability=mod["toxicity_probability"],
                            classification_tag=mod["classification_tag"]
                        )
                        db.save_moderation_alert(
                            message_id=msg_id,
                            rule_triggered=f"Toxicity limit breached: {mod['classification_tag']}",
                            severity="High" if mod["toxicity_probability"] > 0.8 else "Medium",
                            action_taken="CSS Blurred & Counted Down"
                        )
                        st.session_state.active_countdown = (msg_id, datetime.now(), user_msg, 1, active_c["contact_id"])
                        st.session_state.trigger_detection_alert = True
                        st.rerun()
                    else:
                        db.save_message(
                            sender_id=1,
                            receiver_id=active_c["contact_id"],
                            message_text=user_msg,
                            original_text=user_msg,
                            is_toxic=0,
                            toxicity_probability=mod["toxicity_probability"],
                            classification_tag="Safe"
                        )
                        st.rerun()
                        
        st.markdown('</div>', unsafe_allow_html=True)

        # Simulated Live Message Feed Trigger
        st.markdown("---")
        sim_col1, sim_col2 = st.columns([3, 1])
        with sim_col1:
            st.markdown("**Simulate Live Interactive Dialogue Stream**")
            st.write("Triggering the stream will simulate active, real-time WhatsApp dialogue ticks between Aarav, Priya, Rohan, and Kabir. Toxic segments will trigger automatic Aegis AI censors, blurs, and 10s auto-deletes!")
        with sim_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡ Inject Next Chat Stream", type="primary", use_container_width=True):
                total_sim = get_total_dialogue_count()
                if st.session_state.sim_index < total_sim:
                    line = get_dialogue_line(st.session_state.sim_index)
                    mod = classify_message(line["text"])
                    
                    if mod["is_toxic"]:
                        msg_id = db.save_message(
                            sender_id=line["sender_id"],
                            receiver_id=line["receiver_id"],
                            message_text=line["text"],
                            original_text=line["text"],
                            is_toxic=1,
                            toxicity_probability=mod["toxicity_probability"],
                            classification_tag=mod["classification_tag"]
                        )
                        db.save_moderation_alert(
                            message_id=msg_id,
                            rule_triggered=f"Live Stream Flag: {mod['classification_tag']}",
                            severity="High" if mod["toxicity_probability"] > 0.8 else "Medium",
                            action_taken="CSS Blurred & Counted Down"
                        )
                        st.session_state.active_countdown = (msg_id, datetime.now(), line["text"], line["sender_id"], line["receiver_id"])
                        st.session_state.trigger_detection_alert = True
                    else:
                        db.save_message(
                            sender_id=line["sender_id"],
                            receiver_id=line["receiver_id"],
                            message_text=line["text"],
                            original_text=line["text"],
                            is_toxic=0,
                            toxicity_probability=mod["toxicity_probability"],
                            classification_tag="Safe"
                        )
                    
                    st.session_state.sim_index = (st.session_state.sim_index + 1) % total_sim
                    st.rerun()

    # ──────────────────────────────────────────────────────────
    #  TAB 2: 3D GRAPHICS ANALYTICS
    # ──────────────────────────────────────────────────────────
    with tab_analytics:
        st.markdown('<p class="section-header" style="color: #00f0ff;">📊 GPU-Accelerated 3D Visualizer Room</p>', unsafe_allow_html=True)
        stats = db.get_moderation_stats()
        
        ac1, ac2 = st.columns(2)
        with ac1:
            st.markdown("#### 3D Sentiment Constellation")
            st.components.v1.html(get_3d_dashboard_hero(), height=380)
        with ac2:
            st.markdown("#### 3D Volumetric Moderation Columns")
            cat_labels = list(stats["categories"].keys())
            cat_values = list(stats["categories"].values())
            st.components.v1.html(get_3d_bar_chart(cat_labels, cat_values, "Category Volume Grid", height=380), height=380)

    # ──────────────────────────────────────────────────────────
    #  TAB 3: MODERATION AUDIT LEDGER
    # ──────────────────────────────────────────────────────────
    with tab_alerts:
        st.markdown('<p class="section-header" style="color: #ff007f;">🛡️ Relational AI Shield Moderation Logs</p>', unsafe_allow_html=True)
        alerts = db.get_all_alerts()
        
        if alerts:
            df = pd.DataFrame(alerts)
            display_cols = ["alert_id", "sender_name", "receiver_name", "original_text", "toxicity_probability", "rule_triggered", "severity", "action_taken", "timestamp"]
            available = [c for c in display_cols if c in df.columns]
            
            st.dataframe(df[available], use_container_width=True, hide_index=True)
            csv = df[available].to_csv(index=False)
            st.download_button("📥 Export Moderation CSV Ledger", csv, "aegis_moderation_ledger.csv", "text/csv", use_container_width=True)
        else:
            st.info("No moderation alerts currently logged in database audit tables.")
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.expander("⚠️ Danger Zone: Audit Ledger Reset"):
            st.write("Resets all message database indexes, toxic counts, profile behavior statistics, and audit ledgers back to zero.")
            if st.button("Reset Moderation Ledger", type="primary", use_container_width=True):
                db.clear_database()
                st.session_state.sim_index = 0
                st.session_state.active_countdown = None
                st.success("Database fully purged successfully!")
                st.rerun()
