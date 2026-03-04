import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date

# --- 1. CONFIGURAÇÃO DE AMBIENTE E UI ---
st.set_page_config(page_title="Judô Pro | Gestão de Elite", page_icon="🥋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    .stButton>button { border-radius: 8px; font-weight: 600; height: 3.5rem; transition: 0.3s; }
    .stMetric { background-color: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CAMADA DE DADOS (REPOSITORY) ---
class AcademiaDB:
    ATLETAS_FILE = "db_atletas_v45.csv"
    FINANCEIRO_FILE = "db_financeiro_v45.csv"
    
    COLS_A = [
        "ID", "Nome", "Status", "CPF", "Nasc", "Faixa", "WhatsApp", 
        "Responsavel_Legal", "CPF_Resp", "Contato_Emergencia", 
        "Alergias_Saude", "Consentimento_LGPD", "Data_Aceite"
    ]
    COLS_F = ["ID_Lan", "ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor", "Data_PG", "Metodo"]

    @classmethod
    def init(cls):
        if not os.path.exists(cls.ATLETAS_FILE): pd.DataFrame(columns=cls.COLS_A).to_csv(cls.ATLETAS_FILE, index=False)
        if not os.path.exists(cls.FINANCEIRO_FILE): pd.DataFrame(columns=cls.COLS_F).to_csv(cls.FINANCEIRO_FILE, index=False)

    @classmethod
    def load(cls):
        df_a = pd.read_csv(cls.ATLETAS_FILE).fillna("")
        df_f = pd.read_csv(cls.FINANCEIRO_FILE).fillna("")
        # Sanitização de tipos numéricos
        df_a['ID'] = pd.to_numeric(df_a['ID'], errors='coerce')
        df_f['Valor'] = pd.to_numeric(df_f['Valor'], errors='coerce').fillna(0.0)
        return df_a, df_f

    @classmethod
    def save(cls, df_a, df_f):
        df_a.to_csv(cls.ATLETAS_FILE, index=False)
        df_f.to_csv(cls.FINANCEIRO_FILE, index=False)

# Inicialização
AcademiaDB.init()
if 'db_a' not in st.session_state:
    st.session_state.db_a, st.session_state.db_f = AcademiaDB.load()

# --- 3. NAVEGAÇÃO ---
with st.sidebar:
    st.title("🥋 ASSOCIAÇÃO MARTINS")
    menu = st.radio("MÓDULOS", ["📊 Dashboard", "👥 Cadastro Atletas", "💰 Gestão Financeira", "⚙️ Backup & LGPD"])

# --- 4. MÓDULO: CADASTRO COM LGPD ---
if menu == "👥 Cadastro Atletas":
    st.title("👥 Gestão de Matrículas")
    tab_list, tab_cad = st.tabs(["📋 Lista de Alunos", "➕ Nova Matrícula (LGPD)"])
    
    with tab_list:
        st.dataframe(st.session_state.db_a, use_container_width=True, hide_index=True)
        
    with tab_cad:
        with st.form("form_matriz", clear_on_submit=True):
            st.subheader("Ficha de Cadastro Oficial")
            c1, c2, c3 = st.columns([2, 1, 1])
            nome = c1.text_input("Nome Completo*")
            cpf = c2.text_input("CPF do Atleta*")
            nasc = c3.date_input("Nascimento", date(2010, 1, 1), format="DD/MM/YYYY")
            
            st.markdown("---")
            st.caption("🛡️ Proteção e Responsabilidade (LGPD)")
            e1, e2, e3 = st.columns(3)
            resp = e1.text_input("Responsável Legal (se menor)")
            resp_cpf = e2.text_input("CPF do Responsável")
            emerg = e3.text_input("Tel. Emergência*")
            
            saude = st.text_area("Dados Sensíveis: Histórico de Saúde/Alergias")
            
            st.info("📜 Termo: Autorizo o tratamento de dados para fins de gestão acadêmica e segurança.")
            aceite = st.checkbox("Li e concordo com os termos de privacidade (LGPD)")
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome and cpf and aceite:
                    new_id = int(st.session_state.db_a['ID'].max() + 1) if not st.session_state.db_a.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Status": "Ativo", "CPF": cpf, 
                        "Nasc": nasc.strftime("%d/%m/%Y"), "Faixa": "Branca", "WhatsApp": emerg,
                        "Responsavel_Legal": resp, "CPF_Resp": resp_cpf, "Contato_Emergencia": emerg,
                        "Alergias_Saude": saude, "Consentimento_LGPD": "Sim", 
                        "Data_Aceite": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }])
                    st.session_state.db_a = pd.concat([st.session_state.db_a, novo], ignore_index=True)
                    AcademiaDB.save(st.session_state.db_a, st.session_state.db_f)
                    st.success("Matrícula Concluída!"); st.rerun()

# --- 5. MÓDULO: FINANCEIRO (LANÇAMENTO E ESTORNO) ---
elif menu == "💰 Gestão Financeira":
    st.title("💰 Controle de Caixa")
    t_lan, t_est = st.tabs(["💵 Lançar Pagamento", "🔄 Histórico e Estorno"])
    
    with t_lan:
        with st.form("form_pg"):
            ativos = st.session_state.db_a[st.session_state.db_a['Status'] == 'Ativo']
            aluno = st.selectbox("Selecione o Aluno", ativos['Nome'].tolist() if not ativos.empty else ["Nenhum"])
            
            col_f1, col_f2 = st.columns(2)
            data_pg = col_f1.date_input("Data do Recebimento", format="DD/MM/YYYY")
            mes_ref = col_f2.text_input("Mês de Referência", date.today().strftime("%m/%Y"))
            
            valor = st.number_input("Valor Recebido (R$)", value=150.0)
            metodo = st.selectbox("Método de Pagamento", ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Boleto"])
            
            if st.form_submit_button("Confirmar Recebimento"):
                lan_id = int(st.session_state.db_f['ID_Lan'].max() + 1) if not st.session_state.db_f.empty else 1
                novo_pg = pd.DataFrame([{
                    "ID_Lan": lan_id, "Nome_Atleta": aluno, "Mes_Ref": mes_ref, 
                    "Valor": valor, "Data_PG": data_pg.strftime("%d/%m/%Y"), "Metodo": metodo
                }])
                st.session_state.db_f = pd.concat([st.session_state.db_f, novo_pg], ignore_index=True)
                AcademiaDB.save(st.session_state.db_a, st.session_state.db_f)
                st.success("Pagamento Registrado!"); st.rerun()

    with t_est:
        st.subheader("Desfazer Pagamento")
        if not st.session_state.db_f.empty:
            # Ordenação do mais recente
            df_hist = st.session_state.db_f.iloc[::-1]
            opcoes = [f"{r['ID_Lan']} - {r['Nome_Atleta']} (R$ {r['Valor']:.2f})" for _, r in df_hist.iterrows()]
            sel = st.selectbox("Escolha o lançamento para anular", opcoes)
            id_del = int(sel.split(" - ")[0])
            
            if st.button("🔥 Confirmar Estorno Definitivo"):
                st.session_state.db_f = st.session_state.db_f[st.session_state.db_f['ID_Lan'] != id_del]
                AcademiaDB.save(st.session_state.db_a, st.session_state.db_f)
                st.error("Lançamento Removido!"); time.sleep(1); st.rerun()
            
            st.divider()
            st.dataframe(st.session_state.db_f, use_container_width=True, hide_index=True)

# --- 6. DASHBOARD ---
elif menu == "📊 Dashboard":
    st.title("📊 Indicadores Gerenciais")
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(st.session_state.db_a[st.session_state.db_a['Status'] == 'Ativo']))
    c2.metric("Receita Total", f"R$ {st.session_state.db_f['Valor'].sum():,.2f}")
    c3.metric("Lançamentos", len(st.session_state.db_f))

# --- 7. BACKUP ---
elif menu == "⚙️ Backup & LGPD":
    st.title("⚙️ Segurança de Dados")
    st.download_button("📥 Baixar Base de Alunos (CSV)", st.session_state.db_a.to_csv(index=False), "backup_alunos.csv")
    st.download_button("📥 Baixar Histórico Financeiro (CSV)", st.session_state.db_f.to_csv(index=False), "backup_financeiro.csv")
