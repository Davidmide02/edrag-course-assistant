# src/youtube_search.py

import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class YouTubeSearcher:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def search_educational_videos(self, query, max_results=5):
        """
        Search for educational videos related to the query
        """
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=query + " tutorial education",
                part='snippet',
                type='video',
                maxResults=max_results,
                relevanceLanguage='en',
                videoDuration='medium',  # Filter for medium-length videos (4-20 minutes)
                videoDefinition='high',  # Prefer high definition
                order='relevance'        # Sort by relevance
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                description = item['snippet']['description']
                thumbnail = item['snippet']['thumbnails']['default']['url']
                
                videos.append({
                    'id': video_id,
                    'title': title,
                    'channel': channel,
                    'description': description,
                    'thumbnail': thumbnail,
                    'url': f'https://www.youtube.com/watch?v={video_id}'
                })
            
            return videos
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return []

# Example usage
if __name__ == "__main__":
    searcher = YouTubeSearcher()
    results = searcher.search_educational_videos("calculus")
    for video in results:
        print(f"Title: {video['title']}")
        print(f"Channel: {video['channel']}")
        print(f"URL: {video['url']}")
        print()