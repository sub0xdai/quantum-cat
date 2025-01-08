import os
import time
import json
import random
import base64
import requests
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('MINIMAX_API_KEY')
GROUP_ID = os.getenv('MINIMAX_GROUP_ID')
API_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'https://api.minimaxi.chat/v1')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# These images have dimensions >= 300px on both sides
VALID_CAT_IMAGES = [
    'Untitled.jpg',
    
]

class MinimaxClient:
    def __init__(self):
        self.api_key = API_KEY
        self.group_id = GROUP_ID
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not found in environment variables")
        if not self.group_id:
            raise ValueError("MINIMAX_GROUP_ID not found in environment variables")
        
        self.headers = {
            'authorization': f'Bearer {self.api_key}',
            'content-type': 'application/json',
        }

    def get_random_cat_image_base64(self) -> str:
        """Get a random cat image as base64."""
        image_path = os.path.join(ASSETS_DIR, random.choice(VALID_CAT_IMAGES))
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def generate_video(self, prompt: str) -> str:
        """Submit a video generation task."""
        url = f"{API_SERVICE_URL}/video_generation"
        
        # Get a random cat image
        cat_image_base64 = self.get_random_cat_image_base64()
        
        payload = json.dumps({
            "prompt": prompt,
            "model": "video-01",
            "prompt_optimizer": True,
            "first_frame_image": f"data:image/png;base64,{cat_image_base64}"
        })

        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response.raise_for_status()
            response_data = response.json()
            
            if 'task_id' not in response_data:
                raise Exception(f"No task_id in response: {response_data}")
                
            return response_data['task_id']
        except Exception as e:
            print(f"Error in generate_video: {str(e)}")
            print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            raise

    async def check_generation_status(self, task_id: str) -> Tuple[str, str]:
        """Check the status of a video generation task."""
        url = f"{API_SERVICE_URL}/query/video_generation"
        params = {'task_id': task_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            response_data = response.json()
            
            if 'status' not in response_data:
                raise Exception(f"No status in response: {response_data}")
            
            status = response_data.get('status', 'Unknown')
            file_id = response_data.get('file_id', '')
            
            # Print response for debugging
            print(f"Status check response: {response_data}")
            
            return status, file_id
        except Exception as e:
            print(f"Error in check_generation_status: {str(e)}")
            print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            raise

    async def get_video_url(self, file_id: str) -> Optional[str]:
        """Get the download URL for a generated video."""
        url = f"{API_SERVICE_URL}/files/retrieve"
        params = {
            'GroupId': self.group_id,
            'file_id': file_id
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response_data = response.json()
        
        if response.status_code != 200:
            raise Exception(f"Failed to get video URL: {response_data.get('base_resp', {}).get('status_msg', 'Unknown error')}")
            
        return response_data.get('file', {}).get('download_url')

    async def download_video(self, url: str, file_path: str) -> bool:
        """Download a video file from the given URL."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Failed to download video: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error downloading video: {e}")
        return False
