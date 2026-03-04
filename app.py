import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date

# --- 1. CONFIGURAÇÃO CORPORATIVA ---
st.set_page_config(page_title="Judô Pro | Enterprise", page_icon="🥋", layout="wide")

# --- 2. DESIGN SYSTEM (PROFISSIONAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Configuração Global */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F1F5F9; }
    
    /* Sidebar Slate Dark */
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    
    /* Cards e Métricas */
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 12px; padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #E2E8F0;
    }
    
    /* Botões de Alta Performance */
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5rem; background-color: #2563EB;
        color: white; font-weight: 600; border: none; transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #1D4ED8; transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    
    /* Botão Perigo (Estorno) */
    .btn-danger > div > button { background-color: #DC2626 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CAMADA DE DADOS (ENGINE) ---
class JudoEngine:
    @staticmethod
    def initialize():
        files = {
            "db_atletas.csv": ["ID", "Nome", "Status", "CPF", "Nasc", "Sexo", "Faixa", "WhatsApp", "Mensalidade", "Vencimento", "Filiacao", "Obs"],
            "db_financeiro.csv": ["ID_Lan", "ID_Atleta", "Nome", "Mes_Ref", "Valor", "Data_PG", "Metodo"]
        }
        for file, cols in files.items():
            if not os.path.exists(file):
                pd.DataFrame(columns=cols).to_csv(file, index=False)

    @staticmethod
    def load_atletas():
        df = pd.read_csv("db_atletas.csv").fillna("")
        df['Mensalidade'] = pd.to_numeric(df['Mensalidade'], errors='coerce').fillna(0.0)
        return df

    @staticmethod
    def load_financeiro():
        df = pd.read_csv("db_financeiro.csv").fillna("")
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0.0)
        return df

    @staticmethod
    def commit(df_a, df_f):
        df_a.to_csv("db_atletas.csv", index=False)
        df_f.to_csv("db_financeiro.csv", index=False)

# Inicialização
JudoEngine.initialize()

# --- 4. GESTÃO DE ESTADO (SESSION) ---
if 'db_a' not in st.session_state:
    st.session_state.db_a = JudoEngine.load_atletas()
if 'db_f' not in st.session_state:
    st.session_state.db_f = JudoEngine.load_financeiro()
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- 5. SEGURANÇA ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 0.8, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>🥋 Judô Pro Login</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            pw = st.text_input("Chave Administrativa", type="password")
            if st.button("Autenticar"):
                if pw == "judo123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Acesso negado.")
    st.stop()

# --- 6. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### ⚙️ Administração")
    menu = st.radio("MÓDULOS", ["📊 Dashboards", "👥 Atletas", "💰 Caixa e Fluxo"])
    st.divider()
    if st.button("Encerrar Sessão"):
        st.session_state.auth = False
        st.rerun()

# --- MÓDULO 1: DASHBOARDS ---
if menu == "📊 Dashboards":
    st.title("📊 Indicadores de Performance")
    df_a, df_f = st.session_state.db_a, st.session_state.db_f
    
    ativos = df_a[df_a['Status'] == 'Ativo']
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Alunos Ativos", len(ativos))
    c2.metric("Inativos", len(df_a[df_a['Status'] == 'Inativo']))
    
    fat_alvo = ativos['Mensalidade'].sum()
    fat_real = df_f[df_f['Mes_Ref'] == datetime.now().strftime("%m/%Y")]['Valor'].sum()
    
    c3.metric("Receita Alvo", f"R$ {fat_alvo:,.2f}")
    c4.metric("Receita Real (Mês)", f"R$ {fat_real:,.2f}", delta=f"R$ {fat_real - fat_alvo:,.2f}")

# --- MÓDULO 2: ATLETAS (GESTÃO TOTAL) ---
elif menu == "👥 Atletas":
    st.title("👥 Gestão de Atletas")
    tab_l, tab_c, tab_e = st.tabs(["📋 Listagem", "➕ Nova Matrícula", "🔧 Edição Completa"])
    
    with tab_l:
        st.dataframe(st.session_state.db_a, use_container_width=True, hide_index=True)

    with tab_c:
        with st.form("cad_atleta", clear_on_submit=True):
            st.subheader("Nova Matrícula")
            c1, c2, c3 = st.columns([2, 1, 1])
            nome = c1.text_input("Nome Completo*")
            cpf = c2.text_input("CPF*")
            nasc = c3.date_input("Nascimento", date(2010, 1, 1))
            
            c4, c5, c6 = st.columns(3)
            sexo = c4.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            faixa = c5.selectbox("Faixa", ["Branca", "Azul", "Amarela", "Verde", "Roxa", "Marrom", "Preta"])
            tel = c6.text_input("WhatsApp*")
            
            c7, c8 = st.columns(2)
            mensal = c7.number_input("Mensalidade (R$)", value=150.0)
            venc = c8.selectbox("Vencimento", list(range(1, 31)), index=4)
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome and cpf:
                    new_id = int(st.session_state.db_a['ID'].max() + 1) if not st.session_state.db_a.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Status": "Ativo", "CPF": cpf, "Nasc": nasc.strftime("%d/%m/%Y"),
                        "Sexo": sexo, "Faixa": faixa, "WhatsApp": tel, "Mensalidade": mensal, "Vencimento": venc,
                        "Filiacao": date.today().strftime("%d/%m/%Y")
                    }])
                    st.session_state.db_a = pd.concat([st.session_state.db_a, novo], ignore_index=True)
                    JudoEngine.commit(st.session_state.db_a, st.session_state.db_f)
                    st.success("Matrícula realizada!"); time.sleep(1); st.rerun()

    with tab_e:
        if not st.session_state.db_a.empty:
            sel_atleta = st.selectbox("Escolha o atleta para editar", st.session_state.db_a['Nome'].tolist())
            idx = st.session_state.db_a[st.session_state.db_a['Nome'] == sel_atleta].index[0]
            atl = st.session_state.db_a.loc[idx]
            
            with st.form("edit_atleta"):
                st.subheader(f"Editando: {atl['Nome']}")
                c1, c2, c3 = st.columns([2, 1, 1])
                u_nome = c1.text_input("Nome", value=str(atl['Nome']))
                u_status = c2.selectbox("Status", ["Ativo", "Inativo"], index=0 if atl['Status'] == 'Ativo' else 1)
                u_cpf = c3.text_input("CPF", value=str(atl['CPF']))
                
                u_mensal = st.number_input("Mensalidade", value=float(atl['Mensalidade']))
                u_faixa = st.selectbox("Faixa", ["Branca", "Azul", "Amarela", "Verde", "Roxa", "Marrom", "Preta"])
                
                if st.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.db_a.loc[idx, ["Nome", "Status", "CPF", "Mensalidade", "Faixa"]] = [u_nome, u_status, u_cpf, u_mensal, u_faixa]
                    JudoEngine.commit(st.session_state.db_a, st.session_state.db_f)
                    st.success("Atualizado!"); st.rerun()

# --- MÓDULO 3: FINANCEIRO (CAIXA E ESTORNO) ---
elif menu == "💰 Caixa e Fluxo":
    st.title("💰 Gestão de Caixa")
    tab_p, tab_h = st.tabs(["💵 Lançar Pagamento", "🔄 Histórico e Estorno"])
    
    with tab_p:
        ativos = st.session_state.db_a[st.session_state.db_a['Status'] == 'Ativo']
        if not ativos.empty:
            with st.form("pag_form", clear_on_submit=True):
                aluno = st.selectbox("Selecione o Aluno", ativos['Nome'].tolist())
                c1, c2 = st.columns(2)
                p_data = c1.date_input("Data do Recebimento")
                p_mes = c2.text_input("Mês de Referência (MM/AAAA)", date.today().strftime("%m/%Y"))
                
                v_sug = float(ativos[ativos['Nome'] == aluno]['Mensalidade'].values[0])
                p_valor = st.number_input("Valor Pago", value=v_sug)
                
                if st.form_submit_button("Confirmar Baixa"):
                    lan_id = int(st.session_state.db_f['ID_Lan'].max() + 1) if not st.session_state.db_f.empty else 1
                    novo_p = pd.DataFrame([{
                        "ID_Lan": lan_id, "Nome": aluno, "Mes_Ref": p_mes, "Valor": p_valor, "Data_PG": p_data.strftime("%d/%m/%Y")
                    }])
                    st.session_state.db_f = pd.concat([st.session_state.db_f, novo_p], ignore_index=True)
                    JudoEngine.commit(st.session_state.db_a, st.session_state.db_f)
                    st.success("Recebimento registrado!"); st.rerun()
        else: st.warning("Nenhum aluno ativo para recebimento.")

    with tab_h:
        st.subheader("Anulação de Lançamentos")
        if not st.session_state.db_f.empty:
            df_v = st.session_state.db_f.iloc[::-1]
            opcoes = [f"{r['ID_Lan']} | {r['Nome']} | R$ {r['Valor']:.2f}" for _, r in df_v.iterrows()]
            escolha = st.selectbox("Selecione o lançamento para estornar", opcoes)
            id_del = int(escolha.split(" | ")[0])
            
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("EXCLUIR REGISTRO"):
                st.session_state.db_f = st.session_state.db_f[st.session_state.db_f['ID_Lan'] != id_del]
                JudoEngine.commit(st.session_state.db_a, st.session_state.db_f)
                st.error("Lançamento excluído!"); time.sleep(0.5); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
            st.dataframe(st.session_state.db_f, use_container_width=True, hide_index=True)
