import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- GERENCIAMENTO DE ARQUIVOS (DATABASE) ---
DB_ATLETAS = "atletas_v5.csv"
DB_FINANCEIRO = "financeiro_v5.csv"

def load_data():
    cols_atleta = ["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao", "CPF", "RG", "Telefone", "Endereco", "Peso", "Sangue"]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    
    # Carregar ou Criar Atletas
    if os.path.exists(DB_ATLETAS):
        df = pd.read_csv(DB_ATLETAS)
        for col in cols_atleta:
            if col not in df.columns: df[col] = "N/I"
    else:
        df = pd.DataFrame(columns=cols_atleta)
        
    # Carregar ou Criar Financeiro
    if os.path.exists(DB_FINANCEIRO):
        df_fin = pd.read_csv(DB_FINANCEIRO)
        for col in cols_fin:
            if col not in df_fin.columns: df_fin[col] = ""
    else:
        df_fin = pd.DataFrame(columns=cols_fin)
            
    return df, df_fin

def save_data(atleta_df, fin_df):
    atleta_df.to_csv(DB_ATLETAS, index=False)
    fin_df.to_csv(DB_FINANCEIRO, index=False)

# Inicializar Estado da Sessão
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    if os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>Assoc. Roberdrayner Martins</h2>", unsafe_allow_html=True)
    st.divider()
    aba = st.radio("Menu de Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"], key="nav_main_final")

# --- 🏠 DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel de Controle Principal")
    df_a = st.session_state.atletas_df
    df_f = st.session_state.fin_df
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Alunos Matriculados", len(df_a))
    
    receita_total = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    m2.metric("Receita Total (Histórico)", f"R$ {receita_total:,.2f}")
    
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    m3.metric("Judocas Ativos", ativos)

    if not df_a.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_faixa = px.pie(df_a, names='Faixa', title="Distribuição por Graduação", hole=.4)
            st.plotly_chart(fig_faixa, use_container_width=True)
        with col_g2:
            if not df_f.empty:
                fig_fin = px.bar(df_f, x='Mes_Ref', y='Valor_Total', color='Metodo', title="Entradas Mensais")
                st.plotly_chart(fig_fin, use_container_width=True)

# --- 🥋 GESTÃO DE ATLETAS ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    t1, t2 = st.tabs(["➕ Nova Matrícula", "📝 Editar / Excluir"])
    
    with t1:
        with st.form(key="form_cadastro_final"):
            nome_n = st.text_input("Nome Completo*")
            col_a, col_b = st.columns(2)
            faixa_n = col_a.selectbox("Faixa Atual", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor_n = col_b.number_input("Valor Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Confirmar Matrícula"):
                if nome_n:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    nova_linha = pd.DataFrame([[new_id, nome_n, faixa_n, "Ativo", valor_n, datetime.now().strftime("%d/%m/%Y"), "-", "-", "-", "-", 0.0, "N/I"]], 
                                               columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, nova_linha], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"Judoca {nome_n} matriculado com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, preencha o nome.")

    with t2:
        if st.session_state.atletas_df.empty:
            st.info("Nenhum atleta cadastrado.")
        else:
            pesquisa = st.text_input("🔍 Buscar Atleta para Edição")
            df_res = st.session_state.atletas
