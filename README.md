# FTX Python client

A Unofficial Python3 library to interact with [FTX's](https://ftx.com/) API. The library can be used to fetch market
data, make trades, place orders or create third-party clients.

For more information, see [the FTX documentation.](https://docs.ftx.com/)

## Installation

    $ pip install ftx

## Quickstart

This is an introduction on how to get started with FTX client. First, make sure the FTX library is installed.

The next thing you need to do is import the library and get an instance of the client:

    import ftx
    client = ftx.FtxClient()

### Get orderbook

Get the orderbook levels of bid/ask:

    >>> import ftx
    >>> client = ftx.FtxClient()
    >>> result = client.get_orderbook('BTC/USD', 1)
    >>> result
    {'asks': [[11861.0, 1.778]], 'bids': [[11860.5, 0.1]]}

    >>> result['asks']
    [[11861.0, 1.778]]

    >>> result['bids']
    [[11860.5, 0.1]]

### Market's instrument data

The API supports fetching full data for one or multiple markets.

    >>> client.get_market('BTC/USD')
    {'ask': 11849.0, 'baseCurrency': 'BTC', 'bid': 11848.5, 'change1h': 0.00025325004220834034, 'change24h': 0.008983693106825051, 'changeBod': 0.006925855109411514, 'enabled': True, 'last': 11849.0, 'minProvideSize': 0.0001, 'name': 'BTC/USD', 'postOnly': False, 'price': 11849.0, 'priceIncrement': 0.5, 'quoteCurrency': 'USD', 'quoteVolume24h': 9271567.5201, 'restricted': False, 'sizeIncrement': 0.0001, 'type': 'spot', 'underlying': None, 'volumeUsd24h': 9271567.5201}

### Date ranges

Any time-based parameters accept Python `datetime` objects. All timestamps returned from FTX are UTC.

    >>> client = ftx.FtxClient()
    >>> client.get_trades('BTC/USD', 1, datetime.datetime(2020,8,20).timestamp())
    [{'id': 88953674, 'liquidation': False, 'price': 11861.0, 'side': 'sell', 'size': 0.0105, 'time': '2020-08-20T17:33:19.115690+00:00'}]

### Authenticated endpoints

Private endpoints require authentication. Clients authenticate with an API key. For more information,
see:[API keys](https://help.ftx.com/hc/en-us/articles/360044411911-FTX-Features-Overview#h_6a76d63d-e6cd-45db-87ab-5778af4e3b07)

To get an authenticated client instance:

    >>> client = ftx.FtxClient(api_key=<YOUR API KEY>, api_secret=<YOUR API SECRET>)

If you try to access a private endpoint with an unauthenticated client, an error is raised. Calls to private endpoints
work the same as regular ones:

    client.get_open_orders('BTC/USD')

## Advanced usage

### Placing orders

An order can be placed through the `place_order()` function. See
[the API Documentation](https://docs.ftx.com/#place-order) for required and optional parameters.

    client.place_order('BTC/USD', 'sell', 12345.0, 10)

### Modifying orders

Orders can be modified by providing the original order ID.

    >>> client.place_order('BTC/USD', 'sell', 12345.0, 10)
    {"createdAt": "2020-08-20T17:33:19.115690+00:00","filledSize": 0,"id": 9596912,"market": "BTC/USD"...

    >>> client.modify_order(9596912, 12500.0, 15).result()

### Canceling orders

An order can be canceled given the order ID:

    client.cancel_order(9596912).result()


## WebSocket usage
Websocket can be used to subscribe to realtime updates on several channels as described in the [FTX websocket documentation](https://docs.ftx.com/#public-channels).

The `websocket` property on the FtxClient can be used to connect a websocket with the same credentials as the FtxClient object.
To connect using different credentials instantiate a new websocket client using the `FtxWebSocketClient` constructor.


**Example subscription to trade channel**
```python
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
```
