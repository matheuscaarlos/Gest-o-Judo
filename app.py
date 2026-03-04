import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro | Gestão de Academia", page_icon="🥋", layout="wide")

# --- 2. DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stButton>button { border-radius: 8px; font-weight: 600; background-color: #2563EB; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #1D4ED8; transform: translateY(-1px); }
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS ---
DB_ATLETAS = "atleta_v23.csv"
DB_FINANCEIRO = "fin_v23.csv"

COLS_A = ["ID", "Nome", "Data_Nascimento", "Genero", "Faixa", "Responsavel", "Telefone", "Status", "Mensalidade", "Dia_Vencimento", "Obs_Medicas", "Data_Filiacao"]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo"]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    for col in COLS_A:
        if col not in df_a.columns: df_a[col] = ""
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 4. LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        st.markdown("<br><br><h1 style='text-align: center;'>🥋 Judô Pro</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha Admin", type="password")
        if st.button("Entrar"):
            if senha == "judo123":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.title("Judô Pro")
    aba = st.radio("MENU", ["📊 Dashboard", "👥 Alunos", "💰 Financeiro"])
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- 6. TELAS ---

if aba == "📊 Dashboard":
    st.title("📊 Painel de Performance")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']))
    total_caixa = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    c2.metric("Total em Caixa", f"R$ {total_caixa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    faturamento_mensal = pd.to_numeric(df_a[df_a['Status'] == 'Ativo']['Mensalidade'], errors='coerce').sum()
    c3.metric("Faturamento Esperado/Mês", f"R$ {faturamento_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.divider()
    
    # NOVO: Gráfico de Faturamento
    if not df_f.empty:
        st.subheader("📈 Evolução Financeira")
        # Preparar dados para o gráfico (agrupar por Mes_Ref)
        df_f['Valor_Total'] = pd.to_numeric(df_f['Valor_Total'], errors='coerce')
        graf_df = df_f.groupby('Mes_Ref')['Valor_Total'].sum().reset_index()
        fig = px.bar(graf_df, x='Mes_Ref', y='Valor_Total', 
                     title="Receita por Mês de Referência",
                     labels={'Valor_Total': 'Valor (R$)', 'Mes_Ref': 'Mês/Ano'},
                     color_discrete_sequence=['#2563EB'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aguardando os primeiros registros financeiros para gerar o gráfico.")

elif aba == "👥 Alunos":
    st.title("👥 Gestão de Alunos")
    t1, t2 = st.tabs(["📝 Novo Cadastro", "🔧 Editar Aluno"])
    
    with t1:
        with st.form("cad"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome*")
            tel = c2.text_input("Telefone*")
            c3, c4 = st.columns(2)
            faixa = c3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            mensal = c4.number_input("Valor Mensalidade", 150.0)
            venc = st.selectbox("Dia do Vencimento", list(range(1, 31)), index=4)
            if st.form_submit_button("Matricular"):
                if nome and tel:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{"ID": new_id, "Nome": nome, "Status": "Ativo", "Faixa": faixa, "Telefone": tel, "Mensalidade": mensal, "Dia_Vencimento": venc, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")}])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Matriculado!"); time.sleep(1); st.rerun()

    with t2:
        busca = st.text_input("Buscar Aluno")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
        if not df_res.empty:
            sel = st.selectbox("Escolha", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
            id_sel = int(sel.split("(ID: ")[1].replace(")", ""))
            idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
            with st.form("edit"):
                atl = st.session_state.atletas_df.loc[idx]
                e_faixa = st.selectbox("Nova Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(atl['Faixa']))
                e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if atl['Status'] == "Ativo" else 1)
                if st.form_submit_button("Atualizar"):
                    st.session_state.atletas_df.loc[idx, ["Faixa", "Status"]] = [e_faixa, e_status]
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Atualizado!"); time.sleep(1); st.rerun()

elif aba == "💰 Financeiro":
    st.title("💰 Fluxo de Caixa")
    c_pag, c_rec = st.columns([1.2, 0.8])
    
    with c_pag:
        with st.form("pag_form"):
            aluno = st.selectbox("Aluno", st.session_state.atletas_df[st.session_state.atletas_df['Status'] == 'Ativo']['Nome'].tolist())
            
            # NOVO: Escolher a Data de Pagamento
            c_data, c_mes = st.columns(2)
            data_pg = c_data.date_input("Data do Pagamento", datetime.now())
            mes_ref = c_mes.text_input("Mês de Referência", datetime.now().strftime("%m/%Y"))
            
            metodo = st.selectbox("Forma", ["PIX", "Dinheiro", "Misto (Pix + Dinheiro)"])
            val_sug = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
            total = st.number_input("Valor Total (R$)", value=val_sug)
            
            v_p, v_d = 0.0, 0.0
            if "Misto" in metodo:
                st.info("Divisão do Pagamento:")
                cm1, cm2 = st.columns(2)
                v_p = cm1.number_input("Parte Pix", 0.0, total)
                v_din = cm2.number_input("Parte Dinheiro", 0.0, total)
            
            if st.form_submit_button("REGISTRAR RECEBIMENTO"):
                if "Misto" in metodo and (round(v_p + v_din, 2) != round(total, 2)):
                    st.error("A soma não confere!")
                else:
                    id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                    novo_p = pd.DataFrame([{
                        "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": mes_ref, 
                        "Valor_Total": total, "Valor_Pix": v_p if "Misto" in metodo else (total if "PIX" in metodo else 0),
                        "Valor_Dinheiro": v_din if "Misto" in metodo else (total if "Dinheiro" in metodo else 0),
                        "Data_Pagamento": data_pg.strftime("%d/%m/%Y"), "Metodo": metodo
                    }])
                    st.
