import os, json, datetime

def format_json(current_directory, file_name, platform, json_file):
	# set a var to check if json gets formatted
	is_json_formatted = False

	# load in the json file
	with open(json_file, 'r', encoding='utf-8') as file:
		json_data = json.load(file)

	match platform:
		case 'YouTube':
			# format the json
			formatted_json = {
				"original_title": json_data["title"],
				"title": "",
				"upload_url": json_data["webpage_url"],
				"uploader": json_data["uploader"],
				"uploader_url": json_data["channel_url"],
				"tags": [],
				"description": "",
				"original_description": "",
				"upload_date": json_data["upload_date"][:4]+"-"+json_data["upload_date"][4:6]+"-"+json_data["upload_date"][6:],
				"archive_date": str(datetime.date.today()),
				"platform": "YouTube"
			}

			# get tags if present
			if 'tags' in json_data:
				formatted_json['tags'] = json_data['tags']

			# get description if present
			if 'description' in json_data:
				formatted_json['original_description'] = json_data['description']

			# set the var to true
			is_json_formatted = True

	# if any json was formatted,
	if is_json_formatted == True:

		# then write the new json data
		with open(current_directory + '/' + file_name + '.json', 'w', encoding='utf-8') as file:
			json.dump(formatted_json, file, ensure_ascii=False, indent=4)

		# remove the old json file
		os.remove(json_file)