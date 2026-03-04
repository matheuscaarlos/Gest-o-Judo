import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- CONFIGURAÇÃO E BANCO DE DADOS ---
conn = sqlite3.connect('gestao_judo.db', check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS atletas 
                 (id INTEGER PRIMARY KEY, nome TEXT, faixa TEXT, status TEXT, data_adesao DATE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pagamentos 
                 (id INTEGER PRIMARY KEY, atleta_id INTEGER, valor REAL, mes_ref TEXT, pago INTEGER)''')
    conn.commit()

create_tables()

# --- INTERFACE ---
st.title("🥋 Sistema de Gestão - Judô")

menu = ["Cadastrar Atleta", "Gerenciar Atletas", "Financeiro"]
choice = st.sidebar.selectbox("Menu", menu)

# --- CADASTRO ---
if choice == "Cadastrar Atleta":
    st.subheader("Novo Cadastro")
    nome = st.text_input("Nome do Atleta")
    faixa = st.selectbox("Graduação", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
    
    if st.button("Salvar"):
        c.execute("INSERT INTO atletas (nome, faixa, status, data_adesao) VALUES (?, ?, ?, ?)", 
                  (nome, faixa, "Ativo", date.today()))
        conn.commit()
        st.success(f"Atleta {nome} cadastrado com sucesso!")

# --- GESTÃO DE ATLETAS ---
elif choice == "Gerenciar Atletas":
    st.subheader("Lista de Atletas")
    df = pd.read_sql_query("SELECT * FROM atletas", conn)
    
    # Exibir tabela com opção de edição
    for index, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{row['nome']}** - {row['faixa']}")
        status_label = "Inativar" if row['status'] == "Ativo" else "Ativar"
        
        if col2.button(status_label, key=f"btn_{row['id']}"):
            novo_status = "Inativo" if row['status'] == "Ativo" else "Ativo"
            c.execute("UPDATE atletas SET status = ? WHERE id = ?", (novo_status, row['id']))
            conn.commit()
            st.rerun()
            
    st.dataframe(df)

# --- FINANCEIRO ---
elif choice == "Financeiro":
    st.subheader("Controle de Mensalidades")
    df_atletas = pd.read_sql_query("SELECT id, nome FROM atletas WHERE status = 'Ativo'", conn)
    
    atleta_sel = st.selectbox("Selecione o Atleta", df_atletas['nome'].tolist())
    valor = st.number_input("Valor (R$)", min_value=0.0, value=100.0)
    mes = st.selectbox("Mês de Referência", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
    
    if st.button("Registrar Pagamento"):
        atleta_id = df_atletas[df_atletas['nome'] == atleta_sel]['id'].values[0]
        c.execute("INSERT INTO pagamentos (atleta_id, valor, mes_ref, pago) VALUES (?, ?, ?, ?)", 
                  (atleta_id, valor, mes, 1))
        conn.commit()
        st.balloons()
        st.success("Pagamento registrado!")

    st.divider()
    st.write("### Histórico Recente")
    pagamentos = pd.read_sql_query("""
        SELECT atletas.nome, pagamentos.valor, pagamentos.mes_ref 
        FROM pagamentos 
        JOIN atletas ON atletas.id = pagamentos.atleta_id
    """, conn)
    st.table(pagamentos)
