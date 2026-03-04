import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Associação Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- CSS CORRIGIDO (Ajuste no parâmetro unsafe_allow_html) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37; }
    h1 { color: #d4af37; font-family: 'Helvetica'; }
    div[data-testid="stExpander"] { border: 1px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "database_v3.csv"

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            pass
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
st.sidebar.markdown("### Associação\n**Roberdrayner Martins**")
aba = st.sidebar.radio("Navegação", ["📊 Dashboard", "🥋 Atletas", "💰 Financeiro"])

# --- DASHBOARD ---
if aba == "📊 Dashboard":
    st.title("🏯 Painel de Controle")
    df = st.session_state.atletas
    
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Alunos", len(df))
        c2.metric("Em Dia", len(df[df['Status'] == 'Pago']))
        c3.metric("Pendentes", len(df[df['Status'] == 'Pendente']))
        
        # Cálculo de receita (ajuste para tratar vazios)
        receita = pd.to_numeric(df['Mensalidade']).sum() if 'Mensalidade' in df else 0.0
        c4.metric("Receita Estimada", f"R$ {receita:,.2f}")
        
        st.divider()
        st.subheader("Lista Geral de Alunos")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sistema pronto. Vá em 'Atletas' para cadastrar o primeiro membro.")

# --- ABA: ATLETAS ---
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
                        "Nome": nome, "Faixa": faixa, 
                        "Nascimento": datetime.now().strftime("%d/%m/%Y"),
                        "Mensalidade": valor, "Status": "Pendente", 
                        "Ultimo_Pagamento": "-", "Forma_Pagamento": "-"
                    }
                    st.session_state.atletas = pd.concat([st.session_state.atletas, pd.DataFrame([novo])], ignore_index=True)
                    salvar_dados(st.session_state.atletas)
                    st.success("Atleta registrado!")
                    st.rerun()

# --- ABA: FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💸 Controle de Caixa")
    df = st.session_state.atletas
    
    if not df.empty:
        st.subheader("Registrar Recebimento")
        aluno = st.selectbox("Selecione o Aluno", df['Nome'].tolist())
        
        c1, c2, c3 = st.columns(3)
        data_pgto = c1.date_input("Data do Pagamento")
        forma_pgto = c2.selectbox("Forma", ["PIX", "Dinheiro", "Cartão", "Boleto"])
        confirmar = c3.form_submit_button if False else c3.button("Confirmar Pagamento", use_container_width=True)
        
        if confirmar:
            st.session_state.atletas.loc[df['Nome'] == aluno, 'Status'] = 'Pago'
            st.session_state.atletas.loc[df['Nome'] == aluno, 'Ultimo_Pagamento'] = data_pgto.strftime("%d/%m/%Y")
            st.session_state.atletas.loc[df['Nome'] == aluno, 'Forma_Pagamento'] = forma_pgto
            salvar_dados(st.session_state.atletas)
            st.toast(f"Pagamento de {aluno} confirmado!")
            st.rerun()
            
        st.divider()
        st.subheader("Histórico de Pagamentos")
        pagos = df[df['Status'] == 'Pago']
        st.table(pagos[['Nome', 'Ultimo_Pagamento', 'Forma_Pagamento', 'Mensalidade']])
    else:
        st.warning("Cadastre alunos primeiro.")
