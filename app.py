import requests
import pandas as pd

url = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEyMCwiaW5kZXgiOiJJQk9WIiwic2VnbWVudCI6IjEifQ=="

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://sistemaswebb3-listados.b3.com.br/"
}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("Chaves disponíveis no JSON:", data.keys())  
    
    if "results" in data:
        acoes = data["results"]
        df = pd.DataFrame(acoes)

        df.rename(columns={
            "cod": "Código",
            "asset": "Ação",
            "type": "Tipo",
            "theoricalQty": "Qtde. Teórica",
            "part": "Part. (%)"
        }, inplace=True)

        colunas = ["Código", "Ação", "Tipo", "Qtde. Teórica", "Part. (%)"]
        df = df[colunas]

        df.to_csv("carteira_ibov.csv", index=False, encoding="utf-8-sig")
        print(df.head())
    else:
        print("A chave 'results' não foi encontrada no JSON.")
        print("Conteúdo:", data)
else:
    print("Erro no request:", response.status_code)
