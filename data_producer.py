# data_producer.py
import pandas as pd
from kafka import KafkaProducer
import json
import time
from datetime import datetime

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC_RAW = 'finra-ats-raw'
CSV_FILE_PATH = 'synthetic_darkpool_heavy.csv'

VENUE_COORDINATES = {
    'DARK1': {'latitude': 34.0522, 'longitude': -118.2437},
    'DARK2': {'latitude': 40.7128, 'longitude': -74.0060},
    'LIT': {'latitude': 41.8781, 'longitude': -87.6298}
}

def produce_data_to_kafka(file_path, broker, topic):
    producer = KafkaProducer(
        bootstrap_servers=[broker],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all'
    )
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} records from {file_path}")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['trade_value'] = df['price'] * df['quantity']
        df['latitude'] = df['venue'].map(lambda x: VENUE_COORDINATES.get(x, {}).get('latitude'))
        df['longitude'] = df['venue'].map(lambda x: VENUE_COORDINATES.get(x, {}).get('longitude'))
        df = df.sort_values(by='timestamp').reset_index(drop=True)

        print(f"Starting to produce messages to topic: {topic}")
        # Loop multiple times for more data
        NUM_LOOPS = 500 # Increased loops for more data
        total_messages_expected = len(df) * NUM_LOOPS

        for loop_num in range(NUM_LOOPS):
            for index, row in df.iterrows():
                message = {
                    'timestamp': row['timestamp'].isoformat(),
                    'symbol': row['symbol'],
                    'price': row['price'],
                    'quantity': row['quantity'],
                    'venue': row['venue'],
                    'is_spoof': row['is_spoof'],
                    'algo_fingerprint': row['algo_fingerprint'],
                    'order_type': row['order_type'],
                    'order_id': row['order_id'],
                    'side': row['side'],
                    'trade_value': row['trade_value'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude']
                }
                producer.send(topic, value=message)
                if ((loop_num * len(df) + index + 1) % 1000 == 0) or ((loop_num * len(df) + index + 1) == total_messages_expected):
                    print(f"Produced {loop_num * len(df) + index + 1} messages...")
                time.sleep(0.0001) # Reduced delay for faster generation

        producer.flush()
        print(f"Finished producing {total_messages_expected} messages to topic: {topic}")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {file_path}.")
    except Exception as e:
        print(f"An error occurred during data production: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    produce_data_to_kafka(CSV_FILE_PATH, KAFKA_BROKER, KAFKA_TOPIC_RAW)
