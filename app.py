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
    
    # Garantir colunas novas
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

# --- SIDEBAR (Menu principal com chave única para evitar erro de ID) ---
with st.sidebar:
    if os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    st.markdown("### Associação Roberdrayner Martins")
    st.divider()
    # Adicionada a chave única 'key="menu_principal"' para resolver o erro de ID
    aba = st.radio("Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"], key="menu_principal")

# --- DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Dashboard Institucional")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Judocas Matriculados", len(df_a))
    
    receita_total = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    c2.metric("Receita Acumulada", f"R$ {receita_total:,.2f}")
    
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    c3.metric("Atletas Ativos", ativos)

    if not df_a.empty:
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            fig_faixa = px.pie(df_a, names='Faixa', title="Censo de Graduações", hole=.4)
            st.plotly_chart(fig_faixa, use_container_width=True)
        with col_graf2:
            if not df_f.empty:
                fig_fin = px.bar(df_f, x='Mes_Ref', y='Valor_Total', color='Metodo', title="Entradas por Mês")
                st.plotly_chart(fig_fin, use_container_width=True)

# --- GESTÃO DE ATLETAS ---
elif aba == "🥋 Atletas":
    st.title("👥 Controle de Alunos")
    tab1, tab2 = st.tabs(["➕ Novo Cadastro", "🔍 Pesquisa e Edição"])
    
    with tab1:
        with st.form("form_novo_atleta", clear_on_submit=True):
            n = st.text_input("Nome Completo*")
            col_a, col_b = st.columns(2)
            f = col_a.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            v = col_b.number_input("Mensalidade (R$)", value=150.0)
            if st.form_submit_button("Matricular Atleta"):
                if n:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo_row = pd.DataFrame([[new_id, n, f, "Ativo", v, datetime.now().strftime("%d/%m/%Y"), "-", "-", "-", "-", 0.0, "N/I"]], columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_row], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"Oss! {n} matriculado.")
                    st.rerun()

    with tab2:
        busca = st.text_input("🔍 Buscar Atleta por Nome")
        df_busca = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
        st.dataframe(df_busca, use_container_width=True, hide_index=True)
        
        if not df_busca.empty:
            sel_atleta = st.selectbox("Selecione para Editar ou Excluir", df_busca['Nome'].tolist(), key="sel_edit")
            idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == sel_atleta].index[0]
            with st.form("edit_form"):
                enome = st.text_input("Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                evalor = st.number_input("Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                c_edit1, c_edit2 = st.columns(2)
                if c_edit1.form_submit_button("💾 Salvar"):
                    st.session_state.atletas_df.at[idx, 'Nome'] = enome
                    st.session_state.atletas_df.at[idx, 'Mensalidade'] = evalor
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.rerun()
                if c_edit2.form_submit_button("🗑️ Excluir"):
                    st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.rerun()

# --- FINANCEIRO MISTO & FILTRADO ---
elif aba == "💰 Financeiro":
    st.title("💸 Fluxo Financeiro")
    
    with st.expander("💳 Registrar Novo Pagamento", expanded=True):
        col_f1, col_f2 = st.columns(2)
        aluno = col_f1.selectbox("Judoca", st.session_state.atletas_df['Nome'].tolist())
        data_p = col_f2.date_input("Data do Recebimento")
        
        col_f3, col_f4 = st.columns(2)
        mes = col_f3.selectbox("Mês de Ref.", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        forma = col_f4.selectbox("Forma", ["PIX", "Dinheiro", "Misto (PIX + Dinheiro)"])
        
        v_total = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0]
        detalhe = ""
        
        if forma == "Misto (PIX + Dinheiro)":
            cm1, cm2 = st.columns(2)
            vp = cm1.number_input("Valor no PIX", value=v_total/2)
            vd = cm2.number_input("Valor no Dinheiro", value=v_total/2)
            v_total = vp + vd
            detalhe = f"PIX: R${vp:.2f} | Din: R${vd:.2f}"
        
        if st.button("Confirmar Pagamento"):
            id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
            new_pg = pd.DataFrame([[id_a, aluno, mes, v_total, data_p.strftime("%d/%m/%Y"), forma, detalhe]], columns=st.session_state.fin_df.columns)
            st.session_state.fin_df = pd.concat([st.session_state.fin_df, new_pg], ignore_index=True)
            save_data(st.session_state.atletas_df, st.session_state.fin_df)
            st.success(f"Pagamento
