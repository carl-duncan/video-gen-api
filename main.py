import os
import random

import shotstack_sdk as shotstack
import apiaudio
import dotenv
import requests
from shotstack_sdk.api import edit_api
from shotstack_sdk.model.clip import Clip
from shotstack_sdk.model.edit import Edit
from shotstack_sdk.model.offset import Offset
from shotstack_sdk.model.output import Output
from shotstack_sdk.model.soundtrack import Soundtrack
from shotstack_sdk.model.timeline import Timeline
from shotstack_sdk.model.title_asset import TitleAsset
from shotstack_sdk.model.track import Track
from shotstack_sdk.model.video_asset import VideoAsset

dotenv.load_dotenv()

configuration = shotstack.Configuration(host='https://api.shotstack.io/stage/')
configuration.api_key['DeveloperKey'] = os.getenv('SHOT_STACK_API_KEY')
apiaudio.api_key = os.getenv("API_AUDIO_KEY")


def video_search(video_query):
    videos = []
    request = requests.get("https://api.pexels.com/videos/search?query={}&per_page=20".format(video_query),
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
                                  "max_tokens": 100,
                                  "temperature": 0.9})
    json = request.json()
    generated_script = json["choices"][0]["text"].replace("\n", "<break time=\"1s\"/>")
    return generated_script


def voice_over(voice_query):
    script_template = apiaudio.Script().create(scriptText=voice_query)
    apiaudio.Speech().create(scriptId=script_template.get("scriptId"), voice="aria")
    apiaudio.Mastering().create(scriptId=script_template.get("scriptId"), soundTemplate="3am")
    file = apiaudio.Mastering().retrieve(scriptId=script_template.get("scriptId"))
    return {
        "url": file["url"],
        "estimatedLength": script_template["estimatedLength"]
    }


def video_edit(title, videos, voice):
    length = float(voice["estimatedLength"]) + 10.0
    with shotstack.ApiClient(configuration) as api_client:
        api_instance = edit_api.EditApi(api_client)

    tracks = []

    for i in range(0, int(length / 5)):
        random_video = random.choice(videos)
        video_asset = VideoAsset(
            src=random_video,
            volume=0.0,
        )

        if i == 0:
            title_asset = TitleAsset(
                text=title,
                style='minimal',
                color='#ffffff',
                size='medium',
                background='#000000',
                position='center',
                offset=Offset(
                    x=0.0,
                    y=-0.0
                )
            )
            title_clip = Clip(
                asset=title_asset,
                start=0.0,
                length=5.0,
            )

            video_clip = Clip(
                asset=video_asset,
                start=0.0,
                length=10.0,
            )

            video_track = Track(clips=[video_clip])
            title_track = Track(clips=[title_clip])
            tracks.append(title_track)
            tracks.append(video_track)
        else:
            video_clip = Clip(
                asset=video_asset,
                start=len(tracks) * 5.0,
                length=5.0,
            )

            track = Track(clips=[video_clip])
            tracks.append(track)
        videos.remove(random_video)

    soundtrack = Soundtrack(
        src=f"{voice['url']}",
        effect="fadeOut"
    )

    timeline = Timeline(
        background="#000000",
        tracks=tracks,
        soundtrack=soundtrack,
    )
    output = Output(
        format="mp4",
        resolution="sd"
    )
    edit = Edit(
        timeline=timeline,
        output=output
    )

    api_response = api_instance.post_render(edit)
    return api_response['response']['id']


def status(render_id):
    with shotstack.ApiClient(configuration) as api_client:
        api_instance = edit_api.EditApi(api_client)

        return api_instance.get_render(render_id, data=True, merged=True)['response']


if __name__ == '__main__':
    query = "mountains"
    script = generate_script(query)
    print(script)

    voice_over = voice_over(script)

    video_results = video_search(query)
    print(video_results)

    result = video_edit(query, video_results, voice_over)

    print(status(result))
