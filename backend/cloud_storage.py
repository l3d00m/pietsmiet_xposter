from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import requests
from io import BytesIO
from PIL import Image
import os
from backend.api_keys import cloud_client_id, cloud_client_email, cloud_private_key_id, cloud_private_key, \
    cloud_bucket_name
from backend.log_util import log
from backend.firebase_db_util import get_id_of_feed

max_image_size = 4000000
size = 512, 512
image_path = "image.jpg"

credentials_dict = {
    'type': 'service_account',
    'client_id': cloud_client_id,
    'client_email': cloud_client_email,
    'private_key_id': cloud_private_key_id,
    'private_key': cloud_private_key,
}
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict)
client = storage.Client(credentials=credentials, project=cloud_bucket_name)


def store_image_in_gcloud(url, feed):
    try:
        # Get image with timeout
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            # Check that the file is not bigger than max size
            content = r.raw.read(max_image_size + 1, decode_content=True)
            if len(content) > max_image_size:
                raise ValueError('File is too big (maybe it\'s the video instead of the thumb), not downloading!')
        else:
            raise ValueError("Wrong status code at download")

            # Resize the image to save bandwidth and storage
        im = Image.open(BytesIO(content))
        im.thumbnail(size)
        im.save(image_path, format="JPEG")

        # Upload the image to the firebase storage
        bucket = client.get_bucket(cloud_bucket_name)
        blob = bucket.blob(get_storage_path(feed))
        blob.upload_from_filename(image_path, content_type="image/jpg")

        # Cleanup ressources
        log("Debug", "Uploaded image")
        del content
        del im
        os.remove(image_path)

        # Return the download url of the image
        return "https://storage.googleapis.com/" + cloud_bucket_name + "/" + get_storage_path(feed)
    except Exception as e:
        log("Warning", "Couldn't up- / download image" + format(e))

    return None


def remove_image_from_gcloud(feed):
    try:
        # Delete the image from the firebase storage
        bucket = client.get_bucket(cloud_bucket_name)
        blob = bucket.blob(get_storage_path(feed))
        blob.delete()
        log("Debug", "Image deleted")
    except Exception as e:
        log("Warning", "Deleting image failed: " + format(e))


def get_storage_path(feed):
    return "thumbs/" + feed.scope + "/" + get_id_of_feed(feed) + ".jpg"
