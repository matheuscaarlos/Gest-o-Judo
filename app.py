import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro - Edição", page_icon="🥋", layout="wide")

DB_ATLETAS = "atletas_v10.csv"
DB_FINANCEIRO = "financeiro_v10.csv"

def load_data():
    cols_atleta = ["ID", "Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Data_Filiacao"]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=cols_atleta)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=cols_fin)
    if not df_a.empty: df_a['ID'] = df_a['ID'].astype(int)
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 2. MENU ---
with st.sidebar:
    st.header("🥋 Menu")
    aba = st.radio("Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"])

# --- 3. DASHBOARD (Simplificado) ---
if aba == "🏠 Dashboard":
    st.title("📊 Painel")
    df_a = st.session_state.atletas_df
    st.metric("Total de Alunos", len(df_a))
    if not df_a.empty:
        st.plotly_chart(px.pie(df_a, names='Faixa', title="Distribuição por Faixa"), use_container_width=True)

# --- 4. GESTÃO DE ATLETAS (COM EDIÇÃO) ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    
    # SEÇÃO: NOVO CADASTRO
    with st.expander("➕ Nova Matrícula", expanded=False):
        with st.form("form_novo"):
            nome = st.text_input("Nome Completo*")
            c1, c2, c3 = st.columns(3)
            cpf, rg, peso = c1.text_input("CPF"), c2.text_input("RG"), c3.number_input("Peso (kg)", 0.0)
            c4, c5 = st.columns(2)
            tel, email = c4.text_input("WhatsApp"), c5.text_input("Email")
            end = st.text_input("Endereço")
            c6, c7 = st.columns(2)
            faixa = c6.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = c7.number_input("Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Salvar Matrícula"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{"ID": new_id, "Nome": nome, "CPF": cpf, "RG": rg, "Peso": peso, "Faixa": faixa, "Endereco": end, "Telefone": tel, "Email": email, "Status": "Ativo", "Mensalidade": valor, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")}])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Cadastrado!"); st.rerun()

    # SEÇÃO: PESQUISA E EDIÇÃO
    with st.expander("🔍 Pesquisar / Editar / Excluir", expanded=True):
        busca = st.text_input("Buscar por nome...")
        df_f = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
        st.dataframe(df_f[["ID", "Nome", "Faixa", "Telefone", "Status"]], use_container_width=True, hide_index=True)
        
        if not df_f.empty:
            st.divider()
            escolha = st.selectbox("Selecione o atleta para ação:", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_f.iterrows()])
            id_sel = int(escolha.split("(ID: ")[1].replace(")", ""))
            
            # Carregar dados do atleta selecionado para os campos de edição
            idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
            atleta = st.session_state.atletas_df.loc[idx]

            st.markdown(f"### 📝 Editando: {atleta['Nome']}")
            with st.form("form_edicao"):
                # Campos preenchidos com os valores atuais
                ed_nome = st.text_input("Nome", value=atleta['Nome'])
                e1, e2, e3 = st.columns(3)
                ed_cpf = e1.text_input("CPF", value=atleta['CPF'])
                ed_rg = e2.text_input("RG", value=atleta['RG'])
                ed_peso = e3.number_input("Peso", value=float(atleta['Peso']))
                
                e4, e5 = st.columns(2)
                ed_tel = e4.text_input("WhatsApp", value=atleta['Telefone'])
                ed_email = e5.text_input("Email", value=atleta['Email'])
                ed_end = st.text_input("Endereço", value=atleta['Endereco'])
                
                e6, e7, e8 = st.columns(3)
                ed_faixa = e6.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(atleta['Faixa']))
                ed_valor = e7.number_input("Mensalidade", value=float(atleta['Mensalidade']))
                ed_status = e8.selectbox("Status", ["Ativo", "Inativo"], index=0 if atleta['Status'] == "Ativo" else 1)

                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("💾 SALVAR ALTERAÇÕES", use_container_width=True):
                    st.session_state.atletas_df.loc[idx, ["Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Tele
