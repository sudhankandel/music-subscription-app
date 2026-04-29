import json
import boto3


session = boto3.Session(region_name='us-east-1')
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('music')

def load_songs(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        songs_list = data['songs'] 
        for song in songs_list:
            try:
                table.put_item(Item=song)
            except Exception as e:
                print(f"Skipped song: {song.get('title')} - Error: {e}")

        print(f"Successfully loaded {len(songs_list)} songs into the 'music' table.")
        
    except FileNotFoundError:
        print("Error: 2026a2_songs.json not found. Check your file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    load_songs('2026a2_songs.json')