import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Judô Pro - Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- 2. BANCO DE DADOS (CSV) ---
DB_ATLETAS = "atletas_v10.csv"
DB_FINANCEIRO = "financeiro_v10.csv"

def load_data():
    cols_atleta = [
        "ID", "Nome", "CPF", "RG", "Peso", "Faixa", 
        "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Data_Filiacao"
    ]
    cols_fin = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Data_Pagamento", "Metodo", "Detalhe_Misto"]
    
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=cols_atleta)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=cols_fin)
    
    # Sincronizar colunas
    for col in cols_atleta:
        if col not in df_a.columns: df_a[col] = "-"
        
    if not df_a.empty:
        df_a['ID'] = df_a['ID'].astype(int)
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. MENU LATERAL ---
with st.sidebar:
    st.markdown("## 🏯 Roberdrayner Martins")
    aba = st.radio("Navegação Principal", ["🏠 Dashboard", "🥋 Atletas", "💰 Financeiro", "⚙️ Sistema"], key="nav_v10")
    st.divider()
    st.info("Formato de Data: DIA/MÊS/ANO")

# --- 4. DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("📊 Painel de Controle")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    # Métricas rápidas
    m1, m2, m3 = st.columns(3)
    m1.metric("Alunos Cadastrados", len(df_a))
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
    m2.metric("Faturamento Total", f"R$ {receita:,.2f}")
    m3.metric("Status Ativo", len(df_a[df_a['Status'] == 'Ativo']))

    # Gráficos recolhíveis
    with st.expander("📈 Visualizar Gráficos de Desempenho", expanded=True):
        col1, col2 = st.columns(2)
        if not df_a.empty:
            with col1:
                st.plotly_chart(px.pie(df_a, names='Faixa', title="Distribuição por Faixa", hole=0.3), use_container_width=True)
            with col2:
                if not df_f.empty:
                    st.plotly_chart(px.bar(df_f, x='Mes_Ref', y='Valor_Total', color='Metodo', title="Entradas Mensais"), use_container_width=True)
        else:
            st.warning("Sem dados para gerar gráficos.")

# --- 5. GESTÃO DE ATLETAS (COM ABAS RECOLHÍVEIS) ---
elif aba == "🥋 Atletas":
    st.title("👥 Gestão de Integrantes")
    
    # Seção de Cadastro Recolhível
    with st.expander("➕ Nova Matrícula (Clique para expandir)", expanded=False):
        with st.form("form_cadastro_v10", clear_on_submit=True):
            st.markdown("### 📝 Ficha de Cadastro")
            nome = st.text_input("Nome Completo*")
            
            c1, c2, c3 = st.columns(3)
            cpf = c1.text_input("CPF")
            rg = c2.text_input("RG")
            peso = c3.number_input("Peso (kg)", min_value=0.0, step=0.1)
            
            c4, c5 = st.columns(2)
            tel = c4.text_input("WhatsApp")
            email = c5.text_input("Email")
            endereco = st.text_input("Endereço Residencial")
            
            c6, c7 = st.columns(2)
            faixa = c6.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            valor = c7.number_input("Valor da Mensalidade (R$)", value=150.0)
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome:
                    data_br = datetime.now().strftime("%d/%m/%Y")
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "CPF": cpf, "RG": rg, "Peso": peso,
                        "Faixa": faixa, "Endereco": endereco, "Telefone": tel, "Email": email,
                        "Status": "Ativo", "Mensalidade": valor, "Data_Filiacao": data_br
                    }])
                    
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"Oss! {nome} cadastrado!")
                    st.rerun()
                else:
                    st.error("O nome é obrigatório.")

    # Seção de Lista e Edição Recolhível
    with st.expander("🔍 Pesquisar e Gerenciar Alunos", expanded=True):
        busca = st.text_input("🔍 Buscar por nome...")
        df_filtrado = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False)]
        st.dataframe(df_filtrado[["ID", "Nome", "Faixa", "Telefone", "Status"]], use_container_width=True, hide_index=True)
        
        if not df_filtrado.empty:
            st.divider()
            escolha = st.selectbox("Selecione o atleta para exclusão:", 
                                 [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_filtrado.iterrows()])
            id_del = int(escolha.split("(ID: ")[1].replace(")", ""))
            
            if st.button("🗑️ Remover Atleta Selecionado", type="secondary"):
                st.session_state.atletas_df = st.session_state.atletas_df[st.session_state.atletas_df['ID'] != id_del]
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.warning("Atleta excluído.")
                st.rerun()

# --- 6. FINANCEIRO (COM ABAS RECOLHÍVEIS) ---
elif aba == "💰 Financeiro":
    st.title("💸 Gestão de Pagamentos")
    
    with st.expander("💳 Registrar Novo Recebimento", expanded=True):
        if not st.session_state.atletas_df.empty:
            f1, f2 = st.columns(2)
            aluno = f1.selectbox("Selecione o Judoca", st.session_state.atletas_df['Nome'].tolist())
            data_cal = f2.date_input("Data do Pagamento", datetime.now())
            
            f3, f4 = st.columns(2)
            mes = f3.selectbox("Mês de Referência", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            forma = f4.selectbox("Método", ["PIX", "Dinheiro", "Cartão", "Misto"])
            
            v_base = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
            
            if forma == "Misto":
                m1, m2 = st.columns(2)
                vp = m1.number_input("Parte PIX", value=v_base/2)
                vd = m2.number_input("Parte Dinheiro", value=v_base/2)
                v_final = vp + vd
                detalhe = f"PIX: R${vp:.2f} | Din: R${vd:.2f}"
            else:
                v_final = st.number_input("Valor Confirmado", value=v_base)
                detalhe = ""
                
            if st.button("🚀 Confirmar Recebimento"):
                id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                data_br = data_cal.strftime("%d/%m/%Y")
                
                novo_pg = pd.DataFrame([{
                    "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": mes,
                    "Valor_Total": v_final, "Data_Pagamento": data_br,
                    "Metodo": forma, "Detalhe_Misto": detalhe
                }])
                
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pg], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.success(f"Pago em {data_br}!")
                st.rerun()
        else:
            st.warning("Cadastre alunos antes de registrar pagamentos.")

    with st.expander("📊 Histórico Completo de Mensalidades", expanded=False):
        st.dataframe(st.session_state.fin_df, use_container_width=True, hide_index=True)

# --- 7. SISTEMA ---
elif aba == "⚙️ Sistema":
    st.title("⚙️ Administração de Dados")
    
    with st.expander("📥 Exportação e Backup", expanded=True):
        st.write("Clique nos botões abaixo para baixar as planilhas atualizadas.")
        c_b1, c_b2 = st.columns(2)
        c_b1.download_button("Planilha de Atletas", data=st.session_state.atletas_df.to_csv(index=False).encode('utf-8'), 
                           file_name=f"atletas_{datetime.now().strftime('%d_%m_%Y')}.csv")
        c_b2.download_button("Relatório Financeiro", data=st.session_state.fin_df.to_csv(index=False).encode('utf-8'), 
                           file_name=f"financeiro_{datetime.now().strftime('%d_%m_%Y')}.csv")
