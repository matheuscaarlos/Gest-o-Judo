import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- BANCO DE DADOS ---
DB_ATLETAS = "atletas_v5.csv"
DB_FINANCEIRO = "financeiro_v5.csv"

def load_data():
    cols_atleta = ["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao", "CPF", "RG", "Telefone", "Endereco", "Peso", "Sangue"]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    
    df = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=cols_atleta)
    df_fin = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=cols_fin)
    
    for c in cols_atleta: 
        if c not in df.columns: df[c] = "N/I"
    for c in cols_fin: 
        if c not in df_fin.columns: df_fin[c] = ""
            
    return df, df_fin

def save_data(atleta_df, fin_df):
    atleta_df.to_csv(DB_ATLETAS, index=False)
    fin_df.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    st.markdown("### Associação Roberdrayner Martins")
    st.divider()
    aba = st.radio("Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"], key="nav_main_v54")

# --- DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel Administrativo")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Judocas Matriculados", len(df_a))
    receita_val = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    c2.metric("Receita Total Acumulada", f"R$ {receita_val:,.2f}")
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    c3.metric("Alunos Ativos", ativos)

    if not df_a.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_faixa = px.pie(df_a, names='Faixa', title="Distribuição por Graduação", hole=.4)
            st.plotly_chart(fig_faixa, use_container_width=True)
        with col_g2:
            if not df_f.empty:
                fig_fin = px.bar(df_f, x='Mes_Ref', y='Valor_Total', color='Metodo', title="Entradas Mensais")
                st.plotly_chart(fig_fin, use_container_width=True)

# --- GESTÃO DE ATLETAS ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Alunos")
    tab1, tab2 = st.tabs(["➕ Matrícula", "🔍 Editar / Excluir"])
    
    with tab1:
        with st.form(key="form_matricula_v54"):
            nome_n = st.text_input("Nome Completo*")
            c_a, c_b = st.columns(2)
            faixa_n = c_a.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor_n = c_b.number_input("Valor Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome_n:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo_aluno = pd.DataFrame([[new_id, nome_n, faixa_n, "Ativo", valor_n, datetime.now().strftime("%d/%m/%Y"), "-", "-", "-", "-", 0.0, "N/I"]], 
                                              columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_aluno], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"Atleta {nome_n} cadastrado!")
                    st.rerun()

    with tab2:
        pesquisa = st.text_input("🔍 Pesquisar por nome...")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(pesquisa, case=False)]
        st.dataframe(df_res, use_container_width=True, hide_index=True)
        
        if not df_res.empty:
            st.divider()
            atleta_selec = st.selectbox("Escolha um aluno para alterar:", df_res['Nome'].tolist(), key="sel_atleta_edit")
            idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == atleta_selec].index[0]
            
            with st.form(key="form_edicao_final"):
                # CORREÇÃO DA LINHA 100 AQUI: Colchetes fechados corretamente
                e_nome = st.text_input("Alterar Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                e_mensal = st.number_input("Alterar Valor Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if st.session_state.atletas_df.at[idx, 'Status'] == "Ativo" else 1)
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.atletas_df.at[idx, 'Nome'] = e_nome
                    st.session_state.atletas_df.at[idx, 'Mensalidade'] = e_mensal
                    st.session_state.atletas_df.at[idx, 'Status'] = e_status
                    save_data(st.session_state.atletas_df, st.session_state.fin_df
