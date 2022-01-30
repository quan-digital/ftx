import asyncio
import hmac
import json
import time
from typing import Optional

import websockets
from websockets.legacy.client import WebSocketClientProtocol


class FtxWebSocketClient:
    """
    Basic FTX WebSocket client

    See: https://docs.ftx.com/#websocket-api
    """
    _ws: Optional[WebSocketClientProtocol]

    def __init__(self,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 subaccount_name: Optional[str] = None,
                 socket_url='wss://ftx.com/ws',
                 verbose=False):
        """
        Create a websocket client

        :param verbose: set to True to log messages and connection status
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name
        self._ws = None
        self._last_ping = None
        self.verbose = verbose
        self.socket_url = socket_url
        self._queue = asyncio.Queue(maxsize=0)

    async def connect(self):
        """
        Connect to the websocket
        :return:
        """
        self._ws = await websockets.connect(self.socket_url)
        self._log('websocket connected')
        asyncio.create_task(self._loop_fn())
        asyncio.create_task(self._ping_loop_fn())

    @property
    def connected(self):
        """
        True if the websocket is connected and open
        """
        return self._ws and self._ws.open

    def _log(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def _on_message(self, msg):
        if msg and 'type' in msg:
            if msg['type'] != 'pong':
                self._queue.put_nowait(msg)
            else:
                dt = time.time() - self._last_ping
                self._log(f'pong ({round(dt, 2)}s)')

    async def send_message(self, msg):
        """
        Send a message on the websocket

        Example:
            ``client.send_message({'op': 'ping'})``

        :param msg: the message
        """
        self._log('->', msg)
        await self._ws.send(json.dumps(msg))

    async def _ping_loop_fn(self):
        """
        Ping keep-alive loop
        """
        await asyncio.sleep(1)
        while self._ws.open:
            if not self._last_ping:
                self._log('ping')
            self._last_ping = time.time()
            await self.send_message({'op': 'ping'})
            await asyncio.sleep(15)

    async def _loop_fn(self):
        """
        Main message loop
        """
        while self._ws.open:
            msg = await self._ws.recv()
            try:
                self._on_message(json.loads(msg))
            except:
                print('could not parse JSON', msg)

    async def login(self):
        assert self._api_key and self._api_secret, 'api_key and api_secret must be set to use login()'
        ts = int(time.time() * 1000)
        sign = hmac.new(self._api_secret.encode(), f'{ts}websocket_login', 'sha256').hexdigest()
        msg = {'op': 'login', 'args': {'key': self._api_key, 'sign': sign, 'time': ts}}
        await self.send_message(msg)

    async def subscribe(self, channel: str, market: str):
        """
        Subscribe to a channel and market

        :param channel: the channel
        :param market: the market
        """
        await self.send_message({
            'op': 'subscribe',
            'channel': channel,
            'market': market
        })

    async def unsubscribe(self, channel: str, market: str):
        """
        Unsubscribe from a channel and market

        :param channel: the channel
        :param market: the market
        """
        await self.send_message({
            'op': 'unsubscribe',
            'channel': channel,
            'market': market
        })

    async def recv(self):
        """
        Receives a single message from the websocket or waits until one is available

        :return: a message dict
        """
        return await self._queue.get()

