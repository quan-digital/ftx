import asyncio

from ftx import FtxClient


async def main():
    ftx = FtxClient()
    await ftx.websockets.connect()

    first_market = ftx.get_markets()[0]
    await ftx.websockets.subscribe('trades', first_market['name'])

    while ftx.websockets.connected:
        print(await ftx.websockets.recv())


if __name__ == '__main__':
    asyncio.run(main())
