"""
Cyberbullying App WhatsApp - Real-Time AI Moderation Dashboard.
Sleek dark-mode WhatsApp Web Clone with glassmorphic stylings,
real-time message blurring, 10s auto-delete countdowns, and WebGL charts.
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
from modules.three_visualizations import get_3d_dashboard_hero, get_3d_bar_chart, get_3d_pie_chart, get_3d_timeline_helix

# Page Configurations
st.set_page_config(
    page_title="Cyberbullying App WhatsApp",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZER
# ══════════════════════════════════════════════════════════
if "active_contact" not in st.session_state:
    st.session_state.active_contact = 1  # Aarav Sharma by default
if "sim_index" not in st.session_state:
    st.session_state.sim_index = 0
if "active_countdown" not in st.session_state:
    st.session_state.active_countdown = None  # holds (message_id, start_time, original_text)

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
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
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

.whatsapp-sidebar {
    width: 320px;
    background: rgba(10, 15, 28, 0.95);
    border-right: 1px solid rgba(0, 240, 255, 0.1);
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    padding: 1rem;
    background: rgba(16, 24, 43, 0.8);
    border-bottom: 1px solid rgba(0, 240, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.contact-item {
    display: flex;
    align-items: center;
    padding: 0.85rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    cursor: pointer;
    transition: all 0.25s ease;
}
.contact-item:hover {
    background: rgba(0, 240, 255, 0.05);
}
.contact-item.active {
    background: rgba(0, 240, 255, 0.1);
    border-left: 3px solid #00f0ff;
}

.contact-avatar {
    font-size: 1.5rem;
    margin-right: 0.85rem;
}

.contact-info {
    flex-grow: 1;
}

.contact-name {
    font-weight: 600;
    font-size: 0.9rem;
    color: #e2e8f0;
}

.contact-status {
    font-size: 0.75rem;
    color: #00f0ff;
}

/* Chat Bubbles */
.chat-window {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    background: radial-gradient(circle at 50% 50%, #0d131f 0%, #05080f 100%);
}

.chat-header {
    padding: 1rem;
    background: rgba(16, 24, 43, 0.85);
    border-bottom: 1px solid rgba(0, 240, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.message-area {
    flex-grow: 1;
    padding: 1.5rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
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
    padding: 1rem;
    text-align: center;
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
</style>
""", unsafe_allow_html=True)

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
#  TABS ASSEMBLY
# ══════════════════════════════════════════════════════════
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
    
    # Grid layout: WhatsApp interface left, active profile stats right
    chat_grid_left, profile_grid_right = st.columns([2.5, 1])

    with chat_grid_left:
        # Construct the unified WhatsApp layout
        st.markdown('<div class="whatsapp-container">', unsafe_allow_html=True)
        
        # We handle layout through Streamlit Columns inside Tab
        ws_col1, ws_col2 = st.columns([1, 2.5])
        
        # Sidebar with active contacts
        with ws_col1:
            st.markdown('<div style="background: rgba(10,15,28,0.95); height: 74vh; border-right: 1px solid rgba(0,240,255,0.1); padding: 0.5rem;">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin: 0.5rem; color: #00f0ff;">Active Chats</h4>', unsafe_allow_html=True)
            
            for c in all_contacts:
                active_css = "active" if c["contact_id"] == st.session_state.active_contact else ""
                online_dot = "🟢" if c["is_online"] == 1 else "⚫"
                
                # Checkbox / button to select contact
                if st.button(f"{c['avatar']} {c['name']} {online_dot}", key=f"btn_c_{c['contact_id']}", use_container_width=True):
                    st.session_state.active_contact = c["contact_id"]
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Active chat window
        with ws_col2:
            active_c = db.get_contact(st.session_state.active_contact)
            
            # Header
            st.markdown(f"""
            <div style="padding: 0.85rem; background: rgba(16, 24, 43, 0.95); border-bottom: 1px solid rgba(0,240,255,0.1); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-size: 1.3rem; margin-right: 0.5rem;">{active_c['avatar']}</span>
                    <strong style="font-size: 0.95rem; color: #e2e8f0;">{active_c['name']}</strong>
                </div>
                <div style="font-size: 0.75rem; color: #64748b;">
                    Toxicity Index: <span style="color: {'#ff007f' if active_c['toxicity_score'] > 0 else '#00f0ff'}; font-weight: bold;">{int(active_c['toxicity_score']*100)}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
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
                        # Save in DB as toxic/blurred
                        msg_id = db.save_message(
                            sender_id=1,
                            receiver_id=active_c["contact_id"],
                            message_text=user_msg,
                            original_text=user_msg,
                            is_toxic=1,
                            toxicity_probability=mod["toxicity_probability"],
                            classification_tag=mod["classification_tag"]
                        )
                        # Save moderation alert trigger
                        db.save_moderation_alert(
                            message_id=msg_id,
                            rule_triggered=f"Toxicity limit breached: {mod['classification_tag']}",
                            severity="High" if mod["toxicity_probability"] > 0.8 else "Medium",
                            action_taken="CSS Blurred & Counted Down"
                        )
                        # Start 10 seconds auto-delete countdown
                        st.session_state.active_countdown = (msg_id, datetime.now(), user_msg, 1, active_c["contact_id"])
                        st.rerun()
                    else:
                        # Save safe message
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

    # Active profile statistics dashboard panel (Right)
    with profile_grid_right:
        active_c = db.get_contact(st.session_state.active_contact)
        st.markdown('<p class="section-header" style="color: #ffd700; font-size: 0.95rem;">👤 Behavior Profile Card</p>', unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 3rem;">{active_c['avatar']}</span>
                <h3 style="margin: 0.5rem 0 0.2rem 0; color: #e2e8f0;">{active_c['name']}</h3>
                <span style="background: rgba(0, 240, 255, 0.1); border: 1px solid #00f0ff; color: #00f0ff; border-radius: 30px; padding: 2px 10px; font-size: 10px; font-weight: bold;">
                    {'ONLINE' if active_c['is_online'] == 1 else 'OFFLINE'}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"""
                <div class="profile-stats-card" style="border-color: rgba(255, 0, 127, 0.25);">
                    <div style="font-size: 1.5rem; color: #ff007f; font-weight: bold;">{active_c['sent_bully_count']}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Sent Toxicity</div>
                </div>
                """, unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                <div class="profile-stats-card" style="border-color: rgba(255, 215, 0, 0.25);">
                    <div style="font-size: 1.5rem; color: #ffd700; font-weight: bold;">{active_c['received_bully_count']}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Targeted Toxicity</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Toxicity Index:** {int(active_c['toxicity_score']*100)}%")
            st.progress(active_c["toxicity_score"])
            st.markdown("""
            <p style="font-size: 0.7rem; color: #64748b; line-height: 1.45; text-align: justify; margin-top: 0.5rem;">
                *Behavior indexing accumulates all attempted, blurred, and successfully moderated cyberbullying events permanently to profile toxic habits.*
            </p>
            """, unsafe_allow_html=True)

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
                
                # Classify simulated message
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
                
                # Increment index
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
        # Gather metrics from database
        cat_labels = list(stats["categories"].keys())
        cat_values = list(stats["categories"].values())
        st.components.v1.html(get_3d_bar_chart(cat_labels, cat_values, "Category Volume Grid", height=380), height=380)

    # 3D Double Helix Message Timeline Tracker
    st.markdown("---")
    st.markdown("#### 3D Chronological Message Helix")
    all_msgs = db.get_chat_history(1, st.session_state.active_contact)
    if all_msgs:
        st.components.v1.html(get_3d_timeline_helix(all_msgs, "Chronological Chat Strand", height=450), height=450)
    else:
        st.info("No active chat history loaded. Type a message or inject simulated ticks to generate visual data spline curves.")

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
        
        # Custom style highlighting for the dataframe
        st.dataframe(df[available], use_container_width=True, hide_index=True)
        
        # Download ledger CSV
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
