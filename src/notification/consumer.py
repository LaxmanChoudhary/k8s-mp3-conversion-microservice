import os
import pika
import sys
from send import email


def main():
    # rabbitmq conn
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(ch, method, props, body):
        print("Received message. Processing!")
        err = email.notification(body)
        if err:
            print("Error while sending notification.")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"),
        on_message_callback=callback
    )

    print("Waiting for messages, To exit click CTRL + C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        print("starting Notification service...")
        main()
        print("Notification service up and running.")
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
