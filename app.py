import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- 2. BANCO DE DADOS (CSV) ---
DB_ATLETAS = "atletas_v7.csv"
DB_FINANCEIRO = "financeiro_v7.csv"

def load_data():
    cols_atleta = ["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao"]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    
    # Carregar Atletas
    if os.path.exists(DB_ATLETAS):
        df_a = pd.read_csv(DB_ATLETAS)
    else:
        df_a = pd.DataFrame(columns=cols_atleta)
        
    # Carregar Financeiro
    if os.path.exists(DB_FINANCEIRO):
        df_f = pd.read_csv(DB_FINANCEIRO)
    else:
        df_f = pd.DataFrame(columns=cols_fin)
            
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

# Inicializar Estado da Sessão
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. BARRA LATERAL (MENU) ---
with st.sidebar:
    st.header("🥋 Sistema Judô")
    aba = st.radio("Navegação", ["Dashboard", "Atletas", "Financeiro", "Sistema"], key="main_nav")
    st.divider()
    st.info("Assoc. Roberdrayner Martins")

# --- 4. DASHBOARD ---
if aba == "Dashboard":
    st.title("📊 Painel de Controle")
    df_a = st.session_state.atletas_df
    df_f = st.session_state.fin_df
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Alunos", len(df_a))
    
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    m2.metric("Receita Total", f"R$ {receita:,.2f}")
    
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    m3.metric("Alunos Ativos", ativos)

    if not df_a.empty:
        g1, g2 = st.columns(2)
        with g1:
            fig_pie = px.pie(df_a, names='Faixa', title="Distribuição por Faixa", hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            if not df_f.empty:
                fig_bar = px.bar(df_f, x='Mes_Ref', y='Valor_Total', color='Metodo', title="Entradas Mensais")
                st.plotly_chart(fig_bar, use_container_width=True)

# --- 5. ATLETAS ---
elif aba == "Atletas":
    st.title("🥋 Gestão de Alunos")
    tab_cad, tab_edit = st.tabs(["Cadastrar", "Editar/Remover"])
    
    with tab_cad:
        with st.form("form_cad", clear_on_submit=True):
            nome = st.text_input("Nome Completo")
            c1, c2 = st.columns(2)
            faixa = c1.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = c2.number_input("Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Salvar Matrícula"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    hoje = datetime.now().strftime("%d/%m/%Y")
                    
                    novo_atleta = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Faixa": faixa, 
                        "Status": "Ativo", "Mensalidade": valor, "Data_Filiacao": hoje
                    }])
                    
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_atleta], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Atleta cadastrado!")
                    st.rerun()

    with tab_edit:
        if not st.session_state.atletas_df.empty:
            busca = st.text_input("Pesquisar Aluno")
            res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
            st.dataframe(res, use_container_width=True, hide_index=True)
            
            if not res.empty:
                edit_nome = st.selectbox("Escolha para editar", res['Nome'].tolist())
                idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == edit_nome].index[0]
                
                with st.form("form_edit"):
                    st.write(f"Editando: {edit_nome}")
                    novo_n = st.text_input("Novo Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                    novo_v = st.number_input("Novo Valor", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                    novo_s = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if st.session_state.atletas_df.at[idx, 'Status'] == "Ativo" else 1)
                    
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("Salvar Alterações"):
                        st.session_state.atletas_df.at[idx, 'Nome'] = novo_n
                        st.session_state.atletas_df.at[idx, 'Mensalidade'] = novo_v
                        st.session_state.atletas_df.at[idx, 'Status'] = novo_s
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.success("Atualizado!")
                        st.rerun()
                    if b2.form_submit_button("Excluir"):
                        st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.rerun()

# --- 6. FINANCEIRO ---
elif aba == "Financeiro":
    st.title("💰 Financeiro")
    
    with st.expander("Registrar Novo Pagamento", expanded=True):
        if not st.session_state.atletas_df.empty:
            f1, f2 = st.columns(2)
            aluno = f1.selectbox("Selecione o Aluno", st.session_state.atletas_df['Nome'].tolist())
            data_pg = f2.date_input("Data do Pagamento", datetime.now())
            
            f3, f4 = st.columns(2)
            mes_ref = f3.selectbox("Mês Referência", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            metodo = f4.selectbox("Método", ["PIX", "Dinheiro", "Cartão", "Misto"])
            
            val_sugerido = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
            
            detalhe = ""
            if metodo == "Misto":
                m1, m2 = st.columns(2)
                v_pix = m1.number_input("Valor PIX", value=val_sugerido/2)
                v_din = m2.number_input("Valor Dinheiro", value=val_sugerido/2)
                valor_final = v_pix + v_din
                detalhe = f"PIX: {v_pix} | Din: {v_din}"
            else:
                valor_final = st.number_input("Valor Recebido", value=val_sugerido)
            
            if st.button("Confirmar Pagamento"):
                id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                novo_p = pd.DataFrame([{
                    "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": mes_ref,
                    "Valor_Total": valor_final, "Data_Pagamento": data_pg.strftime("%d/%m/%Y"),
                    "Metodo": metodo, "Detalhe_Misto": detalhe
                }])
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.success("Pagamento registrado!")
                st.rerun()

    st.divider()
    st.subheader("Histórico de Mensalidades")
    st.dataframe(st.session_state.fin_df, use_container_width=True, hide_index=True)

# --- 7. SISTEMA ---
elif aba == "Sistema":
    st.title("⚙️ Configurações")
    st.download_button("Exportar Backup CSV", 
                       data=st.session_state.atletas_df.to_csv(index=False).encode('utf-8'), 
                       file_name="backup_judo.csv")
