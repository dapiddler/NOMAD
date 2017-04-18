from flask import Flask
from flask import render_template
import config

app = Flask(__name__)

@app.route("/")
def main():

	print("config details")

	print(config.LOCAL_DNS_PORT)

	return str(config.LOCAL_DNS_PORT)

@app.route("/hello/")
def hello():
	return render_template('index.html')


if __name__ == "__main__":
    app.run(debug = True, host = str(config.LOCAL_DNS_HOST))