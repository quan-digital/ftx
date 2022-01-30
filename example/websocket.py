import asyncio

from ftx import FtxClient


async def main():
    ftx = FtxClient()
    # connect the websocket
    await ftx.websocket.connect()

    first_market = ftx.get_markets()[0]
    # subscribe to the trades channel of first available market
    await ftx.websocket.subscribe('trades', first_market['name'])

    while ftx.websocket.connected:
        # block and wait for next message
        msg = await ftx.websocket.recv()
        if 'channel' in msg and msg['channel'] == 'trades':
            if 'data' in msg:
                # print trade
                print(msg['market'], msg['data'][0]['side'], msg['data'][0]['size'])


if __name__ == '__main__':
    asyncio.run(main())
