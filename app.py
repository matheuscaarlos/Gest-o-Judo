import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- GERENCIAMENTO DE ARQUIVOS ---
DB_ATLETAS = "atletas_v5.csv"
DB_FINANCEIRO = "financeiro_v5.csv"

def load_data():
    cols_atleta = ["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao", "CPF", "RG", "Telefone", "Endereco", "Peso", "Sangue"]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    
    if os.path.exists(DB_ATLETAS):
        df = pd.read_csv(DB_ATLETAS)
        for col in cols_atleta:
            if col not in df.columns: df[col] = "N/I"
    else:
        df = pd.DataFrame(columns=cols_atleta)
        
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

# Inicializar Estado da Sessão - ATENÇÃO AOS NOMES DAS CHAVES
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Assoc. Roberdrayner Martins</h2>", unsafe_allow_html=True)
    st.divider()
    aba = st.radio("Menu", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"], key="nav_v56")

# --- 🏠 DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel Administrativo")
    df_a = st.session_state.atletas_df
    df_f = st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Alunos", len(df_a))
    receita_total = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    c2.metric("Receita Acumulada", f"R$ {receita_total:,.2f}")
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    c3.metric("Ativos", ativos)

    if not df_a.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(df_a, names='Faixa', title="Faixas"), use_container_width=True)
        with col2:
            if not df_f.empty:
                st.plotly_chart(px.bar(df_f, x='Mes_Ref', y='Valor_Total', title="Mensalidades"), use_container_width=True)

# --- 🥋 ATLETAS ---
elif aba == "🥋 Atletas":
    st.title("👥 Alunos")
    t1, t2 = st.tabs(["➕ Novo", "📝 Editar/Excluir"])
    
    with t1:
        with st.form("form_novo_v56"):
            nome = st.text_input("Nome*")
            col_a, col_b = st.columns(2)
            faixa = col_a.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = col_b.number_input("Mensalidade (R$)", value=150.0)
            if st.form_submit_button("Cadastrar"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    nova_row = pd.DataFrame([[new_id, nome, faixa, "Ativo", valor, datetime.now().strftime("%d/%m/%Y"), "-", "-", "-", "-", 0.0, "N/I"]], columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, nova_row], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Cadastrado!")
                    st.rerun()

    with t2:
        if not st.session_state.atletas_df.empty:
            busca = st.text_input("🔍 Buscar por nome")
            # CORREÇÃO AQUI: Usando o nome correto st.session_state.atletas_df
            df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            
            if not df_res.empty:
                aluno_ed = st.selectbox("Selecione para editar", df_res['Nome'].tolist())
                idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_ed].index[0]
                
                with st.form("form_edicao_v56"):
                    enome = st.text_input("Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                    evalor = st.number_input("Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                    if st.form_submit_button("Salvar"):
                        st.session_state.atletas_df.at[idx, 'Nome'] = enome
                        st.session_state.atletas_df.at[idx, 'Mensalidade'] = evalor
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.success("Atualizado!")
                        st.rerun()
                    if st.form_submit_button("🗑️ Excluir"):
                        st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.rerun()

# --- 💰 FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💸 Caixa")
    df_a = st.session_state.atletas_df
    
    with st.expander("💳 Registrar Pagamento", expanded=True):
        if not df_a.empty:
            c1, c2
