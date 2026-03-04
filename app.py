import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Judô Pro - Login", page_icon="🥋", layout="wide")

# --- 2. SISTEMA DE LOGIN ---
# Inicializa o estado de login
if 'logado' not in st.session_state:
    st.session_state.logado = False

# Função de verificação
def verificar_login():
    st.title("🥋 Sistema Judô Pro")
    st.subheader("🔒 Acesso Restrito")
    
    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar no Sistema")
        
        if submit:
            # ⚠️ ALTERE O USUÁRIO E SENHA AQUI:
            if usuario == "admin" and senha == "judo123":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos. Tente novamente.")

# Se não estiver logado, mostra o login e PARA o código aqui.
if not st.session_state.logado:
    verificar_login()
    st.stop()

# ==========================================
# O CÓDIGO ABAIXO SÓ RODA SE ESTIVER LOGADO
# ==========================================

# --- 3. BANCO DE DADOS ---
DB_ATLETAS = "atletas_v15.csv"
DB_FINANCEIRO = "financeiro_v15.csv"

COLS_A = ["ID", "Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Data_Filiacao"]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Observacao"]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    if not df_a.empty: df_a['ID'] = df_a['ID'].astype(int)
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 4. MENU
