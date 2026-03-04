import streamlit as st
import pandas as pd
import os
import time
import hashlib
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
st.set_page_config(page_title="Judô Pro | Gestão Administrativa", page_icon="🥋", layout="wide")

# --- 2. CAMADA DE ESTILO (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    div[data-testid="metric-container"] {
        background-color: #FFFFFF; border: 1px solid #E2E8F0;
        padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        border-radius: 10px; font-weight: 600;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white; border: none; padding: 0.7rem;
        transition: 0.3s all;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3); }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE HASH ---
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(user_input, senha_hash):
    return hash_senha(user_input) == senha_hash

# --- 4. BANCO DE DADOS ---
class DBManager:
    DB_A = "atleta
