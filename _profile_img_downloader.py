import requests, json, shutil, urllib.parse
from pathlib import Path
def get_profile_image(script_directory, current_directory, uploader, platform, upload_url):
	# check if the profile pic already exists:
	if not Path(current_directory + "/profile-images/" + urllib.parse.quote(uploader) + " [" + platform + "].jpg").is_file():

		# get the webpage via requests lib
		page = requests.get(upload_url)

		# read in the response text
		html_str = page.text

		match platform:
			case 'YouTube':
				# trim the response
				html_str = html_str[html_str.index('{"videoOwnerRenderer"'):]
				html_str = html_str[:html_str.index('}]},')] + '}]' + '}'*3

				# parse the html string as json
				profile_image_data = json.loads(html_str)

				# get the profile image url from the dict
				profile_image_url = profile_image_data['videoOwnerRenderer']['thumbnail']['thumbnails'][2]['url']

				# convert to the high resolution image url
				high_res_profile_image_url = profile_image_url.replace('s176', 's1024')

		# set the file name of the profile image
		profile_image_file_name = script_directory + '/profile-images/' + urllib.parse.quote(uploader) + " [" + platform + '].jpg'

		# download and save the profile image
		save_profile_image(high_res_profile_image_url, profile_image_file_name)

def save_profile_image(profile_image_url, file_name):
	profile_image_request_response = requests.get(profile_image_url, stream=True)

	# write the profile image data
	with open(file_name, 'wb') as profile_image:
		shutil.copyfileobj(profile_image_request_response.raw, profile_image)

	# close the response
	del profile_image_request_response
