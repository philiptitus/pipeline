import os
import threading
from subprocess import Popen
from flask_socketio import SocketIO
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pika

# Initialize Flask app and SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# RabbitMQ setup and consumer
def send_message(queue, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(exchange='', routing_key=queue, body=message, properties=pika.BasicProperties(delivery_mode=2))
    connection.close()

def rabbitmq_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='ci_cd', durable=True)

    def callback(ch, method, properties, body):
        socketio.emit('ci_cd_update', {'message': body.decode()})

    channel.basic_consume(queue='ci_cd', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# CI/CD logic
def trigger_build(repo_url, branch='main'):
    import subprocess
    import shutil
    import requests

    def find_artifact(directory):
        for file in os.listdir(directory):
            if file.endswith('.whl'):
                return os.path.join(directory, file)
        return None

    def deploy_artifact(artifact_path):
        url = "http://pipelinebyphil.pythonanywhere.com/upload"
        with open(artifact_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            send_message('ci_cd', "Deployment successful.")
        else:
            send_message('ci_cd', f"Deployment failed with status code {response.status_code}")

    try:
        send_message('ci_cd', 'Build started.. Please Wait ...')

        if os.path.exists('repo'):
            shutil.rmtree('repo')

        subprocess.run(['git', 'clone', repo_url, 'repo'], check=True)
        subprocess.run(['git', 'checkout', branch], cwd='repo', check=True)

        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd='repo', check=True)
        subprocess.run(['pip', 'install', 'wheel'], check=True)

        subprocess.run(['python', 'setup.py', 'build'], cwd='repo', check=True)

        test_result = subprocess.run(['python', '-m', 'unittest', 'discover'], cwd='repo', check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        test_message = "Carrying Out Tests For You ...."
        send_message('ci_cd', test_message)

        if test_result.returncode == 0:
            test_message = "All tests passed successfully."
            send_message('ci_cd', test_message)
        else:
            test_message = f"Some tests failed:\n{test_result.stdout.decode()}\n{test_result.stderr.decode()}"
            send_message('ci_cd', test_message)

        bdist_result = subprocess.run(['python', 'setup.py', 'bdist_wheel'], cwd='repo', check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if bdist_result.returncode == 0:
            artifact_path = find_artifact('repo/dist/')
            if artifact_path:
                deploy_artifact(artifact_path)
                success_message = "All builds and tests completed successfully."
                success_message2 = "Everything Was Deployed Succesffuly😍."

                send_message('ci_cd', success_message)
                send_message('ci_cd', success_message2)

                return {"message": success_message, "test_message": test_message}
            else:
                error_message = "Build artifact not found."
                send_message('ci_cd', error_message)
                return {"message": error_message, "test_message": test_message}
        else:
            error_message = f"An error occurred during the build process:\n{bdist_result.stdout.decode()}\n{bdist_result.stderr.decode()}"
            send_message('ci_cd', error_message)
            return {"message": error_message, "test_message": test_message}
    except subprocess.CalledProcessError as e:
        error_message = f"An error occurred during the build process: {e}"
        send_message('ci_cd', error_message)
        return {"message": error_message, "test_message": ""}
    except Exception as e:
        error_message = f"An error occurred: {e}"
        send_message('ci_cd', error_message)
        return {"message": error_message, "test_message": ""}


@app.route("/") 
def hello(): 
    # message = "Hello, World"
    return render_template('dashboard.html') 


# Flask endpoint
@app.route('/trigger_build', methods=['POST'])
def trigger_build_endpoint():
    data = request.json
    repo_url = data.get('repo_url')
    branch = data.get('branch', 'main')
    result = trigger_build(repo_url, branch)
    return jsonify(result), 200

def run_flask():
    socketio.run(app, host='0.0.0.0', port=8080)

def run_frontend():
    os.system('python -m http.server 8000')

if __name__ == "__main__":
    consumer_thread = threading.Thread(target=rabbitmq_consumer)
    consumer_thread.start()

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    frontend_thread = threading.Thread(target=run_frontend)
    frontend_thread.start()

    flask_thread.join()
    frontend_thread.join()
    consumer_thread.join()
