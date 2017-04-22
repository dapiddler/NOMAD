from flask import Flask
from flask import request
from flask import render_template
import config
from datetime import datetime




app = Flask(__name__)

@app.route("/")
def main():

	print("config details")

	print(config.LOCAL_DNS_PORT)

	return str(config.LOCAL_DNS_PORT)

@app.route("/nomad/")
def nomad():
	ip = config.LOCAL_DNS_HOST
	return render_template('index.html',ip=ip)

@app.route('/_stuff', methods=['GET'])
def stuff():
	if request.method == 'GET':
		test = str(datetime.now())
    	return test


if __name__ == "__main__":
    app.run(debug=True, host=str(config.LOCAL_DNS_HOST))