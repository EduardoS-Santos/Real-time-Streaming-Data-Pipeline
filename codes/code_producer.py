#Producer assinaturas
from kafka import KafkaProducer
from faker import Faker
import random
import json
from datetime import datetime, timedelta

# Configuração do Faker e Kafka
fake = Faker()
producer = KafkaProducer(
    bootstrap_servers='127.0.0.1:9092',  # Endereço do broker Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serializa mensagens como JSON
)

# Nome do tópico
topic = 'assinaturas'

# Gerar mensagens
def generate_message():
    # Campos fixos com valores simulados
    return {
        "idUser": fake.uuid4(),  # Gera um ID único
        "StatusAssinatura": random.choice(["Renovada", "Cancelada"]),
        "Nome": fake.name(),
        "idade": random.randint(18, 80),
        "TipoAssinatura": random.choice(["basic", "standard", "premium"]),
        "UltimoPagamento": fake.date_between(start_date="-1y", end_date="today").strftime('%Y-%m-%d'),
        "pais": fake.country(),
        "genero": random.choice(["Masculino", "Feminino", "Outro"]),
        "DuracaoAssinatura": random.choice(["mensal", "trimestral", "anual"]),
        "HorasAssistidas": random.randint(0, 500),
        "dispositivoConectados": random.choice(["Smartphone", "Laptop", "Smart TV", "Tablet"]),
        "DataDeAdesao": fake.date_between(start_date="-2y", end_date="today").strftime('%Y-%m-%d')
    }

# Enviar mensagens
try:
    for _ in range(100000):  # Enviar 100000 mensagens de exemplo
        message = generate_message()
        producer.send(topic, value=message)
        print(f"Mensagem enviada: {message}")
    producer.flush()  # Garante envio de todas as mensagens
except Exception as e:
    print(f"Erro ao enviar mensagens: {e}")
finally:
    producer.close()