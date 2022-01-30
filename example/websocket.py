import asyncio

from ftx import FtxClient


async def main():
    ftx = FtxClient()
    await ftx.websocket.connect()

    first_market = ftx.get_markets()[0]
    await ftx.websocket.subscribe('trades', first_market['name'])

    while ftx.websocket.connected:
        print(await ftx.websocket.recv())


if __name__ == '__main__':
    asyncio.run(main())
