import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro - Estável", page_icon="🥋", layout="wide")

DB_ATLETAS = "atletas_v15.csv"
DB_FINANCEIRO = "financeiro_v15.csv"

COLS_A = ["ID", "Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Data_Filiacao"]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Observacao"]

def load_data():
    # Carregar arquivos ou criar novos
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    
    # BLINDAGEM 1: Criar colunas faltantes (compatibilidade com CSV antigo)
    for col in COLS_A:
        if col not in df_a.columns:
            df_a[col] = 0.0 if col in ['Peso', 'Mensalidade'] else ""
            
    for col in COLS_F:
        if col not in df_f.columns:
            df_f[col] = ""
            
    # BLINDAGEM 2: Garantir tipos de dados corretos
    if not df_a.empty: 
        df_a['ID'] = df_a['ID'].astype(int)
        df_a['Peso'] = pd.to_numeric(df_a['Peso'], errors='coerce').fillna(0.0)
        df_a['Mensalidade'] = pd.to_numeric(df_a['Mensalidade'], errors='coerce').fillna(150.0)
        # Limpar NaNs de texto
        df_a.fillna("", inplace=True)
        
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

# Inicializar cache
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 2. MENU ---
with st.sidebar:
    st.title("🥋 Menu")
    aba = st.radio("Ir para:", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro"])
    st.divider()
    st.caption("Sistema v15.0 - Sem Erros")

# --- 3. DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("📊 Painel Geral")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    c1, c2 = st.columns(2)
    c1.metric("Total Alunos", len(df_a))
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    c2.metric("Receita Total", f"R$ {receita:,.2f}")
    
    if not df_a.empty:
        st.plotly_chart(px.pie(df_a, names='Faixa', title="Distribuição por Faixa"), use_container_width=True)

# --- 4. ATLETAS ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Alunos")
    
    # 4.1 CADASTRO
    with st.expander("➕ Nova Matrícula", expanded=False):
        with st.form("form_novo"):
            nome = st.text_input("Nome Completo*")
            c1, c2, c3 = st.columns(3)
            cpf = c1.text_input("CPF")
            rg = c2.text_input("RG")
            peso = c3.number_input("Peso (kg)", min_value=0.0, step=0.5)
            
            c4, c5 = st.columns(2)
            tel = c4.text_input("Telefone")
            email = c5.text_input("Email")
            
            end = st.text_input("Endereço Completo")
            
            c6, c7 = st.columns(2)
            faixa = c6.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            val = c7.number_input("Mensalidade Padrão (R$)", value=150.0)
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo_reg = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "CPF": cpf, "RG": rg, "Peso": peso,
                        "Faixa": faixa, "Endereco": end, "Telefone": tel, "Email": email,
                        "Status": "Ativo", "Mensalidade": val, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")
                    }])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_reg], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Aluno cadastrado com sucesso!")
                    time.sleep(1)
                    st.rerun()

    # 4.2 EDIÇÃO
    with st.expander("🔍 Pesquisar e Editar", expanded=True):
        if not st.session_state.atletas_df.empty:
            busca = st.text_input("Filtrar por nome")
            df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
            st.dataframe(df_res[["ID", "Nome", "Faixa", "Telefone", "Status"]], use_container_width=True, hide_index=True)
            
            if not df_res.empty:
                st.divider()
                sel = st.selectbox("Escolha um aluno para editar", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
                id_sel = int(sel.split("(ID: ")[1].replace(")", ""))
                
                # Resgatar dados do aluno exato
                idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
                atleta = st.session_state.atletas_df.loc[idx]

                with st.form("form_edit"):
                    st.subheader(f"Editando: {atleta['Nome']}")
                    
                    e_nome = st.text_input("Nome", value=str(atleta['Nome']))
                    
                    c1, c2, c3 = st.columns(3)
                    e_cpf = c1.text_input("CPF", value=str(atleta['CPF']))
                    e_rg = c2.text_input("RG", value=str(atleta['RG']))
                    # Proteção extra para o peso
                    e_peso = c3.number_input("Peso", value=float(atleta['Peso']) if pd.notna(atleta['Peso']) else 0.0)
                    
                    c4, c5 = st.columns(2)
                    e_tel = c4.text_input("Telefone", value=str(atleta['Telefone']))
                    e_email = c5.text_input("Email", value=str(atleta['Email']))
                    
                    e_end = st.text_input("Endereço", value=str(atleta['Endereco']))
                    
                    # BLINDAGEM: Garantir que a faixa atual seja preservada no SelectBox
                    lista_faixas = ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"]
                    idx_faixa = lista_faixas.index(atleta['Faixa']) if atleta['Faixa'] in lista_faixas else 0
                    
                    c6, c7, c8 = st.columns(3)
                    e_faixa = c6.selectbox("Faixa", lista_faixas, index=idx_faixa)
                    e_val = c7.number_input("Mensalidade", value=float(atleta['Mensalidade']) if pd.notna(atleta['Mensalidade']) else 150.0)
                    e_status = c8.selectbox("Status", ["Ativo", "Inativo"], index=0 if atleta['Status'] == "Ativo" else 1)

                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Salvar Alterações"):
                        st.session_state.atletas_df.loc[idx, ["Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade"]] = [
                            e_nome, e_cpf, e_rg, e_peso, e_faixa, e_end, e_tel, e_email, e_status, e_val
                        ]
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.success("Dados salvos com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    
                    if b2.form_submit_button("🗑️ Excluir Atleta"):
                        st.session_state.atletas_df = st.session_state.atletas_df.drop(idx).reset_index(drop=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.rerun()

# --- 5. FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💸 Controle de Caixa")
    
    with st.expander("💳 Registrar Recebimento", expanded=True):
        if not st.session_state.atletas_df.empty:
            aluno = st.selectbox("Selecionar Aluno", st.session_state.atletas_df['Nome'].tolist())
            data_pg = st.date_input("Data", datetime.now())
            metodo = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão", "Misto"])
            obs = st.text_input("Observação (Ex: Mensalidade de Março)")
            
            # Buscar valor da mensalidade e proteger contra erros
            val_bd = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0]
            val_sugerido = float(val_bd) if pd.notna(val_bd) else 150.0
            
            valor = st.number_input("Confirmar Valor Recebido (R$)", value=val_sugerido)
            
            if st.button("🚀 Confirmar e Gerar Recibo"):
                id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                dt_format = data_pg.strftime("%d/%m/%Y")
                
                novo_pg = pd.DataFrame([{
                    "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": datetime.now().strftime("%B"),
                    "Valor_Total": valor, "Data_Pagamento": dt_format, "Metodo": metodo, "Observacao": obs
                }])
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pg], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                
                st.success("Pagamento Registrado!")
                
                texto_recibo = f"""
                *RECIBO DE JUDÔ* 🥋
                -------------------------
                *Aluno:* {aluno}
                *Data:* {dt_format}
                *Valor:* R$ {valor:.2f}
                *Pagamento:* {metodo}
                *Obs:* {obs if obs else 'Mensalidade'}
                -------------------------
                _Assoc. Roberdrayner Martins_
                """
                st.code(texto_recibo, language="markdown")
                st.info("Copie o texto para enviar via WhatsApp.")
        else:
            st.warning("Cadastre alunos primeiro para registrar pagamentos.")

    with st.expander("📋 Histórico Financeiro", expanded=False):
        st.dataframe(st.session_state.fin_df, use_container_width=True, hide_index=True)
