import os
import sys

# Adiciona a raiz do projeto ao sys.path para garantir que as importações funcionem corretamente
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from agents.triage_agent import TriageAgent

def main():
    # Caminho para o arquivo CSV
    data_path = os.path.join(current_dir, 'data', 'clientes.csv')
    
    agent = TriageAgent(data_path)
    agent.start()

if __name__ == "__main__":
    main()
