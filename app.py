import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, date

# --- 1. ENGINE DE DADOS ATUALIZADA (LGPD) ---
class JudoEngine:
    @staticmethod
    def initialize():
        # Novos campos LGPD: Termo_Consentimento, Finalidade, Responsavel_Dados, Contato_Emergencia
        files = {
            "db_atletas_v43.csv": [
                "ID", "Nome", "Status", "CPF", "Nasc", "Faixa", "WhatsApp", 
                "Responsavel_Legal", "CPF_Resp", "Contato_Emergencia", 
                "Alergias_Saude", "Consentimento_LGPD", "Data_Aceite_Termos"
            ],
            "db_financeiro.csv": ["ID_Lan", "Nome", "Mes_Ref", "Valor", "Data_PG", "Metodo"]
        }
        for file, cols in files.items():
            if not os.path.exists(file):
                pd.DataFrame(columns=cols).to_csv(file, index=False)

    @staticmethod
    def commit(df_a, df_f):
        df_a.to_csv("db_atletas_v43.csv", index=False)
        df_f.to_csv("db_financeiro.csv", index=False)

JudoEngine.initialize()

# --- 2. INTERFACE DE CADASTRO LGPD ---
# (Dentro do seu menu de Alunos > aba Novo Aluno)

with st.form("cad_lgpd", clear_on_submit=True):
    st.subheader("📝 Ficha de Matrícula e Termo de Privacidade")
    
    # Seção 1: Dados Pessoais
    c1, c2, c3 = st.columns([2, 1, 1])
    n_nome = c1.text_input("Nome Completo*")
    n_cpf = c2.text_input("CPF*")
    n_nasc = c3.date_input("Data de Nascimento", date(2010, 1, 1), format="DD/MM/YYYY")
    
    # Seção 2: Responsabilidade e Emergência (Art. 14 LGPD - Crianças/Adolescentes)
    st.markdown("---")
    st.caption("🛡️ Dados de Proteção e Emergência")
    e1, e2, e3 = st.columns(3)
    n_resp = e1.text_input("Responsável Legal (Se menor)")
    n_resp_cpf = e2.text_input("CPF do Responsável")
    n_emergencia = e3.text_input("Telefone de Emergência*")
    
    # Seção 3: Dados Sensíveis (Saúde)
    n_saude = st.text_area("Informações Médicas/Alergias (Dado Sensível - Art. 5, II)")
    
    # Seção 4: Governança de Dados (Compliance)
    st.info("📜 **Termo de Consentimento:** Ao marcar as opções abaixo, o titular (ou responsável) autoriza a Associação Roberdrayner a tratar os dados para fins de gestão acadêmica, segurança e comunicações oficiais.")
    
    col_check1, col_check2 = st.columns(2)
    consent_uso = col_check1.checkbox("Autorizo o tratamento de dados pessoais para gestão da matrícula.")
    consent_saude = col_check2.checkbox("Autorizo o tratamento de dados de saúde para fins de segurança nas aulas.")
    
    if st.form_submit_button("Finalizar Matrícula Blindada"):
        if n_nome and n_cpf and consent_uso:
            new_id = int(st.session_state.db_a['ID'].max() + 1) if not st.session_state.db_a.empty else 1
            
            novo_atleta = pd.DataFrame([{
                "ID": new_id,
                "Nome": n_nome,
                "Status": "Ativo",
                "CPF": n_cpf,
                "Nasc": n_nasc.strftime("%d/%m/%Y"),
                "Faixa": "Branca",
                "WhatsApp": n_emergencia,
                "Responsavel_Legal": n_resp,
                "CPF_Resp": n_resp_cpf,
                "Contato_Emergencia": n_emergencia,
                "Alergias_Saude": n_saude,
                "Consentimento_LGPD": "Sim",
                "Data_Aceite_Termos": datetime.now().strftime("%d/%m/%Y %H:%M")
            }])
            
            st.session_state.db_a = pd.concat([st.session_state.db_a, novo_atleta], ignore_index=True)
            JudoEngine.commit(st.session_state.db_a, st.session_state.db_f)
            st.success("✅ Atleta cadastrado em conformidade com a LGPD!")
            st.rerun()
        else:
            st.error("⚠️ Você deve preencher os campos obrigatórios e aceitar o Termo de Consentimento.")
