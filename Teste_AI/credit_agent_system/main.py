import os
import sys

# Add the project root to sys.path to ensure imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from agents.triage_agent import TriageAgent

def main():
    # Path to the CSV file
    data_path = os.path.join(current_dir, 'data', 'clientes.csv')
    
    agent = TriageAgent(data_path)
    agent.start()

if __name__ == "__main__":
    main()
