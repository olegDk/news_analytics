import asyncio
from nats.aio.client import Client as NATS
from news_pb2 import News  # news_pb2 is the generated module from news.proto


async def run(loop):
    nc = NATS()

    await nc.connect("nats:4222", loop=loop)

    async def message_handler(msg):
        subject = msg.subject
        data = News()
        data.ParseFromString(msg.data)
        print(f"Received a message on '{subject}':\n{data}")

    sid = await nc.subscribe("news", cb=message_handler)

    try:
        await asyncio.sleep(999999)
    except asyncio.CancelledError:
        pass
    finally:
        await nc.unsubscribe(sid)
        await nc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
