import json
import os
import urllib.request
from flask import Flask, request, redirect, jsonify, Response
from werkzeug.utils import secure_filename
from os import walk
import random
import collections


UPLOAD_FOLDER = 'documents'
app = Flask(__name__)
# app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

files = []
for (dir_path, dir_names, filenames) in walk(UPLOAD_FOLDER):
	files.extend(filenames)
	break


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/file-upload/', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message': 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message': 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		resp = jsonify({'message': 'File successfully uploaded'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp


@app.route('/file-list/', methods=['GET'])
def file_list():
	return jsonify({'uploaded files':files})


@app.route('/random-quote/', methods=['GET'])
def random_quote_generator():
	random_file = random.choice(files)
	file_path = os.path.join(UPLOAD_FOLDER, random_file)
	with open(file_path, 'r') as file:
		quotes = file.readlines()
		random_quote = random.choice(quotes)

	if request.headers['Content-type'] == 'text/plain':
		return Response(random_quote, mimetype='text/plain')

	elif request.headers['Content-type'] == 'application/json':
		print(request)
		return jsonify({'random quote':random_quote})

	elif request.headers['Content-type'] == 'application/xml':
		return Response(random_quote, mimetype='application/xml')

	else:
		return random_quote


@app.route('/', methods=['GET'])
def details():
	file_name = random.choice(files)
	file_path = os.path.join(UPLOAD_FOLDER, file_name)
	with open(file_path, 'r') as file:
		quotes = file.readlines()
		random_quote_index = random.choice(range(len(quotes)))
		# random_quote = random.choice(quotes)
		quote = quotes[random_quote_index]
	line_number = random_quote_index + 1
	frequent_letter = collections.Counter(quote.replace(' ', '')).most_common(1)
	return jsonify({'file name': file_name, 'line number': line_number, 'frequent letter': frequent_letter})


@app.route('/backward-quote/<filename>', methods=['GET'])
def backward_quote(filename):
	file_path = os.path.join(UPLOAD_FOLDER, filename)
	with open(file_path, 'r') as file:
		quotes = file.readlines()
	quote = random.choice(quotes)
	backward = quote[::-1]
	return backward


@app.route('/100longest-quotes/', methods=['GET'])
def longest_quotes_hundred():
	all_quotes = []
	for filename in files:
		file_path = os.path.join(UPLOAD_FOLDER, filename)
		with open(file_path, 'r') as file:
			quotes = file.readlines()
		all_quotes.extend(quotes)
	longest_quotes = sorted(all_quotes, key=len, reverse=True)
	return jsonify(longest_quotes[:100])


@app.route('/20quotes-one-file/<filename>', methods=['GET'])
def twenty_quotes_one_file(filename):
	file_path = os.path.join(UPLOAD_FOLDER, filename)
	with open(file_path, 'r') as file:
		quotes = file.readlines()
	longest_quotes = sorted(quotes, key=len, reverse=True)
	return jsonify(longest_quotes[:20])


if __name__ == "__main__":
	app.run(host='0.0.0.0')
