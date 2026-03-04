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
    
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=cols_atleta)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=cols_fin)
            
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.header("🥋 Menu")
    aba = st.radio("Navegação", ["Dashboard", "Atletas", "Financeiro", "Sistema"], key="nav_v71")

# --- 4. DASHBOARD ---
if aba == "Dashboard":
    st.title("📊 Painel Geral")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Alunos", len(df_a))
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    c2.metric("Receita Total", f"R$ {receita:,.2f}")
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    c3.metric("Alunos Ativos", ativos)

    if not df_a.empty:
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.pie(df_a, names='Faixa', title="Alunos por Faixa"), use_container_width=True)
        with g2:
            if not df_f.empty:
                st.plotly_chart(px.bar(df_f, x='Mes_Ref', y='Valor_Total', title="Entradas por Mês"), use_container_width=True)

# --- 5. GESTÃO DE ATLETAS ---
elif aba == "Atletas":
    st.title("👥 Alunos")
    t_cad, t_edit = st.tabs(["Novo Cadastro", "Editar/Excluir"])
    
    with t_cad:
        with st.form("cad_atleta", clear_on_submit=True):
            nome = st.text_input("Nome Completo")
            col1, col2 = st.columns(2)
            faixa = col1.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = col2.number_input("Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Cadastrar"):
                if nome:
                    # AJUSTE: Data de Filiação no formato DD/MM/AAAA
                    data_br = datetime.now().strftime("%d/%m/%Y")
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    
                    novo = pd.DataFrame([{"ID": new_id, "Nome": nome, "Faixa": faixa, "Status": "Ativo", "Mensalidade": valor, "Data_Filiacao": data_br}])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"Matrícula realizada em {data_br}!")
                    st.rerun()

    with t_edit:
        if not st.session_state.atletas_df.empty:
            busca = st.text_input("Buscar Aluno")
            res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
            st.dataframe(res, use_container_width=True, hide_index=True)
            
            if not res.empty:
                aluno_sel = st.selectbox("Escolha para editar", res['Nome'].tolist())
                idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_sel].index[0]
                
                with st.form("edit_atleta"):
                    n_nome = st.text_input("Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                    n_faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=0)
                    n_valor = st.number_input("Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                    
                    if st.form_submit_button("Atualizar"):
                        st.session_state.atletas_df.at[idx, 'Nome'] = n_nome
                        st.session_state.atletas_df.at[idx, 'Faixa'] = n_faixa
                        st.session_state.atletas_df.at[idx, 'Mensalidade'] = n_valor
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.success("Dados salvos!")
                        st.rerun()

# --- 6. FINANCEIRO ---
elif aba == "Financeiro":
    st.title("💰 Caixa")
    
    with st.expander("💳 Novo Pagamento", expanded=True):
        if not st.session_state.atletas_df.empty:
            f1, f2 = st.columns(2)
            aluno = f1.selectbox("Aluno", st.session_state.atletas_df['Nome'].tolist())
            # Seletor de data (o usuário escolhe no calendário)
            data_calendario = f2.date_input("Data do Recebimento", datetime.now())
            
            f3, f4 = st.columns(2)
            mes_ref = f3.selectbox("Mês Referência", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            metodo = f4.selectbox("Método", ["PIX", "Dinheiro", "Cartão", "Misto"])
            
            val_base = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
            
            detalhe = ""
            if metodo == "Misto":
                m1, m2 = st.columns(2)
                vp = m1.number_input("PIX", value=val_base/2)
                vd = m2.number_input("Dinheiro", value=val_base/2)
                valor_final = vp + vd
                detalhe = f"PIX: {vp} | Din: {vd}"
            else:
                valor_final = st.number_input("Valor", value=val_base)
            
            if st.button("Confirmar Pagamento"):
                id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                # AJUSTE: Converte a data do calendário para o formato brasileiro
                data_pag_br = data_calendario.strftime("%d/%m/%Y")
                
                novo_p = pd.DataFrame([{
                    "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": mes_ref,
                    "Valor_Total": valor_final, "Data_Pagamento": data_pag_br,
                    "Metodo": metodo, "Detalhe_Misto": detalhe
                }])
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.success(f"Pago em {data_pag_br}!")
                st.rerun()

    st.divider()
    st.subheader("📊 Histórico")
    st.dataframe(st.session_state.fin_df, use_container_width=True, hide_index=True)

# --- 7. SISTEMA ---
elif aba == "Sistema":
    st.title("⚙️ Backup")
    st.download_button("Exportar Planilha CSV", 
                       data=st.session_state.fin_df.to_csv(index=False).encode('utf-8'), 
                       file_name=f"financeiro_judo_{datetime.now().strftime('%d_%m_%Y')}.csv")
