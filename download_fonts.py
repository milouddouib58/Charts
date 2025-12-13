
import os
import urllib.request
import ssl

# Create directory
os.makedirs("assets/fonts", exist_ok=True)

# Fonts
fonts = {
    "assets/fonts/Amiri-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf",
    "assets/fonts/Amiri-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf"
}

# Context to ignore SSL errors if any
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for path, url in fonts.items():
    print(f"Downloading {path}...")
    try:
        with urllib.request.urlopen(url, context=ctx) as response, open(path, 'wb') as out_file:
            out_file.write(response.read())
        print("Success.")
    except Exception as e:
        print(f"Failed to download {path}: {e}")
