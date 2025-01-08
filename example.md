Video Generation
This API supports generating dynamic videos based on user-provided prompts and images.
This interface submits tasks asynchronously. After the task is submitted, the interface will return the task ID, which can be used to obtain the status of the video generation task and the file ID corresponding to the generated product through the asynchronous task query interface.
After the generation task is completed, you can use the File (Retrieve) interface to download it through the file ID. It should be noted that the valid period of the returned URL is 9 hours (i.e. 32400 seconds) from the beginning of the URL return. After the valid period, the URL will become invalid and the generated information will be lost.
Intro of APIs
There are two APIs: the task of creating video generation and querying the status of video generation. The steps are as follows:
1.
Create a video generation task to get task_id
2.
Query the video generation task status based on task_id
3.
3. If the task is generated successfully, you can use the file_id returned by the query interface to view and download the results through the File API.
Create Video Generation Task
POST https://api.minimaxi.chat/v1/video_generation

We offer support for two distinct video generation patterns: text-to-video and image-to-video.
You can switch between these patterns by adjusting parameters.
Request parameters
AuthorizationstringRequired
API key you got from account setting
headerapplication/jsonRequired
Content-type
modelstringRequired
ID of model. Options:video-01
promptstring
Description of the video.
Note: It should be less than 2000 characters.
prompt_optimizerboolean
Default value:True. The model will automatically optimize the incoming prompt to improve the generation quality If necessary.
For more precise control, this parameter can be set to
False, and the model will follow the instructions more strictly. At this time
It is recommended to provide finer prompts for best results.
first_frame_imagestring
The model will use the image passed in this parameter as the first frame to generate a video.
Supported formats:
- URL of the image
- base64 encoding of the image
Upon passing this parameter, the model is capable of proceeding without a prompt, autonomously determining the progression of the video.
Image specifications:
- format must be JPG, JPEG, or PNG;
- aspect ratio should be greater than 2:5 and less than 5:2; the shorter side must exceed 300 pixels
- file size must not exceed 20MB.
callback_urlstring（If you don’t need to receive our status update messages in real-time, please don’t pass this parameter; you can simply use the Query of Generation Status API.）
When initiating a task creation request, the MiniMax server will send a request with a validation field to the specified request address. When this POST validation request is received, the request address must extract thechallengevalue and return response data containing this value within 3 seconds. If this response is not provided in time, the validation will fail, resulting in a task creation failure.
Sample response data:
{ "challenge": "1a3cs1j-601a-118y-ch52-o48911eabc3u" }
After successfully configuring the callback request address, whenever there is a status change in the video generation task, the MiniMax server will send a callback request to this address, containing the latest task status. The structure of the callback request content matches the response body of the API for querying video generation task status (excluding
video_widthandvideo_height).
Text to video
Image to video
Example request
Copy
import requests
import json

url = "https://api.minimaxi.chat/v1/video_generation"
api_key="Fill in your api_key"

payload = json.dumps({
  "model": "video-01", 
  "prompt": "On a distant planet, there is a MiniMax.",
})
headers = {
  'authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
call back demo
Copy
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
app = FastAPI()
@app.post("/get_callback")
async def get_callback(request: Request):
    try:
        json_data = await request.json()
        challenge = json_data.get("challenge")
        if challenge is not None:
          # is a verification request, just return the challenge
          return {"challenge": challenge}
        else:
            # is a callback request, do your own logic here
            # {
            #     "task_id": "115334141465231360",
            #     "status": "Success",
            #     "file_id": "205258526306433",
            #     "base_resp": {
            #         "status_code": 0,
            #         "status_msg": "success"
            #     }
            # }
            return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, # required
        host="0.0.0.0", # Required
        port=8000, # Required, the port can be configured.
        # ssl_keyfile='yourname.yourDomainName.com.key', # Optional, check whether SSL is enabled.
        # ssl_certfile='yourname.yourDomainName.com.key', # Optional, check whether SSL is enabled.
    )
Response Parameters
task_idstring
The task ID for the asynchronous video generation task is generated, and the results can be retrieved by using this ID in the asynchronous task query interface.
base_resp
Status code and its details.
Show Properties
Example response
Copy
{
    "task_id": "106916112212032",
    "base_resp": {
        "status_code": 0,
        "status_msg": "success"
    }
}
Query of Generation Status
GET https://api.minimaxi.chat/v1/query/video_generation?task_id={task_id}
Request parameters
AuthorizationstringRequired
API key you got from account setting
task_idstringRequired
The task ID to be queried. Only tasks created by Xuan's current account can be queried.
Example request
Copy
import requests
import json

api_key="fill in the api_key"
task_id="fill in the task_id"

url = f"http://api.minimaxi.chat/v1/query/video_generation?task_id={task_id}"

payload = {}
headers = {
  'authorization': f'Bearer {api_key}',
  'content-type': 'application/json',
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
Response Parameters
task_idstring
The task ID being queried this time.
statusstring
Task status, including the following status:
Preparing-The task is preparing
Processing - Generating
Success- The task is successful Success
Fail- The task failed
file_idstring
After the task status changes to Success, this field returns the file ID corresponding to the generated video
base_resp
Status code and its details.
Show Properties
Example response
Copy
{
    "task_id": "176843862716480",
    "status": "Success",
    "file_id": "176844028768320",
    "base_resp": {
        "status_code": 0,
        "status_msg": "success"
    }
}
Retrieve the download URL of the video file
Request parameters
AuthorizationstringRequired
API key you got from account setting.
Content-typeapplication/jsonRequired
Content-type
GroupIdstringRequired
Unique identifier for your account.
file_idstringRequired
Unique Identifier for the file, you got it from the previous step.
Example request
Copy
import requests

group_id = "fill in the groupid"
api_key = "fill in the api key"
file_id = "fill in the file id"

url = f'https://api.minimaxi.chat/v1/files/retrieve?GroupId={group_id}&file_id={file_id}'
headers = {
    'authority': 'api.minimaxi.chat',
    'content-type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

response = requests.get(url, headers=headers)
print(response.text)
Response Parameters
file_idstring
Unique Identifier for the file.
bytesinteger
File size, in bytes.
created_atinteger
Unix timestamp when creating the file, in seconds.
filenamestring
The name of the file.
purposestring
The purpose of using the file.
download_urlstring
The URL you get to download the video.
base_resp
Status code and its details.
Show Properties


Full Example
Here is an example of using the video generation function. The whole process is divided into three steps.
1.
Call the video generation interface to submit the generation task.
2.
Polling video generation asynchronous task query interface to obtain task status and file ID of the generated video.
3.
Call the file download interface to download the generated video by file ID.

import os
import time
import requests
import json

api_key = "Fill in the API Key"

prompt = "Description of your video"
model = "video-01" 
output_file_name = "output.mp4" #Please enter the save path for the generated video here

def invoke_video_generation()->str:
    print("-----------------Submit video generation task-----------------")
    url = "https://api.minimaxi.chat/v1/video_generation"
    payload = json.dumps({
      "prompt": prompt,
      "model": model
    })
    headers = {
      'authorization': 'Bearer ' + api_key,
      'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    task_id = response.json()['task_id']
    print("Video generation task submitted successfully, task ID.："+task_id)
    return task_id

def query_video_generation(task_id: str):
    url = "https://api.minimaxi.chat/v1/query/video_generation?task_id="+task_id
    headers = {
      'authorization': 'Bearer ' + api_key
    }
    response = requests.request("GET", url, headers=headers)
    status = response.json()['status']
    if status == 'Queueing':
        print("...In the queue...")
        return "", 'Queueing'
    elif status == 'Processing':
        print("...Generating...")
        return "", 'Processing'
    elif status == 'Success':
        return response.json()['file_id'], "Finished"
    elif status == 'Fail':
        return "", "Fail"
    else:
        return "", "Unknown"


def fetch_video_result(file_id: str):
    print("---------------Video generated successfully, downloading now---------------")
    url = "https://api.minimaxi.chat/v1/files/retrieve?file_id="+file_id
    headers = {
        'authorization': 'Bearer '+api_key,
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    download_url = response.json()['file']['download_url']
    print("Video download link：" + download_url)
    with open(output_file_name, 'wb') as f:
        f.write(requests.get(download_url).content)
    print("THe video has been downloaded in："+os.getcwd()+'/'+output_file_name)


if __name__ == '__main__':
    task_id = invoke_video_generation()
    print("-----------------Video generation task submitted -----------------")
    while True:
        time.sleep(10)

        file_id, status = query_video_generation(task_id)
        if file_id != "":
            fetch_video_result(file_id)
            print("---------------Successful---------------")
            break
        elif status == "Fail" or status == "Unknown":
            print("---------------Failed---------------")
            break: