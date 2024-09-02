import json
import pika
from gridfs import GridFS
from pika.adapters.blocking_connection import BlockingChannel
from werkzeug.datastructures import FileStorage


def upload(f: FileStorage, fs: GridFS, channel: BlockingChannel, user_access):
    try:
        fid = fs.put(f)
    except Exception as err:
        return "internal server error", 500

    q_msg = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": user_access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(q_msg),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
    except:
        fs.delete(fid)
        return "internal server error", 500


