import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date
import plotly.express as px

# --- 1. CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(page_title="Judô Pro | Gestão Enterprise", page_icon="🥋", layout="wide")

# --- 2. ESTILIZAÇÃO DE ALTA FIDELIDADE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    /* Sidebar Estilizada */
    [data-testid="stSidebar"] { background-color: #1E293B !important; border-right: 1px solid #CBD5E1; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    
    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 12px; padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #E2E8F0;
    }
    
    /* Botões Primários */
    .stButton>button {
        background: #2563EB; color: white; border-radius: 8px; border: none;
        font-weight: 600; transition: all 0.2s; width: 100%; height: 3.5em;
    }
    .stButton>button:hover { background: #1D4ED8; transform: translateY(-1px); }
    
    /* Botão de Estorno/Exclusão */
    .stButton.btn-danger>button { background: #DC2626 !important; }
    
    /* Tabelas */
    .stDataFrame { background: white; border-radius: 10px; border: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DADOS (DATA ENGINE) ---
class JudoCore:
    def __init__(self):
        self.path_a = "db_atletas_v35.csv"
        self.path_f = "db_financeiro_v35.csv"
        self.cols_a = ["ID", "Nome", "Status", "CPF", "Nasc", "Sexo", "Faixa", "WhatsApp", "Responsavel", "CPF_Resp", "Mensalidade", "Vencimento", "Filiacao", "Obs"]
        self.cols_f = ["ID_Lan", "ID_Atleta", "Nome", "Mes_Ref", "Valor", "Data_PG", "Metodo"]
        self.init_db()

    def init_db(self):
        if not os.path.exists(self.path_a): pd.DataFrame(columns=self.cols_a).to_csv(self.path_a, index=False)
        if not os.path.exists(self.path_f): pd.DataFrame(columns=self.cols_f).to_csv(self.path_f, index=False)

    def load_data(self):
        try:
            df_a = pd.read_csv(self.path_a).fillna("")
            df_f = pd.read_csv(self.path_f).fillna("")
            df_a['Mensalidade'] = pd.to_numeric(df_a['Mensalidade'], errors='coerce').fillna(0.0)
            df_f['Valor'] = pd.to_numeric(df_f['Valor'], errors='coerce').fillna(0.0)
            return df_a, df_f
        except Exception:
            return pd.DataFrame(columns=self.cols_a), pd.DataFrame(columns=self.cols_f)

    def save_data(self, df_a, df_f):
        df_a.to_csv(self.path_a, index=False)
        df_f.to_csv(self.path_f, index=False)

# Inicializar Engine
core = JudoCore()
if 'df_a' not in st.session_state or 'df_f' not in st.session_state:
    st.session_state.df_a, st.session_state.df_f = core.load_data()

# --- 4. SEGURANÇA ---
if "auth" not in st.session_state: st.session_state.auth = False

def login():
    if not st.session_state.auth:
        _, col, _ = st.columns([1, 1, 1])
        with col:
            st.markdown("<br><h1 style='text-align:center;'>🥋 Judô Pro</h1>", unsafe_allow_html=True)
            with st.container(border=True):
                pw = st.text_input("Acesso Administrativo", type="password")
                if st.button("Acessar"):
                    if pw == "judo123":
                        st.session_state.auth = True
                        st.rerun()
                    else: st.error("Incorreta.")
        st.stop()

login()

# --- 5. INTERFACE PRINCIPAL ---
with st.sidebar:
    st.markdown("## ⚙️ Painel de Controle")
    menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "👥 Alunos", "💰 Financeiro", "📊 Relatórios"], label_visibility="collapsed")
    st.divider()
    if st.button("Sair"):
        st.session_state.auth = False
        st.rerun()

# --- MODULO: INÍCIO (DASHBOARD) ---
if menu == "🏠 Início":
    st.title("🏠 Visão Geral")
    df_a, df_f = st.session_state.df_a, st.session_state.df_f
    
    ativos = df_a[df_a['Status'] == 'Ativo']
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Alunos Ativos", len(ativos))
    c2.metric("Total de Alunos", len(df_a))
    
    receita_alvo = ativos['Mensalidade'].sum()
    receita_real = df_f[df_f['Mes_Ref'] == datetime.now().strftime("%m/%Y")]['Valor'].sum()
    
    c3.metric("Faturamento Alvo", f"R$ {receita_alvo:,.2f}")
    c4.metric("Recebido (Mes)", f"R$ {receita_real:,.2f}", delta=f"R$ {receita_real - receita_alvo:,.2f}")

    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Faturamento Mensal")
        if not df_f.empty:
            st.plotly_chart(px.bar(df_f.groupby('Mes_Ref')['Valor'].sum().reset_index(), x='Mes_Ref', y='Valor', color_discrete_sequence=['#2563EB']), use_container_width=True)
    with col_g2:
        st.subheader("População por Faixa")
        if not df_a.empty:
            st.plotly_chart(px.pie(df_a, names='Faixa', hole=0.4), use_container_width=True)

# --- MODULO: ALUNOS (CADASTRO E EDIÇÃO TOTAL) ---
elif menu == "👥 Alunos":
    st.title("👥 Gestão de Atletas")
    tab_l, tab_c, tab_e = st.tabs(["📋 Listagem", "✨ Matrícula", "🔧 Edição Completa"])

    with tab_l:
        st.dataframe(st.session_state.df_a, use_container_width=True, hide_index=True)

    with tab_c:
        with st.form("form_cadastro", clear_on_submit=True):
            st.subheader("Nova Ficha de Matrícula")
            c1, c2, c3 = st.columns([2, 1, 1])
            n_nome = c1.text_input("Nome Completo*")
            n_cpf = c2.text_input("CPF*")
            n_nasc = c3.date_input("Nascimento", date(2010, 1, 1))
            
            c4, c5, c6 = st.columns(3)
            n_sexo = c4.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            n_faixa = c5.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            n_tel = c6.text_input("WhatsApp*")
            
            c7, c8, c9 = st.columns(3)
            n_mensal = c7.number_input("Mensalidade (R$)", value=150.0)
            n_venc = c8.selectbox("Vencimento (Dia)", list(range(1, 31)), index=4)
            n_resp = c9.text_input("Responsável (Se menor)")

            n_obs = st.text_area("Observações/Saúde")
            
            if st.form_submit_button("Finalizar Matrícula"):
                if n_nome and n_cpf:
                    new_id = int(st.session_state.df_a['ID'].max() + 1) if not st.session_state.df_a.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": n_nome, "Status": "Ativo", "CPF": n_cpf, "Nasc": n_nasc.strftime("%d/%m/%Y"),
                        "Sexo": n_sexo, "Faixa": n_faixa, "WhatsApp": n_tel, "Responsavel": n_resp, "Mensalidade": n_mensal,
                        "Vencimento": n_venc, "Filiacao": date.today().strftime("%d/%m/%Y"), "Obs": n_obs
                    }])
                    st.session_state.df_a = pd.concat([st.session_state.df_a, novo], ignore_index=True)
                    core.save_data(st.session_state.df_a, st.session_state.df_f)
                    st.success("Matrícula Efetuada!"); st.rerun()
                else: st.error("Preencha os campos obrigatórios.")

    with tab_e:
        st.subheader("Alteração de Cadastro")
        aluno_sel = st.selectbox("Selecione para Editar", st.session_state.df_a['Nome'].tolist() if not st.session_state.df_a.empty else ["Nenhum"])
        if aluno_sel != "Nenhum":
            idx = st.session_state.df_a[st.session_state.df_a['Nome'] == aluno_sel].index[0]
            atl = st.session_state.df_a.loc[idx]
            
            with st.form("form_edicao_master"):
                c1, c2, c3 = st.columns([2, 1, 1])
                u_nome = c1.text_input("Nome", value=str(atl['Nome']))
                u_status = c2.selectbox("Status", ["Ativo", "Inativo"], index=0 if atl['Status'] == 'Ativo' else 1)
                u_cpf = c3.text_input("CPF", value=str(atl['CPF']))
                
                c4, c5, c6 = st.columns(3)
                u_faixa = c4.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=0)
                u_mensal = c5.number_input("Mensalidade", value=float(atl['Mensalidade']))
                u_tel = c6.text_input("WhatsApp", value=str(atl['WhatsApp']))
                
                u_obs = st.text_area("Observações", value=str(atl['Obs']))
                
                if st.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.df_a.loc[idx, ["Nome", "Status", "CPF", "Faixa", "Mensalidade", "WhatsApp", "Obs"]] = [u_nome, u_status, u_cpf, u_faixa, u_mensal, u_tel, u_obs]
                    core.save_data(st.session_state.df_a, st.session_state.df_f)
                    st.success("Cadastro Atualizado!"); st.rerun()

# --- MODULO: FINANCEIRO (LANÇAMENTO E ESTORNO) ---
elif menu == "💰 Financeiro":
    st.title("💰 Controle de Mensalidades")
    tab_p, tab_r = st.tabs(["💵 Receber", "🔄 Estornar/Histórico"])
    
    with tab_p:
        ativos = st.session_state.df_a[st.session_state.df_a['Status'] == 'Ativo']
        if not ativos.empty:
            with st.form("form_pg", clear_on_submit=True):
                aluno_p = st.selectbox("Aluno", ativos['Nome'].tolist())
                c1, c2 = st.columns(2)
                f_data = c1.date_input("Data do PG")
                f_mes = c2.text_input("Mês Ref (MM/AAAA)", date.today().strftime("%m/%Y"))
                
                val_sug = float(ativos[ativos['Nome'] == aluno_p]['Mensalidade'].values[0])
                f_valor = st.number_input("Valor Recebido", value=val_sug)
                f_met = st.selectbox("Meio", ["PIX", "Dinheiro", "Cartão"])
                
                if st.form_submit_button("Confirmar Pagamento"):
                    lan_id = int(st.session_state.df_f['ID_Lan'].max() + 1) if not st.session_state.df_f.empty else 1
                    novo_lan = pd.DataFrame([{"ID_Lan": lan_id, "ID_Atleta": 0, "Nome": aluno_p, "Mes_Ref": f_mes, "Valor": f_valor, "Data_PG": f_data.strftime("%d/%m/%Y"), "Metodo": f_met}])
                    st.session_state.df_f = pd.concat([st.session_state.df_f, novo_lan], ignore_index=True)
                    core.save_data(st.session_state.df_a, st.session_state.df_f)
                    st.success("Pagamento Registrado!"); st.rerun()
        else: st.warning("Sem alunos ativos.")

    with tab_r:
        if not st.session_state.df_f.empty:
            st.subheader("Desfazer Lançamento")
            df_rev = st.session_state.df_f.iloc[::-1]
            lista_lan = [f"{r['ID_Lan']} - {r['Nome']} (R$ {r['Valor']:.2f})" for _, r in df_rev.iterrows()]
            escolha = st.selectbox("Selecione o lançamento para APAGAR", lista_lan)
            id_del = int(escolha.split(" - ")[0])
            
            if st.button("🔥 Confirmar Estorno"):
                st.session_state.df_f = st.session_state.df_f[st.session_state.df_f['ID_Lan'] != id_del]
                core.save_data(st.session_state.df_a, st.session_state.df_f)
                st.error("Lançamento Removido!"); time.sleep(0.5); st.rerun()
            
            st.divider()
            st.dataframe(st.session_state.df_f, use_container_width=True, hide_index=True)
