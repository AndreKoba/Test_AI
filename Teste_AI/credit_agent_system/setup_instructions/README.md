# Sistema de Agentes de Crédito - Instruções de Instalação e Execução

Este guia passo a passo ajudará você a configurar e rodar o Agente de Triagem.

## Pré-requisitos

1.  **Python Instalado**: Você precisa ter o Python instalado no seu computador.
    *   Para verificar se já tem, abra o terminal (Prompt de Comando ou PowerShell) e digite: `python --version`
    *   Se não tiver, baixe e instale a versão mais recente em [python.org](https://www.python.org/downloads/). **Importante**: Durante a instalação, marque a opção "Add Python to PATH".

## Como Rodar o Agente

1.  **Navegue até a pasta do projeto**:
    Abra o terminal e vá para a pasta onde os arquivos foram salvos.
    Exemplo:
    ```bash
    cd "c:/Users/Blue.DESKTOP-NSJBI0D/OneDrive/Teste_AI/credit_agent_system"
    ```

2.  **Execute o arquivo principal**:
    Digite o seguinte comando:
    ```bash
    python main.py
    ```

## Como Usar

1.  O sistema irá iniciar e dar as boas-vindas.
2.  Você será solicitado a digitar um **CPF** e uma **Data de Nascimento**.
3.  Use os dados de teste abaixo para validar o funcionamento:

    | CPF | Data de Nascimento | Nome |
    | :--- | :--- | :--- |
    | 12345678900 | 01/01/1990 | João Silva |
    | 98765432100 | 15/05/1985 | Maria Oliveira |
    | 11122233344 | 20/10/2000 | Pedro Santos |

4.  **Teste de Falha**: Tente digitar dados incorretos. O sistema permite 3 tentativas antes de encerrar.

## Estrutura de Arquivos

*   `main.py`: Arquivo principal que inicia o programa.
*   `agents/triage_agent.py`: Código do Agente de Triagem.
*   `data/clientes.csv`: Base de dados fictícia de clientes.
