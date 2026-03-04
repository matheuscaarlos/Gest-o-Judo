import streamlit as st
import pandas as pd
from datetime import date

# Configuração da página
st.set_page_config(page_title="Gestão Judô Pro", page_icon="🥋")

# Inicialização do "Banco de Dados" (Simulado com Session State)
if 'atletas' not in st.session_state:
    st.session_state.atletas = pd.DataFrame(columns=[
        "Nome", "Graduação (Faixa)", "Data de Nascimento", "Status Financeiro", "Valor Mensalidade"
    ])

# --- SIDEBAR (Navegação) ---
st.sidebar.title("Menu Principal")
menu = st.sidebar.radio("Ir para:", ["Cadastrar Atleta", "Visualizar Alunos", "Financeiro"])

# --- PÁGINA: CADASTRO ---
if menu == "Cadastrar Atleta":
    st.header("📝 Cadastro de Novo Atleta")
    
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo")
        faixa = st.selectbox("Graduação", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
        nascimento = st.date_input("Data de Nascimento", min_value=date(1940, 1, 1))
        mensalidade = st.number_input("Valor da Mensalidade (R$)", min_value=0.0, value=100.0)
        
        enviar = st.form_submit_state("Cadastrar")
        
        if enviar:
            novo_atleta = {
                "Nome": nome,
                "Graduação (Faixa)": faixa,
                "Data de Nascimento": nascimento,
                "Status Financeiro": "Em dia",
                "Valor Mensalidade": mensalidade
            }
            st.session_state.atletas = pd.concat([st.session_state.atletas, pd.DataFrame([novo_atleta])], ignore_index=True)
            st.success(f"Atleta {nome} cadastrado com sucesso!")

# --- PÁGINA: VISUALIZAR ---
elif menu == "Visualizar Alunos":
    st.header("👥 Lista de Atletas")
    if st.session_state.atletas.empty:
        st.info("Nenhum atleta cadastrado ainda.")
    else:
        st.dataframe(st.session_state.atletas, use_container_width=True)

# --- PÁGINA: FINANCEIRO ---
elif menu == "Financeiro":
    st.header("💰 Gestão Financeira")
    
    if st.session_state.atletas.empty:
        st.warning("Cadastre atletas para gerenciar o financeiro.")
    else:
        # Resumo rápido
        total_previsto = st.session_state.atletas["Valor Mensalidade"].sum()
        st.metric("Receita Mensal Prevista", f"R$ {total_previsto:.2f}")
        
        st.subheader("Alterar Status de Pagamento")
        nome_atleta = st.selectbox("Selecione o Atleta", st.session_state.atletas["Nome"])
        novo_status = st.radio("Status", ["Em dia", "Inadimplente"])
        
        if st.button("Atualizar Status"):
            st.session_state.atletas.loc[st.session_state.atletas["Nome"] == nome_atleta, "Status Financeiro"] = novo_status
            st.success(f"Status de {nome_atleta} atualizado!")
            st.rerun()
