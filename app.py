import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date
import plotly.express as px

# --- 1. CORE CONFIGURATION & PROFESSIONAL UI ---
st.set_page_config(page_title="Judô Pro | Gestão Corporativa", page_icon="🥋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    /* Cores e Background */
    .stApp { background-color: #F1F5F9; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    
    /* Metrics Premium */
    div[data-testid="stMetric"] {
        background-color: white; border: 1px solid #E2E8F0;
        padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Botões de Ação */
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #2563EB; color: white; font-weight: 600; border: none;
    }
    .stButton>button:hover { background-color: #1D4ED8; border: none; color: white; }
    
    /* Estorno Button */
    .btn-estorno > div > button { background-color: #DC2626 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (DATABASE LAYER) ---
class Database:
    ATLETAS = "db_atletas_pro.csv"
    FINANCEIRO = "db_financeiro_pro.csv"
    
    COLS_A = ["ID", "Nome", "Status", "CPF", "Nascimento", "Sexo", "Faixa", "Telefone", "Responsavel", "CPF_Resp", "Mensalidade", "Vencimento", "Filiacao", "Obs"]
    COLS_F = ["ID_Lan", "ID_Atleta", "Nome", "Mes_Ref", "Valor", "Data_PG", "Metodo"]

    @classmethod
    def initialize(cls):
        if not os.path.exists(cls.ATLETAS): pd.DataFrame(columns=cls.COLS_A).to_csv(cls.ATLETAS, index=False)
        if not os.path.exists(cls.FINANCEIRO): pd.DataFrame(columns=cls.COLS_F).to_csv(cls.FINANCEIRO, index=False)

    @classmethod
    def load(cls):
        df_a = pd.read_csv(cls.ATLETAS)
        df_f = pd.read_csv(cls.FINANCEIRO)
        # Sanitização de tipos
        df_a['Mensalidade'] = pd.to_numeric(df_a['Mensalidade'], errors='coerce').fillna(0.0)
        df_f['Valor'] = pd.to_numeric(df_f['Valor'], errors='coerce').fillna(0.0)
        return df_a, df_f

    @classmethod
    def save(cls, df_a, df_f):
        df_a.to_csv(cls.ATLETAS, index=False)
        df_f.to_csv(cls.FINANCEIRO, index=False)

Database.initialize()
if 'db_a' not in st.session_state:
    st.session_state.db_a, st.session_state.db_f = Database.load()

# --- 3. AUTHENTICATION ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col_log, _ = st.columns([1, 0.8, 1])
    with col_log:
        st.markdown("<h1 style='text-align:center;'>🥋 Judô Pro</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            pw = st.text_input("Senha Master", type="password")
            if st.button("Acessar Painel"):
                if pw == "judo123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Acesso Negado")
    st.stop()

# --- 4. NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043831.png", width=80)
    menu = st.radio("SISTEMA", ["📊 Dashboard", "👥 Gestão de Alunos", "💰 Financeiro", "⚙️ Backup"])
    st.divider()
    if st.button("Deslogar"):
        st.session_state.auth = False
        st.rerun()

# --- 5. MODULES ---

# DASHBOARD
if menu == "📊 Dashboard":
    st.title("📊 Indicadores Gerenciais")
    df_a, df_f = st.session_state.db_a, st.session_state.db_f
    
    ativos = df_a[df_a['Status'] == 'Ativo']
    faturamento_alvo = ativos['Mensalidade'].sum()
    recebido_mes = df_f[df_f['Mes_Ref'] == datetime.now().strftime("%m/%Y")]['Valor'].sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Alunos Ativos", len(ativos))
    m2.metric("Inadimplência Est.", f"R$ {max(0, faturamento_alvo - recebido_mes):,.2f}", delta_color="inverse")
    m3.metric("Faturamento Alvo", f"R$ {faturamento_alvo:,.2f}")
    m4.metric("Recebido (Mês)", f"R$ {recebido_mes:,.2f}")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Faturamento por Mês")
        if not df_f.empty:
            df_chart = df_f.groupby('Mes_Ref')['Valor'].sum().reset_index()
            st.plotly_chart(px.bar(df_chart, x='Mes_Ref', y='Valor', color_discrete_sequence=['#2563EB']), use_container_width=True)
    with col_g2:
        st.subheader("População por Faixa")
        st.plotly_chart(px.pie(df_a, names='Faixa', hole=0.4), use_container_width=True)

# GESTÃO DE ALUNOS
elif menu == "👥 Gestão de Alunos":
    st.title("👥 Controle de Atletas")
    t_list, t_cad, t_edit = st.tabs(["📋 Listagem", "✨ Matrícula", "🔧 Edição Completa"])
    
    with t_list:
        st.dataframe(st.session_state.db_a, use_container_width=True, hide_index=True)

    with t_cad:
        with st.form("cad_atleta", clear_on_submit=True):
            st.subheader("Nova Matrícula")
            c1, c2, c3 = st.columns([2, 1, 1])
            nome = c1.text_input("Nome Completo*")
            cpf = c2.text_input("CPF*")
            nasc = c3.date_input("Nascimento", date(2010, 1, 1))
            
            c4, c5, c6 = st.columns(3)
            sexo = c4.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            faixa = c5.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            tel = c6.text_input("WhatsApp*")
            
            c7, c8 = st.columns(2)
            mensal = c7.number_input("Mensalidade (R$)", 150.0)
            venc = c8.selectbox("Dia de Vencimento", list(range(1, 31)), index=4)
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome and cpf:
                    new_id = int(st.session_state.db_a['ID'].max() + 1) if not st.session_state.db_a.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Status": "Ativo", "CPF": cpf, "Nascimento": nasc.strftime("%d/%m/%Y"),
                        "Sexo": sexo, "Faixa": faixa, "Telefone": tel, "Mensalidade": mensal, "Vencimento": venc,
                        "Filiacao": date.today().strftime("%d/%m/%Y")
                    }])
                    st.session_state.db_a = pd.concat([st.session_state.db_a, novo], ignore_index=True)
                    Database.save(st.session_state.db_a, st.session_state.db_f)
                    st.success("Salvo!"); st.rerun()
                else: st.error("Preencha Nome e CPF")

    with t_edit:
        st.subheader("Edição de Dados")
        aluno_ed = st.selectbox("Escolha o aluno para alterar", st.session_state.db_a['Nome'].tolist())
        idx = st.session_state.db_a[st.session_state.db_a['Nome'] == aluno_ed].index[0]
        atleta = st.session_state.db_a.loc[idx]
        
        with st.form("form_edicao"):
            c1, c2, c3 = st.columns([2, 1, 1])
            u_nome = c1.text_input("Nome", value=atleta['Nome'])
            u_status = c2.selectbox("Status", ["Ativo", "Inativo"], index=0 if atleta['Status'] == 'Ativo' else 1)
            u_faixa = c3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=0)
            
            u_tel = st.text_input("Telefone", value=str(atleta['Telefone']))
            u_mensal = st.number_input("Mensalidade", value=float(atleta['Mensalidade']))
            u_venc = st.number_input("Vencimento", 1, 31, value=int(atleta['Vencimento']))
            u_obs = st.text_area("Observações", value=str(atleta['Obs']) if pd.notnull(atleta['Obs']) else "")
            
            if st.form_submit_button("Salvar Alterações"):
                st.session_state.db_a.loc[idx, ["Nome", "Status", "Faixa", "Telefone", "Mensalidade", "Vencimento", "Obs"]] = [u_nome, u_status, u_faixa, u_tel, u_mensal, u_venc, u_obs]
                Database.save(st.session_state.db_a, st.session_state.db_f)
                st.success("Dados Atualizados!"); st.rerun()

# FINANCEIRO
elif menu == "💰 Financeiro":
    st.title("💰 Controle de Caixa")
    tab_p, tab_e = st.tabs(["💵 Recebimento", "🔄 Estorno (Desfazer)"])
    
    with tab_p:
        with st.form("pagamento"):
            st.subheader("Registrar Entrada")
            ativos = st.session_state.db_a[st.session_state.db_a['Status'] == 'Ativo']
            aluno = st.selectbox("Aluno", ativos['Nome'].tolist())
            c1, c2 = st.columns(2)
            data_p = c1.date_input("Data do Pagamento")
            mes_r = c2.text_input("Mês Referência", date.today().strftime("%m/%Y"))
            valor = st.number_input("Valor", value=float(ativos[ativos['Nome'] == aluno]['Mensalidade'].values[0]))
            metodo = st.selectbox("Metodo", ["PIX", "Dinheiro", "Cartão"])
            
            if st.form_submit_button("Confirmar Baixa"):
                lan_id = int(st.session_state.db_f['ID_Lan'].max() + 1) if not st.session_state.db_f.empty else 1
                novo_pg = pd.DataFrame([{"ID_Lan": lan_id, "ID_Atleta": 0, "Nome": aluno, "Mes_Ref": mes_r, "Valor": valor, "Data_PG": data_p.strftime("%d/%m/%Y"), "Metodo": metodo}])
                st.session_state.db_f = pd.concat([st.session_state.db_f, novo_pg], ignore_index=True)
                Database.save(st.session_state.db_a, st.session_state.db_f)
                st.success("Pago!"); st.rerun()

    with tab_e:
        st.subheader("Anular Pagamento")
        if not st.session_state.db_f.empty:
            df_reverso = st.session_state.db_f.iloc[::-1]
            opcoes = [f"{r['ID_Lan']} - {r['Nome']} (R$ {r['Valor']:.2f})" for _, r in df_reverso.iterrows()]
            escolha = st.selectbox("Selecione o lançamento para APAGAR", opcoes)
            id_del = int(escolha.split(" - ")[0])
            
            st.markdown(f"**Confirma a exclusão definitiva do lançamento #{id_del}?**")
            st.markdown('<div class="btn-estorno">', unsafe_allow_html=True)
            if st.button("EXCLUIR PAGAMENTO"):
                st.session_state.db_f = st.session_state.db_f[st.session_state.db_f['ID_Lan'] != id_del]
                Database.save(st.session_state.db_a, st.session_state.db_f)
                st.error("Lançamento Removido!"); time.sleep(1); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
            st.dataframe(st.session_state.db_f, use_container_width=True)

# BACKUP
elif menu == "⚙️ Backup":
    st.title("⚙️ Administração de Dados")
    st.write("Baixe seus dados para segurança externa (Excel/CSV)")
    c1, c2 = st.columns(2)
    c1.download_button("📥 Baixar Base de Alunos", st.session_state.db_a.to_csv(index=False), "alunos.csv")
    c2.download_button("📥 Baixar Base Financeira", st.session_state.db_f.to_csv(index=False), "financeiro.csv")
