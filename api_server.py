# api_server.py
from flask import Flask, jsonify
from flask_cors import CORS
from kafka import KafkaConsumer
import json
import threading
import time
from collections import deque
import os 


FLASK_APP_NAME = 'dark_pool_api_inmemory'
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC_AGGREGATED = 'dark-pool-heatmap-data'
MAX_RECORDS_IN_MEMORY = 10000 
HEATMAP_JSON_OUTPUT_PATH = 'heatmap_data.json' 
JSON_DUMP_INTERVAL_SECONDS = 10 

app = Flask(FLASK_APP_NAME)
CORS(app)

latest_heatmap_data = deque(maxlen=MAX_RECORDS_IN_MEMORY)

def save_data_to_json():
    """Saves the current in-memory data (deque) to a JSON file."""
    try:
        
        data_to_save = list(latest_heatmap_data)
        with open(HEATMAP_JSON_OUTPUT_PATH, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Saved {len(data_to_save)} records to {HEATMAP_JSON_OUTPUT_PATH}")
    except Exception as e:
        print(f"Error saving data to JSON file: {e}")

def consume_from_kafka_and_cache():
    """
    Kafka consumer thread function. It consumes messages from the aggregated topic
    and updates the in-memory cache (`latest_heatmap_data`).
    It also periodically triggers saving data to a JSON file.
    """
    consumer = KafkaConsumer(
        KAFKA_TOPIC_AGGREGATED,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='keplergl-data-loader',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print(f"Kafka consumer started for topic: {KAFKA_TOPIC_AGGREGATED}")

    last_dump_time = time.time()

    try:
        for message in consumer:
            data = message.value
            
            if 'window_start' in data and not isinstance(data['window_start'], str):
                data['window_start'] = data['window_start'].isoformat()
            if 'window_end' in data and not isinstance(data['window_end'], str):
                data['window_end'] = data['window_end'].isoformat()
            
            latest_heatmap_data.append(data)

            
            if time.time() - last_dump_time > JSON_DUMP_INTERVAL_SECONDS:
                save_data_to_json()
                last_dump_time = time.time()

    except Exception as e:
        print(f"Error in Kafka consumer thread: {e}")
    finally:
        consumer.close()
        
        if len(latest_heatmap_data) > 0:
            save_data_to_json()

@app.route('/api/heatmap_data', methods=['GET'])
def get_heatmap_data():
    """API endpoint that returns the current aggregated heatmap data from the in-memory cache."""
    return jsonify(list(latest_heatmap_data))

@app.route('/')
def index():
    return "API for Dark Pool Liquidity Heatmap data. Access /api/heatmap_data"

if __name__ == '__main__':
    
    kafka_thread = threading.Thread(target=consume_from_kafka_and_cache)
    kafka_thread.daemon = True 
    kafka_thread.start()


    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False) 

Update on 2025-06-18T17:33:01
Update on 2025-06-15T10:27:04
Update on 2025-06-13T18:16:56
Update on 2025-06-13T12:40:46
Update on 2025-06-13T13:11:35
Update on 2025-06-12T17:37:17
Update on 2025-06-12T18:26:48
Update on 2025-06-11T11:31:04
Update on 2025-06-11T18:50:53
Update on 2025-06-10T16:18:43
Update on 2025-06-10T17:23:50