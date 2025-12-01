import csv
import os

class TriageAgent:
    def __init__(self, data_path):
        self.data_path = data_path
        self.max_attempts = 3

    def start(self):
        print("\n=== Bem-vindo ao Sistema de Atendimento ===")
        print("Olá! Eu sou o seu assistente virtual de triagem.")
        
        cpf = self.authenticate()
        if cpf:
            self.redirect(cpf)
        else:
            print("\nNão foi possível realizar a autenticação após 3 tentativas.")
            print("Por favor, entre em contato com o suporte ou tente novamente mais tarde.")
            print("Encerrando atendimento. Tenha um bom dia!")

    def authenticate(self):
        attempts = 0
        while attempts < self.max_attempts:
            print(f"\nTentativa {attempts + 1} de {self.max_attempts}")
            cpf = input("Por favor, digite seu CPF (apenas números): ").strip()
            dob = input("Por favor, digite sua data de nascimento (DD/MM/AAAA): ").strip()

            if self.validate_user(cpf, dob):
                print(f"\nAutenticação realizada com sucesso!")
                return cpf
            else:
                print("Dados incorretos. Verifique o CPF e a data de nascimento.")
                attempts += 1
        
        return None

    def validate_user(self, cpf_input, dob_input):
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Validação simples: verifica se CPF e Data de Nascimento correspondem a um registro
                    # Removendo não-dígitos do CPF do CSV apenas por precaução
                    db_cpf = row['cpf'].strip()
                    db_dob = row['data_nascimento'].strip()
                    
                    if db_cpf == cpf_input and db_dob == dob_input:
                        print(f"Bem-vindo(a), {row['nome']}!")
                        return True
        except FileNotFoundError:
            print(f"Erro: Base de dados não encontrada em {self.data_path}")
            return False
        except Exception as e:
            print(f"Erro ao ler base de dados: {e}")
            return False
            
        return False

    def redirect(self, cpf):
        from agents.credit_limit_agent import CreditLimitAgent
        from agents.interview_agent import InterviewAgent
        from agents.exchange_agent import ExchangeAgent
        
        while True:
            print("\n------------------------------------------------")
            print("Como posso ajudar você agora?")
            print("1. Gostaria de ver ou aumentar meu Limite de Crédito")
            print("2. Quero atualizar meu cadastro (Entrevista de Crédito)")
            print("3. Preciso consultar a cotação de moedas")
            print("0. Encerrar atendimento")
            
            choice = input("\nDigite o número da opção desejada: ").strip()
            
            if choice == '1':
                rules_path = os.path.join(os.path.dirname(self.data_path), 'score_limite.csv')
                requests_path = os.path.join(os.path.dirname(self.data_path), 'solicitacoes_aumento_limite.csv')
                agent = CreditLimitAgent(self.data_path, rules_path, requests_path)
                agent.process(cpf)
            elif choice == '2':
                agent = InterviewAgent(self.data_path)
                agent.process(cpf)
            elif choice == '3':
                agent = ExchangeAgent()
                agent.process()
            elif choice == '0':
                self.end_execution()
                break
            else:
                print("\nDesculpe, não entendi. Poderia escolher uma das opções abaixo?")

    def end_execution(self):
        """Ferramenta de encerramento para finalizar o loop de execução"""
        print("\nSolicitação de encerramento recebida.")
        print("Foi um prazer atender você. Até a próxima!")
