import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(page_title="Judô Pro | Gestão Roberdrayner", page_icon="🥋", layout="wide")

# --- 2. DESIGN SYSTEM (CSS PROFISSIONAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F1F5F9; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    div[data-testid="metric-container"] {
        background-color: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #E2E8F0;
    }
    .stButton>button { border-radius: 8px; font-weight: 600; background-color: #2563EB; color: white; height: 3em; }
    .stTabs [data-baseweb="tab"] { font-weight: 700; color: #475569; }
    </style>
""", unsafe_allow_html=True)

# --- 3. GESTÃO DE DADOS ---
DB_ATLETAS = "atleta_v24.csv"
DB_FINANCEIRO = "fin_v24.csv"

COLS_A = ["ID", "Nome", "Data_Nascimento", "Genero", "Faixa", "Responsavel", "Telefone", "Status", "Mensalidade", "Dia_Vencimento", "Obs_Medicas", "Data_Filiacao"]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo"]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    for col in COLS_A:
        if col not in df_a.columns: df_a[col] = ""
    return df_a, df_f

def save_data(df_a, df_f):
