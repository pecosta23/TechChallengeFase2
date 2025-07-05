# TechChallengeFase2

# 📈 Pipeline de Dados da B3 com Terraform e AWS

Este projeto provisiona, com Terraform, toda a infraestrutura necessária para extrair, armazenar, processar e consultar dados do pregão da B3. Os dados são obtidos diariamente e armazenados no Amazon S3, processados com AWS Glue e consultados via Athena.

---

## 📦 Componentes da Solução

| Serviço       | Função                                                                 |
|---------------|------------------------------------------------------------------------|
| **S3**        | Armazenamento dos dados brutos e processados                           |
| **Lambda**    | Extração dos dados da B3 e envio para o bucket S3                      |
| **Glue Job**  | Processamento e transformação dos dados (ex: JSON → Parquet)           |
| **Glue Crawler** | Criação/atualização do catálogo de dados no Glue                    |
| **Athena**    | Consultas SQL sobre os dados tratados                                  |
| **EventBridge** | Agendamento diário para execução automática da função Lambda         |

---

## 🚀 Pré-requisitos

- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Conta AWS com permissões para: IAM, S3, Lambda, Glue, Athena, EventBridge
- Executar `aws configure` para configurar suas credenciais

---

## 🔧 Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/b3-pipeline.git
cd src
```

### 2. Configure suas credenciais AWS

```bash
aws configure
```

### 3. Compacte a Lambda

```bash
zip ../files/lambda.zip lambda/extract_b3.py
cd ..
```

### 4. Inicialize e aplique com Terraform

```bash
terraform init
terraform apply
```