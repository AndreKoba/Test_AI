import csv
import os
from datetime import datetime

class CreditLimitAgent:
    def __init__(self, data_path, rules_path, requests_path):
        self.data_path = data_path
        self.rules_path = rules_path
        self.requests_path = requests_path

    def process(self, cpf):
        while True:
            print("\n=== Agente de Limite de Crédito ===")
            print("1. Consultar Limite Atual")
            print("2. Solicitar Aumento de Limite")
            print("0. Voltar ao Menu Principal")
            
            choice = input("Escolha uma opção: ").strip()
            
            if choice == '1':
                self.consult_limit(cpf)
            elif choice == '2':
                self.request_increase(cpf)
            elif choice == '0':
                break
            else:
                print("Opção inválida.")

    def get_client_data(self, cpf):
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['cpf'] == cpf:
                        return row
        except Exception as e:
            print(f"Erro ao ler dados do cliente: {e}")
        return None

    def consult_limit(self, cpf):
        client = self.get_client_data(cpf)
        if client:
            print(f"\nSeu limite atual é: R$ {client.get('limite_atual', '0.00')}")
        else:
            print("\nCliente não encontrado.")

    def request_increase(self, cpf):
        client = self.get_client_data(cpf)
        if not client:
            print("Erro ao recuperar dados do cliente.")
            return

        current_limit = float(client.get('limite_atual', 0))
        score = float(client.get('score', 0))
        
        print(f"\nSeu limite atual: R$ {current_limit:.2f}")
        print(f"Seu score atual: {score}")
        
        try:
            requested_str = input("Qual o novo limite desejado? (apenas números): ").replace(',', '.')
            requested_limit = float(requested_str)
        except ValueError:
            print("Valor inválido.")
            return

        # Check rules
        max_allowed = self.check_rules(score)
        status = 'rejeitado'
        
        if requested_limit <= max_allowed:
            status = 'aprovado'
            print("\nParabéns! Sua solicitação foi APROVADA.")
            # In a real system, we would update the limit in clientes.csv here too.
            # For this exercise, we just log it.
        else:
            print("\nSua solicitação foi REJEITADA com base no seu score atual.")
            print(f"Para o seu score ({score}), o limite máximo permitido é R$ {max_allowed:.2f}")

        # Log request
        self.log_request(cpf, current_limit, requested_limit, status)

        # Handle Rejection
        if status == 'rejeitado':
            self.offer_interview(cpf)

    def check_rules(self, score):
        max_limit = 0.0
        try:
            with open(self.rules_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    min_s = float(row['min_score'])
                    max_s = float(row['max_score'])
                    limit = float(row['max_limite'])
                    
                    if min_s <= score <= max_s:
                        max_limit = limit
                        break
        except Exception as e:
            print(f"Erro ao ler regras de limite: {e}")
        
        return max_limit

    def log_request(self, cpf, current, requested, status):
        try:
            file_exists = os.path.isfile(self.requests_path)
            with open(self.requests_path, mode='a', encoding='utf-8', newline='') as csvfile:
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
            print("Solicitação registrada com sucesso.")
        except Exception as e:
            print(f"Erro ao registrar solicitação: {e}")

    def offer_interview(self, cpf):
        print("\n--- Sugestão ---")
        print("Gostaria de realizar uma Entrevista de Crédito para tentar atualizar seu score?")
        print("Isso pode ajudar a aumentar seu limite no futuro.")
        choice = input("Deseja realizar a entrevista agora? (s/n): ").strip().lower()
        
        if choice.startswith('s'):
            from agents.interview_agent import InterviewAgent
            # Assuming data_path is the same for all agents
            agent = InterviewAgent(self.data_path)
            agent.process(cpf)
        else:
            print("Entendido. Retornando ao menu.")
