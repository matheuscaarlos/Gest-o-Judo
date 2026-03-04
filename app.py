import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro - Recibos", page_icon="🥋", layout="wide")

DB_ATLETAS = "atletas_v13.csv"
DB_FINANCEIRO = "financeiro_v13.csv"

def load_data():
    cols_a = ["ID", "Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Data_Filiacao"]
    cols_f = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=cols_a)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=cols_f)
    if not df_a.empty: df_a['ID'] = df_a['ID'].astype(int)
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 2. MENU ---
aba = st.sidebar.radio("Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro"])

# --- 3. ATLETAS (EDIÇÃO E CADASTRO) ---
if aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    
    with st.expander("➕ Nova Matrícula"):
        with st.form("f_novo"):
            n_nome = st.text_input("Nome Completo*")
            n_faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            n_val = st.number_input("Mensalidade (R$)", value=150.0)
            if st.form_submit_button("Salvar"):
                if n_nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{"ID": new_id, "Nome": n_nome, "Faixa": n_faixa, "Mensalidade": n_val, "Status": "Ativo", "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")}])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Cadastrado!"); st.rerun()

    with st.expander("🔍 Editar / Excluir Atleta", expanded=True):
        busca = st.text_input("Buscar por nome")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
        st.dataframe(df_res[["ID", "Nome", "Faixa", "Status"]], use_container_width=True, hide_index=True)
        
        if not df_res.empty:
            sel = st.selectbox("Selecionar para Editar", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
            id_sel = int(sel.split("(ID: ")[1].replace(")", ""))
            idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
            
            with st.form("f_edicao"):
                atleta = st.session_state.atletas_df.loc[idx]
                e_nome = st.text_input("Nome", value=atleta['Nome'])
                e_faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=0)
                e_val = st.number_input("Mensalidade", value=float(atleta['Mensalidade']))
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.atletas_df.at[idx, 'Nome'] = e_nome
                    st.session_state.atletas_df.at[idx, 'Faixa'] = e_faixa
                    st.session_state.atletas_df.at[idx, 'Mensalidade'] = e_val
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Atualizado!"); st.rerun()
                if c2.form_submit_button("🗑️ Excluir"):
                    st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.rerun()

# --- 4. FINANCEIRO & RECIBO ---
elif aba == "💰 Financeiro":
    st.title("💸 Caixa & Recibos")
    
    with st.expander("💳 Registrar Pagamento", expanded=True):
        if not st.session_state.atletas_df.empty:
            aluno_nome = st.selectbox("Aluno", st.session_state.atletas_df['Nome'].tolist())
            data_pg = st.date_input("Data do Pagamento", datetime.now())
            metodo = st.selectbox("Método", ["PIX", "Dinheiro", "Cartão", "Misto"])
            
            # Valor sugerido do cadastro
            v_sug = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_nome]['Mensalidade'].values[0])
            valor = st.number_input("Valor Recebido (R$)", value=v_sug)
            
            if st.button("🚀 Confirmar e Gerar Recibo"):
                id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_nome]['ID'].values[0]
                dt_str = data_pg.strftime("%d/%m/%Y")
                
                # Salvar no financeiro
                novo_p = pd.DataFrame([{"ID_Atleta": id_a, "Nome_Atleta": aluno_nome, "Mes_Ref": datetime.now().strftime("%B"), "Valor_Total": valor, "Data_Pagamento": dt_str, "Metodo": metodo}])
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                
                st.success("Pagamento Registrado!")
                
                # GERADOR DE TEXTO
