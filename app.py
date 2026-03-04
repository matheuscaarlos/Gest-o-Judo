import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro - Estável", page_icon="🥋", layout="wide")

DB_ATLETAS = "atletas_v10.csv"
DB_FINANCEIRO = "financeiro_v10.csv"

# Definição das colunas em variáveis para evitar linhas gigantes
COLS_ATLETA = [
    "ID", "Nome", "CPF", "RG", "Peso", "Faixa", 
    "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Data_Filiacao"
]
COLS_FIN = [
    "ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", 
    "Data_Pagamento", "Metodo", "Detalhe_Misto"
]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_ATLETA)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_FIN)
    if not df_a.empty: 
        df_a['ID'] = df_a['ID'].astype(int)
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 2. MENU ---
with st.sidebar:
    st.header("🥋 Menu Principal")
    aba = st.radio("Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"])

# --- 3. DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("📊 Painel Administrativo")
    df_a = st.session_state.atletas_df
    st.metric("Total de Alunos", len(df_a))
    if not df_a.empty:
        st.plotly_chart(px.pie(df_a, names='Faixa', title="Distribuição por Faixa"), use_container_width=True)

# --- 4. GESTÃO DE ATLETAS (CORRIGIDO) ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    
    with st.expander("➕ Nova Matrícula", expanded=False):
        with st.form("form_novo"):
            n_nome = st.text_input("Nome Completo*")
            c1, c2, c3 = st.columns(3)
            n_cpf, n_rg, n_peso = c1.text_input("CPF"), c2.text_input("RG"), c3.number_input("Peso (kg)", 0.0)
            c4, c5 = st.columns(2)
            n_tel, n_email = c4.text_input("WhatsApp"), c5.text_input("Email")
            n_end = st.text_input("Endereço")
            c6, c7 = st.columns(2)
            n_faixa = c6.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            n_valor = c7.number_input("Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Salvar Matrícula"):
                if n_nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    data_f = datetime.now().strftime("%d/%m/%Y")
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": n_nome, "CPF": n_cpf, "RG": n_rg, "Peso": n_peso,
                        "Faixa": n_faixa, "Endereco": n_end, "Telefone": n_tel, "Email": n_email,
                        "Status": "Ativo", "Mensalidade": n_valor, "Data_Filiacao": data_f
                    }])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Cadastrado!"); st.rerun()

    with st.expander("🔍 Pesquisar / Editar / Excluir", expanded=True):
        busca = st.text_input("Buscar por nome...")
        df_f = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
        st.dataframe(df_f[["ID", "Nome", "Faixa", "Telefone", "Status"]], use_container_width=True, hide_index=True)
        
        if not df_f.empty:
            st.divider()
            escolha = st.selectbox("Selecione para editar:", [f"{r['Nome']} (ID: {r['ID']
