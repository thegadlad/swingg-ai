# dashboard.py (Final Secure & Feature-Complete Version)

import streamlit as st
import os
import glob
import json
from universes import NIFTY_50, NIFTY_MIDCAP_100, HIGH_LIQUIDITY_SMALLCAPS
from moderator import run_moderator_session
from tools import get_full_analysis

# --- Page Configuration ---
st.set_page_config(page_title="Swingg AI", page_icon="📈", layout="wide")

# --- Securely Load API Keys ---
# This is the single source of truth for secrets in our app
if 'GOOGLE_API_KEY' not in os.environ:
    try:
        os.environ['GOOGLE_API_KEY'] = st.secrets["GEMINI_API_KEY"]
    except Exception as e:
        st.error(f"Error loading Gemini API key: {e}. Make sure it's in your .streamlit/secrets.toml file.")

# --- ADVANCED CSS FOR A PROFESSIONAL LOOK ---
st.markdown("""
    <style>
        .main-content {
            max-width: 900px;
            margin: auto;
        }
        .stExpander {
            border: 1px solid #333 !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2) !important;
            padding: 10px !important;
            margin-bottom: 20px;
        }
        .stExpander header {
            font-size: 1.25rem;
            font-weight: bold;
        }
        h1, h3 { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER & INTRO ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.title("Swingg AI")
st.subheader("Your Conversational Multi-Agent Trading Ecosystem", divider="rainbow")

# --- Function to display the validation report ---
def display_validation_report():
    st.header("Validation of Previous Day's Watchlist", divider="gray")
    list_of_files = glob.glob('watchlist_*.json')
    if not list_of_files:
        st.info("No previous watchlist found to validate.")
        return

    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        previous_results = json.load(f)
    
    previous_watchlist = previous_results.get('watchlist_candidates', [])
    if not previous_watchlist:
        st.write(f"Previous watchlist from `{os.path.basename(latest_file)}` was empty.")
        return

    for stock in previous_watchlist:
        with st.expander(f"{stock['ticker']} ({stock['name']})"):
            current_analysis = get_full_analysis(stock['ticker'])
            if not current_analysis:
                st.error("Could not retrieve current data.")
                continue
            
            status, details = "Signal Intact", "Conditions remain similar."
            if current_analysis['passes_volume']:
                status, details = "✅ Signal Strengthened", "Volume breakout detected!"
            elif not current_analysis['passes_sma'] or not current_analysis['passes_rsi']:
                status, details = "❌ Signal Weakened", "Trend or momentum has broken down."
            
            st.markdown(f"**Status:** {status} <br> **Details:** *{details}*", unsafe_allow_html=True)

# --- Main App Logic ---
if 'new_reports' not in st.session_state:
    st.session_state.new_reports = []
if 'validation_run' not in st.session_state:
    st.session_state.validation_run = False

if st.button("Find Today's Opportunities", type="primary"):
    st.session_state.validation_run = True
    with st.spinner("Agent is running... This may take several minutes."):
        combined_universe = NIFTY_50 + NIFTY_MIDCAP_100 + HIGH_LIQUIDITY_SMALLCAPS
        unique_stocks = sorted(list(set(combined_universe)))
        st.session_state.new_reports = run_moderator_session(unique_stocks)

# --- Display Reports ---
if st.session_state.validation_run:
    display_validation_report()

    if st.session_state.new_reports:
        st.header("Today's New High-Priority Watchlist", divider="gray")
        for report in st.session_state.new_reports:
            with st.expander(f"{report['ticker']} ({report['name']})"):
                targets = report['targets']
                sma_20 = report['sma_20']
                col1, col2, col3 = st.columns(3)
                col1.metric(label="Stop-Loss (20-day SMA)", value=f"₹{sma_20:.2f}")
                col2.metric(label="Price Target 1", value=targets.get('target_1', 'N/A'))
                col3.metric(label="Price Target 2", value=targets.get('target_2', 'N/A'))
                st.markdown("---")
                st.markdown("### AI Debate & Analysis")
                st.markdown(report['report'])
    else:
        st.info("No new stocks met the criteria today.")

st.markdown('</div>', unsafe_allow_html=True)