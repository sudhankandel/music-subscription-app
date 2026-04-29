from turtle import title

import boto3
from matplotlib import artist
import requests
import json

session = boto3.Session(region_name='us-east-1')
s3 = session.client('s3')
bucket_name = 'music-images-a2-75' # Replace with your bucket name

# Create the bucket if it doesn't exist
try:
    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket {bucket_name} created successfully!")
except s3.exceptions.BucketAlreadyOwnedByYou:
    print(f"Bucket {bucket_name} already exists, proceeding...")
except Exception as e:
    print(f"Could not create bucket: {e}")

def upload_images_to_s3(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        songs_list = data['songs']

    for song in songs_list:
        url = song.get('img_url')
        title = song.get('title')
        artist = song.get('artist')
        
        file_extension = url.split('.')[-1]
        safe_artist = str(artist).replace(' ', '_').replace('/', '_')
        safe_title = str(title).replace(' ', '_').replace('/', '_')
        s3_key = f"{safe_artist}-{safe_title}.{file_extension}"

        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                s3.upload_fileobj(
                    response.raw, 
                    bucket_name, 
                    s3_key, 
                    ExtraArgs={'ContentType': 'image/jpeg'} # This tells the browser to display it!
                )
                print(f"Uploaded: {s3_key}")
            else:
                print(f"Failed to download {url}")
        except Exception as e:
            print(f"Error uploading {title}: {e}")

if __name__ == "__main__":
    upload_images_to_s3('2026a2_songs.json')