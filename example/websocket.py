import asyncio

from ftx import FtxClient


async def main():
    ftx = FtxClient(ws_queue_size=16)
    # connect the websocket
    await ftx.websocket.connect()

    # subscribe to a channel
    await ftx.websocket.subscribe('trades', 'BTC-PERP')

    while ftx.websocket.connected:
        # block and wait for next message
        msg = await ftx.websocket.recv()
        if msg and 'channel' in msg and msg['channel'] == 'trades':
            if 'data' in msg:
                # print the trade price
                print('price:', msg['data'][0]['price'])

    await ftx.websocket.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
