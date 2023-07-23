import os
import random
import requests
from dotenv import load_dotenv


def get_last_comic_number():
    current_comic_url = 'https://xkcd.com/info.0.json'
    xkcd_response = requests.get(current_comic_url)
    xkcd_response.raise_for_status()
    last_comic_number = xkcd_response.json()['num']
    return last_comic_number


def fetch_comic_info(last_comic_number):
    random_comic_number = random.randint(1, last_comic_number)
    comic_url = f"""https://xkcd.com/{random_comic_number}/info.0.json"""
    comic_response = requests.get(comic_url)
    comic_response.raise_for_status()

    image_url = comic_response.json()['img']
    comments = comic_response.json()['alt']
    image_name = f"""comic_{random_comic_number}.jpg"""

    image_response = requests.get(image_url)
    image_response.raise_for_status()

    with open(image_name, 'wb') as file:
        file.write(image_response.content)
    return image_name, comments


def get_vk_upload_id(vk_group_id, vk_access_token):
    method = 'photos.getWallUploadServer'
    vk_url = f'''https://api.vk.com/method/{method}?group_id={vk_group_id}&access_token={vk_access_token}&v=5.131'''
    vk_response = requests.get(vk_url)
    upload_id = vk_response.json()['response']["upload_url"]
    return upload_id


def upload_photo_to_vk_server(upload_url, image_name):
    with open(image_name, 'rb') as file:
        files = {
            'photo': file,
        }
        vk_response = requests.post(upload_url, files=files)
        vk_response.raise_for_status()
        upload_result = vk_response.json()
    os.remove(image_name)
    return upload_result


def save_photo_to_vk_wall(vk_group_id, vk_access_token, upload_result):
    method = 'photos.saveWallPhoto'
    vk_url = f'''https://api.vk.com/method/{method}'''
    data = {
        "group_id": vk_group_id,
        "access_token": vk_access_token,
        "v": "5.131",
        "photo": upload_result['photo'],
        "server": upload_result['server'],
        "hash": upload_result['hash'],
    }
    vk_response = requests.post(vk_url, data=data)
    vk_response.raise_for_status()
    saved_photo_info = vk_response.json()
    return saved_photo_info



def public_post_to_wall(vk_group_id, vk_access_token, saved_photo_info, comments):
    method = 'wall.post'
    vk_url = f'''https://api.vk.com/method/{method}'''
    attachments = f"photo{saved_photo_info['response'][0]['owner_id']}_{saved_photo_info['response'][0]['id']}"
    data = {
        "owner_id": -int(vk_group_id),
        "access_token": vk_access_token,
        "v": "5.131",
        "attachments": attachments,
        "message": comments
    }
    vk_response = requests.post(vk_url, data=data)
    vk_response.raise_for_status()
    if vk_response.status_code == 200:
        print("Comix posted successfully!")

def main():
    load_dotenv()
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')

    last_comic_number = get_last_comic_number()
    image_name, comments = fetch_comic_info(last_comic_number)
    upload_url = get_vk_upload_id(vk_group_id, vk_access_token)
    upload_result = upload_photo_to_vk_server(upload_url, image_name)
    saved_photo_info = save_photo_to_vk_wall(vk_group_id, vk_access_token, upload_result)
    result = public_post_to_wall(vk_group_id, vk_access_token, saved_photo_info, comments)


if __name__ == "__main__":
    main()

