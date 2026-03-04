import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Judô Pro | Gestão Platinum", page_icon="🥋", layout="wide")

# --- CSS PROFISSIONAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: 0.3s; width: 100%; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE DE DADOS ---
class JudoDB:
    FILE_A = "atletas_v33.csv"
    FILE_F = "financeiro_v33.csv"
    
    COLS_A = [
        "ID", "Nome", "Status", "CPF", "Data_Nascimento", "Sexo", 
        "Faixa", "Telefone", "Responsavel", "CPF_Responsavel", 
        "Mensalidade", "Dia_Vencimento", "Data_Filiacao", "Obs_Medicas"
    ]
    COLS_F = ["ID_Lancamento", "ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor", "Data_PG", "Metodo"]

    @classmethod
    def init(cls):
        if not os.path.exists(cls.FILE_A): pd.DataFrame(columns=cls.COLS_A).to_csv(cls.FILE_A, index=False)
        if not os.path.exists(cls.FILE_F): pd.DataFrame(columns=cls.COLS_F).to_csv(cls.FILE_F, index=False)

    @classmethod
    def load(cls):
        df_a = pd.read_csv(cls.FILE_A)
        df_f = pd.read_csv(cls.FILE_F)
        # Garantir que o ID do lançamento exista para poder deletar
        if "ID_Lancamento" not in df_f.columns:
            df_f.insert(0, "ID_Lancamento", range(len(df_f)))
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
        st.markdown("<h1 style='text-align:center;'>🥋 Judô Pro</h1>", unsafe_allow_html=True)
        senha = st.text_input("Acesso Administrativo", type="password")
        if st.button("Entrar"):
            if senha == "judo123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("MENU PRINCIPAL", ["📊 Dashboard", "👥 Alunos", "💰 Financeiro"])

# --- MÓDULO FINANCEIRO (COM FUNÇÃO DESFAZER) ---
if menu == "💰 Financeiro":
    st.title("💰 Gestão Financeira e Fluxo de Caixa")
    
    tab_pag, tab_estorno = st.tabs(["💵 Lançar Pagamento", "🔄 Histórico e Estorno (Desfazer)"])
    
    with tab_pag:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            with st.form("form_pagamento_novo", clear_on_submit=True):
                st.subheader("Receber Mensalidade")
                ativos = st.session_state.df_a[st.session_state.df_a['Status'] == 'Ativo']
                aluno_sel = st.selectbox("Selecione o Aluno", ativos['Nome'].tolist() if not ativos.empty else ["Nenhum aluno ativo"])
                
                c_d, c_m = st.columns(2)
                data_pg = c_d.date_input("Data PG", date.today())
                mes_ref = c_m.text_input("Mês Ref (MM/AAAA)", date.today().strftime("%m/%Y"))
                
                # Busca valor da mensalidade do aluno selecionado
                val_base = 150.0
                if not ativos.empty and aluno_sel in ativos['Nome'].values:
                    val_base = float(ativos[ativos['Nome'] == aluno_sel]['Mensalidade'].values[0])
                
                valor_final = st.number_input("Valor Recebido", value=val_base)
                metodo_pg = st.selectbox("Meio de Pagamento", ["PIX", "Dinheiro", "Cartão", "Misto"])
                
                if st.form_submit_button("Confirmar Pagamento"):
                    if not ativos.empty:
                        # Gerar novo ID único para o lançamento
                        novo_id_lan = int(st.session_state.df_f['ID_Lancamento'].max() + 1) if not st.session_state.df_f.empty else 1
                        id_atleta = ativos[ativos['Nome'] == aluno_sel]['ID'].values[0]
                        
                        novo_pg = pd.DataFrame([{
                            "ID_Lancamento": novo_id_lan,
                            "ID_Atleta": id_atleta,
                            "Nome_Atleta": aluno_sel,
                            "Mes_Ref": mes_ref,
                            "Valor": valor_final,
                            "Data_PG": data_pg.strftime("%d/%m/%Y"),
                            "Metodo": metodo_pg
                        }])
                        
                        st.session_state.df_f = pd.concat([st.session_state.df_f, novo_pg], ignore_index=True)
                        JudoDB.save(st.session_state.df_a, st.session_state.df_f)
                        st.success(f"Pagamento de {aluno_sel} registrado com sucesso!")
                        time.sleep(1); st.rerun()
        with col2:
            st.info("💡 **Dica Profissional:** Use o Mês de Referência para controlar qual mensalidade está sendo paga (Ex: 03/2024), mesmo que o pagamento ocorra em outra data.")
            if not st.session_state.df_f.empty:
                st.subheader("Últimas 5 Entradas")
                st.dataframe(st.session_state.df_f.tail(5), use_container_width=True, hide_index=True)

    with tab_estorno:
        st.subheader("🔄 Desfazer Lançamentos (Estorno)")
        st.write("Selecione um pagamento abaixo para removê-lo do sistema.")
        
        if not st.session_state.df_f.empty:
            # Ordenar pelo mais recente para facilitar
            df_reverso = st.session_state.df_f.iloc[::-1]
            
            # Criar uma lista legível para o selectbox
            opcoes_estorno = [
                f"ID: {r['ID_Lancamento']} | {r['Nome_Atleta']} | R$ {r['Valor']:.2f} | Ref: {r['Mes_Ref']}" 
                for _, r in df_reverso.iterrows()
            ]
            
            selecionado = st.selectbox("Escolha o pagamento que deseja CANCELAR:", opcoes_estorno)
            id_para_deletar = int(selecionado.split("|")[0].replace("ID: ", "").strip())
            
            # Detalhes do registro antes de deletar
            detalhe = st.session_state.df_f[st.session_state.df_f['ID_Lancamento'] == id_para_deletar].iloc[0]
            
            st.warning(f"⚠️ **ATENÇÃO:** Você está prestes a excluir o pagamento de **{detalhe['Nome_Atleta']}** no valor de **R$ {detalhe['Valor']:.2f}** referente a **{detalhe['Mes_Ref']}**.")
            
            col_btn1, col_btn2 = st.columns([1, 4])
            if col_btn1.button("🔥 DESFAZER PAGAMENTO"):
                # Remover do DataFrame
                st.session_state.df_f = st.session_state.df_f[st.session_state.df_f['ID_Lancamento'] != id_para_deletar]
                JudoDB.save(st.session_state.df_a, st.session_state.df_f)
                st.error("Pagamento estornado/removido do banco de dados!")
                time.sleep(1); st.rerun()
            
            st.divider()
            st.subheader("📋 Histórico Completo")
            st.dataframe(st.session_state.df_f, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum lançamento financeiro encontrado.")

# --- DEMAIS ABAS (DASHBOARD E ALUNOS - RESUMIDAS PARA O EXEMPLO) ---
elif menu == "📊 Dashboard":
    st.title("📊 Indicadores")
    st.metric("Total em Caixa", f"R$ {st.session_state.df_f['Valor'].sum():,.2f}")
    st.plotly_chart(px.line(st.session_state.df_f, x='Data_PG', y='Valor', title="Fluxo de Caixa"), use_container_width=True)

elif menu == "👥 Alunos":
    st.info("Módulo de gestão de alunos ativo. Utilize as funções de Edição Total liberadas na versão anterior.")
    st.dataframe(st.session_state.df_a, use_container_width=True)
