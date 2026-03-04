import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="Judô Pro - Acesso Restrito", page_icon="🔐", layout="wide")

# Defina sua senha aqui
SENHA_MESTRE = "judo123" 

def verificar_login():
    """Gerencia a tela de login"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("""
            <style>
            .login-container {
                max-width: 400px;
                margin: 100px auto;
                padding: 30px;
                background-color: #f8f9fa;
                border-radius: 15px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.image("https://cdn-icons-png.flaticon.com/512/3043/3043831.png", width=100)
            st.title("Acesso Restrito")
            st.subheader("Assoc. Roberdrayner Martins")
            
            senha_input = st.text_input("Digite a Senha de Acesso", type="password")
            if st.button("Entrar no Sistema", use_container_width=True):
                if senha_input == SENHA_MESTRE:
                    st.session_state.autenticado = True
                    st.success("Acesso liberado!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Senha incorreta. Tente novamente.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- INÍCIO DO SISTEMA APÓS LOGIN ---
if verificar_login():
    
    # --- 2. ESTILOS CSS ---
    st.markdown("""
        <style>
        .stButton>button { border-radius: 8px; transition: all 0.3s ease; font-weight: 600; }
        div[data-testid="stMetricValue"] { color: #1D3557; font-weight: bold; }
        .sidebar-user { padding: 10px; background: #e9ecef; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    # --- 3. BANCO DE DADOS ---
    DB_ATLETAS = "atleta_v18.csv"
    DB_FINANCEIRO = "fin_v18.csv"

    COLS_A = ["ID", "Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Dia_Vencimento", "Data_Filiacao"]
    COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo", "Observacao"]

    def load_data():
        df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
        df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
        # Garantir colunas novas (Dia de Vencimento e Valores Mistos)
        for col in COLS_A:
            if col not in df_a.columns: df_a[col] = 5 if col == 'Dia_Vencimento' else ""
        for col in COLS_F:
            if col not in df_f.columns: df_f[col] = 0.0 if "Valor_" in col else ""
        return df_a, df_f

    def save_data(df_a, df_f):
        df_a.to_csv(DB_ATLETAS, index=False)
        df_f.to_csv(DB_FINANCEIRO, index=False)

    if 'atletas_df' not in st.session_state:
        st.session_state.atletas_df, st.session_state.fin_df = load_data()

    # --- 4. MENU LATERAL ---
    with st.sidebar:
        st.markdown('<div class="sidebar-user">👤 <b>Sensei Conectado</b></div>', unsafe_allow_html=True)
        aba = st.radio("Navegação Principal", ["🏠 Dashboard", "👥 Atletas", "💰 Financeiro"])
        st.divider()
        if st.button("🚪 Sair do Sistema"):
            st.session_state.autenticado = False
            st.rerun()

    # --- 5. DASHBOARD ---
    if aba == "🏠 Dashboard":
        st.title("📊 Painel Administrativo")
        df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
        c1, c2, c3 = st.columns(3)
        c1.metric("🥋 Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']))
        receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum() if not df_f.empty else 0
        c2.metric("💳 Faturamento Total", f"R$ {receita:,.2f}")
        c3.metric("📅 Mês Atual", datetime.now().strftime("%B"))

    # --- 6. ATLETAS (CADASTRO + DIA VENCIMENTO) ---
    elif aba == "👥 Atletas":
        st.title("👥 Gestão de Judocas")
        with st.expander("➕ Nova Matrícula"):
            with st.form("form_cadastro"):
                nome = st.text_input("Nome Completo*")
                c1, c2, c3 = st.columns(3)
                cpf, rg, peso = c1.text_input("CPF"), c2.text_input("RG"), c3.number_input("Peso (kg)", 0.0)
                c4, c5, c6 = st.columns(3)
                tel = c4.text_input("WhatsApp")
                val_mensal = c5.number_input("Valor Mensalidade (R$)", value=150.0)
                vencimento = c6.number_input("Melhor Dia de Vencimento", 1, 31, 5)
                faixa = st.selectbox("Faixa Atual", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
                if st.form_submit_button("Salvar Matrícula"):
                    if nome:
                        new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                        novo = pd.DataFrame([{"ID": new_id, "Nome": nome, "CPF": cpf, "RG": rg, "Peso": peso, "Faixa": faixa, "Telefone": tel, "Status": "Ativo", "Mensalidade": val_mensal, "Dia_Vencimento": vencimento, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")}])
                        st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.toast("Sucesso!"); time.sleep(0.5); st.rerun()

        # EDIÇÃO (MANTENDO FUNCIONALIDADES ANTERIORES)
        with st.expander("🔍 Editar Alunos", expanded=True):
            busca = st.text_input("Buscar por nome...")
            df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
            st.dataframe(df_res[["ID", "Nome", "Faixa", "Dia_Vencimento", "Status"]], use_container_width=True, hide_index=True)
            if not df_res.empty:
                sel = st.selectbox("Escolha um aluno:", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
                id_sel = int(sel.split("(ID: ")[1].replace(")", ""))
                idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
                with st.form("form_edit"):
                    atleta = st.session_state.atletas_df.loc[idx]
                    e_venc = st.number_input("Alterar Vencimento", value=int(atleta['Dia_Vencimento']))
                    e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if atleta['Status'] == "Ativo" else 1)
                    if st.form_submit_button("Salvar Alterações"):
                        st.session_state.atletas_df.at[idx, 'Dia_Vencimento'] = e_venc
                        st.session_state.atletas_df.at[idx, 'Status'] = e_status
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.toast("Atualizado!"); time.sleep(0.5); st.rerun()

    # --- 7. FINANCEIRO (PAGAMENTO MISTO DETALHADO) ---
    elif aba == "💰 Financeiro":
        st.title("💸 Controle de Caixa")
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            with st.form("form_pag"):
                aluno = st.selectbox("Selecionar Aluno", st.session_state.atletas_df['Nome'].tolist())
                c_d, c_m = st.columns(2)
                data_pg = c_d.date_input("Data", datetime.now())
                metodo = c_m.selectbox("Método", ["PIX", "Dinheiro", "Misto (Pix + Dinheiro)"])
                
                val_bd = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
                total = st.number_input("Valor Total (R$)", value=val_bd)
                
                v_pix, v_din = 0.0, 0.0
                if metodo == "Misto (Pix + Dinheiro)":
                    st.warning("Divida o valor abaixo:")
                    cm1, cm2 = st.columns(2)
                    v_pix = cm1.number_input("R$ em Pix", 0.0, total)
                    v_din = cm2.number_input("R$ em Dinheiro", 0.0, total)
                
                if st.form_submit_button("Confirmar Pagamento", use_container_width=True):
                    if metodo == "Misto (Pix + Dinheiro)" and (round(v_pix + v_din, 2) != round(total, 2)):
                        st.error("A soma do Pix e Dinheiro deve ser igual ao Valor Total!")
                    else:
                        id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                        novo_pg = pd.DataFrame([{
                            "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": data_pg.strftime("%m/%Y"),
                            "Valor_Total": total, "Valor_Pix": v_pix if "Misto" in metodo else (total if "PIX" in metodo else 0),
                            "Valor_Dinheiro": v_din if "Misto" in metodo else (total if "Dinheiro" in metodo else 0),
                            "Data_Pagamento": data_pg.strftime("%d/%m/%Y"), "Metodo": metodo, "Observacao": ""
                        }])
                        st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pg], ignore_index=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        
                        detalhe = f"\n*Divisão:* Pix: R${v_pix:.2f} | Din: R${v_din:.2f}" if "Misto" in metodo else ""
                        st.session_state.recibo = f"""*RECIBO JUDÔ* 🥋\n*Aluno:* {aluno}\n*Data:* {data_pg.strftime("%d/%m/%Y")}\n*Valor:* R$ {total:.2f}\n*Metodo:* {metodo}{detalhe}\n_Assoc. Roberdrayner Martins_"""
                        st.rerun()

        with col2:
            if 'recibo' in st.session_state:
                st.subheader("📱 Recibo Gerado")
                st.code(st.session_state.recibo, language="markdown")
