## Video Generator
This project provides a simple web service for generating short video clips based on a given query. 
The service uses the Pexels API to search for matching video files, the OpenAI API to generate a poem based on the query, 
the apiaudio API to create an audio recording of the poem, and the shotstack API to combine the video files, audio recording, and a title into a short video clip.

## Requirements
- Python 3.7 or higher
- Pexels API key
- OpenAI API key
- apiaudio API key
- shotstack API key

## Installation
To install the required dependencies, run:

`pip install -r requirements.txt`

## Usage
To start the web service, run:

`uvicorn main:app`

The service will be available at http://localhost:8000.

To generate a video clip, make a POST request to the /generate-video endpoint with the query as the request body. For example:


`curl -X POST -H "Content-Type: application/json" -d '{"query": "nature"}' http://localhost:8000/generate-video`

The response will contain a status_id field with a unique ID for the video generation process, and a url field with the URL of the generated video clip if it is available.

To check the status of the video generation process, make a GET request to the /status/{status_id} endpoint with the status_id from the previous response. For example:

`curl http://localhost:8000/status/123456`

The response will contain a status field with the current status of the process (either done, processing), and a url field with the URL of the generated video clip if it is available.

