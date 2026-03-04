import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Judô Pro | Gestão Profissional", page_icon="🥋", layout="wide")

# --- CSS PROFISSIONAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    .main-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; }
    .stButton>button { border-radius: 8px; font-weight: 600; height: 3em; transition: 0.3s; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE DE DADOS ---
class JudoDB:
    FILE_A = "atletas_v31.csv"
    FILE_F = "financeiro_v31.csv"
    
    # Novas colunas fundamentais implementadas
    COLS_A = [
        "ID", "Nome", "Status", "CPF", "Data_Nascimento", "Sexo", 
        "Faixa", "Telefone", "Responsavel", "CPF_Responsavel", 
        "Mensalidade", "Dia_Vencimento", "Data_Filiacao", "Obs_Medicas"
    ]
    COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor", "Data_PG", "Metodo"]

    @classmethod
    def init(cls):
        if not os.path.exists(cls.FILE_A): pd.DataFrame(columns=cls.COLS_A).to_csv(cls.FILE_A, index=False)
        if not os.path.exists(cls.FILE_F): pd.DataFrame(columns=cls.COLS_F).to_csv(cls.FILE_F, index=False)

    @classmethod
    def load(cls):
        df_a = pd.read_csv(cls.FILE_A)
        df_f = pd.read_csv(cls.FILE_F)
        return df_a, df_f

    @classmethod
    def save(cls, df_a, df_f):
        df_a.to_csv(cls.FILE_A, index=False)
        df_f.to_csv(cls.FILE_F, index=False)

JudoDB.init()

if 'df_a' not in st.session_state:
    st.session_state.df_a, st.session_state.df_f = JudoDB.load()

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🥋 Acesso Judô Pro</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha Administrativa", type="password")
        if st.button("Entrar"):
            if senha == "judo123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("MENU", ["📊 Painel Geral", "👥 Gestão de Alunos", "💰 Financeiro"])

# --- MÓDULO 1: PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title("📊 Indicadores Acadêmicos")
    df_a = st.session_state.df_a
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']))
    c2.metric("Alunos Inativos", len(df_a[df_a['Status'] == 'Inativo']))
    c3.metric("Faturamento Alvo/Mês", f"R$ {df_a[df_a['Status'] == 'Ativo']['Mensalidade'].sum():,.2f}")

    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Distribuição por Faixa")
        if not df_a.empty:
            st.plotly_chart(px.pie(df_a, names='Faixa', hole=0.3), use_container_width=True)
    with col_r:
        st.subheader("Novas Filiações (Ano)")
        # Lógica de crescimento simples
        st.info("Estatísticas de crescimento serão exibidas aqui conforme o uso.")

# --- MÓDULO 2: GESTÃO DE ALUNOS ---
elif menu == "👥 Gestão de Alunos":
    st.title("👥 Controle de Atletas")
    tab_lista, tab_cadastro = st.tabs(["📋 Lista e Status", "✨ Nova Matrícula"])

    with tab_lista:
        st.subheader("Busca e Gerenciamento")
        col_b1, col_b2 = st.columns([2, 1])
        search = col_b1.text_input("Pesquisar por Nome ou CPF")
        status_filter = col_b2.selectbox("Filtrar Status", ["Todos", "Ativo", "Inativo"])
        
        df_res = st.session_state.df_a.copy()
        if search:
            df_res = df_res[df_res['Nome'].str.contains(search, case=False) | df_res['CPF'].str.contains(search)]
        if status_filter != "Todos":
            df_res = df_res[df_res['Status'] == status_filter]
        
        st.dataframe(df_res, use_container_width=True, hide_index=True)

        if not df_res.empty:
            st.divider()
            st.subheader("⚙️ Ações Rápidas (Ativar/Inativar/Editar)")
            sel_aluno = st.selectbox("Selecione o atleta para modificar:", df_res['Nome'].tolist())
            idx = st.session_state.df_a[st.session_state.df_a['Nome'] == sel_aluno].index[0]
            aluno_atual = st.session_state.df_a.loc[idx]

            with st.form("form_edit_status"):
                c1, c2, c3 = st.columns(3)
                novo_status = c1.selectbox("Alterar Status", ["Ativo", "Inativo"], index=0 if aluno_atual['Status'] == "Ativo" else 1)
                nova_faixa = c2.selectbox("Atualizar Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=0)
                nova_mensal = c3.number_input("Mensalidade", value=float(aluno_atual['Mensalidade']))
                
                if st.form_submit_button("Confirmar Alterações"):
                    st.session_state.df_a.loc[idx, ['Status', 'Faixa', 'Mensalidade']] = [novo_status, nova_faixa, nova_mensal]
                    JudoDB.save(st.session_state.df_a, st.session_state.df_f)
                    st.success(f"Status de {sel_aluno} atualizado para {novo_status}!")
                    time.sleep(1); st.rerun()

    with tab_cadastro:
        with st.form("form_cadastro_full", clear_on_submit=True):
            st.subheader("📝 Ficha Cadastral Completa")
            
            st.markdown("**Informações Pessoais**")
            c1, c2, c3 = st.columns([2, 1, 1])
            nome = c1.text_input("Nome Completo*")
            cpf = c2.text_input("CPF*")
            dt_nasc = c3.date_input("Data de Nascimento", date(2010, 1, 1))
            
            c4, c5, c6 = st.columns(3)
            sexo = c4.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            faixa = c5.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            tel = c6.text_input("WhatsApp/Telefone*")
            
            st.divider()
            st.markdown("**Responsável (Se menor)**")
            r1, r2 = st.columns(2)
            resp = r1.text_input("Nome do Responsável")
            resp_cpf = r2.text_input("CPF do Responsável")
            
            st.divider()
            st.markdown("**Financeiro e Saúde**")
            f1, f2 = st.columns(2)
            mensalidade = f1.number_input("Valor da Mensalidade (R$)", value=150.0)
            vencimento = f2.selectbox("Dia de Vencimento", list(range(1, 31)), index=4)
            obs = st.text_area("Observações Médicas ou Gerais")

            if st.form_submit_button("Finalizar Matrícula"):
                if nome and cpf and tel:
                    new_id = int(st.session_state.df_a['ID'].max() + 1) if not st.session_state.df_a.empty else 1
                    novo_atleta = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Status": "Ativo", "CPF": cpf,
                        "Data_Nascimento": dt_nasc.strftime("%d/%m/%Y"), "Sexo": sexo,
                        "Faixa": faixa, "Telefone": tel, "Responsavel": resp,
                        "CPF_Responsavel": resp_cpf, "Mensalidade": mensalidade,
                        "Dia_Vencimento": vencimento, "Data_Filiacao": date.today().strftime("%d/%m/%Y"),
                        "Obs_Medicas": obs
                    }])
                    st.session_state.df_a = pd.concat([st.session_state.df_a, novo_atleta], ignore_index=True)
                    JudoDB.save(st.session_state.df_a, st.session_state.df_f)
                    st.success("Matrícula realizada com sucesso!")
                    time.sleep(1); st.rerun()
                else:
                    st.error("Campos com * são obrigatórios!")

# --- MÓDULO 3: FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.title("💰 Gestão de Mensalidades")
    
    col_receber, col_historico = st.columns([1, 1.3])
    
    with col_receber:
        st.subheader("Registrar Recebimento")
        # Só permite cobrar de alunos ATIVOS
        ativos = st.session_state.df_a[st.session_state.df_a['Status'] == 'Ativo']
        
        if not ativos.empty:
            with st.form("form_pagamento"):
                aluno_pag = st.selectbox("Aluno", ativos['Nome'].tolist())
                c_d, c_m = st.columns(2)
                data_pg = c_d.date_input("Data do Recebimento", date.today())
                mes_ref = c_m.text_input("Mês de Referência (Ex: 03/2024)", date.today().strftime("%m/%Y"))
                
                val_sug = float(ativos[ativos['Nome'] == aluno_pag]['Mensalidade'].values[0])
                valor_pg = st.number_input("Valor Recebido", value=val_sug)
                metodo = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão", "Transferência"])
                
                if st.form_submit_button("Confirmar Baixa"):
                    id_a = ativos[ativos['Nome'] == aluno_pag]['ID'].values[0]
                    novo_pg = pd.DataFrame([{
                        "ID_Atleta": id_a, "Nome_Atleta": aluno_pag, "Mes_Ref": mes_ref,
                        "Valor": valor_pg, "Data_PG": data_pg.strftime("%d/%m/%Y"), "Metodo": metodo
                    }])
                    st.session_state.df_f = pd.concat([st.session_state.df_f, novo_pg], ignore_index=True)
                    JudoDB.save(st.session_state.df_a, st.session_state.df_f)
                    st.success("Pagamento registrado!")
                    st.code(f"RECIBO: {aluno_pag} | Valor: R${valor_pg:.2f} | Ref: {mes_ref}")
                    time.sleep(0.5); st.rerun()
        else:
            st.warning("Não existem alunos ATIVOS cadastrados para realizar cobrança.")

    with col_historico:
        st.subheader("Últimos Lançamentos")
        st.dataframe(st.session_state.df_f.tail(15), use_container_width=True, hide_index=True)
