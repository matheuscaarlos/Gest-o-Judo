import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- 2. BANCO DE DADOS (CSV) ---
DB_ATLETAS = "atletas_v8.csv"
DB_FINANCEIRO = "financeiro_v8.csv"

def load_data():
    cols_atleta = ["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao"]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=cols_atleta)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=cols_fin)
    
    # Garantir que IDs sejam inteiros
    if not df_a.empty:
        df_a['ID'] = df_a['ID'].astype(int)
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

# Inicializar Estado da Sessão
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. MENU LATERAL ---
with st.sidebar:
    st.header("🥋 Menu Principal")
    aba = st.radio("Navegação", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"], key="nav_v8")
    st.divider()
    st.caption("Assoc. Roberdrayner Martins v8.0")

# --- 4. DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("📊 Painel de Controle")
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
                st.plotly_chart(px.bar(df_f, x='Mes_Ref', y='Valor_Total', title="Entradas Mensais"), use_container_width=True)

# --- 5. GESTÃO DE ATLETAS (CORREÇÃO DE EXCLUSÃO) ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Judocas")
    t_cad, t_edit = st.tabs(["➕ Novo Cadastro", "📝 Editar / Excluir"])
    
    with t_cad:
        with st.form("form_cadastro", clear_on_submit=True):
            nome = st.text_input("Nome Completo*")
            col1, col2 = st.columns(2)
            faixa = col1.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = col2.number_input("Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome:
                    data_hoje = datetime.now().strftime("%d/%m/%Y")
                    # Gerar ID único robusto
                    novo_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    
                    novo_registro = pd.DataFrame([{
                        "ID": novo_id, "Nome": nome, "Faixa": faixa, 
                        "Status": "Ativo", "Mensalidade": valor, "Data_Filiacao": data_hoje
                    }])
                    
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_registro], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"Atleta {nome} cadastrado com sucesso!")
                    st.rerun()

    with t_edit:
        if not st.session_state.atletas_df.empty:
            busca = st.text_input("🔍 Pesquisar por nome", key="busca_atleta")
            # Filtragem para exibição
            df_filtrado = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            if not df_filtrado.empty:
                st.divider()
                # Seleção baseada em Nome + ID para não haver erro com nomes iguais
                lista_nomes = [f"{row['Nome']} (ID: {row['ID']})" for _, row in df_filtrado.iterrows()]
                escolha = st.selectbox("Selecione o atleta para ação:", lista_nomes)
                
                # Extrair o ID da string de escolha
                id_para_acao = int(escolha.split("(ID: ")[1].replace(")", ""))
                
                col_btn1, col_btn2 = st.columns(2)
                
                if col_btn1.button("🗑️ EXCLUIR ATLETA", type="secondary", use_container_width=True):
                    # Localizar e remover pelo ID (mais seguro que índice)
                    st.session_state.atletas_df = st.session_state.atletas_df[st.session_state.atletas_df['ID'] != id_para_acao]
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.warning("Registro removido permanentemente.")
                    st.rerun()
                
                st.caption("Nota: Para editar, cadastre novamente ou altere via planilha Excel (Sistema).")
        else:
            st.info("Nenhum atleta matriculado.")

# --- 6. FINANCEIRO (DATAS BRASILEIRAS) ---
elif aba == "💰 Financeiro":
    st.title("💸 Caixa e Recebimentos")
    
    with st.expander("💳 Registrar Pagamento", expanded=True):
        if not st.session_state.atletas_df.empty:
            f1, f2 = st.columns(2)
            aluno = f1.selectbox("Judoca", st.session_state.atletas_df['Nome'].tolist())
            data_calendario = f2.date_input("Data do Recebimento", datetime.now())
            
            f3, f4 = st.columns(2)
            mes_ref = f3.selectbox("Mês Referência", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            metodo = f4.selectbox("Método", ["PIX", "Dinheiro", "Cartão", "Misto"])
            
            # Busca automática do valor da mensalidade
            v_base = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
            
            detalhe = ""
            if metodo == "Misto":
                m1, m2 = st.columns(2)
                vp = m1.number_input("Valor PIX", value=v_base/2)
                vd = m2.number_input("Valor Dinheiro", value=v_base/2)
                valor_total = vp + vd
                detalhe = f"Misto: PIX R${vp:.2f} | Din: R${vd:.2f}"
            else:
                valor_total = st.number_input("Confirmar Valor", value=v_base)
            
            if st.button("🚀 Confirmar Pagamento"):
                id_atleta = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                data_formatada = data_calendario.strftime("%d/%m/%Y")
                
                novo_pag = pd.DataFrame([{
                    "ID_Atleta": id_atleta, "Nome_Atleta": aluno, "Mes_Ref": mes_ref,
                    "Valor_Total": valor_total, "Data_Pagamento": data_formatada,
                    "Metodo": metodo, "Detalhe_Misto": detalhe
                }])
                
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pag], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.success(f"Pagamento de {aluno} registrado em {data_formatada}!")
                st.rerun()

    st.divider()
    st.subheader("📊 Histórico de Transações")
    st.dataframe(st.session_state.fin_df, use_container_width=True, hide_index=True)

# --- 7. SISTEMA ---
elif aba == "⚙️ Sistema":
    st.title("⚙️ Administração de Dados")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Backup")
        st.download_button("📥 Baixar Planilha de Atletas (CSV)", 
                           data=st.session_state.atletas_df.to_csv(index=False).encode('utf-8'), 
                           file_name=f"atletas_judo_{datetime.now().strftime('%d_%m_%Y')}.csv")
    with c2:
        st.subheader("Limpeza")
        if st.button("⚠️ Resetar Financeiro (CUIDADO)"):
            st.session_state.fin_df = pd.DataFrame(columns=st.session_state.fin_df.columns)
            save_data(st.session_state.atletas_df, st.session_state.fin_df)
            st.rerun()
