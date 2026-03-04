import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Judô Pro - Roberdrayner", page_icon="🥋", layout="wide")

# --- 2. ESTILOS CUSTOMIZADOS (CSS) ---
st.markdown("""
    <style>
    /* Estilização dos Botões com Transição */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease-in-out;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        border-color: #E63946;
        color: #E63946;
    }
    
    /* Estilização das Métricas (Dashboard) */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        color: #1D3557;
        font-weight: bold;
    }
    
    /* Cabeçalhos dos Expanders mais limpos */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1D3557;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. BANCO DE DADOS (LÓGICA BLINDADA MANTIDA) ---
DB_ATLETAS = "atletas_v16.csv"
DB_FINANCEIRO = "financeiro_v16.csv"

COLS_A = ["ID", "Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Data_Filiacao"]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Observacao"]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    
    for col in COLS_A:
        if col not in df_a.columns: df_a[col] = 0.0 if col in ['Peso', 'Mensalidade'] else ""
    for col in COLS_F:
        if col not in df_f.columns: df_f[col] = ""
            
    if not df_a.empty: 
        df_a['ID'] = df_a['ID'].astype(int)
        df_a['Peso'] = pd.to_numeric(df_a['Peso'], errors='coerce').fillna(0.0)
        df_a['Mensalidade'] = pd.to_numeric(df_a['Mensalidade'], errors='coerce').fillna(150.0)
        df_a.fillna("", inplace=True)
        
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 4. MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043831.png", width=80) # Ícone genérico de artes marciais
    st.title("Assoc. Roberdrayner")
    st.caption("🥋 Gestão de Judô - v16.0")
    st.divider()
    aba = st.radio("Navegação Principal", ["🏠 Dashboard", "👥 Atletas", "💰 Financeiro"])
    st.divider()
    st.markdown("Desenvolvido para **Alta Performance**.")

# --- 5. DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("📊 Painel de Controle")
    st.markdown("Tenha uma visão geral do seu dojo.")
    
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    st.divider()
    
    # Grid de Métricas
    c1, c2, c3 = st.columns(3)
    ativos = len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0
    inativos = len(df_a[df_a['Status'] == 'Inativo']) if not df_a.empty else 0
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    
    c1.metric("🥋 Alunos Ativos", ativos, delta=f"{inativos} Inativos", delta_color="off")
    c2.metric("💳 Receita Total", f"R$ {receita:,.2f}")
    c3.metric("📝 Total Cadastros", len(df_a))
    
    st.divider()
    
    if not df_a.empty:
        st.subheader("📈 Estatísticas")
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.plotly_chart(px.pie(df_a, names='Faixa', title="Distribuição de Alunos por Faixa", hole=0.4), use_container_width=True)
        with col_graf2:
            if not df_f.empty:
                df_f_mensal = df_f.groupby('Mes_Ref')['Valor_Total'].sum().reset_index()
                st.plotly_chart(px.bar(df_f_mensal, x='Mes_Ref', y='Valor_Total', title="Faturamento Mensal", color_discrete_sequence=['#1D3557']), use_container_width=True)

# --- 6. ATLETAS ---
elif aba == "👥 Atletas":
    st.title("👥 Gestão de Atletas")
    st.markdown("Cadastre novos judocas ou atualize informações existentes.")
    
    # 6.1 CADASTRO
    with st.expander("➕ Inserir Nova Matrícula", expanded=False):
        with st.form("form_novo", clear_on_submit=True):
            st.subheader("Dados Pessoais")
            nome = st.text_input("Nome Completo*")
            c1, c2, c3 = st.columns(3)
            cpf, rg, peso = c1.text_input("CPF"), c2.text_input("RG"), c3.number_input("Peso (kg)", min_value=0.0, step=0.5)
            
            st.subheader("Contato & Endereço")
            c4, c5 = st.columns(2)
            tel, email = c4.text_input("Telefone / WhatsApp"), c5.text_input("E-mail")
            end = st.text_input("Endereço Completo")
            
            st.subheader("Dados do Dojo")
            c6, c7 = st.columns(2)
            faixa = c6.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            val = c7.number_input("Mensalidade Acordada (R$)", value=150.0)
            
            st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
            if st.form_submit_button("🚀 Finalizar Matrícula", use_container_width=True):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo_reg = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "CPF": cpf, "RG": rg, "Peso": peso,
                        "Faixa": faixa, "Endereco": end, "Telefone": tel, "Email": email,
                        "Status": "Ativo", "Mensalidade": val, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")
                    }])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_reg], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.toast("✅ Atleta matriculado com sucesso!", icon="🥋")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("O campo 'Nome Completo' é obrigatório.")

    # 6.2 EDIÇÃO
    with st.expander("🔍 Pesquisar, Editar ou Remover", expanded=True):
        if not st.session_state.atletas_df.empty:
            busca = st.text_input("🔎 Digite o nome do aluno para buscar...")
            df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
            
            # Tabela estilizada (ocultando colunas irrelevantes para a busca rápida)
            st.dataframe(df_res[["ID", "Nome", "Faixa", "Telefone", "Status"]], use_container_width=True, hide_index=True)
            
            if not df_res.empty:
                st.divider()
                sel = st.selectbox("Selecione um aluno da lista acima para gerenciar:", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
                id_sel = int(sel.split("(ID: ")[1].replace(")", ""))
                idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
                atleta = st.session_state.atletas_df.loc[idx]

                with st.form("form_edit"):
                    st.markdown(f"### 📝 Perfil: **{atleta['Nome']}**")
                    
                    e_nome = st.text_input("Nome Completo", value=str(atleta['Nome']))
                    
                    c1, c2, c3 = st.columns(3)
                    e_cpf, e_rg, e_peso = c1.text_input("CPF", value=str(atleta['CPF'])), c2.text_input("RG", value=str(atleta['RG'])), c3.number_input("Peso (kg)", value=float(atleta['Peso']) if pd.notna(atleta['Peso']) else 0.0)
                    
                    c4, c5 = st.columns(2)
                    e_tel, e_email = c4.text_input("Telefone", value=str(atleta['Telefone'])), c5.text_input("Email", value=str(atleta['Email']))
                    e_end = st.text_input("Endereço", value=str(atleta['Endereco']))
                    
                    lista_faixas = ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"]
                    idx_faixa = lista_faixas.index(atleta['Faixa']) if atleta['Faixa'] in lista_faixas else 0
                    
                    c6, c7, c8 = st.columns(3)
                    e_faixa = c6.selectbox("Faixa", lista_faixas, index=idx_faixa)
                    e_val = c7.number_input("Mensalidade", value=float(atleta['Mensalidade']) if pd.notna(atleta['Mensalidade']) else 150.0)
                    e_status = c8.selectbox("Status", ["Ativo", "Inativo"], index=0 if atleta['Status'] == "Ativo" else 1)

                    st.markdown("<br>", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        st.session_state.atletas_df.loc[idx, ["Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade"]] = [
                            e_nome, e_cpf, e_rg, e_peso, e_faixa, e_end, e_tel, e_email, e_status, e_val
                        ]
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.toast("✅ Perfil atualizado!", icon="💾")
                        time.sleep(1)
                        st.rerun()
                    
                    if b2.form_submit_button("🗑️ Excluir Permanentemente", use_container_width=True):
                        st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.toast("⚠️ Atleta removido do sistema.", icon="🗑️")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("Nenhum atleta cadastrado no momento.")

# --- 7. FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💸 Controle de Caixa e Mensalidades")
    st.markdown("Registre recebimentos e gere recibos automaticamente para o WhatsApp.")
    
    with st.container():
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("💳 Novo Recebimento")
            if not st.session_state.atletas_df.empty:
                with st.form("form_pagamento", clear_on_submit=True):
                    aluno = st.selectbox("Selecione o Aluno", st.session_state.atletas_df['Nome'].tolist())
                    
                    col_d, col_m = st.columns(2)
                    data_pg = col_d.date_input("Data do Pagamento", datetime.now())
                    metodo = col_m.selectbox("Meio de Pagamento", ["PIX", "Dinheiro", "Cartão", "Misto"])
                    
                    obs = st.text_input("Referência / Observação (Ex: Mensalidade de Abril)")
                    
                    # Buscar valor sugerido para exibir no form
                    val_sugerido = 150.0
                    if aluno:
                        val_bd = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0]
                        val_sugerido = float(val_bd) if pd.notna(val_bd) else 150.0
                        
                    valor = st.number_input("Valor Recebido (R$)", value=val_sugerido)
                    
                    if st.form_submit_button("🧾 Confirmar e Gerar Recibo", use_container_width=True):
                        id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                        dt_format = data_pg.strftime("%d/%m/%Y")
                        
                        novo_pg = pd.DataFrame([{
                            "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": datetime.now().strftime("%B"),
                            "Valor_Total": valor, "Data_Pagamento": dt_format, "Metodo": metodo, "Observacao": obs
                        }])
                        st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pg], ignore_index=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        
                        # Guardar o texto do recibo na sessão para mostrar fora do form
                        st.session_state.ultimo_recibo = f"""*RECIBO DE JUDÔ* 🥋
-------------------------
*Aluno:* {aluno}
*Data:* {dt_format}
*Valor:* R$ {valor:.2f}
*Pagamento:* {metodo}
*Obs:* {obs if obs else 'Mensalidade'}
-------------------------
_Assoc. Roberdrayner Martins_"""
                        
                        st.toast("✅ Pagamento computado com sucesso!", icon="💰")
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.warning("Cadastre alunos primeiro.")

        with c2:
            st.subheader("📱 Recibo (WhatsApp)")
            if 'ultimo_recibo' in st.session_state:
                st.success("Recibo gerado com sucesso!")
                st.code(st.session_state.ultimo_recibo, language="markdown")
                st.caption("👆 Clique no botão de cópia no canto superior direito da caixa preta para copiar o texto.")
            else:
                st.info("O recibo aparecerá aqui após a confirmação do pagamento.")

    st.divider()
    
    with st.expander("📋 Histórico Completo de Entradas", expanded=False):
        st.dataframe(st.session_state.fin_df, use_container_width=True, hide_index=True)
