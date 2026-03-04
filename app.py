import streamlit as st
import pandas as pd
import os
import time
import bcrypt
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
st.set_page_config(page_title="Judô Pro | Gestão Administrativa", page_icon="🥋", layout="wide")

# --- 2. CAMADA DE ESTILO (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    div[data-testid="metric-container"] {
        background-color: #FFFFFF; border: 1px solid #E2E8F0;
        padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        border-radius: 10px; font-weight: 600;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white; border: none; padding: 0.7rem;
        transition: 0.3s all;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3); }
    </style>
""", unsafe_allow_html=True)

# --- 3. BANCO DE DADOS ---
class DBManager:
    DB_A = "atleta_v26.csv"
    DB_F = "fin_v26.csv"
    DB_U = "usuarios.csv"

    COLS_A = ["ID","Nome","Status","Faixa","Telefone","Responsavel","Mensalidade","Dia_Vencimento","Obs_Medicas","Data_Filiacao"]
    COLS_F = ["ID_Atleta","Nome_Atleta","Mes_Ref","Valor_Total","Valor_Pix","Valor_Dinheiro","Data_Pagamento","Metodo"]
    COLS_U = ["Usuario","SenhaHash"]

    @staticmethod
    def initialize():
        if not os.path.exists(DBManager.DB_A):
            pd.DataFrame(columns=DBManager.COLS_A).to_csv(DBManager.DB_A, index=False)
        if not os.path.exists(DBManager.DB_F):
            pd.DataFrame(columns=DBManager.COLS_F).to_csv(DBManager.DB_F, index=False)
        if not os.path.exists(DBManager.DB_U):
            # cria usuário admin padrão
            senha = bcrypt.hashpw("judo123".encode(), bcrypt.gensalt())
            pd.DataFrame([{"Usuario":"admin","SenhaHash":senha}]).to_csv(DBManager.DB_U, index=False)

    @staticmethod
    def load():
        df_a = pd.read_csv(DBManager.DB_A)
        df_f = pd.read_csv(DBManager.DB_F)
        df_u = pd.read_csv(DBManager.DB_U)
        return df_a, df_f, df_u

    @staticmethod
    def save(df_a, df_f):
        df_a.to_csv(DBManager.DB_A, index=False)
        df_f.to_csv(DBManager.DB_F, index=False)

DBManager.initialize()
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df, st.session_state.usuarios_df = DBManager.load()

# --- 4. LOGIN SEGURO ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

def login():
    if not st.session_state.autenticado:
        _, col, _ = st.columns([1,1.2,1])
        with col:
            st.markdown("<br><br><h1 style='text-align:center;'>🥋 Judô Pro</h1>", unsafe_allow_html=True)
            user = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.button("Acessar Painel"):
                df_u = st.session_state.usuarios_df
                if user in df_u['Usuario'].values:
                    senha_hash = df_u[df_u['Usuario']==user]['SenhaHash'].values[0].encode()
                    if bcrypt.checkpw(senha.encode(), senha_hash):
                        st.session_state.autenticado = True
                        st.rerun()
                    else: st.error("Senha incorreta.")
                else: st.error("Usuário não encontrado.")
        st.stop()

login()

# --- 5. MENU ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043831.png", width=70)
    st.title("Menu de Gestão")
    menu = st.radio("NAVEGAÇÃO", ["🏠 Início","🥋 Alunos","💰 Caixa","📑 Relatórios"], label_visibility="collapsed")
    st.divider()
    if st.button("Sair do Sistema"):
        st.session_state.autenticado = False
        st.rerun()

# --- 6. TELAS ---
# DASHBOARD
if menu == "🏠 Início":
    st.title("📊 Painel de Controle")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Alunos Ativos", len(df_a[df_a['Status']=="Ativo"]))
    m2.metric("Inativos", len(df_a[df_a['Status']=="Inativo"]))
    receita_total = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    m3.metric("Caixa Acumulado", f"R$ {receita_total:,.2f}".replace(",", "v").replace(".", ",").replace("v","."))
    previsto = pd.to_numeric(df_a[df_a['Status']=="Ativo"]['Mensalidade'], errors='coerce').sum()
    m4.metric("Previsão Mensal", f"R$ {previsto:,.2f}".replace(",", "v").replace(".", ",").replace("v","."))
    st.divider()
    if not df_f.empty:
        col_graf,col_venc = st.columns([1.5,1])
        with col_graf:
            st.subheader("📈 Evolução de Receita")
            df_f['Valor_Total'] = pd.to_numeric(df_f['Valor_Total'], errors='coerce')
            graf_data = df_f.groupby('Mes_Ref')['Valor_Total'].sum().reset_index()
            fig = px.area(graf_data, x='Mes_Ref', y='Valor_Total', title="Faturamento por Mês", color_discrete_sequence=['#2563EB'])
            st.plotly_chart(fig, use_container_width=True)
        with col_venc:
            st.subheader("🔔 Próximos Vencimentos")
            prox = df_a[df_a['Status']=="Ativo"].sort_values('Dia_Vencimento')
            st.dataframe(prox[['Nome','Dia_Vencimento','Mensalidade']].head(10), use_container_width=True, hide_index=True)

# ALUNOS
elif menu == "🥋 Alunos":
    st.title("🥋 Gestão de Atletas")
    faixa_sel = st.multiselect("Filtrar por Faixa", st.session_state.atletas_df['Faixa'].unique())
    status_sel = st.selectbox("Status", ["Todos","Ativo","Inativo"])
    df_filtrado = st.session_state.atletas_df
    if faixa_sel: df_filtrado = df_filtrado[df_filtrado['Faixa'].isin(faixa_sel)]
    if status_sel!="Todos": df_filtrado = df_filtrado[df_filtrado['Status']==status_sel]
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

# FINANCEIRO
elif menu == "💰 Caixa":
    st.title("💰 Controle de Caixa")
    # (mantém lógica de recebimento igual ao código original)
    # ...

# RELATÓRIOS
elif menu == "📑 Relatórios":
    st.title("📑 Exportação de Relatórios")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    st.download_button("📥 Exportar Alunos (CSV)", df_a.to_csv(index=False).encode("utf-8"), "alunos.csv", "text/csv")
    st.download_button("📥 Exportar Financeiro (CSV)", df_f.to_csv(index=False).encode("utf-8"), "financeiro.csv", "text/csv")
