import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date
import plotly.express as px

# --- 1. CORE ENGINE & DESIGN SYSTEM ---
st.set_page_config(page_title="Judô Pro | Gestão Enterprise", page_icon="🥋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F1F5F9; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    
    /* Dashboard Cards */
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 12px; padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #E2E8F0;
    }
    
    /* Buttons Customization */
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.2rem; background-color: #2563EB;
        color: white; font-weight: 600; border: none; transition: 0.2s;
    }
    .stButton>button:hover { background-color: #1D4ED8; transform: translateY(-1px); }
    .btn-danger > div > button { background-color: #DC2626 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA PERSISTENCE LAYER (BLINDADA) ---
class JudoDB:
    FILE_A = "db_atletas_v46.csv"
    FILE_F = "db_financeiro_v46.csv"
    
    COLS_A = [
        "ID", "Nome", "Status", "CPF", "Nasc", "Faixa", "WhatsApp", 
        "Resp_Legal", "CPF_Resp", "Emergencia", "Obs_Saude", "LGPD", "Data_Aceite"
    ]
    COLS_F = ["ID_Lan", "ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor", "Data_PG", "Metodo"]

    @classmethod
    def init(cls):
        if not os.path.exists(cls.FILE_A): pd.DataFrame(columns=cls.COLS_A).to_csv(cls.FILE_A, index=False)
        if not os.path.exists(cls.FILE_F): pd.DataFrame(columns=cls.COLS_F).to_csv(cls.FILE_F, index=False)

    @classmethod
    def load(cls):
        df_a = pd.read_csv(cls.FILE_A).fillna("")
        df_f = pd.read_csv(cls.FILE_F).fillna("")
        # Normalização de tipos para evitar erros de cálculo
        df_f['Valor'] = pd.to_numeric(df_f['Valor'], errors='coerce').fillna(0.0)
        return df_a, df_f

    @classmethod
    def save(cls, df_a, df_f):
        df_a.to_csv(cls.FILE_A, index=False)
        df_f.to_csv(cls.FILE_F, index=False)

JudoDB.init()

# --- 3. SESSION STATE MANAGEMENT ---
if 'db_a' not in st.session_state:
    st.session_state.db_a, st.session_state.db_f = JudoDB.load()

# --- 4. NAVIGATION & SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043831.png", width=80)
    st.title("JUDÔ PRO")
    menu = st.radio("SISTEMA", ["📊 Dashboards", "👥 Atletas", "💰 Financeiro", "⚙️ Config/Backup"])
    st.divider()
    st.caption(f"Versão 46.0 | {datetime.now().strftime('%Y')}")

# --- MÓDULO: ATLETAS (GESTÃO 360º) ---
if menu == "👥 Atletas":
    st.title("👥 Gestão de Atletas")
    tab_list, tab_cad, tab_edit = st.tabs(["📋 Listagem Ativa", "➕ Nova Matrícula", "🔧 Edição Rápida"])
    
    with tab_list:
        # Busca inteligente
        search = st.text_input("🔍 Buscar por nome ou CPF")
        df_show = st.session_state.db_a
        if search:
            df_show = df_show[df_show['Nome'].str.contains(search, case=False) | df_show['CPF'].str.contains(search)]
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    with tab_cad:
        with st.form("form_cadastro_v46", clear_on_submit=True):
            st.subheader("Ficha de Matrícula (Padrão PT-BR)")
            c1, c2, c3 = st.columns([2, 1, 1])
            nome = c1.text_input("Nome Completo*")
            cpf = c2.text_input("CPF*")
            nasc = c3.date_input("Nascimento", date(2010, 1, 1), format="DD/MM/YYYY")
            
            st.markdown("---")
            st.caption("🛡️ Seção LGPD & Emergência")
            e1, e2, e3 = st.columns(3)
            resp = e1.text_input("Responsável (Se menor)")
            emerg = e2.text_input("WhatsApp Emergência*")
            faixa = e3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            
            obs = st.text_area("Histórico Médico / Alergias")
            aceite = st.checkbox("Autorizo o tratamento de dados conforme LGPD para fins esportivos.*")
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome and cpf and aceite:
                    new_id = int(st.session_state.db_a['ID'].max() + 1) if not st.session_state.db_a.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Status": "Ativo", "CPF": cpf, "Nasc": nasc.strftime("%d/%m/%Y"),
                        "Faixa": faixa, "WhatsApp": emerg, "Resp_Legal": resp, "Emergencia": emerg,
                        "Obs_Saude": obs, "LGPD": "Sim", "Data_Aceite": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }])
                    st.session_state.db_a = pd.concat([st.session_state.db_a, novo], ignore_index=True)
                    JudoDB.save(st.session_state.db_a, st.session_state.db_f)
                    st.success("Atleta matriculado com sucesso!"); st.rerun()
                else: st.error("Erro: Preencha os campos obrigatórios e aceite a LGPD.")

# --- MÓDULO: FINANCEIRO (LANÇAMENTO COM MÉTODO) ---
elif menu == "💰 Financeiro":
    st.title("💰 Controle Financeiro")
    t_pag, t_hist = st.tabs(["💵 Lançar Pagamento", "🔄 Histórico e Estorno"])
    
    with t_pag:
        with st.form("baixa_pagamento"):
            ativos = st.session_state.db_a[st.session_state.db_a['Status'] == 'Ativo']
            aluno = st.selectbox("Selecione o Aluno", ativos['Nome'].tolist() if not ativos.empty else ["Nenhum"])
            
            f1, f2, f3 = st.columns(3)
            valor = f1.number_input("Valor (R$)", min_value=0.0, value=150.0)
            data_pg = f2.date_input("Data do Recebimento", format="DD/MM/YYYY")
            metodo = f3.selectbox("Método", ["PIX", "Dinheiro", "Cartão", "Boleto"])
            
            mes_ref = st.text_input("Mês Referência", date.today().strftime("%m/%Y"))
            
            if st.form_submit_button("Confirmar Baixa de Mensalidade"):
                lan_id = int(st.session_state.db_f['ID_Lan'].max() + 1) if not st.session_state.db_f.empty else 1
                novo_pg = pd.DataFrame([{
                    "ID_Lan": lan_id, "Nome_Atleta": aluno, "Mes_Ref": mes_ref, 
                    "Valor": valor, "Data_PG": data_pg.strftime("%d/%m/%Y"), "Metodo": metodo
                }])
                st.session_state.db_f = pd.concat([st.session_state.db_f, novo_pg], ignore_index=True)
                JudoDB.save(st.session_state.db_a, st.session_state.db_f)
                st.success(f"Pagamento de {aluno} registrado!"); st.rerun()

    with t_hist:
        st.subheader("Anulação de Lançamentos")
        if not st.session_state.db_f.empty:
            df_rev = st.session_state.db_f.iloc[::-1] # Ver mais recentes primeiro
            sel = st.selectbox("Escolha o lançamento para estornar", [f"{r['ID_Lan']} - {r['Nome_Atleta']} (R$ {r['Valor']:.2f})" for _, r in df_rev.iterrows()])
            id_del = int(sel.split(" - ")[0])
            
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("🔥 DESFAZER PAGAMENTO"):
                st.session_state.db_f = st.session_state.db_f[st.session_state.db_f['ID_Lan'] != id_del]
                JudoDB.save(st.session_state.db_a, st.session_state.db_f)
                st.error("Lançamento estornado!"); time.sleep(1); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
            st.dataframe(st.session_state.db_f, use_container_width=True, hide_index=True)

# --- MÓDULO: DASHBOARDS (VISUALIZAÇÃO DE DADOS) ---
elif menu == "📊 Dashboards":
    st.title("📊 Indicadores Gerenciais")
    df_a, df_f = st.session_state.db_a, st.session_state.db_f
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']))
    m2.metric("Arrecadação Total", f"R$ {df_f['Valor'].sum():,.2f}")
    m3.metric("Ticket Médio", f"R$ {df_f['Valor'].mean() if not df_f.empty else 0:,.2f}")

    if not df_f.empty:
        # Gráfico de Faturamento por Método
        fig = px.pie(df_f, values='Valor', names='Metodo', title="Distribuição por Meio de Pagamento", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# --- MÓDULO: BACKUP ---
elif menu == "⚙️ Config/Backup":
    st.title("⚙️ Administração")
    st.subheader("💾 Exportação de Segurança")
    st.write("Baixe suas bases de dados para salvaguarda externa.")
    st.download_button("📥 Backup Atletas (CSV)", df_a.to_csv(index=False), "backup_atletas.csv")
    st.download_button("📥 Backup Financeiro (CSV)", df_f.to_csv(index=False), "backup_financeiro.csv")
