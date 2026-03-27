import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO # To treat bytes as a file

# 1. Get the Metadata (JSON) [data about data] 
# NASA requires a key; 'DEMO_KEY' is the public one for testing.
metadata_req = requests.get('https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY')
data = metadata_req.json() #from the metadata,
image_url = data.get('url') #get The actual link to the image

# 2. Get the Actual Image with the image link
image_req = requests.get(image_url)

# BytesIO(image_req.content) makes the raw data "look" like a file to Pillow
img = Image.open(BytesIO(image_req.content))

# 3. Setup Drawing
draw = ImageDraw.Draw(img)
# Fallback: If EXIF is empty, use the NASA Title
watermark_text = data.get('title', "Shadow Army Intel")

# Note: "arial.ttf" might not be found on all systems (especially Linux/Mac). 
# If it fails, use ImageFont.load_default()
try:
    font = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()

# 4. Calculation for Positioning
# We use textbbox to find the "Box" the text takes up
bbox = draw.textbbox((0, 0), watermark_text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

image_width, image_height = img.size
position = (image_width - text_width - 20, image_height - text_height - 20)

# 5. Execute & Save
draw.text(position, watermark_text, font=font, fill=(255, 255, 255))
img.save("nasa_scout_report.jpg")
img.show()