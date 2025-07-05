import sys
import boto3
from datetime import datetime
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import lit, to_date
from awsglue.utils import getResolvedOptions

# Pega parâmetros do Glue Job (como o bucket e data de referência)
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET', 'DATE'])

bucket = args['BUCKET']               # Ex: b3-pipeline-data
data_referencia = args['DATE']       # Ex: 2025-07-04

# Inicializa contexto Spark + Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Caminho de entrada
input_path = f"s3://{bucket}/raw/b3/ibov/{data_referencia}/pregao.json"

# Caminho de saída (sem /ano=... porque será particionado)
output_path = f"s3://{bucket}/processed/b3/ibov/"

# Lê JSON
df = spark.read.json(input_path)

# Extrai data como partições
data = datetime.strptime(data_referencia, "%Y-%m-%d")
df = df.withColumn("ano", lit(data.year)) \
       .withColumn("mes", lit(data.month)) \
       .withColumn("dia", lit(data.day))

# Escreve em Parquet particionado por ano/mes/dia
df.write.mode("append") \
  .partitionBy("ano", "mes", "dia") \
  .format("parquet") \
  .save(output_path)