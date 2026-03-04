import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date

# --- 1. CONFIGURAÇÃO DE TEMA E CORES ---
st.set_page_config(page_title="Judô Pro | Enterprise", page_icon="🥋", layout="wide")

st.markdown("""
    <style>
    /* Importação de Fonte Moderna */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    :root {
        --primary: #2563EB;
        --sidebar: #0F172A;
        --background: #F8FAFC;
        --text-dark: #1E293B;
        --success: #10B981;
        --danger: #E11D48;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Background Geral */
    .stApp { background-color: var(--background); }

    /* Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar) !important;
        border-right: 1px solid #1E293B;
    }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
    
    /* Títulos e Textos */
    h1, h2, h3 { color: var(--text-dark) !important; font-weight: 700 !important; }

    /* Cards de Métricas Estilizados */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        padding: 1.5rem !important;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricValue"] { color: var(--primary) !important; font-weight: 700; }

    /* Botões Primários */
    .stButton>button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border-radius: 10px;
        border: none;
        height: 3.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
        color: white;
    }

    /* Botão de Estorno (Danger) */
    .btn-estorno > div > button {
        background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%) !important;
        border: none !important;
    }

    /* Tabs (Abas) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F5F9;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: var(--primary) !important;
        font-weight: 700;
        border-bottom: 2px solid var(--primary) !important;
    }

    /* Dataframes e Tabelas */
    .stDataFrame {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. EXEMPLO DE APLICAÇÃO NOS MÓDULOS ---

# No Módulo Financeiro, use a classe de cor para o estorno:
# st.markdown('<div class="btn-estorno">', unsafe_allow_html=True)
# if st.button("Confirmar Estorno"):
#     ...
# st.markdown('</div>', unsafe_allow_html=True)

# No Dashboard, as métricas já herdam o estilo:
st.title("🥋 Dashboard Estratégico")
c1, c2, c3 = st.columns(3)
c1.metric("Alunos Ativos", "142", "+5% cresc.")
c2.metric("Receita Mensal", "R$ 21.300,00", "Dentro da meta")
c3.metric("Inadimplência", "2.1%", "-0.4% queda", delta_color="inverse")

st.divider()

# Exemplo de Abas Modernas
t1, t2 = st.tabs(["📊 Gráficos", "📋 Listagem"])
with t1:
    st.info("As abas agora possuem contraste elevado para facilitar a navegação.")
