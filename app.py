import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="Judô Pro - Assoc. Roberdrayner", page_icon="🥋", layout="wide")

SENHA_MESTRE = "judo123"

# --- CSS REFINADO ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 10px; font-weight: 600; height: 3em; transition: 0.3s; }
    .stButton>button:hover { background-color: #E63946; color: white; transform: translateY(-2px); }
    [data-testid="stMetric"] { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .status-ativo { color: green; font-weight: bold; }
    .status-inativo { color: red; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3043/3043831.png", width=80)
        st.title("🥋 Judô Pro")
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar"):
            if senha == SENHA_MESTRE:
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# --- 2. BANCO DE DADOS (COLUNAS EXPANDIDAS) ---
DB_ATLETAS = "atleta_v20.csv"
DB_FINANCEIRO = "fin_v20.csv"

# Adicionados: Data_Nascimento, Responsavel, Obs_Medicas, Genero
COLS_A = [
    "ID", "Nome", "Data_Nascimento", "Genero", "CPF", "RG", "Peso", "Faixa", 
    "Responsavel", "Telefone", "Email", "Endereco", "Status", 
    "Mensalidade", "Dia_Vencimento", "Obs_Medicas", "Data_Filiacao"
]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo", "Observacao"]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    # Garantir que todas as colunas novas existam no arquivo antigo
    for col in COLS_A:
        if col not in df_a.columns: df_a[col] = ""
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. MENU LATERAL ---
with st.sidebar:
    st.title("🥋 Judô Pro")
    st.divider()
    aba = st.radio("Menu", ["🏠 Dashboard", "👥 Alunos", "💰 Financeiro"])
    st.divider()
    if st.button("🚪 Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- 4. DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("📊 Resumo Geral")
    df_a = st.session_state.atletas_df
    df_f = st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']) if not df_a.empty else 0)
    receita = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    c2.metric("Caixa Total", f"R$ {receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Data", datetime.now().strftime("%d/%m/%Y"))

# --- 5. ALUNOS (CADASTRO E EDIÇÃO COMPLETA) ---
elif aba == "👥 Alunos":
    st.title("👥 Gestão de Alunos")
    tab_cad, tab_edit = st.tabs(["📝 Novo Cadastro", "🔍 Consultar e Editar"])

    with tab_cad:
        with st.form("form_novo", clear_on_submit=True):
            st.subheader("Informações Básicas")
            c1, c2, c3 = st.columns([2, 1, 1])
            n_nome = c1.text_input("Nome Completo*")
            n_nasc = c2.date_input("Data de Nascimento", min_value=datetime(1940,1,1))
            n_gen = c3.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
            
            st.subheader("Documentação e Contato")
            c4, c5, c6 = st.columns(3)
            n_cpf = c4.text_input("CPF")
            n_resp = c5.text_input("Nome do Responsável (se menor)")
            n_tel = c6.text_input("Telefone/WhatsApp*")
            
            st.subheader("Dados do Dojo")
            c7, c8, c9, c10 = st.columns(4)
            n_faixa = c7.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            n_peso = c8.number_input("Peso (kg)", 0.0)
            n_mensal = c9.number_input("Mensalidade (R$)", 150.0)
            n_venc = c10.selectbox("Dia Vencimento", list(range(1, 31)), index=4)
            
            n_obs = st.text_area("Observações Médicas ou Gerais")
            
            if st.form_submit_button("Realizar Matrícula"):
                if n_nome and n_tel:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{
                        "ID": new_id, "Nome": n_nome, "Data_Nascimento": n_nasc.strftime("%d/%m/%Y"),
                        "Genero": n_gen, "CPF": n_cpf, "Peso": n_peso, "Faixa": n_faixa, "Responsavel": n_resp,
                        "Telefone": n_tel, "Status": "Ativo", "Mensalidade": n_mensal, "Dia_Vencimento": n_venc,
                        "Obs_Medicas": n_obs, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")
                    }])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Aluno matriculado com sucesso!")
                    time.sleep(1); st.rerun()
                else: st.error("Nome e Telefone são obrigatórios.")

    with tab_edit:
        busca = st.text_input("🔍 Buscar aluno pelo nome...")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
        
        if not df_res.empty:
            sel_aluno = st.selectbox("Selecione o aluno para ver detalhes ou editar:", 
                                     [f"{r['Nome']} (ID: {r['ID']})" for _, r in df_res.iterrows()])
            
            id_sel = int(sel_aluno.split("(ID: ")[1].replace(")", ""))
            idx = st.session_state.atletas_df[st.session_state.atletas_df['ID'] == id_sel].index[0]
            atleta = st.session_state.atletas_df.loc[idx]

            st.divider()
            with st.form("form_edicao"):
                st.subheader(f"Editando Perfil: {atleta['Nome']}")
                col1, col2, col3 = st.columns([2, 1, 1])
                e_nome = col1.text_input("Nome", value=str(atleta['Nome']))
                e_status = col2.selectbox("Status", ["Ativo", "Inativo"], index=0 if atleta['Status'] == "Ativo" else 1)
                e_faixa = col3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"], index=["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"].index(atleta['Faixa']))
                
                col4, col5, col6 = st.columns(3)
                e_tel = col4.text_input("Telefone", value=str(atleta['Telefone']))
                e_mensal = col5.number_input("Mensalidade (R$)", value=float(atleta['Mensalidade']))
                e_venc = col6.selectbox("Dia Vencimento", list(range(1, 31)), index=int(atleta['Dia_Vencimento'])-1)
                
                e_resp = st.text_input("Responsável", value=str(atleta['Responsavel']))
                e_obs = st.text_area("Observações Médicas", value=str(atleta['Obs_Medicas']))
                
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                    st.session_state.atletas_df.loc[idx, ["Nome", "Status", "Faixa", "Telefone", "Mensalidade", "Dia_Vencimento", "Responsavel", "Obs_Medicas"]] = [
                        e_nome, e_status, e_faixa, e_tel, e_mensal, e_venc, e_resp, e_obs
                    ]
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success("Dados atualizados!")
                    time.sleep(1); st.rerun()
                
                if c_btn2.form_submit_button("🗑️ Excluir Aluno", use_container_width=True):
                    st.session_state.atletas_df = st.session_state.atletas_df.drop(idx)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.warning("Aluno removido.")
                    time.sleep(1); st.rerun()
        else:
            st.info("Nenhum aluno encontrado.")

# --- 6. FINANCEIRO (MANTIDO) ---
elif aba == "💰 Financeiro":
    st.title("💰 Controle Financeiro")
    c_f, c_r = st.columns([1.2, 0.8])
    with c_f:
        with st.form("pag_form"):
            aluno_f = st.selectbox("Aluno", st.session_state.atletas_df[st.session_state.atletas_df['Status'] == 'Ativo']['Nome'].tolist())
            metodo = st.selectbox("Forma", ["PIX", "Dinheiro", "Misto (Pix + Dinheiro)"])
            valor_base = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_f]['Mensalidade'].values[0])
            total = st.number_input("Total R$", value=valor_base)
            
            v_p, v_d = 0.0, 0.0
            if "Misto" in metodo:
                cm1, cm2 = st.columns(2)
                v_p = cm1.number_input("Valor Pix", 0.0, total)
                v_d = cm2.number_input("Valor Dinheiro", 0.0, total)
            
            if st.form_submit_button("Confirmar Pagamento"):
                if "Misto" in metodo and (round(v_p + v_d, 2) != round(total, 2)):
                    st.error("A soma não bate!")
                else:
                    id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno_f]['ID'].values[0]
                    novo_p = pd.DataFrame([{"ID_Atleta": id_a, "Nome_Atleta": aluno_f, "Mes_Ref": datetime.now().strftime("%m/%Y"), "Valor_Total": total, "Valor_Pix": v_p if "Misto" in metodo else (total if "PIX" in metodo else 0), "Valor_Dinheiro": v_d if "Misto" in metodo else (total if "Dinheiro" in metodo else 0), "Data_Pagamento": datetime.now().strftime("%d/%m/%Y"), "Metodo": metodo}])
                    st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_p], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.session_state.recibo = f"*RECIBO JUDÔ* 🥋\n*Aluno:* {aluno_f}\n*Valor:* R${total:.2f}\n*Data:* {datetime.now().strftime('%d/%m/%Y')}"
                    st.rerun()
    with c_r:
        if 'recibo' in st.session_state:
            st.code(st.session_state.recibo)
            st.info("Recibo pronto para copiar.")
