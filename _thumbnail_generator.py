import _template_generator, pathlib, os, shutil, io
from html2image import Html2Image
from PIL import Image, ImageFilter, ImageCms

# return whether an image slice has more than one color
def has_multiple_colors(image_slice):
    colors_amount = image_slice.getcolors()

    # if there are not more than 255 colors,
    if colors_amount is not None:
        colors_amount = len(colors_amount)
    else:
        colors_amount = 2
    return colors_amount > 1

# return where the platform logo section ends (pixel index)
def get_platform_logo_end(attribution_banner_slice):
    platform_logo_last_pixel = 0
    current_pixel = -1
    while platform_logo_last_pixel == 0:
        current_pixel += 1
        if attribution_banner_slice.getpixel((current_pixel, 0)) != (0, 0, 0, 255):
            platform_logo_last_pixel = current_pixel - 1
    return platform_logo_last_pixel

# validates a thumbnail and returns a boolean of whether it rendered correctly
def validate_thumbnail(current_directory, file_name):

    # load the newly-rendered thumbnail
    thumbnail = Image.open(current_directory + '/' + file_name + '.png')

    # slice the attribution banner and locate where the platform logo section stops
    attribution_banner_slice = thumbnail.crop((0, 904, 1920, 905))

    # find where the platform logo section ends
    pf_logo_end = get_platform_logo_end(attribution_banner_slice)
    print("pf logo ends: " + str(pf_logo_end))

    # cut out certain UI components of the thumbnail to check for color
    profile_image_slice = thumbnail.crop((pf_logo_end+49, 936, pf_logo_end+161, 1048))
    uploader_slice = thumbnail.crop((pf_logo_end+161, 936, pf_logo_end+273, 1048))
    background_slice = thumbnail.crop((0, 792, 112, 904))
    min_font_size_slice = thumbnail.crop((1888, 936, 1920, 1048))
    
    # profile_image_slice.show()
    # uploader_slice.show()
    # background_slice.show()
    # min_font_size_slice.show()

    # evaluate if the profile image and uploader components are missing
    has_profile_image = has_multiple_colors(profile_image_slice)
    has_uploader = has_multiple_colors(uploader_slice)
    has_min_font_size = not has_multiple_colors(min_font_size_slice)

    # if the background is only 1 color, make sure it's not all white (missing)
    if not has_multiple_colors(background_slice):
        if background_slice.getcolors()[0][1] == (255, 255, 255, 255):
            has_background = False
        else:
            has_background = True
    else:
        has_background = True

    # close the opened image
    thumbnail.close()

    # log some output of the validation tests to the console
    print('has_profile_image:' + str(has_profile_image))
    print('has_uploader:' + str(has_uploader))
    print('has_background:' + str(has_background))
    print('has_min_font_size:' + str(has_min_font_size))

    # all components must be present to pass the validation test
    return {
        "has_profile_image": has_profile_image,
        "has_uploader": has_uploader,
        "has_background": has_background,
        "has_min_font_size": has_min_font_size
    }

def generate_thumbnail(current_directory, file_name, original_thumbnail, uploader, profile_image, platform, square_corners, uploader_font_size):

    # get the script and current directories
    script_directory = str(pathlib.Path(__file__).parent.resolve())

    # generate the blurred thumbnail path and file name
    blurred_thumbnail = current_directory + '/' + file_name + '-blurred_thumbnail.png'

    # blur the original thumbnail to use as a background image
    blur_thumbnail(
        current_directory, original_thumbnail,
        blurred_thumbnail
    )
    # generate the html/css templates with the coresponding image-urls and text
    _template_generator.generate_template(
        script_directory, current_directory, file_name,
        original_thumbnail, uploader, profile_image,
        blurred_thumbnail, platform, square_corners, uploader_font_size
    )
    # capture a headless screenshot of the template
    capture_screenshot(
        current_directory, file_name
    )

    # clean up and remove the temp files
    os.remove(blurred_thumbnail)
    shutil.rmtree(current_directory + '/' + file_name + '-template')

    # if pycache exists, remove it
    if pathlib.Path(current_directory + '/__pycache__').is_dir():
        shutil.rmtree(current_directory + '/__pycache__')

def blur_thumbnail(current_directory, original_thumbnail, blurred_thumbnail):

    # load the original thumbnail
    new_thumbnail = Image.open(original_thumbnail)

    # apply the blur effect to the original thumbnail
    new_thumbnail = new_thumbnail.filter(ImageFilter.GaussianBlur(100))

    # save the blurred thumbnail, then close it
    new_thumbnail.save(blurred_thumbnail)
    new_thumbnail.close()

def capture_screenshot(current_directory, file_name):

    # set the template and the template-temp directories
    new_template_directory = current_directory + '/' + file_name + '-template'
    temp_new_template_directory = new_template_directory + '/temp/'

    # initialize html2image
    hti = Html2Image(
        temp_path=temp_new_template_directory,
        output_path=current_directory,

        # specify the forced color profile (otherwise colors get washed out)
        custom_flags=['--force-color-profile=srgb']
    )

    # point to the path of the template files
    html = new_template_directory + '/index.html'
    css = new_template_directory + '/style.css'

    # set the filename of the new thumbnail
    new_file_name = file_name + '.png'

    # create the screenshot
    hti.screenshot(
        html_file=html,
        css_file=css,
        size=(1920,1080),
        save_as=new_file_name
    )

    # load the newly-rendered thumbnail/screenshot and get the size
    screenshot = Image.open(current_directory + '/' + new_file_name)
    width, height = screenshot.size

    # get the color profile settings
    iccProfile = screenshot.info.get('icc_profile')

    # set the dimensions to 1920x1080
    left = (width - 1920)/2
    top = (height - 1080)/2
    right = (width + 1920)/2
    bottom = (height + 1080)/2

    # Crop the center of the thumbnail, save and close the file
    screenshot = screenshot.crop((left, top, right, bottom))
    # screenshot.show()
    screenshot.save(current_directory + '/' + new_file_name, icc_profile=iccProfile)
    screenshot.close()