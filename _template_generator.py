import pathlib, os, urllib.parse

def generate_template(script_directory, current_directory, file_name,
	original_thumbnail, uploader, profile_image, blurred_thumbnail, 
	platform, square_corners, uploader_font_size):

	# get the working directory, then create a new directory to contain our new templates
	new_template_directory = current_directory + '/' + file_name + '-template'
	os.mkdir(pathlib.Path(new_template_directory))

	# also create a directory to contain the temp clones of our templates
	# the 'html2image' lib makes temp copies of our files,
	# this is necessary so the files aren't attempted to copy to the same directory
	os.mkdir(pathlib.Path(new_template_directory + '/temp'))

	# create the new html and css templates
	generate_html(script_directory, new_template_directory, original_thumbnail, uploader, platform, square_corners)
	generate_css(script_directory, new_template_directory, profile_image, blurred_thumbnail, uploader_font_size)

def generate_html(script_directory, current_directory, original_thumbnail,
	uploader, platform, square_corners):

	# load in the html template
	with open(script_directory + '/template/index.html', 'r') as html_template:
		html = html_template.read()

	# replace the thumbnail URL and uploader name in the html
	html = html.replace('[original_thumbnail]', urllib.parse.quote(original_thumbnail))
	html = html.replace('[uploader]', uploader)
	html = html.replace('[platform]', platform.lower())
	html = html.replace('[platform_image]', get_platform_logo_extension(script_directory, platform))
	html = html.replace('[square_corners]', str(square_corners).lower())

	# create a new html template and write our changes
	with open(current_directory + '/index.html', 'w') as new_html_template:
		new_html_template.write(html)

def generate_css(script_directory, current_directory, profile_image,
	blurred_thumbnail, uploader_font_size):

	# load in the css template
	with open(script_directory + '/template/style.css', 'r') as css_template:
		css = css_template.read()

	# get the path for the profile image
	profile_image_path = script_directory + "/profile-images/" + urllib.parse.quote(profile_image)

	# replace the image URLs in the css
	css = css.replace('[profile_image]', profile_image_path)
	css = css.replace('[blurred_thumbnail]', urllib.parse.quote(blurred_thumbnail))
	css = css.replace('[font_file]', script_directory + '/template/assets/circular-medium.ttf')
	css = css.replace('[uploader_font_size]', str(uploader_font_size))

	# create a new css template and write our changes
	with open(current_directory + '/style.css', 'w') as new_css_template:
		new_css_template.write(css)

def get_platform_logo_extension(script_directory, platform):
	if (os.path.isfile(script_directory + '/template/assets/platform-logos/' + platform.lower() + '.svg')):
		return script_directory + '/template/assets/platform-logos/' + platform.lower() + '.svg'
	else:
		return script_directory + '/template/assets/platform-logos/' + platform.lower() + '.png'