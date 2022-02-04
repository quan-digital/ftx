import asyncio

from ftx import FtxClient


async def main():
    ftx = FtxClient(ws_max_queue_size=16)
    # connect the websocket
    await ftx.websocket.connect()

    # subscribe to the trades channel
    await ftx.websocket.subscribe('trades', 'BTC-PERP')

    trades = []
    while ftx.websocket.connected and len(trades) < 10:
        # block and wait for next message
        msg = await ftx.websocket.recv()
        if msg and 'channel' in msg and msg['channel'] == 'trades':
            if 'data' in msg:
                # print trade
                print(ftx.websocket.messages_dropped, 'messages dropped, price:', msg['data'][0]['price'])

    if ftx.websocket.connected:
        await ftx.websocket.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
