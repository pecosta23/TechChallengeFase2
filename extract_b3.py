import json
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from datetime import datetime
from io import BytesIO


B3_URL = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEyMCwiaW5kZXgiOiJJQk9WIiwic2VnbWVudCI6IjEifQ=="


def _extract_data():
    hoje = datetime.today().strftime("%Y-%m-%d")

    # Fetch and process data
    dados = _fetch_b3_data()

    # Criar DataFrame
    df = pd.DataFrame(dados)
    table = pa.Table.from_pandas(df)

    # Convert to parquet and upload to S3
    buffer = BytesIO()
    pq.write_table(table, buffer)

    s3_path = f"b3/{hoje}/data.parquet"
    s3_bucket = "b3-raw-pipeline-data"
    s3 = boto3.client("s3")
    s3.put_object(Bucket=s3_bucket, Key=s3_path, Body=buffer.getvalue())

    return {"statusCode": 200, "body": json.dumps(f"Dados enviados para {hoje}")}


def _fetch_b3_data():
    response = requests.get(B3_URL, timeout=1000)
    if response.status_code == 200:
        return response.json().get("results")
    else:
        raise requests.RequestException(
            f"Failed to fetch data from B3: {response.status_code}"
        )


if __name__ == "__main__":
    _extract_data()
