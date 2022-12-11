from fastapi import FastAPI

from utils import generate_script, video_edit, voice_over, video_search, status

app = FastAPI()


@app.post("/generate-video")
def generate_video(query: str):
    script = generate_script(query)
    voice_over_result = voice_over(script)
    video_results = video_search(query)
    result = video_edit(query, video_results, voice_over_result)
    return result


@app.get("/status/{status_id}")
def get_status(status_id: str):
    result = status(status_id)
    return {
        "status": result['status'],
        "url": result['url']
    }
