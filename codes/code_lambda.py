import json
import boto3
import pymongo
from datetime import datetime
from pymongo.errors import BulkWriteError
import io

# Conexão com o MongoDB
MONGO_URI = "SUA_URL_MONGO"
DATABASE_NAME = "seu_database"
COLLECTION_NAME = "sua_colecao"

def connect_to_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return collection

def cast_column_types(record):
    # Converte os tipos de dados conforme o schema
    if 'DataDeAdesao' in record:
        record['DataDeAdesao'] = datetime.fromisoformat(record['DataDeAdesao']) if record['DataDeAdesao'] else None
    if 'UltimoPagamento' in record:
        record['UltimoPagamento'] = datetime.fromisoformat(record['UltimoPagamento']) if record['UltimoPagamento'] else None
    if 'HorasAssistidas' in record:
        record['HorasAssistidas'] = int(record['HorasAssistidas']) if record['HorasAssistidas'] is not None else None
    if 'idade' in record:
        record['idade'] = int(record['idade']) if record['idade'] is not None else None
    return record

def lambda_handler(event, context):
    # Conecta ao S3
    s3_client = boto3.client('s3')

    # Extrai informações do evento
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Verifica se o arquivo está no prefixo esperado
    if not object_key.startswith("teste/"):
        return {
            "statusCode": 400,
            "body": json.dumps("Arquivo fora do prefixo esperado.")
        }

    # Faz download do arquivo do S3
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')
        print("Arquivo carregado do S3 com sucesso.")
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Erro ao obter arquivo do S3: {str(e)}")
        }

    # Carrega o JSON diretamente como uma lista de dicionários
    try:
        records = json.loads(file_content)  # Carrega diretamente como uma lista de dicionários
        print("Total de registros carregados:", len(records))
        print("Primeiros registros carregados:", records[:5])  # Log os primeiros 5 registros
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps(f"Erro ao carregar JSON: {str(e)}")
        }

    # Remover duplicatas com base no campo 'idUser'
    seen_ids = set()
    unique_records = []
    for record in records:
        if not isinstance(record, dict):
            print("Erro: registro não é um dicionário:", record)
            continue
        # Usando 'idUser' para validar duplicatas
        user_id = record.get("idUser")  # Usando o campo 'idUser'
        if not user_id:
            print(f"Erro: Campo 'idUser' não encontrado no registro: {record}")
            continue
        if user_id not in seen_ids:
            seen_ids.add(user_id)
            unique_records.append(record)

    print(f"Total de registros após remoção de duplicatas: {len(unique_records)}")

    # Atualiza os tipos de dados conforme o schema
    processed_records = []
    for record in unique_records:
        try:
            processed_record = cast_column_types(record)
            if not isinstance(processed_record, dict):
                print("Erro: registro processado não é um dicionário:", processed_record)
                continue
            processed_records.append(processed_record)
        except Exception as e:
            print("Erro ao processar registro:", record, e)

    print(f"Total de registros processados: {len(processed_records)}")

    # Conecta ao MongoDB
    collection = connect_to_mongo()

    # Insere os dados em blocos
    batch_size = 10000
    for i in range(0, len(processed_records), batch_size):
        batch = processed_records[i:i + batch_size]
        if batch:
            print(f"Inserindo {len(batch)} documentos no MongoDB.")
            try:
                collection.insert_many(batch)
                print(f"{len(batch)} documentos inseridos com sucesso no MongoDB.")
            except BulkWriteError as bwe:
                return {
                    "statusCode": 500,
                    "body": json.dumps(f"Erro ao inserir no MongoDB: {bwe.details}")
                }
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps(f"Erro geral ao inserir no MongoDB: {str(e)}")
                }

    return {
        "statusCode": 200,
        "body": json.dumps(f"Processamento do arquivo {object_key} concluído com sucesso.")
    }
