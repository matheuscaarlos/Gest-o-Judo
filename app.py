import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO ESTÉTICA AVANÇADA ---
st.set_page_config(page_title="Associação Roberdrayner Martins", page_icon="🥋", layout="wide")

# CSS Personalizado para um visual mais "Premium"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37; }
    h1 { color: #d4af37; font-family: 'Helvetica'; }
    .stButton>button { background-color: #d4af37; color: black; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_stdio=True)

DB_FILE = "database_v2.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=[
        "ID", "Nome", "Faixa", "Nascimento", "Mensalidade", 
        "Status", "Ultimo_Pagamento", "Forma_Pagamento"
    ])

def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)

if 'atletas' not in st.session_state:
    st.session_state.atletas = carregar_dados()

# --- SIDEBAR ---
st.sidebar.title("🥋 Gestão de Judô")
st.sidebar.subheader("Assoc. Roberdrayner Martins")
aba = st.sidebar.radio("Navegação", ["📊 Dashboard", "🥋 Atletas", "💰 Financeiro"])

# --- DASHBOARD ---
if aba == "📊 Dashboard":
    st.title("🏯 Painel de Controle Institucional")
    df = st.session_state.atletas
    
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Alunos", len(df))
        c2.metric("Em Dia", len(df[df['Status'] == 'Pago']))
        c3.metric("Pendentes", len(df[df['Status'] == 'Pendente']))
        c4.metric("Receita Estimada", f"R$ {df['Mensalidade'].sum():,.2f}")
        
        st.divider()
        st.subheader("Situação dos Atletas")
        st.dataframe(df.style.applymap(lambda x: 'color: #00ff00' if x == 'Pago' else ('color: #ff4b4b' if x == 'Pendente' else ''), subset=['Status']), use_container_width=True)
    else:
        st.info("O sistema está pronto. Comece cadastrando os atletas da associação.")

# --- ABA: ATLETAS (Cadastro e Lista) ---
elif aba == "🥋 Atletas":
    st.title("📝 Gestão de Integrantes")
    
    with st.expander("➕ Cadastrar Novo Atleta", expanded=True):
        with st.form("cadastro"):
            col1, col2, col3 = st.columns([2, 1, 1])
            nome = col1.text_input("Nome do Judoca")
            faixa = col2.selectbox("Graduação", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = col3.number_input("Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Finalizar Cadastro"):
                if nome:
                    novo = {
                        "ID": len(st.session_state.atletas) + 1,
                        "Nome": nome, "Faixa": faixa, "Nascimento": datetime.now().strftime("%d/%m/%Y"),
                        "Mensalidade": valor, "Status": "Pendente", 
                        "Ultimo_Pagamento": "-", "Forma_Pagamento": "-"
                    }
                    st.session_state.atletas = pd.concat([st.session_state.atletas, pd.DataFrame([novo])], ignore_index=True)
                    salvar_dados(st.session_state.atletas)
                    st.success("Atleta registrado!")
                    st.rerun()

# --- ABA: FINANCEIRO (Data e Forma de Pagamento) ---
elif aba == "💰 Financeiro":
    st.title("💸 Controle de Caixa")
    df = st.session_state.atletas
    
    if not df.empty:
        st.subheader("Baixa em Mensalidades")
        aluno = st.selectbox("Selecione o Aluno", df['Nome'].tolist())
        
        col1, col2, col3 = st.columns(3)
        data_pgto = col1.date_input("Data do Pagamento")
        forma_pgto = col2.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Transferência"])
        confirmar = col3.button("Confirmar Recebimento", use_container_width=True)
        
        if confirmar:
            st.session_state.atletas.loc[df['Nome'] == aluno, 'Status'] = 'Pago'
            st.session_state.atletas.loc[df['Nome'] == aluno, 'Ultimo_Pagamento'] = data_pgto.strftime("%d/%m/%Y")
            st.session_state.atletas.loc[df['Nome'] == aluno, 'Forma_Pagamento'] = forma_pgto
            salvar_dados(st.session_state.atletas)
            st.balloons()
            st.success(f"Pagamento de {aluno} registrado com sucesso!")
            st.rerun()
            
        st.divider()
        st.subheader("Histórico Recente")
        st.table(df[df['Status'] == 'Pago'][['Nome', 'Ultimo_Pagamento', 'Forma_Pagamento', 'Mensalidade']])
    else:
        st.warning("Cadastre alunos para gerenciar o financeiro.")
