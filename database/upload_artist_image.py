import json
import boto3
import requests
import os
from urllib.parse import urlparse

BUCKET_NAME = "music-artist-images-79"

s3 = boto3.client("s3", region_name="us-east-1")

with open("../2026a2_songs.json", "r") as file:
    data = json.load(file)

songs = data["songs"]

uploaded_urls = set()

for song in songs:
    image_url = song["img_url"]

    if image_url in uploaded_urls:
        continue

    response = requests.get(image_url)

    if response.status_code == 200:
        filename = os.path.basename(urlparse(image_url).path)
        s3_key = f"artist-images/{filename}"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=response.content,
            ContentType="image/jpeg"
        )

        uploaded_urls.add(image_url)
        print(f"Uploaded: {filename}")
    else:
        print(f"Failed to download: {image_url}")

print("Artist image upload completed")