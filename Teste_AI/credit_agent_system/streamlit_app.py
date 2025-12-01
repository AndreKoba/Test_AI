import streamlit as st
import os
import csv
import json
import urllib.request
from datetime import datetime

# --- Configuration & Setup ---
st.set_page_config(page_title="Sistema de Agentes de Crédito", page_icon="🏦")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CLIENTES_CSV = os.path.join(DATA_DIR, 'clientes.csv')
SCORE_RULES_CSV = os.path.join(DATA_DIR, 'score_limite.csv')
LOGS_CSV = os.path.join(DATA_DIR, 'solicitacoes_aumento_limite.csv')

# --- Helper Functions (Logic from Agents) ---

def authenticate_user(cpf_input, dob_input):
    """Validates user against clientes.csv"""
    try:
        with open(CLIENTES_CSV, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['cpf'].strip() == cpf_input and row['data_nascimento'].strip() == dob_input:
                    return row
    except Exception as e:
        st.error(f"Erro ao ler banco de dados: {e}")
    return None

def get_client_data(cpf):
    """Refreshes client data from CSV"""
    try:
        with open(CLIENTES_CSV, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['cpf'] == cpf:
                    return row
    except Exception:
        pass
    return None

def check_limit_rules(score):
    """Checks max limit allowed for a score"""
    max_limit = 0.0
    try:
        with open(SCORE_RULES_CSV, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                min_s = float(row['min_score'])
                max_s = float(row['max_score'])
                limit = float(row['max_limite'])
                if min_s <= score <= max_s:
                    max_limit = limit
                    break
    except Exception:
        pass
    return max_limit

def log_request(cpf, current, requested, status):
    """Logs limit increase request"""
    try:
        file_exists = os.path.isfile(LOGS_CSV)
        with open(LOGS_CSV, mode='a', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['cpf_cliente', 'data_hora_solicitacao', 'limite_atual', 'novo_limite_solicitado', 'status_pedido']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                'cpf_cliente': cpf,
                'data_hora_solicitacao': datetime.now().isoformat(),
                'limite_atual': current,
                'novo_limite_solicitado': requested,
                'status_pedido': status
            })
    except Exception as e:
        st.error(f"Erro ao logar solicitação: {e}")

def calculate_score(data):
    """Calculates credit score based on formula"""
    peso_renda = 30
    peso_emprego = {"formal": 300, "autônomo": 200, "desempregado": 0}
    peso_dependentes = {0: 100, 1: 80, 2: 60, "3+": 30}
    peso_dividas = {"sim": -100, "não": 100}

    income = data['income']
    expenses = data['expenses']
    job_type = data['job_type']
    dependents = data['dependents']
    has_debts = data['has_debts']

    part_income = (income / (expenses + 1)) * peso_renda
    part_job = peso_emprego.get(job_type, 0)
    
    # Handle dependents key
    dep_key = dependents if dependents in [0, 1, 2] else "3+"
    part_dependents = peso_dependentes.get(dep_key, 30)
    
    part_debts = peso_dividas.get(has_debts, 0)

    raw_score = part_income + part_job + part_dependents + part_debts
    return max(0, min(1000, int(raw_score)))

def update_client_score(cpf, new_score):
    """Updates score in CSV"""
    rows = []
    updated = False
    try:
        with open(CLIENTES_CSV, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['cpf'] == cpf:
                    row['score'] = str(new_score)
                    updated = True
                rows.append(row)
        
        if updated:
            with open(CLIENTES_CSV, mode='w', encoding='utf-8', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return True
    except Exception as e:
        st.error(f"Erro ao atualizar DB: {e}")
    return False

def get_exchange_rate(currency):
    """Fetches exchange rate from API"""
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data.get('rates', {}).get(currency)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
    return None


def format_currency(value):
    if value is None:
        return ""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_currency(value_str):
    if not value_str:
        return 0.0
    try:
        clean_str = value_str.replace(".", "").replace(",", ".")
        return float(clean_str)
    except ValueError:
        return 0.0

def currency_input(label, key, value=0.0):
   
    text_key = f"{key}_text"
    
    if text_key not in st.session_state:
        st.session_state[text_key] = format_currency(value)

    def on_change():
        raw_val = st.session_state[text_key]
        parsed = parse_currency(raw_val)
        st.session_state[text_key] = format_currency(parsed)

    st.text_input(
        label,
        key=text_key,
        on_change=on_change
    )

    return parse_currency(st.session_state[text_key])


def view_login():
    st.header("🔐 Triagem - Login")
    st.write("Bem-vindo ao Sistema de Agentes de Crédito.")
    
    with st.form("login_form"):
        cpf = st.text_input("CPF (apenas números)")
        # Changed to date_input for automatic slash formatting
        dob_date = st.date_input("Data de Nascimento", min_value=datetime(1900, 1, 1), format="DD/MM/YYYY")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            dob = dob_date.strftime("%d/%m/%Y")
            user = authenticate_user(cpf, dob)
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                st.session_state['cpf'] = user['cpf']
                st.success(f"Bem-vindo(a), {user['nome']}!")
                st.rerun()
            else:
                st.error("Dados incorretos. Tente novamente.")

def view_credit_limit():
    st.header("💳 Limite de Crédito")
    
    user = get_client_data(st.session_state['cpf'])
    if not user:
        st.error("Erro ao carregar dados.")
        return

    current_limit = float(user.get('limite_atual', 0))
    score = float(user.get('score', 0))

    st.metric("Limite Atual", f"R$ {current_limit:.2f}")
    st.metric("Seu Score", f"{int(score)}")

    st.subheader("Solicitar Aumento")
    st.subheader("Solicitar Aumento")
    with st.form("limit_form"):
        new_limit = currency_input("Novo limite desejado (R$)", key="limit_input")
        submit = st.form_submit_button("Solicitar")
        
        if submit:
            max_allowed = check_limit_rules(score)
            if new_limit <= max_allowed:
                status = 'aprovado'
                st.success("✅ Parabéns! Sua solicitação foi APROVADA.")
            else:
                status = 'rejeitado'
                st.error("❌ Solicitação REJEITADA com base no seu score atual.")
                st.info(f"Limite máximo permitido para seu score: R$ {max_allowed:.2f}")
                st.warning("💡 Dica: Vá para a aba 'Entrevista' para tentar melhorar seu score!")
            
            log_request(st.session_state['cpf'], current_limit, new_limit, status)

def view_interview():
    st.header("📝 Entrevista de Crédito")
    st.write("Responda as perguntas abaixo para recalcular seu score.")
    
    with st.form("interview_form"):
        income = currency_input("Renda Mensal (R$)", key="income_input")
        job_type = st.selectbox("Tipo de Emprego", ["formal", "autônomo", "desempregado"])
        expenses = currency_input("Despesas Fixas Mensais (R$)", key="expenses_input")
        dependents = st.selectbox("Número de Dependentes", [0, 1, 2, 3]) # 3 represents 3+
        has_debts = st.radio("Possui dívidas ativas?", ["não", "sim"])
        
        submit = st.form_submit_button("Calcular Novo Score")
        
        if submit:
            data = {
                "income": income,
                "job_type": job_type,
                "expenses": expenses,
                "dependents": dependents,
                "has_debts": has_debts
            }
            new_score = calculate_score(data)
            if update_client_score(st.session_state['cpf'], new_score):
                st.success(f"✅ Score atualizado com sucesso! Novo Score: {new_score}")
                st.balloons()
            else:
                st.error("Erro ao atualizar score.")

def view_exchange():
    st.header("💱 Agente de Câmbio")
    st.write("Consulte a cotação do Dólar (USD) em tempo real.")
    
    currency = st.text_input("Código da Moeda (ex: BRL, EUR, JPY)", "BRL").upper()
    
    if st.button("Consultar Cotação"):
        if currency:
            rate = get_exchange_rate(currency)
            if rate:
                st.info(f"🇺🇸 1 USD = {rate:.4f} {currency}")
            else:
                st.error("Moeda não encontrada ou erro de conexão.")

# --- Fluxo Main ---

def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        view_login()
    else:
        st.sidebar.title(f"Olá, {st.session_state['user']['nome']}")
        menu = st.sidebar.radio(
            "Menu",
            ["🏠 Home", "💳 Limite de Crédito", "📝 Entrevista", "💱 Câmbio", "🚪 Sair"]
        )
        
        if menu == "🏠 Home":
            st.title("Painel Principal")
            st.write("Selecione uma opção no menu lateral para começar.")
            st.info("Use o menu para navegar entre os agentes.")
        elif menu == "💳 Limite de Crédito":
            view_credit_limit()
        elif menu == "📝 Entrevista":
            view_interview()
        elif menu == "💱 Câmbio":
            view_exchange()
        elif menu == "🚪 Sair":
            terminate_session()

def terminate_session():
    """Ferramenta de encerramento para finalizar a execução"""
    st.session_state['authenticated'] = False
    st.rerun()

if __name__ == "__main__":
    main()
