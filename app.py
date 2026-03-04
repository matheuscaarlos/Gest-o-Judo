import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Judô Pro | Estabilidade Total", page_icon="🥋", layout="wide")

# Estilo profissional (High-Contrast)
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button { background-color: #1E293B; color: white; font-weight: 600; border-radius: 8px; }
    div[data-testid="stMetric"] { background-color: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS COM VALIDAÇÃO ---
class JudoDB:
    FILE_A = "db_atletas_v36.csv"
    FILE_F = "db_financeiro_v36.csv"
    COLS_A = ["ID", "Nome", "Status", "CPF", "Nasc", "Sexo", "Faixa", "WhatsApp", "Mensalidade", "Vencimento"]

    @classmethod
    def init_db(cls):
        if not os.path.exists(cls.FILE_A): pd.DataFrame(columns=cls.COLS_A).to_csv(cls.FILE_A, index=False)
        if not os.path.exists(cls.FILE_F): pd.DataFrame(columns=["ID_Lan", "Nome", "Valor", "Mes_Ref", "Data_PG"]).to_csv(cls.FILE_F, index=False)

    @classmethod
    def load_data(cls):
        df_a = pd.read_csv(cls.FILE_A).fillna("")
        df_f = pd.read_csv(cls.FILE_F).fillna("")
        return df_a, df_f

JudoDB.init_db()
if 'df_a' not in st.session_state:
    st.session_state.df_a, st.session_state.df_f = JudoDB.load_data()

# --- INTERFACE ---
st.title("🥋 Gestão Judô Pro")

tab_cad, tab_fin = st.tabs(["➕ Nova Matrícula", "💰 Financeiro"])

with tab_cad:
    with st.form("novo_cadastro", clear_on_submit=True):
        st.subheader("Dados do Aluno")
        c1, c2, c3 = st.columns([2, 1, 1])
        n_nome = c1.text_input("Nome Completo")
        n_cpf = c2.text_input("CPF")
        
        # O segredo está aqui: o date_input SEMPRE retorna um objeto date.
        n_nasc = c3.date_input("Data de Nascimento", date(2010, 1, 1))
        
        c4, c5 = st.columns(2)
        n_faixa = c4.selectbox("Faixa", ["Branca", "Azul", "Amarela", "Verde", "Roxa", "Marrom", "Preta"])
        n_mensal = c5.number_input("Mensalidade", 150.0)
        
        submit = st.form_submit_button("Salvar Matrícula")
        
        if submit:
            if n_nome and n_cpf:
                # CORREÇÃO DO ERRO: Garantimos que n_nasc é um objeto date antes do strftime
                if isinstance(n_nasc, (date, datetime)):
                    data_formatada = n_nasc.strftime("%d/%m/%Y")
                else:
                    # Caso venha como string por algum erro de cache, convertemos
                    data_formatada = str(n_nasc)
                
                new_id = int(st.session_state.df_a['ID'].max() + 1) if not st.session_state.df_a.empty else 1
                
                novo_registro = pd.DataFrame([{
                    "ID": new_id,
                    "Nome": n_nome,
                    "Status": "Ativo",
                    "CPF": n_cpf,
                    "Nasc": data_formatada,
                    "Faixa": n_faixa,
                    "Mensalidade": n_mensal
                }])
                
                st.session_state.df_a = pd.concat([st.session_state.df_a, novo_registro], ignore_index=True)
                st.session_state.df_a.to_csv(JudoDB.FILE_A, index=False)
                st.success(f"Aluno {n_nome} matriculado com sucesso!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Campos obrigatórios ausentes!")

with tab_fin:
    st.subheader("Histórico Financeiro")
    st.dataframe(st.session_state.df_f, use_container_width=True)
