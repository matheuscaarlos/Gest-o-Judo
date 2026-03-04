import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

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
    st.title("🥋 Menu Principal")
    aba = st.radio("Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"], key="nav_main")

# --- 🏠 DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel Administrativo")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    # Criando colunas específicas para esta seção
    m1, m2, m3 = st.columns(3)
    m1.metric("Alunos Matriculados", len(df_a))
    receita_total = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    m2.metric("Receita Acumulada", f"R$ {receita_total:,.2f}")
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    m3.metric("Judocas Ativos", ativos)

    if not df_a.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.plotly_chart(px.pie(df_a, names='Faixa', title="Distribuição por Faixa"), use_container_width=True)
        with col_g2:
            if not df_f.empty:
                st.plotly_chart(px.bar(df_f, x='Mes_Ref', y='Valor_Total', title="Faturamento por Mês"), use_container_width=True)

# --- 🥋 ATLETAS ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Alunos")
    t1, t2 = st.tabs(["➕ Matrícula", "📝 Editar/Excluir"])
    
    with t1:
        with st.form("form_novo"):
            nome_n = st.text_input("Nome Completo*")
            col_a, col_b = st.columns(2)
            faixa_n = col_a.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor_n = col_b.number_input("Mensalidade (R$)", value=150.0)
            if st.form_submit_button("Finalizar Matrícula"):
                if nome_n:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([[new_id, nome_n, faixa_n, "Ativo", valor_n, datetime.now().strftime("%d/%m/%Y"), "-", "-", "-", "-", 0.0, "N/I"]], columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Matrícula realizada!")
                    st.rerun()

    with t2:
        if not st.session_state.atletas_df.empty:
            pesquisa = st.text_input("🔍 Pesquisar por nome")
            df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(pesquisa, case=False)]
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            
            aluno_edit = st.selectbox("Selecione para editar:", df_res['Nome'].tolist())
            idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_edit].index[0]
            
            with st.form("form_edit"):
                enome = st.text_input("Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                evalor = st.number_input("Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                if st.form_submit_button("Salvar Alterações"):
                    st.session_state.atletas_df.at[idx, 'Nome'] = enome
                    st.session_state.atletas_df.at[idx, 'Mensalidade'] = evalor
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Atualizado!")
                    st.rerun()

# --- 💰 FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💸 Fluxo de Caixa")
    
    with st.expander("💳 Registrar Recebimento", expanded=True):
        if not st.session_state.atletas_df.empty:
            # CORREÇÃO DO NAMEERROR: Definindo c1 e c2 especificamente para esta aba
            f1, f2 = st.columns(2)
            aluno_p = f1.selectbox("Atleta", st.session_state.atletas_df['Nome'].tolist())
            data_p = f2.date_input("Data do Pagamento",
