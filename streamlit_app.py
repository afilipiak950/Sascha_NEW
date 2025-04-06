import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import requests
import asyncio
from typing import Dict, List, Optional
import os
import time
import plotly.express as px
import plotly.graph_objects as go

from app.core.config import settings
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.agents.interaction_agent import InteractionAgent
from app.agents.post_draft_agent import PostDraftAgent
from app.agents.connection_agent import ConnectionAgent
from app.agents.hashtag_agent import HashtagAgent
from app.models.interaction import InteractionType

# Konfiguration
st.set_page_config(
    page_title="LinkedIn Agent Orchestrator",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für moderneres Design
st.markdown("""
<style>
    /* Grundlegendes Layout */
    .main {
        background-color: #f8f9fa;
        padding: 1rem;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #0077B5 0%, #00A0DC 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metriken */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #0077B5, #00A0DC);
    }
    
    /* Agent Status */
    .agent-status {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .agent-status:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Progress Bar */
    .progress-bar {
        height: 4px;
        background: #e5e7eb;
        border-radius: 2px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .progress-value {
        height: 100%;
        background: linear-gradient(90deg, #0077B5 0%, #00A0DC 100%);
        border-radius: 2px;
        transition: width 0.5s ease;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .status-badge:hover {
        transform: scale(1.05);
    }
    .status-success {
        background-color: #ecfdf5;
        color: #059669;
    }
    .status-pending {
        background-color: #fffbeb;
        color: #d97706;
    }
    
    /* Activity Feed */
    .activity-feed {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    .activity-item {
        padding: 1rem;
        border-bottom: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    .activity-item:hover {
        background: #f8f9fa;
    }
    .activity-item:last-child {
        border-bottom: none;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #0077B5 0%, #00A0DC 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Inputs */
    .stTextInput>div>div {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div:focus-within {
        border-color: #0077B5;
        box-shadow: 0 0 0 3px rgba(0,119,181,0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        color: #1a1f36;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #f0f7ff;
        border-bottom: 2px solid #0077B5;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1 style="margin: 0;">LinkedIn Agent Orchestrator</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Monitor and control your LinkedIn automation activities.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png", width=50)
    st.title("Agent Hub")
    
    # Navigation
    selected_page = st.selectbox(
        "Navigation",
        ["Dashboard", "Post Agent", "Connection Agent", "Engagement Agent", "Hashtag Monitor", "Schedule"],
        format_func=lambda x: f"{'📊' if x == 'Dashboard' else '📝' if x == 'Post Agent' else '🤝' if x == 'Connection Agent' else '📈' if x == 'Engagement Agent' else '🔍' if x == 'Hashtag Monitor' else '⏰'} {x}"
    )

# Hauptbereich
st.title("Dashboard")
st.markdown("Monitor and control your LinkedIn automation activities.")

# Metriken-Übersicht
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: 600; color: #1a1f36;">12</div>
        <div style="color: #6b7280; font-size: 0.875rem;">Posts Created</div>
        <div style="color: #059669; font-size: 0.875rem;">+3 this week</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: 600; color: #1a1f36;">173</div>
        <div style="color: #6b7280; font-size: 0.875rem;">New Connections</div>
        <div style="color: #059669; font-size: 0.875rem;">+39 this week</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: 600; color: #1a1f36;">254</div>
        <div style="color: #6b7280; font-size: 0.875rem;">Engagement Actions</div>
        <div style="color: #059669; font-size: 0.875rem;">+82 this week</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: 600; color: #1a1f36;">87</div>
        <div style="color: #6b7280; font-size: 0.875rem;">Hashtag Interactions</div>
        <div style="color: #059669; font-size: 0.875rem;">+14 this week</div>
    </div>
    """, unsafe_allow_html=True)

# Agent Status
st.subheader("Agent Status")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="agent-status">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0;">Post Agent</h4>
                <p style="color: #6b7280; margin: 0.5rem 0;">Creates posts on your behalf</p>
            </div>
            <div class="status-badge status-success">Inactive</div>
        </div>
        <div class="progress-bar">
            <div class="progress-value" style="width: 25%;"></div>
        </div>
        <div style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
            1/4 tasks • Last activity: 2024-04-06 10:15 AM
        </div>
    </div>

    <div class="agent-status">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0;">Connection Agent</h4>
                <p style="color: #6b7280; margin: 0.5rem 0;">Finds and connects with relevant profiles</p>
            </div>
            <div class="status-badge status-success">Inactive</div>
        </div>
        <div class="progress-bar">
            <div class="progress-value" style="width: 60%;"></div>
        </div>
        <div style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
            24/40 tasks • Last activity: 2024-04-06 11:30 AM
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="agent-status">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0;">Engagement Agent</h4>
                <p style="color: #6b7280; margin: 0.5rem 0;">Likes and comments on posts</p>
            </div>
            <div class="status-badge status-success">Inactive</div>
        </div>
        <div class="progress-bar">
            <div class="progress-value" style="width: 40%;"></div>
        </div>
        <div style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
            4/10 tasks • Last activity: 2024-04-06 09:45 AM
        </div>
    </div>

    <div class="agent-status">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0;">Hashtag Monitor</h4>
                <p style="color: #6b7280; margin: 0.5rem 0;">Tracks and engages with hashtag content</p>
            </div>
            <div class="status-badge status-success">Inactive</div>
        </div>
        <div class="progress-bar">
            <div class="progress-value" style="width: 80%;"></div>
        </div>
        <div style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
            8/10 tasks • Last activity: 2024-04-06 10:00 AM
        </div>
    </div>
    """, unsafe_allow_html=True)

# Recent Activity
st.subheader("Recent Activity")
st.markdown("""
<div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #e5e7eb;">
    <div style="padding: 1rem; border-bottom: 1px solid #e5e7eb;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #0a66c2;"></div>
            <div style="flex: 1;">
                <div>Created a new post about AI in marketing</div>
                <small style="color: #6b7280;">2024-04-06 10:15 AM</small>
            </div>
            <span class="status-badge status-success">success</span>
        </div>
    </div>
    
    <div style="padding: 1rem; border-bottom: 1px solid #e5e7eb;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #059669;"></div>
            <div style="flex: 1;">
                <div>Connected with 15 marketing professionals</div>
                <small style="color: #6b7280;">2024-04-06 09:30 AM</small>
            </div>
            <span class="status-badge status-success">success</span>
        </div>
    </div>
    
    <div style="padding: 1rem; border-bottom: 1px solid #e5e7eb;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #7c3aed;"></div>
            <div style="flex: 1;">
                <div>Commented on 3 posts about data science</div>
                <small style="color: #6b7280;">2024-04-06 08:45 AM</small>
            </div>
            <span class="status-badge status-success">success</span>
        </div>
    </div>
    
    <div style="padding: 1rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #eab308;"></div>
            <div style="flex: 1;">
                <div>Monitoring #artificialintelligence trends</div>
                <small style="color: #6b7280;">2024-04-06 08:00 AM</small>
            </div>
            <span class="status-badge status-pending">pending</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)