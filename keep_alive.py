from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ម៉ាក Seu កំពុងដំណើរការយ៉ាងរលូន ២៤/ម៉ោង!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()