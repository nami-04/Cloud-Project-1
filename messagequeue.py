import pika
def uploadQueueClub(studentId):
    url = "amqps://namitha:NamiHarshu%40866@b-4a8f3d89-c5e3-4c5b-b1a1-a3c3b0c0c0c0.mq.us-east-1.amazonaws.com:5671"
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel() 
    channel.queue_declare(queue='club')
    channel.basic_publish(exchange='',routing_key='club',body = studentId)
    connection.close()

def uploadQueueEvent(studentId):
    url = "amqps://namitha:NamiHarshu%40866@b-4a8f3d89-c5e3-4c5b-b1a1-a3c3b0c0c0c0.mq.us-east-1.amazonaws.com:5671"
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel() 
    channel.queue_declare(queue='event')
    channel.basic_publish(exchange='',routing_key='event',body = studentId)
    connection.close()