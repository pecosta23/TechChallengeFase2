import requests
import pandas as pd
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_DEFAULT_REGION")

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

bucket_name = 'tech2fiap2025'

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

        df['data_coleta'] = datetime.now().strftime('%Y-%m-%d')

        df.rename(columns={
            "cod": "Código",
            "asset": "Ação",
            "type": "Tipo",
            "theoricalQty": "Qtde. Teórica",
            "part": "Part. (%)"
        }, inplace=True)

        colunas = ["data_coleta", "Código", "Ação", "Tipo", "Qtde. Teórica", "Part. (%)"]
        df = df[colunas]

        def enviar_particionado_s3(df, bucket_name, s3_client):
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            
            print(f"Enviando dados particionados em Parquet para {len(df)} ações...")
            
            for _, row in df.iterrows():
                codigo_acao = row['Código']
                
                df_acao = pd.DataFrame([row])
                
                ano = datetime.now().strftime('%Y')
                mes = datetime.now().strftime('%m')
                dia = datetime.now().strftime('%d')
                
                s3_key = f"dados/ano={ano}/mes={mes}/dia={dia}/acao={codigo_acao}/carteira_ibov_{codigo_acao}_{data_hoje}.parquet"
                
                local_temp_file = f"temp_{codigo_acao}_{data_hoje}.parquet"
                
                try:
                    df_acao.to_parquet(local_temp_file, index=False, engine='pyarrow')
  
                    s3_client.upload_file(local_temp_file, bucket_name, s3_key)
                    print(f"✓ {codigo_acao}: s3://{bucket_name}/{s3_key}")
                    
                    os.remove(local_temp_file)
                    
                except Exception as e:
                    print(f"✗ Erro ao enviar {codigo_acao}: {e}")
                    
                    if os.path.exists(local_temp_file):
                        os.remove(local_temp_file)
            
            print(f"Finalizado! {len(df)} arquivos Parquet enviados com particionamento.")

        enviar_particionado_s3(df, bucket_name, s3)
        
        local_file_path = f"carteira_ibov_consolidado_{datetime.now().strftime('%Y-%m-%d')}.parquet"
        s3_file_key_consolidado = f"dados/consolidado/carteira_ibov_{datetime.now().strftime('%Y-%m-%d')}.parquet"
        
        df.to_parquet(local_file_path, index=False, engine='pyarrow')
        print(f"\nArquivo consolidado salvo localmente em Parquet: {local_file_path}")
        print(df.head())

        s3.upload_file(local_file_path, bucket_name, s3_file_key_consolidado)
        print(f"Arquivo consolidado Parquet enviado para S3: s3://{bucket_name}/{s3_file_key_consolidado}")
        
        os.remove(local_file_path)
    else:
        print("A chave 'results' não foi encontrada no JSON.")
        print("Conteúdo:", data)
else:
    print("Erro no request:", response.status_code)
