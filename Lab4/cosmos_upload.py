import os
import pandas as pd
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
import uuid

# Завантаження змінних з .env
load_dotenv()

#  Налаштування підключення
endpoint = os.getenv("COSMOS_URI")
key = os.getenv("COSMOS_KEY")
database_name = "FlightsDB"
container_name = "JanFlights"

# Ініціалізація клієнта
client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# Читання підготовленого файлу
df = pd.read_csv("flights_to_cosmos.csv")

print(f"Починаємо завантаження {len(df)} записів...")

#  Завантаження даних
for index, row in df.iterrows():
    # Перетворення рядку датафрейму в словник (JSON)
    item = row.to_dict()
    
    # Cosmos DB обов'язково потребує унікальне поле 'id' (рядок)
    item['id'] = str(uuid.uuid4())
    
    # Виправляємо NaN значення (якщо є)
    item = {k: (None if pd.isna(v) else v) for k, v in item.items()}

    try:
        container.create_item(body=item)
        if index % 500 == 0:
            print(f"Оброблено {index} записів...")
    except Exception as e:
        print(f"Помилка на рядку {index}: {e}")

print("Завантаження завершено успішно!")