import _json_formatter, _profile_img_downloader, _thumbnail_generator, os, pathlib, urllib.parse, json
from yt_dlp import YoutubeDL

download_youtube_video = True

# if downloading a new video from YouTube,
if download_youtube_video == True:

	# get/set the initial youtube video url
	upload_url = 'https://vimeo.com/26427650?embedded=true&source=vimeo_logo&owner=905661'
	uploader = ''
	profile_image = ''
	original_thumbnail = ''
	platform = 'YouTube'
	square_corners = False
	file_name = ''

# if fixing an old thumbnail or making a custom video,
else:
	upload_url = ''
	uploader = 'Jack Rhysider'
	profile_image = 'Jack%20Rhysider [YouTube].jpeg'
	original_thumbnail = '/users/matthewnau/Downloads/image.jpeg'
	platform = 'Spotify'
	square_corners = False
	file_name = 'watermark'

# get the current directory
current_directory = str(pathlib.Path().resolve())

# set the output directory for all files (defult is current_directory)
output_directory = current_directory

# set yt-dlp's options
ydl_opts = {
	'writethumbnail': True,
	'writeinfojson': True,
	'writesubtitles': True,
	'writeautomaticsub': True,
	'subtitlesformat': 'srt',
	'subtitleslangs': ['en'],
	'outtmpl': '%(title)s.%(ext)s',
	'nocheckcertificate': True,
	'restrictfilenames': True,
	'merge_output_format': 'mkv',
    'postprocessors': [{
        'key': 'FFmpegSubtitlesConvertor',
        'format': 'srt'
    }, {
    	'key': 'FFmpegEmbedSubtitle'
	}]
}

# download the video
if upload_url != '':
	with YoutubeDL(ydl_opts) as ydl:
		ydl.download([upload_url])

	# set the json file to the most recent (just downloaded)
	json_file = os.popen("ls -t '" + output_directory + "'/*.json | head -1").read().strip()

	# extract the file name without its extension
	file_name = json_file[::-1][10:][::-1]
	file_name = file_name[::-1][:file_name[::-1].index('/')][::-1]

	# format the json file
	_json_formatter.format_json(
		output_directory,
		file_name,
		"YouTube",
		json_file
	)

	# load in the new json file
	with open(output_directory + '/' + file_name + '.json', 'r', encoding='utf-8') as file:
		json_data = json.load(file)

# if no profile pic has been set,
if profile_image == '':

	# then download the uploader profile image
	_profile_img_downloader.get_profile_image(
		str(pathlib.Path(__file__).parent.resolve()),
		output_directory,
		json_data['uploader'],
		json_data['platform'],
		upload_url
	)
	# set the new profile image
	profile_image = urllib.parse.quote(json_data['uploader']) + ' [' + platform + '].jpg'

# if no thumbnail has been set,
if original_thumbnail == '':
	original_thumbnail = output_directory + '/' + file_name + '.webp'

# if no platform has been set,
if platform == '':
	platform = json_data['platform']

# if no uploader has been set,
if uploader == '':
	uploader = json_data['uploader']

# set the initial validation to false
is_validated = False
render_attempts = 0
uploader_font_size = 2.3

# generate and re-generate a thumbnail until it passes validation
while not is_validated:

	# increase the counter
	render_attempts += 1

	# log the current thumbnail render attempt
	print("generating thumbnail: attempt " + str(render_attempts) + ". Using uploader font size: " + str(uploader_font_size) + "rem")

	# create the new thumbnail
	_thumbnail_generator.generate_thumbnail(
		output_directory, #output directory
		file_name, #file name
		original_thumbnail, #original thumbnail
		uploader, #uploader name
		profile_image, #profile image
		platform, #platform
		square_corners, #square corners
		uploader_font_size #uploader font size
	)

	# update the is_validated to the result of the validation
	validation_output = _thumbnail_generator.validate_thumbnail(
		output_directory, #output directory
		file_name #file name
	)

	# if uploader name is cut off (too large to fit), decrease font size
	if not validation_output["has_min_font_size"]:
		uploader_font_size = round(uploader_font_size - 0.1, 2)

	# if all tests pass, update is_validated
	if not any(value == False for value in validation_output.values()):
		is_validated = True

# print a success message when pipeline finishes
if is_validated:
	print("Thumbnail created successfully after " + str(render_attempts) + " attempt(s)!")
