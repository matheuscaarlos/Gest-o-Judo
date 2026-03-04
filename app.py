import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date
import plotly.express as px

# --- 1. CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="Judô Pro v28", page_icon="🥋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #F8FAFC; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; }
    .stButton>button { border-radius: 8px; font-weight: 600; height: 3em; width: 100%; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    .status-ativo { color: #10B981; font-weight: bold; }
    .status-inativo { color: #EF4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (DATA ENGINE) ---
DB_ATLETAS = "atleta_v28.csv"
DB_FINANCEIRO = "fin_v28.csv"

def init_db():
    cols_a = ["ID", "Nome", "Status", "Faixa", "Telefone", "Responsavel", "Mensalidade", "Dia_Vencimento", "Data_Filiacao", "Obs"]
    cols_f = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Timestamp"]
    
    if not os.path.exists(DB_ATLETAS): pd.DataFrame(columns=cols_a).to_csv(DB_ATLETAS, index=False)
    if not os.path.exists(DB_FINANCEIRO): pd.DataFrame(columns=cols_f).to_csv(DB_FINANCEIRO, index=False)

def load_data():
    df_a = pd.read_csv(DB_ATLETAS)
    df_f = pd.read_csv(DB_FINANCEIRO)
    # Garantir tipos de dados corretos
    df_a['Mensalidade'] = pd.to_numeric(df_a['Mensalidade'], errors='coerce').fillna(0)
    df_f['Valor_Total'] = pd.to_numeric(df_f['Valor_Total'], errors='coerce').fillna(0)
    return df_a, df_f

def save_all(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

init_db()
if 'atletas' not in st.session_state:
    st.session_state.atletas, st.session_state.financeiro = load_data()

# --- 3. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 0.8, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🥋 Judô Pro</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            pw = st.text_input("Chave de Acesso", type="password")
            if st.button("Entrar"):
                if pw == "judo123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Chave inválida.")
    st.stop()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("Sistema de Gestão")
    aba = st.radio("Módulos", ["📊 Dashboard", "👥 Atletas", "💰 Financeiro", "⚙️ Ajustes"])
    st.divider()
    if st.button("Sair"):
        st.session_state.auth = False
        st.rerun()

# --- 5. MÓDULOS ---

# --- DASHBOARD ---
if aba == "📊 Dashboard":
    st.title("📊 Inteligência de Negócio")
    df_a = st.session_state.atletas
    df_f = st.session_state.financeiro
    
    c1, c2, c3, c4 = st.columns(4)
    ativos = df_a[df_a['Status'] == 'Ativo']
    c1.metric("Alunos Ativos", len(ativos))
    
    receita_mes = df_f[df_f['Mes_Ref'] == datetime.now().strftime("%m/%Y")]['Valor_Total'].sum()
    c2.metric("Receita (Mês Atual)", f"R$ {receita_mes:,.2f}")
    
    alvo = ativos['Mensalidade'].sum()
    c3.metric("Faturamento Alvo", f"R$ {alvo:,.2f}")
    
    gap = alvo - receita_mes
    c4.metric("Inadimplência Estimada", f"R$ {max(0, gap):,.2f}", delta=f"{gap:.2f}", delta_color="inverse")

    st.divider()
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        if not df_f.empty:
            st.subheader("Fluxo de Receita Mensal")
            graf_f = df_f.groupby('Mes_Ref')['Valor_Total'].sum().reset_index()
            st.plotly_chart(px.line(graf_f, x='Mes_Ref', y='Valor_Total', markers=True), use_container_width=True)
    with col_g2:
        st.subheader("Distribuição por Faixa")
        st.plotly_chart(px.pie(df_a, names='Faixa', hole=0.4), use_container_width=True)

# --- ATLETAS ---
elif aba == "👥 Atletas":
    st.title("👥 Gestão de Atletas")
    t_list, t_novo = st.tabs(["📋 Lista de Alunos", "➕ Matricular"])
    
    with t_list:
        busca = st.text_input("Pesquisar aluno...")
        df_view = st.session_state.atletas[st.session_state.atletas['Nome'].str.contains(busca, case=False, na=False)]
        st.dataframe(df_view, use_container_width=True, hide_index=True)
        
        if not df_view.empty:
            st.divider()
            st.subheader("Editar Atleta Selecionado")
            sel = st.selectbox("Escolha o aluno para modificar:", df_view['Nome'].tolist())
            idx = st.session_state.atletas[st.session_state.atletas['Nome'] == sel].index[0]
            
            with st.form("edit_atleta"):
                c1, c2, c3 = st.columns(3)
                e_status = c1.selectbox("Status", ["Ativo", "Inativo"], index=0 if st.session_state.atletas.loc[idx, 'Status'] == 'Ativo' else 1)
                e_faixa = c2.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=0)
                e_mensal = c3.number_input("Mensalidade", value=float(st.session_state.atletas.loc[idx, 'Mensalidade']))
                
                if st.form_submit_button("Salvar Alterações"):
                    st.session_state.atletas.loc[idx, ['Status', 'Faixa', 'Mensalidade']] = [e_status, e_faixa, e_mensal]
                    save_all(st.session_state.atletas, st.session_state.financeiro)
                    st.success("Dados atualizados!")
                    time.sleep(0.5); st.rerun()

    with t_novo:
        with st.form("cad_novo"):
            c1, c2 = st.columns(2)
            n_nome = c1.text_input("Nome Completo*")
            n_tel = c2.text_input("WhatsApp*")
            
            c3, c4, c5 = st.columns(3)
            n_faixa = c3.selectbox("Faixa Inicial", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            n_mensal = c4.number_input("Valor Mensalidade", 150.0)
            n_venc = c5.selectbox("Dia de Vencimento", list(range(1, 31)), index=4)
            
            if st.form_submit_button("Confirmar Matrícula"):
                if n_nome and n_tel:
                    new_id = int(st.session_state.atletas['ID'].max() + 1) if not st.session_state.atletas.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": n_nome, "Status": "Ativo", "Faixa": n_faixa, 
                        "Telefone": n_tel, "Mensalidade": n_mensal, "Dia_Vencimento": n_venc,
                        "Data_Filiacao": date.today().strftime("%d/%m/%Y")
                    }])
                    st.session_state.atletas = pd.concat([st.session_state.atletas, novo], ignore_index=True)
                    save_all(st.session_state.atletas, st.session_state.financeiro)
                    st.success("Matrícula realizada!"); time.sleep(1); st.rerun()

# --- FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💰 Controle Financeiro")
    
    col_reg, col_hist = st.columns([1, 1.5])
    
    with col_reg:
        st.subheader("Registrar Pagamento")
        ativos = st.session_state.atletas[st.session_state.atletas['Status'] == 'Ativo']
        if not ativos.empty:
            with st.form("reg_pag"):
                aluno = st.selectbox("Selecione o Aluno", ativos['Nome'].tolist())
                c_d, c_m = st.columns(2)
                f_data = c_d.date_input("Data do Recebimento", date.today())
                f_mes = c_m.text_input("Mês Ref (MM/AAAA)", date.today().strftime("%m/%Y"))
                
                f_val = st.number_input("Valor Pago", value=float(ativos[ativos['Nome'] == aluno]['Mensalidade'].values[0]))
                f_met = st.selectbox("Forma", ["PIX", "Dinheiro", "Cartão", "Misto"])
                
                if st.form_submit_button("Confirmar Recebimento"):
                    novo_p = pd.DataFrame([{
                        "ID_Atleta": ativos[ativos['Nome'] == aluno]['ID'].values[0],
                        "Nome_Atleta": aluno, "Mes_Ref": f_mes, "Valor_Total": f_val,
                        "Data_Pagamento": f_data.strftime("%d/%m/%Y"), "Metodo": f_met,
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }])
                    st.session_state.financeiro = pd.concat([st.session_state.financeiro, novo_p], ignore_index=True)
                    save_all(st.session_state.atletas, st.session_state.financeiro)
                    st.success(f"Pagamento de {aluno} registrado!")
                    st.code(f"--- RECIBO JUDÔ ---\nAluno: {aluno}\nValor: R${f_val:.2f}\nData: {f_data.strftime('%d/%m/%Y')}")
                    time.sleep(1); st.rerun()
        else: st.warning("Não há alunos ativos cadastrados.")

    with col_hist:
        st.subheader("Histórico de Entradas")
        # Filtro de Data Simples
        f_busca = st.text_input("Filtrar histórico (Nome ou Mês)...")
        df_hist = st.session_state.financeiro[st.session_state.financeiro['Nome_Atleta'].str.contains(f_busca, case=False, na=False) | 
                                            st.session_state.financeiro['Mes_Ref'].str.contains(f_busca, na=False)]
        st.dataframe(df_hist.tail(20), use_container_width=True, hide_index=True)

elif aba == "⚙️ Ajustes":
    st.title("⚙️ Configurações do Sistema")
    st.write("Versão do Banco de Dados: 28.0 (Estável)")
    if st.button("Baixar Backup dos Dados (CSV)"):
        st.download_button("Atletas", st.session_state.atletas.to_csv(index=False), "atletas_backup.csv", "text/csv")
        st.download_button("Financeiro", st.session_state.financeiro.to_csv(index=False), "financeiro_backup.csv", "text/csv")
