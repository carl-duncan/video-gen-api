import os
import dotenv
import boto3 as boto3
import requests

dotenv.load_dotenv()


def video_search(video_query):
    videos = []
    request = requests.get("https://api.pexels.com/videos/search?query={}&per_page=5".format(video_query),
                           headers={"Authorization": f"{os.getenv('PEXEL_API_KEY')}"})
    print(request.raw.read())
    json = request.json()
    for video in json["videos"]:
        for video_file in video["video_files"]:
            if video_file["width"] == 1920 and video_file["height"] == 1080:
                videos.append(video_file["link"])
    return videos


def generate_script(script_query):
    request = requests.post("https://api.openai.com/v1/completions",
                            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
                                , "Content-Type": "application/json"},
                            json={"model": "text-davinci-003",
                                  "prompt": f"{script_query} poem",
                                  "max_tokens": 4000,
                                  "temperature": 0.9})
    json = request.json()
    generated_script = json["choices"][0]["text"].replace("\n", "<break time=\"1s\"/>")
    generated_script = f"<speak> {generated_script} </speak>"
    return generated_script


def voice_over(voice_query):
    boto3.setup_default_session(region_name='us-east-1')
    polly = boto3.client('polly')
    response = polly.synthesize_speech(VoiceId='Matthew',
                                       OutputFormat='mp3',
                                       TextType='ssml',
                                       Text=voice_query)
    file = open('voice.mp3', 'wb')
    file.write(response['AudioStream'].read())
    file.close()

    pass


def video_edit():
    # edit the video
    pass


def upload_video():
    # upload the video
    pass


if __name__ == '__main__':
    query = "motivation"
    script = generate_script(query)
    print(script)

    voice_over(script)

    video_results = video_search(query)
    print(video_results)
