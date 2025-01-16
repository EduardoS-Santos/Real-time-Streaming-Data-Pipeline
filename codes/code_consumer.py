import json
from kafka import KafkaConsumer
import boto3
from concurrent.futures import ThreadPoolExecutor

# Configuração do Kafka Consumer
consumer = KafkaConsumer(
    'assinaturas',  # Nome do tópico
    bootstrap_servers='127.0.0.1:9092',
    auto_offset_reset='latest',  # Lê mensagens mais recentes
    enable_auto_commit=False,  # Commit manual para controle
    group_id='consumer-group-1',  # Identificador do grupo
    value_deserializer=lambda x: x.decode('utf-8')  # Converte para string
)

# Configuração do S3
s3_client = boto3.client(
    's3',
    aws_access_key_id='sua_acess_key',
    aws_secret_access_key='sua_secret_key',
    region_name='sua_regiao'
)

# Nome do bucket e arquivo no S3
bucket_name = 'nome_do_bubket'
assinaturas_file_prefix = 'teste/assinaturas_batch_'

# Função para salvar dados no S3
def save_to_s3(batch_id, data):
    try:
        # Criar um arquivo exclusivo para cada batch (evita sobrescrever)
        s3_key = f"{assinaturas_file_prefix}{batch_id}.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(data, ensure_ascii=False)
        )
        print(f"{len(data)} registros salvos no S3: {s3_key}")
    except Exception as e:
        print(f"Erro ao salvar no S3 (batch {batch_id}): {e}")

# Processar mensagens em batch
def process_batch(batch_id, messages):
    try:
        # Converte as mensagens em JSON
        batch_data = [json.loads(msg.value) for msg in messages]
        save_to_s3(batch_id, batch_data)
    except Exception as e:
        print(f"Erro ao processar batch {batch_id}: {e}")

# Consumindo mensagens do Kafka
try:
    print("Aguardando mensagens no Kafka...")

    batch_size = 10000  # Processar em lotes de 10000 mensagens
    batch = []
    batch_id = 0
    executor = ThreadPoolExecutor(max_workers=4)  # Processar até 4 batches em paralelo

    for message in consumer:
        batch.append(message)

        # Quando atingir o tamanho do lote, processa
        if len(batch) >= batch_size:
            batch_id += 1
            executor.submit(process_batch, batch_id, batch)  # Envia o lote para processamento em thread separada
            batch = []  # Limpa o lote após o envio para processamento

        

    # Processar mensagens restantes no final
    if batch:
        batch_id += 1
        process_batch(batch_id, batch)

except KeyboardInterrupt:
    print("Consumo interrompido pelo usuário.")
finally:
    consumer.close()
    print("Consumer Kafka encerrado.")
