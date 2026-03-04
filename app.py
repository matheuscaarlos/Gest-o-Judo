import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from PIL import Image

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Assoc. Roberdrayner Martins", page_icon="🥋", layout="wide")

# --- DATABASE ENGINE ---
DB_ATLETAS = "atletas_v4.csv"
DB_FINANCEIRO = "financeiro_v4.csv"

def load_data():
    atleta_df = pd.read_csv(DB_ATLETAS) if os.path.exists(DB_ATLETAS) else pd.DataFrame(columns=["ID", "Nome", "Faixa", "Status", "Mensalidade", "Data_Filiacao"])
    fin_df = pd.read_csv(DB_FINANCEIRO) if os.path.exists(DB_FINANCEIRO) else pd.DataFrame(columns=["ID_Atleta", "Mes_Ref", "Ano_Ref", "Valor", "Data_Pgto", "Metodo"])
    return atleta_df, fin_df

def save_data(atleta_df, fin_df):
    atleta_df.to_csv(DB_ATLETAS, index=False)
    fin_df.to_csv(DB_FINANCEIRO, index=False)

# --- CSS CUSTOMIZADO (DESIGN SYSTEM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .main { background-color: #f0f2f6; }
    
    /* Card de Métricas Estilizado */
    .metric-box {
        background: linear-gradient(135deg, #1a237e 0%, #303f9f 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background: #d4af37;
        color: #1a237e;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background: #1a237e;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .sidebar-text { color: #1a237e !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
if 'atletas_df' not in st.session_state:
    st.session_state.atletas_df, st.session_state.fin_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #1a237e;'>Menu Gestão</h2>", unsafe_allow_html=True)
    aba = st.radio("", ["🏠 Dashboard", "🥋 Gestão de Alunos", "💰 Financeiro Pro", "⚙️ Sistema"])
    st.divider()
    st.info("Associação Roberdrayner Martins de Judô")

# --- 🏠 DASHBOARD ---
if aba == "🏠 Dashboard":
    st.title("🏯 Painel de Performance")
    df_a = st.session_state.atletas_df
    df_f = st.session_state.fin_df
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-box"><h4>Atletas</h4><h2>{len(df_a)}</h2></div>', unsafe_allow_html=True)
    with c2:
        receita_total = df_f['Valor'].sum() if not df_f.empty else 0
        st.markdown(f'<div class="metric-box"><h4>Caixa Total</h4><h2>R${receita_total:,.2f}</h2></div>', unsafe_allow_html=True)
    with c3:
        ativos = len(df_a[df_a['Status'] == 'Ativo'])
        st.markdown(f'<div class="metric-box"><h4>Ativos</h4><h2>{ativos}</h2></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-box"><h4>Graduados</h4><h2>{len(df_a[df_a["Faixa"] != "Branca"])}</h2></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Distribuição de Faixas")
        if not df_a.empty:
            fig_faixa = px.pie(df_a, names='Faixa', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_faixa, use_container_width=True)
            
    with col_right:
        st.subheader("📈 Arrecadação por Mês")
        if not df_f.empty:
            df_f['Data_Pgto'] = pd.to_datetime(df_f['Data_Pgto'], dayfirst=True)
            receita_mensal = df_f.groupby(df_f['Data_Pgto'].dt.strftime('%B'))['Valor'].sum()
            st.bar_chart(receita_mensal)

# --- 🥋 GESTÃO DE ALUNOS ---
elif aba == "🥋 Gestão de Alunos":
    st.title("👥 Cadastro e Matrícula")
    
    tab1, tab2 = st.tabs(["Novo Aluno", "Lista de Judocas"])
    
    with tab1:
        with st.form("cadastro"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome Completo")
            faixa = c2.selectbox("Faixa Atual", ["Branca", "Cinza", "Azul", "Amarela", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
            mensalidade = c1.number_input("Valor Mensalidade", value=150.0)
            status = c2.selectbox("Status Inicial", ["Ativo", "Inativo"])
            
            if st.form_submit_button("Matricular Atleta"):
                novo_id = len(st.session_state.atletas_df) + 1
                novo_atleta = pd.DataFrame([[novo_id, nome, faixa, status, mensalidade, datetime.now().strftime("%d/%m/%Y")]], 
                                           columns=st.session_state.atletas_df.columns)
                st.session_state.atletas_df = pd.concat([st.session_state.atletas_df, novo_atleta], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.success(f"Oss! {nome} agora faz parte da associação.")
                st.rerun()

    with tab2:
        st.dataframe(st.session_state.atletas_df, use_container_width=True, hide_index=True)

# --- 💰 FINANCEIRO PRO ---
elif aba == "💰 Financeiro Pro":
    st.title("💸 Gestão de Recebimentos")
    
    col_input, col_hist = st.columns([1, 2])
    
    with col_input:
        st.subheader("Registrar Pagamento")
        if not st.session_state.atletas_df.empty:
            atleta_nome = st.selectbox("Selecione o Aluno", st.session_state.atletas_df['Nome'])
            mes = st.selectbox("Mês de Referência", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            metodo = st.radio("Forma", ["PIX", "Dinheiro", "Cartão", "Transferência"], horizontal=True)
            valor_pago = st.number_input("Valor Recebido", value=150.0)
            
            if st.button("Confirmar Recebimento"):
                id_atleta = st.session_state.atletas_df[st.session_state.atletas_df['Nome'] == atleta_nome]['ID'].values[0]
                novo_pgto = pd.DataFrame([[id_atleta, mes, 2024, valor_pago, datetime.now().strftime("%d/%m/%Y"), metodo]], 
                                         columns=st.session_state.fin_df.columns)
                st.session_state.fin_df = pd.concat([st.session_state.fin_df, novo_pgto], ignore_index=True)
                save_data(st.session_state.atletas_df, st.session_state.fin_df)
                st.balloons()
                st.rerun()
        else:
            st.warning("Nenhum atleta cadastrado.")

    with col_hist:
        st.subheader("Histórico Geral")
        # Merge para mostrar nomes no financeiro
        if not st.session_state.fin_df.empty:
            df_view = st.session_state.fin_df.merge(st.session_state.atletas_df[['ID', 'Nome']], left_on='ID_Atleta', right_on='ID')
            st.dataframe(df_view[['Nome', 'Mes_Ref', 'Valor', 'Data_Pgto', 'Metodo']], use_container_width=True)

# --- ⚙️ SISTEMA ---
elif aba == "⚙️ Sistema":
    st.title("⚙️ Configurações e Backup")
    if st.button("📥 Exportar Dados para Excel"):
        with pd.ExcelWriter("Relatorio_Assoc_Martins.xlsx") as writer:
            st.session_state.atletas_df.to_excel(writer, sheet_name='Atletas')
            st.session_state.fin_df.to_excel(writer, sheet_name='Financeiro')
        st.success("Relatório gerado com sucesso!")
        
    if st.button("⚠️ Resetar Sistema (Apagar Tudo)"):
        if os.path.exists(DB_ATLETAS): os.remove(DB_ATLETAS)
        if os.path.exists(DB_FINANCEIRO): os.remove(DB_FINANCEIRO)
        st.session_state.clear()
        st.rerun()
