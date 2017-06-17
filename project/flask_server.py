"""
	Python back-end (flask server) of labelling tool.

	Project structure:
	- static/ contains `notes_photos/` and `scripts/`

	# NOTE:
	#
	# Remember to set the environment variable:
	# $ export FLASK_APP="flask_server.py"
	# Then run using:
	# $ flask run
	#
	#
	# DEVELOPMENT:
	# $ python3 render_js_css_template.py && flask run
	#
	#
"""

from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
import glob
import os
import json
import copy

app = Flask(__name__)
app.config.update(TEMPLATES_AUTO_RELOAD=True)

client = MongoClient()
db = client['labels_db'] # use existing database

def get_style_version(dir_path):

	considered_files = glob.glob(dir_path)
	considered_files = list(filter(lambda x : len(x.split('.'))==3, 
								   considered_files))

	fn = lambda x: int(x.split('.')[1])
	files = sorted(considered_files, key=fn)

	for f in files:

		first_part = f.split('.')[0].split('/')[-1]
		ext = f.split('.')[-1]

		if first_part == 'main'\
			and ext == 'js':
			
			version = f.split('.')[1]

	return int(version)


def insert_label_to_mongodb(data):
	db.labels_db.update({'img_path': data['img_path']}, data, upsert=True)


def remove_label_from_mongodb(data):
	result = db.labels_db.delete_many({'img_path': data['img_path']})

	return result.deleted_count

def get_label_from_mongodb(img_path):
	label = []

	try:
		label = db.labels_db.find({'img_path': img_path})[0]
		
		del label['_id'] # not json-friendly object
		print('Found label for img path {}'.format(img_path))

	except Exception as e:
		print('No label found for img_path {}'.format(img_path))

	return label

def get_dataset_info_from_mongodb():
	info_dict = {}

	# TODO(hichame): implement metrics functions
	# - num annotated images
	# - total num images

	return info_dict

@app.route('/get_label', methods=['POST'])
def get_label():
	try:
		label = get_label_from_mongodb(request.json['img_path'])

		return jsonify(dict(label))
	except Exception as e:
		print('ERROR: {}'.format(e))
		return jsonify(result=300)


@app.route('/get_label_count', methods=['POST'])
def get_dataset_info():
	try:
		ajax_dict = copy.copy(request.json)
		db_info = get_dataset_info_from_mongodb()
		print('Received labels of image {}'.format(label['img_path']))
		
		return jsonify(result=200)
	except Exception as e:
		print('ERROR: {}'.format(e))
		return jsonify(result=300)


@app.route('/insert_label', methods=['POST'])
def insert_label():
	try:
		label = copy.copy(request.json)
		insert_label_to_mongodb(label)
		print('Received labels of image {}'.format(label['img_path']))
		
		return jsonify(result=200)
	except Exception as e:
		print('ERROR: {}'.format(e))
		return jsonify(result=300)


@app.route('/reset', methods=['POST'])
def reset():
	try:
		label = copy.copy(request.json)
		
		num_delete = remove_label_from_mongodb(label)

		print('Removed {} records'.format(num_delete))
		return jsonify(result=200)
	
	except Exception as e:

		print('ERROR: {}'.format(e))
		return jsonify(result=300)

@app.route('/')
def index():
	style_version = get_style_version('static/scripts/js/*')
	
	main_js = 'static/scripts/js/main.{}.js'.format(style_version)
	main_css = 'static/scripts/css/style.{}.css'.format(style_version)
	
	print('Using scripts: {}, {}'.format(os.path.basename(main_css), 
								   os.path.basename(main_js)))

	return render_template('index.html', 
						   main_js=main_js,
						   main_css=main_css)