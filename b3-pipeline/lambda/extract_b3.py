import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = "b3-pipeline-data"
    hoje = datetime.today().strftime('%Y-%m-%d')

    # Exemplo de payload simulado
    dados = [{"ticker": "PETR4", "preco": 38.12, "volume": 1000000}]
    s3.put_object(
        Bucket=bucket,
        Key=f'raw/b3/ibov/{hoje}/pregao.json',
        Body=json.dumps(dados)
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f'Dados enviados para {hoje}')
    }