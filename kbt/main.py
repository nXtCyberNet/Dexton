from flask import Flask, request, jsonify
from kubernetes import client, config
import redis
import logging
import random
import string

# Function to generate a random ID
def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Connect to Redis
try:
    r = redis.StrictRedis(host='34.29.40.160', port=6379, db=0)
except Exception as e:
    app.logger.error(f"Error connecting to Redis: {str(e)}")

# Load Kubernetes configuration
try:
    config.load_incluster_config()
except Exception as e:
    app.logger.error(f"Error loading Kubernetes config: {str(e)}")

v1 = client.CoreV1Api()

NAMESPACE = 'default'

# Function to add pod to a user
def add_pod_to_user(username, pod_name):
    try:
        r.sadd(username, pod_name)
    except Exception as e:
        app.logger.error(f"Error adding pod to user: {str(e)}")

# Function to get pods for a user
def get_pods_for_user(username):
    try:
        return r.smembers(username)
    except Exception as e:
        app.logger.error(f"Error getting pods for user: {str(e)}")
        return set()

@app.route('/start_pod', methods=['POST'])
def start_pod():
    data = request.json
    username = data.get('USERNAME')
    api_key = data.get('API_KEY')
    api_secret = data.get('API_SECRET')
    discord_key = data.get('DISCORD_API_KEY')
    percentage = data.get('CAPITAL_PERCENTAGE')

    if not username:
        app.logger.error('username is required')
        return jsonify({'error': 'username is required'}), 400

    try:
        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {'name': f"{username}-{id_generator()}"},
            'spec': {
                'containers': [
                    {
                        'name': 'container',
                        'image': 'asia-south2-docker.pkg.dev/centered-memory-446823-p9/dexton/stockbot:latest',
                        'imagePullPolicy': 'Always',
                        'env': [
                            {'name': 'API_KEY', 'value': api_key},
                            {'name': 'API_SECRET', 'value': api_secret},
                            {'name': 'DISCORD_API_KEY', 'value': discord_key},
                            {'name': 'CAPITAL_PERCENTAGE', 'value': str(percentage)}
                        ]
                    }
                ]
            }
        }
       
        pod_name = pod_manifest['metadata']['name']
        v1.create_namespaced_pod(namespace=NAMESPACE, body=pod_manifest)
        add_pod_to_user(username, pod_name)
        
        app.logger.info(f"Pod started with name: {pod_name}")
        return jsonify({'message': 'Pod started', 'pod_name': pod_name}), 200
    except Exception as e:
        app.logger.error(f"Error starting pod: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop_pod', methods=['POST'])
def stop_pod():
    data = request.json
    username = data.get('USERNAME')
    pod_names = get_pods_for_user(username)

    if not pod_names:
        app.logger.error('Pod name is required')
        return jsonify({'error': 'Pod name is required'}), 400

    try:
        for pod_name in pod_names:
            pod_name = pod_name.decode('utf-8')
            v1.delete_namespaced_pod(name=pod_name, namespace=NAMESPACE)
            app.logger.info(f"Pod stopped with name: {pod_name}")
            result = r.delete(username)
            
        return jsonify({'message': 'Pods stopped', 'pod_names': [pod_name.decode('utf-8') for pod_name in pod_names]}), 200
    except Exception as e:
        app.logger.error(f"Error stopping pod: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/list_pods', methods=['GET'])
def list_pods():
    try:
        pods = v1.list_namespaced_pod(namespace=NAMESPACE)
        pod_list = []
        for pod in pods.items:
            pod_list.append({
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'status': pod.status.phase,
                'node': pod.spec.node_name,
                'start_time': pod.status.start_time
            })
        return jsonify(pod_list), 200
    except Exception as e:
        app.logger.error(f"Error listing pods: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)
