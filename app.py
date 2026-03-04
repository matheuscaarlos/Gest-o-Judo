import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from PIL import Image

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- BANCO DE DADOS ---
DB_ATLETAS = "atletas_v4_5.csv"
DB_FINANCEIRO = "financeiro_v4_5.csv"

def load_data():
    cols = ["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao", 
            "CPF", "RG", "Telefone", "Endereco", "Peso", "Sangue"]
    if os.path.exists(DB_ATLETAS):
        df = pd.read_csv(DB_ATLETAS)
        # Garante que colunas novas existam se você estiver vindo de uma versão antiga
        for col in cols:
            if col not in df.columns: df[col] = "-"
        return df, (pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=["ID_Atleta", "Mes_Ref", "Ano_Ref", "Valor", "Data_Pgto", "Metodo"]))
    return pd.DataFrame(columns=cols), pd.DataFrame(columns=["ID_Atleta", "Mes_Ref", "Ano_Ref", "Valor", "Data_Pgto", "Metodo"])

def save_data(atleta_df, fin_df):
    atleta_df.to_csv(DB_ATLETAS, index=False)
    fin_df.to_csv(DB_FINANCEIRO, index=False)

# --- CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .stButton>button { border-radius: 5px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    st.markdown(f"<h3 style='text-align: center;'>Associação Roberdrayner Martins</h3>", unsafe_allow_html=True)
    aba = st.radio("Menu", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"])

# --- DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel Geral")
    df_a = st.session_state.atletas_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Alunos", len(df_a))
    c2.metric("Ativos", len(df_a[df_a['Status'] == 'Ativo']))
    c3.metric("Faturamento Mensal", f"R$ {pd.to_numeric(df_a['Mensalidade'], errors='coerce').sum():,.2f}")
    
    if not df_a.empty:
        fig = px.pie(df_a, names='Faixa', title="Distribuição de Graduação", hole=.4)
        st.plotly_chart(fig, use_container_width=True)

# --- GESTÃO DE ATLETAS (CADASTRO, EDIÇÃO, EXCLUSÃO) ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    
    aba_interna = st.tabs(["➕ Novo Cadastro", "📝 Editar/Excluir"])
    
    with aba_interna[0]:
        with st.form("form_cadastro", clear_on_submit=True):
            st.subheader("Informações Pessoais")
            c1, c2, c3 = st.columns(3)
            nome = c1.text_input("Nome Completo*")
            cpf = c2.text_input("CPF")
            rg = c3.text_input("RG")
            
            c4, c5, c6 = st.columns(3)
            tel = c4.text_input("Telefone/WhatsApp")
            peso = c5.number_input("Peso (kg)", value=70.0)
            sangue = c6.selectbox("Tipo Sanguíneo", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "N/I"])
            
            end = st.text_input("Endereço Completo")
            
            st.divider()
            st.subheader("Dados da Academia")
            c7, c8, c9 = st.columns(3)
            faixa = c7.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            mensalidade = c8.number_input("Valor Mensalidade", value=150.0)
            status = c9.selectbox("Status", ["Ativo", "Inativo"])
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome:
                    novo_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo_atleta = pd.DataFrame([[novo_id, nome, faixa, status, mensalidade, datetime.now().strftime("%d/%m/%Y"), cpf, rg, tel, end, peso, sangue]], 
                                               columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_atleta], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"{nome} cadastrado!")
                    st.rerun()
                else: st.error("O campo Nome é obrigatório.")

    with aba_interna[1]:
        if st.session_state.atletas_df.empty:
            st.info("Nenhum atleta para exibir.")
        else:
            escolha = st.selectbox("Selecione um atleta para modificar", st.session_state.atletas_df['Nome'].tolist())
            idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == escolha].index[0]
            
            with st.form("editar_atleta"):
                st.subheader(f"Editando: {escolha}")
                c1, c2 = st.columns(2)
                novo_nome = c1.text_input("Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                nova_faixa = c2.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], 
                                         index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(st.session_state.atletas_df.at[idx, 'Faixa']))
                
                c3, c4, c5 = st.columns(3)
                novo_status = c3.selectbox("Status", ["Ativo", "Inativo"], index=0 if st.session_state.atletas_df.at[idx, 'Status'] == "Ativo" else 1)
                novo_valor = c4.number_input("Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                novo_tel = c5.text_input("Telefone", value=str(st.session_state.atletas_df.at[idx, 'Telefone']))

                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.atletas_df.at[idx, 'Nome'] = novo_nome
                    st.session_state.atletas_df.at[idx, 'Faixa'] = nova_faixa
                    st.session_state.atletas_df.at[idx, 'Status'] = novo_status
                    st.session_state.atletas_df.at[idx, 'Mensalidade'] = novo_valor
                    st.session_state.atletas_df.at[idx, 'Telefone'] = novo_tel
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Dados atualizados!")
                    st.rerun()
                
                if col_btn2.form_submit_button("🗑️ APAGAR ATLETA"):
                    st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.warning("Atleta removido do sistema.")
                    st.rerun()

# --- FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💸 Financeiro")
    df_a = st.session_state.atletas_df
    if not df_a.empty:
        aluno = st.selectbox("Aluno", df_a['Nome'].tolist())
        valor_sugerido = df_a[df_a['Nome'] == aluno]['Mensalidade'].values[0]
        if st.button(f"Confirmar Recebimento de R$ {valor_sugerido}"):
            st.success(f"Pagamento de {aluno} registrado!")
    else: st.warning("Cadastre atletas primeiro.")

# --- SISTEMA ---
elif aba == "⚙️ Sistema":
    st.title("⚙️ Configurações")
    st.download_button("📥 Baixar Excel Completo", data=st.session_state.atletas_df.to_csv().encode('utf-8'), file_name="relatorio_judo.csv")
