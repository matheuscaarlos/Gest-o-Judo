import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import locale

# Tenta configurar o locale para Português Brasil (ajuste conforme o SO)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass # Mantém padrão se o servidor não suportar

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="Judô Pro - Assoc. Roberdrayner", page_icon="🥋", layout="wide")

SENHA_MESTRE = "judo123"

# --- CSS PROFISSIONAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #f4f7f9; }
    
    /* Login Container */
    .st-emotion-cache-1r6slb0 { border-radius: 20px; border: 1px solid #e0e0e0; padding: 40px; background: white; }
    
    /* Botões */
    .stButton>button {
        border-radius: 12px; background: #1D3557; color: white; border: none;
        padding: 10px 24px; transition: all 0.3s ease; width: 100%;
    }
    .stButton>button:hover { background: #E63946; transform: scale(1.02); }
    
    /* Cards do Dashboard */
    [data-testid="stMetric"] {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 5px solid #1D3557;
    }
    
    /* Customização do Recibo */
    code { color: #155724 !important; background: #d4edda !important; font-size: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container():
            st.image("https://cdn-icons-png.flaticon.com/512/3043/3043831.png", width=80)
            st.title("🥋 Judô Pro")
            st.subheader("Assoc. Roberdrayner Martins")
            senha = st.text_input("Senha de Acesso", type="password")
            if st.button("Acessar Painel"):
                if senha == SENHA_MESTRE:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Senha inválida.")
    st.stop()

# --- 2. BANCO DE DADOS ---
DB_ATLETAS = "atleta_v19.csv"
DB_FINANCEIRO = "fin_v19.csv"

COLS_A = ["ID", "Nome", "CPF", "RG", "Peso", "Faixa", "Endereco", "Telefone", "Email", "Status", "Mensalidade", "Dia_Vencimento", "Data_Filiacao"]
COLS_F = ["ID_Atleta", "Nome_Atleta", "Mes_Ref", "Valor_Total", "Valor_Pix", "Valor_Dinheiro", "Data_Pagamento", "Metodo", "Observacao"]

def load_data():
    df_a = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=COLS_A)
    df_f = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=COLS_F)
    return df_a, df_f

def save_data(df_a, df_f):
    df_a.to_csv(DB_ATLETAS, index=False)
    df_f.to_csv(DB_FINANCEIRO, index=False)

if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- 3. MENU LATERAL ---
with st.sidebar:
    st.title("🥋 Judô Pro")
    st.markdown(f"🗓️ **{datetime.now().strftime('%d de %B de %Y')}**")
    st.divider()
    aba = st.radio("Navegação", ["🏠 Início", "👥 Alunos", "💰 Caixa"], label_visibility="collapsed")
    st.divider()
    if st.button("🚪 Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- 4. DASHBOARD ---
if aba == "🏠 Início":
    st.title("📊 Painel de Controle")
    df_a, df_f = st.session_state.atletas_df, st.session_state.fin_df
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Alunos Ativos", len(df_a[df_a['Status'] == 'Ativo']))
    
    total_recebido = pd.to_numeric(df_f['Valor_Total'], errors='coerce').sum()
    c2.metric("Total em Caixa", f"R$ {total_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    faturamento_previsto = pd.to_numeric(df_a[df_a['Status'] == 'Ativo']['Mensalidade'], errors='coerce').sum()
    c3.metric("Faturamento Mensal Previsto", f"R$ {faturamento_previsto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.divider()
    st.subheader("📌 Próximos Vencimentos")
    hoje = datetime.now().day
    proximos = df_a[(df_a['Status'] == 'Ativo') & (df_a['Dia_Vencimento'] >= hoje)].sort_values('Dia_Vencimento')
    st.table(proximos[['Nome', 'Dia_Vencimento', 'Mensalidade']].head(5))

# --- 5. ALUNOS ---
elif aba == "👥 Alunos":
    st.title("👥 Gestão de Alunos")
    tab1, tab2 = st.tabs(["📝 Novo Cadastro", "🔍 Consultar e Editar"])
    
    with tab1:
        with st.form("novo_aluno"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome Completo*")
            cpf = c2.text_input("CPF")
            
            c3, c4, c5 = st.columns(3)
            faixa = c3.selectbox("Faixa", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            mensalidade = c4.number_input("Mensalidade (R$)", value=150.00, step=10.0)
            vencimento = c5.selectbox("Dia de Vencimento", list(range(1, 31)), index=4)
            
            tel = st.text_input("Telefone (WhatsApp)")
            
            if st.form_submit_button("Finalizar Matrícula"):
                if nome:
                    new_id = int(st.session_state.atletas_df['ID'].max() + 1) if not st.session_state.atletas_df.empty else 1
                    novo = pd.DataFrame([{"ID": new_id, "Nome": nome, "CPF": cpf, "Faixa": faixa, "Telefone": tel, "Status": "Ativo", "Mensalidade": mensalidade, "Dia_Vencimento": vencimento, "Data_Filiacao": datetime.now().strftime("%d/%m/%Y")}])
                    st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    st.success(f"Matrícula de {nome} realizada!")
                    time.sleep(1); st.rerun()

    with tab2:
        busca = st.text_input("Buscar por nome...")
        df_res = st.session_state.atletas_df[st.session_state.atletas_df['Nome'].str.contains(busca, case=False, na=False)]
        st.dataframe(df_res[["ID", "Nome", "Faixa", "Status", "Dia_Vencimento", "Mensalidade"]], use_container_width=True, hide_index=True)

# --- 6. FINANCEIRO ---
elif aba == "💰 Caixa":
    st.title("💰 Gestão Financeira")
    
    c_form, c_recibo = st.columns([1.2, 0.8])
    
    with c_form:
        st.subheader("Registrar Pagamento")
        with st.form("pagamento_form"):
            aluno = st.selectbox("Selecione o Aluno", st.session_state.atletas_df[st.session_state.atletas_df['Status'] == 'Ativo']['Nome'].tolist())
            metodo = st.selectbox("Meio de Pagamento", ["PIX", "Dinheiro", "Cartão", "Misto (Pix + Dinheiro)"])
            
            val_padrao = float(st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['Mensalidade'].values[0])
            total = st.number_input("Valor Total (R$)", value=val_padrao)
            
            v_pix, v_din = 0.0, 0.0
            if "Misto" in metodo:
                cc1, cc2 = st.columns(2)
                v_pix = cc1.number_input("Valor no Pix", 0.0, total)
                v_din = cc2.number_input("Valor no Dinheiro", 0.0, total)
            
            if st.form_submit_button("Confirmar e Gerar Recibo"):
                if "Misto" in metodo and (round(v_pix + v_din, 2) != round(total, 2)):
                    st.error("A soma não confere com o total!")
                else:
                    data_hj = datetime.now().strftime("%d/%m/%Y")
                    id_a = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == aluno]['ID'].values[0]
                    
                    novo_pg = pd.DataFrame([{
                        "ID_Atleta": id_a, "Nome_Atleta": aluno, "Mes_Ref": datetime.now().strftime("%B/%Y"),
                        "Valor_Total": total, "Valor_Pix": v_pix if "Misto" in metodo else (total if "PIX" in metodo else 0),
                        "Valor_Dinheiro": v_din if "Misto" in metodo else (total if "Dinheiro" in metodo else 0),
                        "Data_Pagamento": data_hj, "Metodo": metodo
                    }])
                    st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pg], ignore_index=True)
                    save_data(st.session_state.atletas_df, st.session_state.fin_df)
                    
                    detalhe = f"\n*Divisão:* Pix: R${v_pix:.2f} | Din: R${v_din:.2f}" if "Misto" in metodo else ""
                    st.session_state.ultimo_recibo = f"""*RECIBO DE JUDÔ* 🥋\n--------------------------\n*Aluno:* {aluno}\n*Data:* {data_hj}\n*Valor:* R$ {total:.2f}\n*Forma:* {metodo}{detalhe}\n--------------------------\n_Assoc. Roberdrayner Martins_"""
                    st.rerun()

    with c_recibo:
        st.subheader("📱 Recibo WhatsApp")
        if "ultimo_recibo" in st.session_state:
            st.code(st.session_state.ultimo_recibo, language="markdown")
            st.info("Copie e cole na conversa do aluno.")
        else:
            st.write("Aguardando registro...")

    st.divider()
    st.subheader("📋 Histórico Recente")
    st.dataframe(st.session_state.fin_df.tail(10), use_container_width=True)
