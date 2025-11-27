import json
import urllib.request
import urllib.error

class ExchangeAgent:
    def __init__(self):
        self.api_url = "https://open.er-api.com/v6/latest/USD"

    def process(self):
        print("\n=== Agente de Câmbio ===")
        print("Posso consultar a cotação do Dólar (USD) para diversas moedas.")
        
        while True:
            target_currency = input("\nPara qual moeda você deseja ver a cotação? (ex: BRL, EUR, JPY) ou 'sair' para voltar: ").strip().upper()
            
            if target_currency == 'SAIR':
                print("Encerrando consulta de câmbio.")
                break
            
            if not target_currency:
                continue

            self.get_rate(target_currency)

    def get_rate(self, target_currency):
        print(f"Buscando cotação atual para USD -> {target_currency}...")
        
        try:
            with urllib.request.urlopen(self.api_url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    rates = data.get('rates', {})
                    
                    rate = rates.get(target_currency)
                    
                    if rate:
                        print(f"\nCotação Atual:")
                        print(f"1 USD = {rate:.4f} {target_currency}")
                        print(f"Última atualização: {data.get('time_last_update_utc', 'Desconhecido')}")
                    else:
                        print(f"Moeda '{target_currency}' não encontrada na base de dados.")
                else:
                    print("Não foi possível acessar o serviço de cotação no momento.")
                    
        except urllib.error.URLError as e:
            print(f"Erro de conexão: {e.reason}")
            print("Verifique sua conexão com a internet.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
