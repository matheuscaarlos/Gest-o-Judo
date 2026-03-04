import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro - Assoc. Roberdrayner", page_icon="🥋", layout="wide")

DB_ATLETAS = "atletas_v14.csv"
DB_FINANCEIRO = "financeiro_v14.csv"

# Definição centralizada de colunas para evitar erros de digitação
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

# --- 2. MENU LATERAL ---
with st.sidebar:
    st.title("🥋 Menu")
    aba = st.radio("Ir para:", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro"])
    st.divider()
    st.caption("v14.0 - Sistema Completo")

# --- 3. DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("📊 Painel Geral")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    c1, c2 = st.columns(2)
    c1.metric("Total Alunos", len(df_a))
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    c2.metric("Receita Total", f"R$ {receita:,.2f}")
    if not df_a.empty:
        import plotly.express as px
        st.plotly_chart(px.pie(df_a, names='Faixa', title="Distribuição por Faixa"), use_container_width=True)

# --- 4. ATLETAS (CADASTRO COMPLETO + EDIÇÃO) ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Alunos")
    
    # NOVO CADASTRO (RECOLHÍVEL)
    with st.expander("➕ Nova Matrícula", expanded=False):
        with st.form("form_novo_v14"):
            nome = st.text_input("Nome Completo*")
            c1, c2, c3 = st.columns(3)
            cpf, rg, peso = c1.text_input("CPF"), c2.text_input("RG"), c3.number_input("Peso (kg)", 0.0)
            c4, c5 = st.columns(2)
            tel, email = c4.text_input("Telefone"), c5.text_input("Email")
            end = st.text_input("Endereço Completo")
            c6, c7 = st.columns(2)
            faixa = c6.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            val = c7.number_input("Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo_reg = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "CPF": cpf, "RG": rg, "Peso": peso,
                        "Faixa": faixa, "Endereco": end, "Telefone": tel, "Email": email,
                        "Status": "Ativo", "Mensalidade": val, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")
                    }])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_reg], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Matrícula Realizada!"); st.rerun()

    # BUSCA E EDIÇÃO (RECOLHÍVEL)
    with st.expander("🔍 Pesquisar e Editar", expanded=True):
        busca = st.text_input("Filtrar por nome")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
        st.dataframe(df_res[["ID", "
