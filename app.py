import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Judô Pro - Administrativo", page_icon="🥋", layout="wide")

SENHA_MESTRE = "judo123"

# --- 2. BANCO DE DADOS (LÓGICA DE REPARAÇÃO) ---
DB_ATLETAS = "atleta_v21.csv"
DB_FINANCEIRO = "fin_v21.csv"

# Todas as colunas que o sistema PRECISA ter
COLS_A = [
    "ID", "Nome", "Data_Nascimento", "Genero", "CPF", "RG", "Peso", "Faixa", 
    "Responsavel", "Telefone", "Email", "Endereco", "Status", 
    "Mensalidade", "Dia_Vencimento", "Obs_Medicas", "Data_Filiacao"
]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo", "Observacao"]

def load_data():
    # Carrega ou cria Atletas
    if os.path.exists(DB_ATLETAS):
        df_a = pd.read_csv(DB_ATLETAS)
        # REPARAÇÃO: Se faltar alguma coluna nova no CSV antigo, ele cria agora
        for col in COLS_A:
            if col not in df_a.columns:
                df_a[col] = "" if col != "Dia_Vencimento" else 5
    else:
        df_a = pd.DataFrame(columns=COLS_A)
    
    # Carrega ou cria Financeiro
    if os.path.exists(DB_FINANCEIRO):
        df_f = pd.read_csv(DB_FINANCEIRO)
        for col in COLS_F:
            if col not in df_f.columns:
                df_f[col] = 0.0 if "Valor_" in col else ""
    else:
        df_f = pd.DataFrame(columns=COLS_F)
        
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

# Inicialização
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🥋 Judô Pro Login")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha == SENHA_MESTRE:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("Assoc. Roberdrayner")
    aba = st.radio("Menu", ["📊 Dashboard", "👥 Alunos", "💰 Financeiro"])
    st.divider()
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- 5. DASHBOARD ---
if aba == "📊 Dashboard":
    st.title("📊 Dashboard")
    df_a = st.session_state.atletas_df
    df_f = st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0)
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    c2.metric("Receita Total", f"R$ {receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Data", datetime.now().strftime("%d/%m/%Y"))

# --- 6. ALUNOS ---
elif aba == "👥 Alunos":
    st.title("👥 Gestão de Alunos")
    tab1, tab2 = st.tabs(["📝 Cadastrar", "🔍 Consultar/Editar"])

    with tab1:
        with st.form("form_novo_atleta"):
            st.subheader("Dados Pessoais")
            nome = st.text_input("Nome Completo*")
            c1, c2, c3 = st.columns([2, 1, 1])
            nasc = c1.date_input("Nascimento", min_value=datetime(1940,1,1), format="DD/MM/YYYY")
            gen = c2.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
            cpf = c3.text_input("CPF")
            
            st.subheader("Responsável e Contato")
            resp = st.text_input("Nome do Responsável (se menor)")
            tel = st.text_input("Telefone/WhatsApp*")
            
            st.subheader("Dojo")
            c4, c5, c6 = st.columns(3)
            faixa = c4.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            mensal = c5.number_input("Mensalidade (R$)", 150.0)
            venc = c6.selectbox("Vencimento (Dia)", list(range(1, 31)), index=4)
            
            obs = st.text_area("Observações/Saúde")
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome and tel:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": nome, "Data_Nascimento": nasc.strftime("%d/%m/%Y"),
                        "Genero": gen, "CPF": cpf, "Faixa": faixa, "Responsavel": resp,
                        "Telefone": tel, "Status": "Ativo", "Mensalidade": mensal, "Dia_Vencimento": venc,
                        "Obs_Medicas": obs, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")
                    }])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Aluno matriculado!")
                    time.sleep(1); st.rerun()
                else: st.warning("Preencha Nome e Telefone!")

    with tab2:
        busca = st.text_input("🔍 Buscar aluno...")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
        
        if not df_res.empty:
            sel = st.selectbox("Selecione para editar:", [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
            id_sel = int(sel.split("(ID: ")[1].replace(")", ""))
            idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
            atleta = st.session_state.atletas_df.loc[idx]

            with st.form("form_edicao"):
                st.markdown(f"### Editando: {atleta['Nome']}")
                c1, c2 = st.columns(2)
                e_nome = c1.text_input("Nome", value=str(atleta['Nome']))
                e_status = c2.selectbox("Status", ["Ativo", "Inativo"], index=0 if atleta['Status'] == "Ativo" else 1)
                
                c3, c4, c5 = st.columns(3)
                e_faixa = c3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(atleta['Faixa']))
                e_mensal = c4.number_input("Mensalidade", value=float(atleta['Mensalidade']))
                e_venc = c5.selectbox("Dia Vencimento", list(range(1, 31)), index=int(atleta['Dia_Vencimento'])-1 if atleta['Dia_Vencimento'] else 4)
                
                e_resp = st.text_input("Responsável", value=str(atleta['Responsavel']))
                e_obs = st.text_area("Obs. Médicas", value=str(atleta['Obs_Medicas']))
                
                if st.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.atletas_df.loc[idx, ["Nome", "Status", "Faixa", "Mensalidade", "Dia_Vencimento", "Responsavel", "Obs_Medicas"]] = [
                        e_nome, e_status, e_faixa, e_mensal, e_venc, e_resp, e_obs
                    ]
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Dados atualizados!")
                    time.sleep(1); st.rerun()
        else: st.info("Nenhum aluno encontrado.")

# --- 7. FINANCEIRO ---
elif aba == "💰 Financeiro":
    st.title("💰 Financeiro")
    col_f, col_r = st.columns([1.2, 0.8])
    
    with col_f:
        if not st.session_state.atletas_df.empty:
            with st.form("form_pag"):
                aluno_f = st.selectbox("Aluno", st.session_state.atletas_df[st.session_state.atletas_df['Status'] == 'Ativo']['Nome'].tolist())
                metodo = st.selectbox("Meio", ["PIX", "Dinheiro", "Misto (Pix + Dinheiro)"])
                
                valor_base = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_f]['Mensalidade'].values[0])
                total = st.number_input("Valor Total (R$)", value=valor_base)
                
                v_p, v_d = 0.0, 0.0
                if "Misto" in metodo:
                    cm1, cm2 = st.columns(2)
                    v_p = cm1.number_input("Pix (R$)", 0.0, total)
                    v_d = cm2.number_input("Dinheiro (R$)", 0.0, total)
                
                if st.form_submit_button("✅ Confirmar Pagamento"):
                    if "Misto" in metodo and (round(v_p + v_d, 2) != round(total, 2)):
                        st.error("A soma do Pix + Dinheiro não fecha com o total!")
                    else:
                        id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_f]['ID'].values[0]
                        novo_p = pd.DataFrame([{"ID_Atleta": id_a, "Nome_Atleta": aluno_f, "Mes_Ref": datetime.now().strftime("%m/%Y"), "Valor_Total": total, "Valor_Pix": v_p if "Misto" in metodo else (total if "PIX" in metodo else 0), "Valor_Dinheiro": v_d if "Misto" in metodo else (total if "Dinheiro" in metodo else 0), "Data_Pagamento": datetime.now().strftime("%d/%m/%Y"), "Metodo": metodo}])
                        st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
                        save_data(st.session_state.atletas_df, st.session_state.fin_df)
                        st.session_state.recibo = f"*RECIBO JUDÔ* 🥋\n*Aluno:* {aluno_f}\n*Valor:* R${total:.2f}\n*Data:* {datetime.now().strftime('%d/%m/%Y')}\n*Metodo:* {metodo}"
                        st.rerun()
        else: st.warning("Cadastre alunos primeiro.")

    with col_r:
        if 'recibo' in st.session_state:
            st.subheader("📱 Recibo")
            st.code(st.session_state.recibo)
            st.info("Copie para o WhatsApp.")

    st.divider()
    st.subheader("Histórico")
    st.dataframe(st.session_state.fin_df.tail(10), use_container_width=True)
