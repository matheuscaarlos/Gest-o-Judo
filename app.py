import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from PIL import Image

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- BANCO DE DADOS ---
DB_ATLETAS = "atletas_v5.csv"
DB_FINANCEIRO = "financeiro_v5.csv"

def load_data():
    cols_atleta = ["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao", "CPF", "RG", "Telefone", "Endereco", "Peso", "Sangue"]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    
    if os.path.exists(DB_ATLETAS):
        df = pd.read_csv(DB_ATLETAS)
        for col in cols_atleta:
            if col not in df.columns: df[col] = "Não Informado"
    else:
        df = pd.DataFrame(columns=cols_atleta)
        
    if os.path.exists(DB_FINANCEIRO):
        df_fin = pd.read_csv(DB_FINANCEIRO)
        for col in cols_fin:
            if col not in df_fin.columns: df_fin[col] = ""
    else:
        df_fin = pd.DataFrame(columns=cols_fin)
        
    return df, df_fin

def save_data(atleta_df, fin_df):
    atleta_df.to_csv(DB_ATLETAS, index=False)
    fin_df.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    st.markdown("### Associação Roberdrayner Martins")
    aba = st.radio("Menu", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"])

# --- DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel de Controle")
    df_a = st.session_state.atletas_df
    df_f = st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Cadastrados", len(df_a))
    
    receita_mes = 0
    if not df_f.empty:
        # Soma valores totais convertendo para numérico
        receita_mes = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    
    c2.metric("Receita Total (Histórico)", f"R$ {receita_mes:,.2f}")
    
    if not df_a.empty:
        fig = px.pie(df_a, names='Faixa', title="Distribuição por Faixas", hole=.4)
        st.plotly_chart(fig, use_container_width=True)

# --- ATLETAS ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    tab_cad, tab_edit = st.tabs(["➕ Novo Cadastro", "📝 Editar ou Excluir"])
    
    with tab_cad:
        with st.form("form_novo"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome Completo*")
            tel = c2.text_input("Telefone/WhatsApp")
            
            c3, c4 = st.columns(2)
            faixa = c3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = c4.number_input("Valor Mensalidade Padrão", value=150.0)
            
            if st.form_submit_button("✅ Cadastrar"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([[new_id, nome, faixa, "Ativo", valor, datetime.now().strftime("%d/%m/%Y"), "-", "-", tel, "-", 0.0, "N/I"]], 
                                       columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"{nome} cadastrado!")
                    st.rerun()

    with tab_edit:
        if not st.session_state.atletas_df.empty:
            sel = st.selectbox("Selecione para Editar", st.session_state.atletas_df['Nome'].tolist())
            idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == sel].index[0]
            with st.form("form_edit"):
                n_nome = st.text_input("Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                n_val = st.number_input("Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.form_submit_button("💾 Salvar"):
                    st.session_state.atletas_df.at[idx, 'Nome'] = n_nome
                    st.session_state.atletas_df.at[idx, 'Mensalidade'] = n_val
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.rerun()
                if c_btn2.form_submit_button("🗑️ Excluir"):
                    st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.rerun()

# --- FINANCEIRO (NOVA FUNCIONALIDADE MISTA) ---
elif aba == "💰 Financeiro":
    st.title("💸 Gestão de Pagamentos")
    
    with st.container(border=True):
        st.subheader("Registrar Recebimento")
        c1, c2 = st.columns(2)
        
        aluno_f = c1.selectbox("Atleta", st.session_state.atletas_df['Nome'].tolist())
        data_pg = c2.date_input("Data do Pagamento", datetime.now())
        
        c3, c4 = st.columns(2)
        mes_ref = c3.selectbox("Mês de Referência", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        metodo = c4.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão", "Misto (PIX + Dinheiro)"])
        
        # Lógica para Pagamento Misto
        detalhe_misto = ""
        valor_total = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_f]['Mensalidade'].values[0]
        
        if metodo == "Misto (PIX + Dinheiro)":
            st.info("Informe a divisão dos valores:")
            col_m1, col_m2 = st.columns(2)
            v_pix = col_m1.number_input("Valor no PIX (R$)", value=valor_total/2)
            v_din = col_m2.number_input("Valor no Dinheiro (R$)", value=valor_total/2)
            valor_total = v_pix + v_din
            detalhe_misto = f"PIX: R${v_pix:.2f} | Din: R${v_din:.2f}"
        else:
            valor_total = st.number_input("Confirmar Valor Total (R$)", value=float(valor_total))

        if st.button("🚀 Confirmar Recebimento"):
            id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_f]['ID'].values[0]
            
            novo_pgto = pd.DataFrame([[
                id_a, 
                aluno_f, 
                mes_ref, 
                valor_total, 
                data_pg.strftime("%d/%m/%Y"), 
                metodo, 
                detalhe_misto
            ]], columns=st.session_state.fin_df.columns)
            
            st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pgto], ignore_index=True)
            save_data(st.session_state.atletas_df, st.session_state.fin_df)
            st.balloons()
            st.success(f"Pagamento de {aluno_f} registrado!")

    st.divider()
    st.subheader("📊 Histórico de Entradas")
    if not st.session_state.fin_df.empty:
        st.dataframe(st.session_state.fin_df[['Nome_Atleta', 'Mes_Ref', 'Valor_Total', 'Data_Pagamento', 'Metodo', 'Detalhe_Misto']], 
                     use_container_width=True, hide_index=True)

# --- SISTEMA ---
elif aba == "⚙️ Sistema":
    st.title("⚙️ Configurações")
    st.download_button("📥 Exportar Relatório Financeiro", data=st.session_state.fin_df.to_csv(index=False).encode('utf-8'), file_name="financeiro_judo.csv")

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    st.markdown("### Associação Roberdrayner Martins")
    aba = st.radio("Menu", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"])

# --- DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel de Controle")
    df_a = st.session_state.atletas_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Cadastrados", len(df_a))
    c2.metric("Ativos", len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0)
    
    receita = pd.to_numeric(df_a['Mensalidade'], errors='coerce').sum() if not df_a.empty else 0.0
    c3.metric("Mensalidade Prevista", f"R$ {receita:,.2f}")
    
    if not df_a.empty:
        fig = px.pie(df_a, names='Faixa', title="Graduação dos Alunos", hole=.4, 
                     color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig, use_container_width=True)

# --- ATLETAS (CADASTRO, EDIÇÃO E EXCLUSÃO) ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    
    tab_cad, tab_edit = st.tabs(["➕ Novo Cadastro", "📝 Editar ou Excluir"])
    
    with tab_cad:
        with st.form("form_novo_atleta", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            nome = col1.text_input("Nome Completo*")
            cpf = col2.text_input("CPF")
            rg = col3.text_input("RG")
            
            col4, col5, col6 = st.columns(3)
            tel = col4.text_input("Telefone")
            peso = col5.number_input("Peso (kg)", value=70.0)
            sangue = col6.selectbox("Sangue", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "N/I"])
            
            endereco = st.text_input("Endereço")
            
            st.divider()
            col7, col8, col9 = st.columns(3)
            faixa = col7.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = col8.number_input("Mensalidade", value=150.0)
            status_init = col9.selectbox("Status", ["Ativo", "Inativo"])
            
            if st.form_submit_button("✅ Salvar Cadastro"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo_atleta = pd.DataFrame([[new_id, nome, faixa, status_init, valor, datetime.now().strftime("%d/%m/%Y"), cpf, rg, tel, endereco, peso, sangue]], 
                                               columns=st.session_state.atletas_df.columns)
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_atleta], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"{nome} cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("O nome é obrigatório.")

    with tab_edit:
        if st.session_state.atletas_df.empty:
            st.info("Nenhum atleta cadastrado.")
        else:
            atleta_selecionado = st.selectbox("Selecione para Editar/Excluir", st.session_state.atletas_df['Nome'].tolist())
            idx = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == atleta_selecionado].index[0]
            
            # Formulário de Edição
            with st.form("form_edicao"):
                st.subheader(f"Editando Registro de {atleta_selecionado}")
                e_col1, e_col2 = st.columns(2)
                novo_nome = e_col1.text_input("Nome", value=st.session_state.atletas_df.at[idx, 'Nome'])
                novo_tel = e_col2.text_input("Telefone", value=str(st.session_state.atletas_df.at[idx, 'Telefone']))
                
                e_col3, e_col4, e_col5 = st.columns(3)
                nova_faixa = e_col3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], 
                                              index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(st.session_state.atletas_df.at[idx, 'Faixa']))
                novo_status = e_col4.selectbox("Status", ["Ativo", "Inativo"], index=0 if st.session_state.atletas_df.at[idx, 'Status'] == "Ativo" else 1)
                novo_valor = e_col5.number_input("Mensalidade", value=float(st.session_state.atletas_df.at[idx, 'Mensalidade']))
                
                # Botoes de acao dentro do form (precisam ser submit_button)
                c_btn1, c_btn2 = st.columns(2)
                btn_save = c_btn1.form_submit_button("💾 SALVAR ALTERAÇÕES")
                btn_del = c_btn2.form_submit_button("🗑️ EXCLUIR ATLETA")
                
                if btn_save:
                    st.session_state.atletas_df.at[idx, 'Nome'] = novo_nome
                    st.session_state.atletas_df.at[idx, 'Telefone'] = novo_tel
                    st.session_state.atletas_df.at[idx, 'Faixa'] = nova_faixa
                    st.session_state.atletas_df.at[idx, 'Status'] = novo_status
                    st.session_state.atletas_df.at[idx, 'Mensalidade'] = novo_valor
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Dados atualizados!")
                    st.rerun()
                
                if btn_del:
                    st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.warning("Atleta removido.")
                    st.rerun()

# --- FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💸 Controle Financeiro")
    df_a = st.session_state.atletas_df
    
    if df_a.empty:
        st.warning("Cadastre atletas primeiro.")
    else:
        with st.container(border=True):
            aluno_f = st.selectbox("Registrar Pagamento para:", df_a['Nome'].tolist())
            mes_f = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            metodo_f = st.radio("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão", "Boleto"], horizontal=True)
            
            valor_ref = df_a[df_a['Nome'] == aluno_f]['Mensalidade'].values[0]
            
            if st.button(f"Confirmar Recebimento de R$ {valor_ref}"):
                id_a = df_a[df_a['Nome'] == aluno_f]['ID'].values[0]
                novo_p = pd.DataFrame([[id_a, mes_f, 2024, valor_ref, datetime.now().strftime("%d/%m/%Y"), metodo_f]], 
                                       columns=st.session_state.fin_df.columns)
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.balloons()
                st.success(f"Pagamento de {aluno_f} registrado!")

# --- SISTEMA ---
elif aba == "⚙️ Sistema":
    st.title("⚙️ Configurações")
    st.download_button("📥 Exportar Backup (CSV)", data=st.session_state.atletas_df.to_csv(index=False).encode('utf-8'), file_name="atletas_judo.csv")
    if st.button("🔴 RESET TOTAL (LIMPAR TUDO)"):
        if os.path.exists(DB_ATLETAS): os.remove(DB_ATLETAS)
        if os.path.exists(DB_FINANCEIRO): os.remove(DB_FINANCEIRO)
        st.session_state.clear()
        st.rerun()
