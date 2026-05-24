import os
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import pandas as pd

# Завантажуємо змінні з .env
load_dotenv()

#  Налаштування підключення
endpoint = os.getenv("COSMOS_URI")
key = os.getenv("COSMOS_KEY")
database_name = "FlightsDB"
container_name = "JanFlights"

client = CosmosClient(endpoint, key)
container = client.get_database_client(database_name).get_container_client(container_name)

#  Запит: всі авіалінії та їх запізнення
query = "SELECT c.airline, c.departure_delay FROM c WHERE IS_NUMBER(c.departure_delay)"

print("Запитуємо дані з Cosmos DB...")

# Отримуємо дані
items = list(container.query_items(query=query, enable_cross_partition_query=True))
print(f"Отримано {len(items)} записів. Починаємо розрахунок...")

# Використовуємо Pandas для швидкої агрегації (як справжні Data Scientists)
df = pd.DataFrame(items)
# Групуємо по авіалінії та рахуємо середнє
result = df.groupby('airline')['departure_delay'].mean().round(3).reset_index()

# Сортуємо: найбільші запізнення зверху
top_10 = result.sort_values(by='departure_delay', ascending=False).head(10)

# Скидаємо індекси та робимо їх від 1 до 10
top_10 = top_10.reset_index(drop=True)
top_10.index = top_10.index + 1

print("\nТоп-10 авіаліній з найбільшим середнім запізненням (31 січня):")
print("-" * 60)
print(top_10.to_string(header=True, index=True))
