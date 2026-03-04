import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Judô Pro | Gestão de Elite",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENGINE DE ESTILIZAÇÃO PROFISSIONAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F1F5F9; }
    
    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #E2E8F0;
    }
    
    /* Botões Premium */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: #1E293B;
        color: white;
        font-weight: 600;
        border: none;
        padding: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #334155;
        border-color: #334155;
        transform: translateY(-1px);
    }
    
    /* Status Badges */
    .status-active { color: #059669; font-weight: 700; background: #D1FAE5; padding: 4px 8px; border-radius: 6px; }
    .status-inactive { color: #DC2626; font-weight: 700; background: #FEE2E2; padding: 4px 8px; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# --- CAMADA DE PERSISTÊNCIA DE DADOS (DB) ---
class DataManager:
    ATLETAS_FILE = "db_atletas_v30.csv"
    FINANCE_FILE = "db_finance_v30.csv"
    
    COLS_ATLETAS = ["ID", "Nome", "Status", "Faixa", "Telefone", "Responsavel", "Mensalidade", "Vencimento", "Filiacao"]
    COLS_FINANCE = ["ID_Atleta", "Nome", "Mes_Ref", "Valor", "Data_PG", "Metodo", "Timestamp"]

    @classmethod
    def initialize(cls):
        if not os.path.exists(cls.ATLETAS_FILE):
            pd.DataFrame(columns=cls.COLS_ATLETAS).to_csv(cls.ATLETAS_FILE, index=False)
        if not os.path.exists(cls.FINANCE_FILE):
            pd.DataFrame(columns=cls.COLS_FINANCE).to_csv(cls.FINANCE_FILE, index=False)

    @classmethod
    def load_atletas(cls):
        df = pd.read_csv(cls.ATLETAS_FILE)
        df['Mensalidade'] = pd.to_numeric(df['Mensalidade'], errors='coerce').fillna(0.0)
        return df

    @classmethod
    def load_finance(cls):
        df = pd.read_csv(cls.FINANCE_FILE)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0.0)
        return df

    @classmethod
    def save(cls, df_a, df_f):
        df_a.to_csv(cls.ATLETAS_FILE, index=False)
        df_f.to_csv(cls.FINANCE_FILE, index=False)

# Inicialização do Banco
DataManager.initialize()

# --- GESTÃO DE ESTADO (SESSION STATE) ---
if 'db_a' not in st.session_state:
    st.session_state.db_a = DataManager.load_atletas()
if 'db_f' not in st.session_state:
    st.session_state.db_f = DataManager.load_finance()
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- AUTENTICAÇÃO ---
if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        st.markdown("<br><br><h1 style='text-align:center;'>🥋 Judô Pro 30</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            user_key = st.text_input("Chave de Segurança", type="password")
            if st.button("Acessar Sistema"):
                if user_key == "judo123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Chave inválida.")
    st.stop()

# --- SIDEBAR E NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### 🥋 Gestão de Academia")
    st.divider()
    menu = st.radio("MÓDULOS", ["📊 Dashboard", "👥 Alunos", "💰 Financeiro", "📋 Relatórios"])
    st.divider()
    if st.button("Sair do Sistema"):
        st.session_state.auth = False
        st.rerun()

# --- MÓDULOS DO SISTEMA ---

# 1. DASHBOARD
if menu == "📊 Dashboard":
    st.title("📊 Indicadores de Performance")
    
    # Cálculos em tempo real
    df_a = st.session_state.db_a
    df_f = st.session_state.db_f
    
    ativos = df_a[df_a['Status'] == 'Ativo']
    receita_mes = df_f[df_f['Mes_Ref'] == datetime.now().strftime("%m/%Y")]['Valor'].sum()
    faturamento_alvo = ativos['Mensalidade'].sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Alunos Ativos", len(ativos))
    m2.metric("Inativos", len(df_a[df_a['Status'] == 'Inativo']))
    m3.metric("Faturamento Alvo", f"R$ {faturamento_alvo:,.2f}")
    m4.metric("Receita no Mês", f"R$ {receita_mes:,.2f}", delta=f"{receita_mes - faturamento_alvo:.2f}")

    st.divider()
    
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.subheader("📈 Evolução Financeira")
        if not df_f.empty:
            df_chart = df_f.groupby('Mes_Ref')['Valor'].sum().reset_index()
            fig = px.area(df_chart, x='Mes_Ref', y='Valor', title="Receita por Competência", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Sem dados financeiros para gerar gráficos.")
        
    with col_r:
        st.subheader("🥋 Distribuição de Faixas")
        if not df_a.empty:
            fig_pie = px.pie(df_a, names='Faixa', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

# 2. ALUNOS
elif menu == "👥 Alunos":
    st.title("👥 Gestão de Alunos")
    t1, t2 = st.tabs(["📋 Listagem e Filtros", "➕ Nova Matrícula"])
    
    with t1:
        search = st.text_input("Filtrar por nome...")
        filtered_df = st.session_state.db_a[st.session_state.db_a['Nome'].str.contains(search, case=False, na=False)]
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        if not filtered_df.empty:
            st.markdown("---")
            st.subheader("🔧 Central de Edição")
            sel_aluno = st.selectbox("Escolha o aluno para editar:", filtered_df['Nome'].tolist())
            idx = st.session_state.db_a[st.session_state.db_a['Nome'] == sel_aluno].index[0]
            
            with st.form("edit_form"):
                c1, c2, c3 = st.columns(3)
                e_status = c1.selectbox("Status", ["Ativo", "Inativo"], index=0 if st.session_state.db_a.loc[idx, 'Status'] == 'Ativo' else 1)
                e_faixa = c2.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], 
                                       index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(st.session_state.db_a.loc[idx, 'Faixa']))
                e_mensal = c3.number_input("Mensalidade (R$)", value=float(st.session_state.db_a.loc[idx, 'Mensalidade']))
                
                if st.form_submit_button("💾 Atualizar Cadastro"):
                    st.session_state.db_a.loc[idx, ['Status', 'Faixa', 'Mensalidade']] = [e_status, e_faixa, e_mensal]
                    DataManager.save(st.session_state.db_a, st.session_state.db_f)
                    st.success("Dados salvos com sucesso!")
                    time.sleep(0.5); st.rerun()

    with t2:
        with st.form("new_aluno"):
            st.subheader("📝 Ficha de Matrícula")
            c1, c2 = st.columns(2)
            n_nome = c1.text_input("Nome Completo*")
            n_tel = c2.text_input("WhatsApp*")
            
            c3, c4, c5 = st.columns(3)
            n_faixa = c3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            n_mensal = c4.number_input("Mensalidade", value=150.0)
            n_venc = c5.selectbox("Dia de Vencimento", list(range(1, 31)), index=4)
            
            if st.form_submit_button("🚀 Confirmar Matrícula"):
                if n_nome and n_tel:
                    new_id = int(st.session_state.db_a['ID'].max() + 1) if not st.session_state.db_a.empty else 1
                    novo_atleta = pd.DataFrame([{
                        "ID": new_id, "Nome": n_nome, "Status": "Ativo", "Faixa": n_faixa,
                        "Telefone": n_tel, "Mensalidade": n_mensal, "Vencimento": n_venc,
                        "Filiacao": date.today().strftime("%d/%m/%Y")
                    }])
                    st.session_state.db_a = pd.concat([st.session_state.db_a, novo_atleta], ignore_index=True)
                    DataManager.save(st.session_state.db_a, st.session_state.db_f)
                    st.success("Aluno matriculado com sucesso!")
                    time.sleep(1); st.rerun()
                else: st.warning("Preencha Nome e Telefone.")

# 3. FINANCEIRO
elif menu == "💰 Financeiro":
    st.title("💰 Gestão Financeira")
    
    col_l, col_r = st.columns([1, 1.2])
    
    with col_l:
        with st.container(border=True):
            st.subheader("💳 Lançar Pagamento")
            ativos = st.session_state.db_a[st.session_state.db_a['Status'] == 'Ativo']
            
            if not ativos.empty:
                with st.form("pag_form", clear_on_submit=True):
                    f_aluno = st.selectbox("Selecione o Aluno", ativos['Nome'].tolist())
                    c1, c2 = st.columns(2)
                    f_data = c1.date_input("Data do Pagamento", date.today())
                    f_mes = c2.text_input("Mês Ref (MM/AAAA)", date.today().strftime("%m/%Y"))
                    
                    val_sugerido = float(ativos[ativos['Nome'] == f_aluno]['Mensalidade'].values[0])
                    f_valor = st.number_input("Valor Pago", value=val_sugerido)
                    f_metodo = st.selectbox("Forma", ["PIX", "Dinheiro", "Cartão", "Misto"])
                    
                    if st.form_submit_button("💰 Registrar Recebimento"):
                        id_atleta = ativos[ativos['Nome'] == f_aluno]['ID'].values[0]
                        novo_pg = pd.DataFrame([{
                            "ID_Atleta": id_atleta, "Nome": f_aluno, "Mes_Ref": f_mes,
                            "Valor": f_valor, "Data_PG": f_data.strftime("%d/%m/%Y"),
                            "Metodo": f_metodo, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }])
                        st.session_state.db_f = pd.concat([st.session_state.db_f, novo_pg], ignore_index=True)
                        DataManager.save(st.session_state.db_a, st.session_state.db_f)
                        st.success(f"Pagamento de {f_aluno} registrado!")
                        st.session_state.last_recibo = f"*RECIBO JUDÔ*\nAluno: {f_aluno}\nValor: R$ {f_valor:.2f}\nData: {f_data.strftime('%d/%m/%Y')}\nRef: {f_mes}"
                        st.rerun()
            else: st.error("Nenhum aluno ativo para cobrança.")

    with col_r:
        st.subheader("📱 Último Recibo Gerado")
        if 'last_recibo' in st.session_state:
            st.code(st.session_state.last_recibo, language="markdown")
            st.caption("Copie o texto acima e envie ao aluno.")
        
        st.divider()
        st.subheader("📋 Últimos 10 Lançamentos")
        st.dataframe(st.session_state.db_f.tail(10), use_container_width=True, hide_index=True)

# 4. RELATÓRIOS
elif menu == "📋 Relatórios":
    st.title("📋 Central de Relatórios")
    df_f = st.session_state.db_f
    
    if not df_f.empty:
        st.subheader("Filtragem de Dados")
        meses = df_f['Mes_Ref'].unique().tolist()
        sel_mes = st.multiselect("Filtrar por Mês de Referência:", meses, default=meses[-1:])
        
        relatorio = df_f[df_f['Mes_Ref'].isin(sel_mes)]
        st.write(f"Exibindo {len(relatorio)} registros encontrados.")
        st.dataframe(relatorio, use_container_width=True)
        
        # Exportação
        csv = relatorio.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Relatório Filtrado (CSV)", csv, "relatorio_judo.csv", "text/csv")
    else:
        st.info("Ainda não há lançamentos financeiros para gerar relatórios.")
