import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro | Administrativo", page_icon="🥋", layout="wide")

# --- 2. BANCO DE DADOS ---
DB_ATLETAS = "atleta_v27.csv"
DB_FINANCEIRO = "fin_v27.csv"

def load_data():
    cols_a = ["ID", "Nome", "Status", "Faixa", "Telefone", "Responsavel", "Mensalidade", "Dia_Vencimento", "Obs_Medicas", "Data_Filiacao"]
    cols_f = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo"]
    
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=cols_a)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=cols_f)
    
    # Reparação de colunas para compatibilidade
    for col in cols_a:
        if col not in df_a.columns: df_a[col] = ""
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        st.title("🥋 Judô Pro")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha == "judo123":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Incorreta")
    st.stop()

# --- 4. NAVEGAÇÃO ---
aba = st.sidebar.radio("Navegação", ["Dashboard", "Alunos", "Financeiro"])

# --- 5. TELAS ---

if aba == "Dashboard":
    st.title("📊 Resumo Administrativo")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']))
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    c2.metric("Total em Caixa", f"R$ {receita:,.2f}")
    c3.metric("Data", datetime.now().strftime("%d/%m/%Y"))
    
    if not df_f.empty:
        df_f['Valor_Total'] = pd.to_numeric(df_f['Valor_Total'], errors='coerce')
        fig = px.bar(df_f.groupby('Mes_Ref')['Valor_Total'].sum().reset_index(), 
                     x='Mes_Ref', y='Valor_Total', title="Faturamento Mensal")
        st.plotly_chart(fig, use_container_width=True)

elif aba == "Alunos":
    st.title("👥 Gestão de Alunos")
    t1, t2 = st.tabs(["Cadastrar", "Editar"])
    
    with t1:
        # FORMULÁRIO DE CADASTRO
        with st.form("form_novo_aluno"):
            st.subheader("Dados do Novo Aluno")
            nome = st.text_input("Nome Completo")
            tel = st.text_input("Telefone")
            faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            mensal = st.number_input("Mensalidade", 150.0)
            venc = st.selectbox("Dia Vencimento", list(range(1, 31)), index=4)
            resp = st.text_input("Responsável")
            obs = st.text_area("Observações Médicas")
            
            # O BOTÃO DEVE ESTAR AQUI (DENTRO DO WITH)
            submit_cad = st.form_submit_button("Finalizar Matrícula")
            
            if submit_cad:
                if nome and tel:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{"ID": new_id, "Nome": nome, "Status": "Ativo", "Faixa": faixa, "Telefone": tel, "Responsavel": resp, "Mensalidade": mensal, "Dia_Vencimento": venc, "Obs_Medicas": obs}])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Salvo!")
                    time.sleep(1); st.rerun()
                else: st.error("Nome e Telefone são obrigatórios!")

    with t2:
        busca = st.text_input("Buscar Aluno")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
        if not df_res.empty:
            sel = st.selectbox("Selecione o aluno", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
            idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == int(sel.split("(ID: ")[1].replace(")", ""))].index[0]
            
            # FORMULÁRIO DE EDIÇÃO
            with st.form("form_editar_aluno"):
                atl = st.session_state.atletas_df.loc[idx]
                e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if atl['Status'] == "Ativo" else 1)
                e_faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(atl['Faixa']))
                e_mensal = st.number_input("Mensalidade", value=float(atl['Mensalidade']))
                e_obs = st.text_area("Notas", value=str(atl['Obs_Medicas']))
                
                # BOTÃO DE EDIÇÃO (DENTRO DO WITH)
                submit_edit = st.form_submit_button("Atualizar Cadastro")
                
                if submit_edit:
                    st.session_state.atletas_df.loc[idx, ["Status", "Faixa", "Mensalidade", "Obs_Medicas"]] = [e_status, e_faixa, e_mensal, e_obs]
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Atualizado!")
                    time.sleep(1); st.rerun()

elif aba == "Financeiro":
    st.title("💰 Financeiro")
    with st.form("form_pag"):
        aluno = st.selectbox("Aluno", st.session_state.atletas_df[st.session_state.atletas_df['Status'] == 'Ativo']['Nome'].tolist())
        c1, c2 = st.columns(2)
        data_p = c1.date_input("Data do Pagamento", datetime.now())
        mes_r = c2.text_input("Mês Referência (MM/AAAA)", datetime.now().strftime("%m/%Y"))
        valor = st.number_input("Valor Recebido", 150.0)
        metodo = st.selectbox("Forma", ["PIX", "Dinheiro", "Misto"])
        
        # BOTÃO FINANCEIRO (DENTRO DO WITH)
        submit_fin = st.form_submit_button("Confirmar Pagamento")
        
        if submit_fin:
            id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
            novo_p = pd.DataFrame([{"ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": mes_r, "Valor_Total": valor, "Data_Pagamento": data_p.strftime("%d/%m/%Y"), "Metodo": metodo}])
            st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
            save_data(st.session_state.atletas_df, st.session_state.fin_df)
            st.success("Pagamento Registrado!")
            st.code(f"RECIBO: {aluno} - R${valor:.2f} - Data: {data_p.strftime('%d/%m/%Y')}")
