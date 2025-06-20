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
Update on 2025-06-10T17:43:01
Update on 2025-06-09T17:38:42
Update on 2025-06-09T11:42:10
Update on 2025-06-08T11:24:49
Update on 2025-06-08T17:32:54
Update on 2025-06-08T17:10:24
Update on 2025-06-06T17:04:46
Update on 2025-06-05T14:41:07
Update on 2025-06-05T09:40:54
Update on 2025-06-03T12:07:28
Update on 2025-06-02T14:02:06
Update on 2025-06-02T09:34:20
Update on 2025-06-02T18:38:50
Update on 2025-06-01T11:06:30
Update on 2025-06-01T09:21:19
Update on 2025-05-31T16:33:57
Update on 2025-05-31T09:29:35
Update on 2025-05-30T17:57:52
Update on 2025-05-30T16:15:34
Update on 2025-05-28T12:48:46
Update on 2025-05-28T17:16:08
Update on 2025-05-28T11:46:42
Update on 2025-05-27T16:43:36
Update on 2025-05-26T14:26:35
Update on 2025-05-26T12:41:14
Update on 2025-05-26T12:50:08
Update on 2025-05-25T09:21:20
Update on 2025-05-25T18:53:37
Update on 2025-05-24T18:33:32
Update on 2025-05-23T10:28:38
Update on 2025-05-23T16:11:33
Update on 2025-05-23T12:05:11
Update on 2025-05-22T14:25:16
Update on 2025-05-20T09:20:27
Update on 2025-05-20T12:29:30