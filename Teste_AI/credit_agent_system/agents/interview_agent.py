import csv
import os

class InterviewAgent:
    def __init__(self, data_path):
        self.data_path = data_path

    def process(self, cpf):
        print("\n=== Entrevista de Crédito ===")
        print("Vamos coletar alguns dados para calcular seu novo score de crédito.")
        
        data = self.collect_data()
        if data:
            score = self.calculate_score(data)
            print(f"\nSeu novo score calculado é: {score}")
            
            if self.update_db(cpf, score):
                print("Seu score foi atualizado com sucesso na nossa base de dados.")
            else:
                print("Houve um erro ao atualizar seu score na base de dados.")
            
            print("\nRedirecionando de volta ao menu principal...")
            # In a real system, we might loop back or call a specific agent. 
            # Here we just return, which goes back to the Triage menu loop.

    def collect_data(self):
        try:
            print("\nPor favor, responda as seguintes perguntas:")
            
            # Renda mensal
            income = float(input("1. Qual sua renda mensal? (apenas números): ").replace(',', '.'))
            
            # Tipo de emprego
            print("2. Qual seu tipo de emprego?")
            print("   [1] Formal")
            print("   [2] Autônomo")
            print("   [3] Desempregado")
            job_option = input("   Opção: ").strip()
            job_map = {'1': 'formal', '2': 'autônomo', '3': 'desempregado'}
            job_type = job_map.get(job_option)
            if not job_type:
                print("Opção inválida. Considerando 'desempregado' por segurança.")
                job_type = 'desempregado'

            # Despesas fixas
            expenses = float(input("3. Quais suas despesas fixas mensais? (apenas números): ").replace(',', '.'))
            
            # Número de dependentes
            dependents_str = input("4. Quantos dependentes você tem? (0, 1, 2, 3+): ").strip()
            if dependents_str in ['0', '1', '2']:
                dependents = int(dependents_str)
            else:
                # Treat anything else as 3+ or just use the string key for logic if needed, 
                # but the formula uses keys like 0, 1, 2, "3+".
                # Let's standardize to the keys expected by the formula.
                try:
                    val = int(dependents_str)
                    if val >= 3:
                        dependents = "3+"
                    else:
                        dependents = val
                except:
                    dependents = "3+"

            # Dívidas ativas
            debts_input = input("5. Possui dívidas ativas? (s/n): ").strip().lower()
            has_debts = "sim" if debts_input.startswith('s') else "não"
            
            return {
                "income": income,
                "job_type": job_type,
                "expenses": expenses,
                "dependents": dependents,
                "has_debts": has_debts
            }

        except ValueError:
            print("\nErro: Valor inválido inserido. A entrevista foi cancelada.")
            return None

    def calculate_score(self, data):
        # Formula:
        # score = ( (renda_mensal / (despesas + 1)) * peso_renda + peso_emprego[tipo_emprego] + peso_dependentes[num_dependentes] + peso_dividas[tem_dividas] )
        
        peso_renda = 30
        peso_emprego = {
            "formal": 300,
            "autônomo": 200,
            "desempregado": 0
        }
        peso_dependentes = {
            0: 100,
            1: 80,
            2: 60,
            "3+": 30
        }
        peso_dividas = {
            "sim": -100,
            "não": 100
        }

        income = data['income']
        expenses = data['expenses']
        job_type = data['job_type']
        dependents = data['dependents']
        has_debts = data['has_debts']

        # Calculate parts
        part_income = (income / (expenses + 1)) * peso_renda
        part_job = peso_emprego.get(job_type, 0)
        part_dependents = peso_dependentes.get(dependents, 30) # Default to lowest if key mismatch
        part_debts = peso_dividas.get(has_debts, 0)

        raw_score = part_income + part_job + part_dependents + part_debts
        
        # Clamp between 0 and 1000
        final_score = max(0, min(1000, int(raw_score)))
        
        return final_score

    def update_db(self, cpf, new_score):
        # We need to read all, update the specific row, and write back.
        # This is not efficient for huge DBs but fine for CSV.
        rows = []
        updated = False
        
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                if 'score' not in fieldnames:
                    fieldnames.append('score')
                
                for row in reader:
                    if row['cpf'] == cpf:
                        row['score'] = str(new_score)
                        updated = True
                    rows.append(row)
            
            if updated:
                with open(self.data_path, mode='w', encoding='utf-8', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Erro ao atualizar banco de dados: {e}")
            return False
