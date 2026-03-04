import streamlit as st
import pandas as pd
import os
from datetime import date

# --- CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="Judô Control v2", page_icon="🥋", layout="wide")

# Nome do arquivo que servirá como nosso "Banco de Dados"
DB_FILE = "database_judo.csv"

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=[
        "Nome", "Graduação", "Nascimento", "Status", "Mensalidade"
    ])

def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)

# Inicializa os dados na sessão
if 'atletas' not in st.session_state:
    st.session_state.atletas = carregar_dados()

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3003/3003613.png", width=100)
st.sidebar.title("Academia de Judô")
aba = st.sidebar.selectbox("Navegação", ["Painel Geral", "Cadastrar Atleta", "Financeiro", "Configurações"])

# --- ABA: PAINEL GERAL (DASHBOARD) ---
if aba == "Painel Geral":
    st.title("🏯 Painel de Controle")
    
    df = st.session_state.atletas
    
    if not df.empty:
        # Métricas de topo
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Atletas", len(df))
        c2.metric("Atletas em Dia", len(df[df['Status'] == 'Em dia']))
        c3.metric("Inadimplentes", len(df[df['Status'] == 'Pendente']), delta_color="inverse")
        
        st.divider()
        
        # Busca e Tabela
        st.subheader("Lista de Alunos")
        busca = st.text_input("🔍 Buscar por nome...")
        df_filtrado = df[df['Nome'].str.contains(busca, case=False)]
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.info("Bem-vindo! Comece cadastrando seu primeiro atleta no menu lateral.")

# --- ABA: CADASTRO ---
elif aba == "Cadastrar Atleta":
    st.title("📝 Novo Cadastro")
    
    with st.form("cadastro_atleta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome Completo")
        faixa = col2.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
        nascimento = col1.date_input("Data de Nascimento", min_value=date(1940,1,1))
        valor = col2.number_input("Valor Mensalidade (R$)", value=120.0)
        
        if st.form_submit_button("Salvar Atleta"):
            if nome:
                novo_registro = {
                    "Nome": nome, "Graduação": faixa, 
                    "Nascimento": str(nascimento), "Status": "Em dia", "Mensalidade": valor
                }
                st.session_state.atletas = pd.concat([st.session_state.atletas, pd.DataFrame([novo_registro])], ignore_index=True)
                salvar_dados(st.session_state.atletas)
                st.success(f"Oss! {nome} adicionado.")
            else:
                st.error("O nome é obrigatório.")

# --- ABA: FINANCEIRO ---
elif aba == "Financeiro":
    st.title("💰 Gestão Financeira")
    df = st.session_state.atletas
    
    if not df.empty:
        st.subheader("Atualizar Pagamentos")
        nome_sel = st.selectbox("Escolha o aluno:", df['Nome'].tolist())
        novo_status = st.radio("Situação:", ["Em dia", "Pendente"], horizontal=True)
        
        if st.button("Confirmar Alteração"):
            st.session_state.atletas.loc[st.session_state.atletas['Nome'] == nome_sel, 'Status'] = novo_status
            salvar_dados(st.session_state.atletas)
            st.toast(f"Status de {nome_sel} atualizado!", icon="✅")
            st.rerun()
            
        # Resumo visual
        st.divider()
        faturamento = df['Mensalidade'].sum()
        st.write(f"### Previsão de Faturamento: R$ {faturamento:,.2f}")
    else:
        st.warning("Sem dados financeiros disponíveis.")

# --- ABA: CONFIGURAÇÕES ---
elif aba == "Configurações":
    st.title("⚙️ Configurações")
    if st.button("🗑️ Apagar Todos os Dados"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.session_state.atletas = pd.DataFrame(columns=["Nome", "Graduação", "Nascimento", "Status", "Mensalidade"])
            st.warning("Todos os dados foram apagados.")
