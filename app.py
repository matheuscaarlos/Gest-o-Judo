import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date

# --- 1. ARQUITETURA DE ESTILO (UI/UX) ---
st.set_page_config(page_title="Judô Pro | Enterprise", page_icon="🥋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8FAFC; }
    
    /* Metrics Card */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 1.5rem !important;
        border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* Global Buttons */
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5rem; background-color: #0F172A;
        color: white; font-weight: 600; border: none; transition: 0.3s ease;
    }
    .stButton>button:hover { background-color: #334155; transform: translateY(-1px); }
    
    /* Status Badges */
    .badge-ativo { background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 600; }
    .badge-inativo { background-color: #FEE2E2; color: #991B1B; padding: 4px 12px; border-radius: 20px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CAMADA DE PERSISTÊNCIA (DATABASE) ---
class JudoRepository:
    def __init__(self):
        self.file_atletas = "judo_db_atletas.csv"
        self.file_financeiro = "judo_db_financeiro.csv"
        self.init_files()

    def init_files(self):
        if not os.path.exists(self.file_atletas):
            cols = ["ID", "Nome", "Status", "CPF", "Nascimento", "Sexo", "Faixa", "WhatsApp", 
                    "Responsavel", "CPF_Resp", "Mensalidade", "Vencimento", "Filiacao", "Obs"]
            pd.DataFrame(columns=cols).to_csv(self.file_atletas, index=False)
        if not os.path.exists(self.file_financeiro):
            cols = ["ID_Lan", "ID_Atleta", "Nome", "Mes_Ref", "Valor", "Data_PG", "Metodo"]
            pd.DataFrame(columns=cols).to_csv(self.file_financeiro, index=False)

    def load_atletas(self):
        df = pd.read_csv(self.file_atletas).fillna("")
        df['Mensalidade'] = pd.to_numeric(df['Mensalidade'], errors='coerce').fillna(0.0)
        return df

    def load_financeiro(self):
        df = pd.read_csv(self.file_financeiro).fillna("")
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0.0)
        return df

    def save(self, df_a, df_f):
        df_a.to_csv(self.file_atletas, index=False)
        df_f.to_csv(self.file_financeiro, index=False)

# Instância Global
repo = JudoRepository()

# --- 3. CONTROLE DE ESTADO ---
if 'db_a' not in st.session_state:
    st.session_state.db_a = repo.load_atletas()
if 'db_f' not in st.session_state:
    st.session_state.db_f = repo.load_financeiro()
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- 4. AUTENTICAÇÃO ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 0.8, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>🥋 Judô Pro Login</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            user_key = st.text_input("Chave Administrativa", type="password")
            if st.button("Entrar no Sistema"):
                if user_key == "judo123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Acesso negado.")
    st.stop()

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.title("SISTEMA JUDÔ")
    st.divider()
    menu = st.radio("MÓDULOS", ["📊 Dashboard", "👥 Alunos", "💰 Financeiro", "⚙️ Ajustes"])
    st.divider()
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

# --- MÓDULO: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Painel Executivo")
    df_a, df_f = st.session_state.db_a, st.session_state.db_f
    
    ativos = df_a[df_a['Status'] == 'Ativo']
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Alunos Ativos", len(ativos))
    c2.metric("Inativos", len(df_a[df_a['Status'] == 'Inativo']))
    
    alvo = ativos['Mensalidade'].sum()
    real = df_f[df_f['Mes_Ref'] == datetime.now().strftime("%m/%Y")]['Valor'].sum()
    
    c3.metric("Faturamento Alvo", f"R$ {alvo:,.2f}")
    c4.metric("Recebido (Mês)", f"R$ {real:,.2f}", delta=f"{real - alvo:,.2f}")

# --- MÓDULO: ALUNOS ---
elif menu == "👥 Alunos":
    st.title("👥 Gestão de Atletas")
    t1, t2, t3 = st.tabs(["📋 Listagem", "➕ Nova Matrícula", "🔧 Edição Completa"])
    
    with t1:
        st.dataframe(st.session_state.db_a, use_container_width=True, hide_index=True)

    with t2:
        with st.form("cad_master", clear_on_submit=True):
            st.subheader("Ficha de Matrícula")
            c1, c2, c3 = st.columns([2, 1, 1])
            f_nome = c1.text_input("Nome Completo*")
            f_cpf = c2.text_input("CPF*")
            f_nasc = c3.date_input("Nascimento", date(2010, 1, 1))
            
            c4, c5, c6 = st.columns(3)
            f_faixa = c4.selectbox("Faixa", ["Branca", "Azul", "Amarela", "Verde", "Roxa", "Marrom", "Preta"])
            f_mensal = c5.number_input("Mensalidade (R$)", value=150.0)
            f_tel = c6.text_input("WhatsApp*")
            
            if st.form_submit_button("Finalizar Matrícula"):
                if f_nome and f_cpf:
                    new_id = int(st.session_state.db_a['ID'].max() + 1) if not st.session_state.db_a.empty else 1
                    # PROTEÇÃO DE DATA: Convertendo para string apenas no salvamento
                    nasc_str = f_nasc.strftime("%d/%m/%Y") if isinstance(f_nasc, (date, datetime)) else str(f_nasc)
                    
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": f_nome, "Status": "Ativo", "CPF": f_cpf, 
                        "Nascimento": nasc_str, "Faixa": f_faixa, "WhatsApp": f_tel, 
                        "Mensalidade": f_mensal, "Filiacao": date.today().strftime("%d/%m/%Y")
                    }])
                    st.session_state.db_a = pd.concat([st.session_state.db_a, novo], ignore_index=True)
                    repo.save(st.session_state.db_a, st.session_state.db_f)
                    st.success("Matrícula realizada!"); time.sleep(1); st.rerun()

    with t3:
        if not st.session_state.db_a.empty:
            sel_nome = st.selectbox("Selecione para editar:", st.session_state.db_a['Nome'].tolist())
            idx = st.session_state.db_a[st.session_state.db_a['Nome'] == sel_nome].index[0]
            atl = st.session_state.db_a.loc[idx]
            
            with st.form("edicao_total"):
                c1, c2, c3 = st.columns([2, 1, 1])
                e_nome = c1.text_input("Nome", value=atl['Nome'])
                e_status = c2.selectbox("Status", ["Ativo", "Inativo"], index=0 if atl['Status'] == 'Ativo' else 1)
                e_faixa = c3.selectbox("Faixa", ["Branca", "Azul", "Amarela", "Verde", "Roxa", "Marrom", "Preta"])
                
                e_mensal = st.number_input("Mensalidade", value=float(atl['Mensalidade']))
                e_obs = st.text_area("Observações", value=atl['Obs'])
                
                if st.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.db_a.at[idx, 'Nome'] = e_nome
                    st.session_state.db_a.at[idx, 'Status'] = e_status
                    st.session_state.db_a.at[idx, 'Faixa'] = e_faixa
                    st.session_state.db_a.at[idx, 'Mensalidade'] = e_mensal
                    st.session_state.db_a.at[idx, 'Obs'] = e_obs
                    repo.save(st.session_state.db_a, st.session_state.db_f)
                    st.success("Alterado!"); st.rerun()

# --- MÓDULO: FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.title("💰 Gestão Financeira")
    col_a, col_b = st.columns([1, 1.2])
    
    with col_a:
        with st.form("pagamento_baixa", clear_on_submit=True):
            st.subheader("Receber Mensalidade")
            lista_ativos = st.session_state.db_a[st.session_state.db_a['Status'] == 'Ativo']
            aluno = st.selectbox("Aluno", lista_ativos['Nome'].tolist())
            c1, c2 = st.columns(2)
            p_data = c1.date_input("Data PG")
            p_mes = c2.text_input("Mês Ref (MM/AAAA)", date.today().strftime("%m/%Y"))
            
            val_base = float(lista_ativos[lista_ativos['Nome'] == aluno]['Mensalidade'].values[0])
            p_valor = st.number_input("Valor Pago", value=val_base)
            
            if st.form_submit_button("💰 Baixar"):
                new_id_f = int(st.session_state.db_f['ID_Lan'].max() + 1) if not st.session_state.db_f.empty else 1
                novo_p = pd.DataFrame([{
                    "ID_Lan": new_id_f, "Nome": aluno, "Mes_Ref": p_mes, 
                    "Valor": p_valor, "Data_PG": p_data.strftime("%d/%m/%Y")
                }])
                st.session_state.db_f = pd.concat([st.session_state.db_f, novo_p], ignore_index=True)
                repo.save(st.session_state.db_a, st.session_state.db_f)
                st.success("Pago!"); st.rerun()

    with col_b:
        st.subheader("Histórico e Estorno")
        if not st.session_state.db_f.empty:
            df_view = st.session_state.db_f.iloc[::-1]
            sel_estorno = st.selectbox("Estornar lançamento:", [f"{r['ID_Lan']} - {r['Nome']}" for _, r in df_view.iterrows()])
            id_del = int(sel_estorno.split(" - ")[0])
            
            if st.button("🔥 Confirmar Estorno"):
                st.session_state.db_f = st.session_state.db_f[st.session_state.db_f['ID_Lan'] != id_del]
                repo.save(st.session_state.db_a, st.session_state.db_f)
                st.error("Removido!"); time.sleep(0.5); st.rerun()
            
            st.dataframe(st.session_state.db_f, use_container_width=True, hide_index=True)
