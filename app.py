import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(
    page_title="Assoc. Roberdrayner Martins",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DESIGN SYSTEM (CSS PROFISSIONAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* Background Geral */
    .stApp { background-color: #f8f9fa; }
    
    /* Sidebar Custom */
    [data-testid="stSidebar"] { background-color: #1a237e; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Cards de Métricas */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-bottom: 4px solid #d4af37;
        text-align: center;
    }
    
    /* Estilização de Tabelas e Containers */
    div[data-testid="stExpander"] {
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #1a237e;
        color: white;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #d4af37;
        color: #1a237e;
    }

    /* Badge Status */
    .badge-pago { background-color: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-pendente { background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DADOS ---
DB_FILE = "gestao_judo_v3.csv"

def init_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=[
        "ID", "Nome", "Faixa", "Nascimento", "Mensalidade", 
        "Status", "Ultimo_Pgto", "Metodo", "Cadastro_Em"
    ])

if 'df' not in st.session_state:
    st.session_state.df = init_db()

def save():
    st.session_state.df.to_csv(DB_FILE, index=False)

# --- SIDEBAR E CABEÇALHO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3003/3003613.png", width=80)
    st.title("Sistema de Gestão")
    st.markdown("---")
    menu = st.radio("MENU", ["📈 Dashboard", "👥 Atletas", "💰 Financeiro", "⚙️ Ajustes"])
    st.markdown("---")
    st.caption("Assoc. Roberdrayner Martins de Judô v3.0")

# --- CONTEÚDO PRINCIPAL ---

if menu == "📈 Dashboard":
    st.markdown(f"<h1>🏯 Painel Administrativo</h1>", unsafe_allow_html=True)
    df = st.session_state.df
    
    # KPIs Superiores
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{len(df)}</h3><p>Total Alunos</p></div>', unsafe_allow_html=True)
    with c2:
        pagos = len(df[df['Status'] == 'Pago'])
        st.markdown(f'<div class="metric-card"><h3>{pagos}</h3><p>Pagos</p></div>', unsafe_allow_html=True)
    with c3:
        atraso = len(df[df['Status'] == 'Pendente'])
        st.markdown(f'<div class="metric-card"><h3>{atraso}</h3><p>Pendentes</p></div>', unsafe_allow_html=True)
    with c4:
        total = df['Mensalidade'].astype(float).sum() if not df.empty else 0
        st.markdown(f'<div class="metric-card"><h3>R$ {total:,.2f}</h3><p>Faturamento</p></div>', unsafe_allow_html=True)

    st.markdown("### 🥋 Visão Geral dos Alunos")
    if not df.empty:
        # Tabela Profissional
        st.dataframe(df[['Nome', 'Faixa', 'Status', 'Ultimo_Pgto', 'Metodo']], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado registrado até o momento.")

elif menu == "👥 Atletas":
    st.markdown("<h1>👥 Gestão de Atletas</h1>", unsafe_allow_html=True)
    
    with st.expander("➕ Matricular Novo Aluno", expanded=True):
        with st.form("add_atleta"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo")
            nasc = col2.date_input("Data de Nascimento", min_value=datetime(1950,1,1))
            
            col3, col4 = st.columns(2)
            faixa = col3.selectbox("Faixa Atual", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = col4.number_input("Valor da Mensalidade", value=150.0)
            
            if st.form_submit_button("Confirmar Matrícula"):
                if nome:
                    new_id = len(st.session_state.df) + 1
                    new_data = {
                        "ID": new_id, "Nome": nome, "Faixa": faixa, 
                        "Nascimento": nasc, "Mensalidade": valor, 
                        "Status": "Pendente", "Ultimo_Pgto": "-", 
                        "Metodo": "-", "Cadastro_Em": datetime.now().strftime("%d/%m/%Y")
                    }
                    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
                    save()
                    st.success(f"Matrícula de {nome} realizada!")
                    st.rerun()

    st.markdown("---")
    # Busca de Alunos
    busca = st.text_input("🔍 Pesquisar Judoca...")
    if busca:
        resultados = st.session_state.df[st.session_state.df['Nome'].str.contains(busca, case=False)]
        st.dataframe(resultados, use_container_width=True)

elif menu == "💰 Financeiro":
    st.markdown("<h1>💰 Controle Financeiro</h1>", unsafe_allow_html=True)
    df = st.session_state.df
    
    if not df.empty:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Dar Baixa")
            aluno_sel = st.selectbox("Selecione o Aluno", df['Nome'].tolist())
            data_pg = st.date_input("Data do Recebimento")
            forma = st.selectbox("Forma", ["PIX", "Dinheiro", "Cartão", "Boleto"])
            
            if st.button("Confirmar Pagamento"):
                st.session_state.df.loc[df['Nome'] == aluno_sel, ['Status', 'Ultimo_Pgto', 'Metodo']] = ['Pago', data_pg.strftime("%d/%m/%Y"), forma]
                save()
                st.toast("Financeiro Atualizado!")
                st.rerun()
        
        with col2:
            st.subheader("Relatório de Recebimentos")
            # Filtro de inadimplentes
            apenas_pagos = df[df['Status'] == 'Pago']
            st.dataframe(apenas_pagos[['Nome', 'Ultimo_Pgto', 'Metodo', 'Mensalidade']], use_container_width=True)
            
            if st.button("Limpar Mês (Resetar todos para Pendente)"):
                st.session_state.df['Status'] = 'Pendente'
                save()
                st.rerun()

elif menu == "⚙️ Ajustes":
    st.markdown("<h1>⚙️ Configurações</h1>", unsafe_allow_html=True)
    st.write("Configurações do sistema e backup.")
    
    if st.button("📥 Baixar Backup (Excel)"):
        st.session_state.df.to_excel("backup_judo.xlsx", index=False)
        st.success("Arquivo gerado na pasta do sistema!")
        
    if st.button("🔴 APAGAR TUDO (CUIDADO)"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.session_state.df = init_db()
            st.rerun()
