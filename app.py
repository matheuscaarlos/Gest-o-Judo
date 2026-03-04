import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro | Assoc. Roberdrayner", page_icon="🥋", layout="wide")

# --- 2. ESTILIZAÇÃO (CSS) ---
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
    .stButton>button { border-radius: 8px; font-weight: 600; background-color: #2563EB; color: white; transition: 0.3s; width: 100%; }
    .stButton>button:hover { background-color: #1D4ED8; transform: translateY(-1px); }
    </style>
""", unsafe_allow_html=True)

# --- 3. BANCO DE DADOS (COM CORREÇÃO DE INDENTAÇÃO) ---
DB_ATLETAS = "atleta_v25.csv"
DB_FINANCEIRO = "fin_v25.csv"

COLS_A = ["ID", "Nome", "Status", "Faixa", "Telefone", "Responsavel", "Mensalidade", "Dia_Vencimento", "Obs_Medicas", "Data_Filiacao"]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo"]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    # Garante que colunas novas existam
    for col in COLS_A:
        if col not in df_a.columns: df_a[col] = ""
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 4. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br><h1 style='text-align: center;'>🥋 Judô Pro</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar no Sistema"):
            if senha == "judo123":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

# --- 5. NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.title("Administração")
    aba = st.radio("Escolha uma Aba:", ["📊 Dashboard", "👥 Alunos", "💰 Financeiro"])
    st.divider()
    if st.button("🚪 Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- 6. TELAS ---

if aba == "📊 Dashboard":
    st.title("📊 Painel Geral")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']))
    total_receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    c2.metric("Receita Total", f"R$ {total_receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    faturamento_alvo = pd.to_numeric(df_a[df_a['Status'] == 'Ativo']['Mensalidade'], errors='coerce').sum()
    c3.metric("Faturamento Alvo/Mês", f"R$ {faturamento_alvo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.divider()
    
    if not df_f.empty:
        st.subheader("📈 Crescimento Financeiro")
        df_f['Valor_Total'] = pd.to_numeric(df_f['Valor_Total'], errors='coerce')
        resumo = df_f.groupby('Mes_Ref')['Valor_Total'].sum().reset_index()
        fig = px.bar(resumo, x='Mes_Ref', y='Valor_Total', title="Receita por Mês de Referência", color_discrete_sequence=['#2563EB'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Lance pagamentos para visualizar o gráfico.")

elif aba == "👥 Alunos":
    st.title("👥 Gestão de Alunos")
    tab_c, tab_e = st.tabs(["📝 Cadastrar", "🔧 Editar"])
    
    with tab_c:
        with st.form("form_cadastro"):
            nome = st.text_input("Nome Completo*")
            c1, c2, c3 = st.columns(3)
            tel = c1.text_input("WhatsApp*")
            faixa = c2.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            mensal = c3.number_input("Mensalidade (R$)", 150.0)
            venc = st.selectbox("Dia de Vencimento", list(range(1, 31)), index=4)
            resp = st.text_input("Responsável (Se menor)")
            obs = st.text_area("Observações Médicas")
            if st.form_submit_button("Salvar Matrícula"):
                if nome and tel:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Status": "Ativo", "Faixa": faixa, "Telefone": tel,
                        "Responsavel": resp, "Mensalidade": mensal, "Dia_Vencimento": venc, "Obs_Medicas": obs,
                        "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")
                    }])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Cadastrado com sucesso!"); time.sleep(1); st.rerun()

    with tab_e:
        busca = st.text_input("Pesquisar aluno...")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
        if not df_res.empty:
            sel = st.selectbox("Escolha o aluno:", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
            id_sel = int(sel.split("(ID: ")[1].replace(")", ""))
            idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
            atl = st.session_state.atletas_df.loc[idx]
            with st.form("form_edicao"):
                st.write(f"Editando: {atl['Nome']}")
                e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if atl['Status'] == "Ativo" else 1)
                e_faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(atl['Faixa']))
                e_venc = st.selectbox("Dia Vencimento", list(range(1, 31)), index=int(atl['Dia_Vencimento'])-1 if atl['Dia_Vencimento'] else 4)
                e_mensal = st.number_input("Mensalidade", value=float(atl['Mensalidade']))
                if st.form_submit_button("Salvar Alterações"):
                    st.session_state.atletas_df.loc[idx, ["Status", "Faixa", "Dia_Vencimento", "Mensalidade"]] = [e_status, e_faixa, e_venc, e_mensal]
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Alterado!"); time.sleep(1); st.rerun()

elif aba == "💰 Financeiro":
    st.title("💰 Financeiro")
    col_pg, col_rec = st.columns([1.2, 0.8])
    with col_pg:
        with st.form("form_fin"):
            aluno = st.selectbox("Aluno", st.session_state.atletas_df[st.session_state.atletas_df['Status'] == 'Ativo']['Nome'].tolist())
            c_data, c_mes = st.columns(2)
            data_pg = c_data.date_input("Data do Pagamento", datetime.now())
            mes_ref = c_mes.text_input("Mês de Referência", datetime.now().strftime("%m/%Y"))
            metodo = st.selectbox("Meio", ["PIX", "Dinheiro", "Misto (Pix + Dinheiro)"])
            val_sug = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
            total = st.number_input("Total R$", value=val_sug)
            v_p, v_d = 0.0, 0.0
            if "Misto" in metodo:
                cm1, cm2 = st.columns(2)
                v_p = cm1.number_input("Pix R$", 0.0, total)
                v_d = cm2.number_input("Dinheiro R$", 0.0, total)
            if st.form_submit_button("Confirmar Pagamento"):
                if "Misto" in metodo and (round(v_p + v_d, 2) != round(total, 2)):
                    st.error("A soma não confere!")
                else:
                    id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                    novo_p = pd.DataFrame([{
                        "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": mes_ref, 
                        "Valor_Total": total, "Valor_Pix": v_p if "Misto" in metodo else (total if "PIX" in metodo else 0),
                        "Valor_Dinheiro": v_d if "Misto" in metodo else (total if "Dinheiro" in metodo else 0),
                        "Data_Pagamento": data_pg.strftime("%d/%m/%Y"), "Metodo": metodo
                    }])
                    st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.session_state.recibo = f"*RECIBO JUDÔ*\n*Aluno:* {aluno}\n*Data:* {data_pg.strftime('%d/%m/%Y')}\n*Valor:* R${total:.2f}"
                    st.rerun()
    with col_rec:
        if 'recibo' in st.session_state:
            st.code(st.session_state.recibo)
    st.divider()
    st.dataframe(st.session_state.fin_df.tail(10), use_container_width=True)
