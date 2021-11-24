import requests

from celery import Celery

app = Celery('tasks')


def get_image(url):
    try:
        response = requests.get(url, stream=True)
    except requests.HTTPError:
        print('unable to get response')
        return None
    return response


def save_to_disk(response, filename):
    with open(f"data/images/{filename}.jpg", 'wb') as f:
        total = response.headers.get("content-length")
        if total is None:
            f.write(response.content)
        else:
            for data in response.iter_content(chunk_size=4096):
                f.write(data)


def store(data, adv_id, img_number=None):
    filename = f"{adv_id}-{img_number}"
    save_to_disk(data, filename)


@app.task
def download_image(advertisement):
    for i, img in enumerate(advertisement['image']):
        response = img['url']
        store(response, advertisement['post_id'], i + 1)
