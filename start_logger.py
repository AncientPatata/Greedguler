import subprocess
# from threading import Thread
from flask import Flask, request
import json
import ngrok
from configs import *

app = Flask(__name__)
log_file_path = "server_log.json"

@app.route('/log', methods=['POST'])
def log_data():
    data = request.json
    with open(log_file_path, 'a') as log_file:
        json.dump(data, log_file)
        log_file.write('\n')
    return 'Logged', 200

def start_ngrok(port=5020):
    listener = ngrok.forward(port, authtoken=NGROK_AUTHTOKEN)
    print(f"Ngrok tunnel established at: {listener.url()}")
    with open('./azure_batch/ngrok_url.txt', 'w') as url_file:
        url_file.write(listener.url())
            
            

# def start_ngrok_async(port=5020):
#     ngrok_thread = Thread(target=start_ngrok, args=(port,))
#     ngrok_thread.start()

PORT = 5020

# with app.app_context():
#     start_ngrok_async(PORT)
    

if __name__ == "__main__":
    start_ngrok(port=PORT)
    app.run(debug=False, use_reloader=False, port=PORT)