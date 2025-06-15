# simple_aggregator.py
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC_RAW = 'finra-ats-raw'
KAFKA_TOPIC_AGGREGATED = 'dark-pool-heatmap-data'

WINDOW_SIZE_MINUTES = 5

def get_window_start(timestamp, window_size_minutes):
    dt_object = timestamp
    total_seconds = int(dt_object.timestamp())
    window_seconds = window_size_minutes * 60
    window_start_seconds = (total_seconds // window_seconds) * window_seconds
    return datetime.fromtimestamp(window_start_seconds)

def consume_and_aggregate():
    consumer = KafkaConsumer(
        KAFKA_TOPIC_RAW,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='simple-aggregator-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all'
    )

    print(f"Simple Aggregator: Consumer started for topic: {KAFKA_TOPIC_RAW}")
    print(f"Simple Aggregator: Producer configured for topic: {KAFKA_TOPIC_AGGREGATED}")

    current_windows = defaultdict(lambda: {'window_start': None, 'total_trade_value': 0.0,
                                           'total_quantity': 0, 'num_trades': 0, 'sum_price': 0.0,
                                           'latitude': None, 'longitude': None})

    try:
        for message in consumer:
            trade_data = message.value
            trade_timestamp = datetime.fromisoformat(trade_data['timestamp'])

            window_start_dt = get_window_start(trade_timestamp, WINDOW_SIZE_MINUTES)
            window_end_dt = window_start_dt + timedelta(minutes=WINDOW_SIZE_MINUTES)

            key = (trade_data['symbol'], trade_data['venue'])
            window_state = current_windows[key]

            if window_state['window_start'] is None:
                window_state['window_start'] = window_start_dt
                window_state['latitude'] = trade_data['latitude']
                window_state['longitude'] = trade_data['longitude']
            elif window_start_dt > window_state['window_start']:
                if window_state['num_trades'] > 0:
                    aggregated_output = {
                        'window_start': window_state['window_start'].isoformat(),
                        'window_end': (window_state['window_start'] + timedelta(minutes=WINDOW_SIZE_MINUTES)).isoformat(),
                        'venue': key[1],
                        'symbol': key[0],
                        'total_trade_value': window_state['total_trade_value'],
                        'total_quantity': window_state['total_quantity'],
                        'num_trades': window_state['num_trades'],
                        'avg_price': window_state['sum_price'] / window_state['num_trades'] if window_state['num_trades'] > 0 else 0.0,
                        'latitude': window_state['latitude'],
                        'longitude': window_state['longitude']
                    }
                    producer.send(KAFKA_TOPIC_AGGREGATED, key=f"{key[0]}-{key[1]}".encode('utf-8'), value=aggregated_output)

                window_state['window_start'] = window_start_dt
                window_state['total_trade_value'] = 0.0
                window_state['total_quantity'] = 0
                window_state['num_trades'] = 0
                window_state['sum_price'] = 0.0
                window_state['latitude'] = trade_data['latitude']
                window_state['longitude'] = trade_data['longitude']

            window_state['total_trade_value'] += trade_data['trade_value']
            window_state['total_quantity'] += trade_data['quantity']
            window_state['num_trades'] += 1
            window_state['sum_price'] += trade_data['price']

    except Exception as e:
        print(f"Error in Simple Aggregator: {e}")
    finally:
        producer.flush()
        producer.close()
        consumer.close()
        print("Simple Aggregator: Consumer and Producer closed.")

if __name__ == '__main__':
    print("Starting Simple Aggregator...")
    consume_and_aggregate()
    print("Simple Aggregator finished.")
