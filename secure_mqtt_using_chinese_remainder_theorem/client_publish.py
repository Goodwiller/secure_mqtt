import logging
import asyncio
import threading
import time


from amqtt.client import MQTTClient, ConnectException
from amqtt.mqtt.constants import QOS_0, QOS_1, QOS_2


#
# This sample shows how to publish messages to broker using different QOS
# Debug outputs shows the message flows
#

logger = logging.getLogger(__name__)



async def con():
    print("Connection process started at ", time.time())	
    C = MQTTClient()
    await C.connect("mqtt://0.0.0.0:1883/")
    print("Connection process ended at ", time.time())
    print("Subscription process started at ", time.time())	
    await C.subscribe(
        [
            ("default", QOS_1),
        ]
    )
    return C


async def test_coro(C):

    print("publish Co_routine started...")
    print("Publish process started at ", time.time())
    tasks = [
        asyncio.ensure_future(C.publish("default", b"Hello")),
    ]
    await asyncio.wait(tasks)


async def test_coro2(C):
    #listening to all messages on the default channel

    print("listen Co_routine started...")
    a = 1
    count = 0
    try:
        while a == 1:
            message = await C.deliver_message()
            packet = message.publish_packet
            print(
                "%s => %s"
                % (packet.variable_header.topic_name, str(packet.payload.data))
            )
            if (packet.payload.data[0] == 'N' and count == 0):
                print("Subscription process ended and new group key acheived at ", time.time())
                count = count + 1
            else:
                print("Publish process ended at ", time.time())
        await C.unsubscribe(["default"])
        await C.disconnect()
    except ClientException as ce:
        logger.error("Client exception: %s" % ce)


async def run_concurrently(C):
    await asyncio.gather(test_coro2(C), test_coro(C))


if __name__ == "__main__":
    formatter = (
        "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    )
    formatter = "%(message)s"
    logging.basicConfig(level=logging.CRITICAL, format=formatter)

    C = asyncio.get_event_loop().run_until_complete(con())

    asyncio.get_event_loop().run_until_complete(run_concurrently(C))
