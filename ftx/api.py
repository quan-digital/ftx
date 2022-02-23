import hmac
import time
import urllib.parse
from typing import Optional, Dict, Any, List

from ciso8601 import parse_datetime
from requests import Request, Session, Response


class FtxClient:
    def __init__(
        self,
        base_url: str = "https://ftx.com/api/",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        subaccount_name: Optional[str] = None,
    ) -> None:
        self._session = Session()
        self._base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self,
                path: str,
                params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._base_url + path, **kwargs)
        if self._api_key:
            self._sign_request(request)
        response = self._session.send(request.prepare())

        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode(
        )
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload,
                             'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(
                self._subaccount_name)

    @staticmethod
    def _process_response(response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

    #
    # Authentication required methods
    #
    def authentication_required(fn):
        """Annotation for methods that require auth."""

        def wrapped(self, *args, **kwargs):
            if not self._api_key:
                raise TypeError("You must be authenticated to use this method")
            else:
                return fn(self, *args, **kwargs)

        return wrapped

    @authentication_required
    def get_account_info(self) -> dict:
        return self._get('account')

    @authentication_required
    def get_open_orders(self, market: Optional[str] = None) -> List[dict]:
        return self._get('orders', {'market': market})

    @authentication_required
    def get_order_status(self, existing_order_id: int) -> dict:
        return self._get(f'orders/{existing_order_id}')

    @authentication_required
    def get_order_history(self,
                          market: Optional[str] = None,
                          side: Optional[str] = None,
                          order_type: Optional[str] = None,
                          start_time: Optional[float] = None,
                          end_time: Optional[float] = None) -> List[dict]:
        return self._get(
            'orders/history', {
                'market': market,
                'side': side,
                'orderType': order_type,
                'start_time': start_time,
                'end_time': end_time
            })

    @authentication_required
    def get_conditional_order_history(
            self,
            market: Optional[str] = None,
            side: Optional[str] = None,
            type: Optional[str] = None,
            order_type: Optional[str] = None,
            start_time: Optional[float] = None,
            end_time: Optional[float] = None) -> List[dict]:
        return self._get(
            'conditional_orders/history', {
                'market': market,
                'side': side,
                'type': type,
                'orderType': order_type,
                'start_time': start_time,
                'end_time': end_time
            })

    @authentication_required
    def modify_order(
        self,
        existing_order_id: Optional[str] = None,
        existing_client_order_id: Optional[str] = None,
        price: Optional[float] = None,
        size: Optional[float] = None,
        client_order_id: Optional[str] = None,
    ) -> dict:
        assert (existing_order_id is None) ^ (existing_client_order_id is None), \
            'Must supply exactly one ID for the order to modify'
        assert (price is None) or (size is
                                   None), 'Must modify price or size of order'
        path = f'orders/{existing_order_id}/modify' if existing_order_id is not None else \
            f'orders/by_client_id/{existing_client_order_id}/modify'
        return self._post(
            path, {
                **({
                    'size': size
                } if size is not None else {}),
                **({
                    'price': price
                } if price is not None else {}),
                **({
                    'clientId': client_order_id
                } if client_order_id is not None else {}),
            })

    @authentication_required
    def get_conditional_orders(self,
                               market: Optional[str] = None) -> List[dict]:
        return self._get('conditional_orders', {'market': market})

    @authentication_required
    def place_order(self,
                    market: str,
                    side: str,
                    price: float,
                    size: float,
                    type: str = 'limit',
                    reduce_only: bool = False,
                    ioc: bool = False,
                    post_only: bool = False,
                    client_id: Optional[str] = None,
                    # reject_on_price_band: Optional[bool] = None,
                    reject_After_Ts: Optional[float] = None) -> dict:
        return self._post(
            'orders', {
                'market': market,
                'side': side,
                'price': price,
                'size': size,
                'type': type,
                'reduceOnly': reduce_only,
                'ioc': ioc,
                'postOnly': post_only,
                'clientId': client_id,
                # 'rejectOnPriceBand': reject_on_price_band,
                'rejectAfterTs': reject_After_Ts
            })

    @authentication_required
    def place_conditional_order(self,
                                market: str,
                                side: str,
                                size: float,
                                type: str,
                                limit_price: Optional[float] = None,
                                reduce_only: bool = False,
                                trigger_price: Optional[float] = None,
                                orderPrice:    Optional[float] = None,
                                trail_value: Optional[float] = None,
                                retry_until_filled: Optional[bool] = None,
                                ) -> dict:
        """
        To send a Stop Market order, set type='stop' and supply a trigger_price
        To send a Stop Limit order, also supply a limit_price
        To send a Take Profit Market order, set type='trailing_stop' and supply a trigger_price
        To send a Trailing Stop order, set type='trailing_stop' and supply a trail_value
        """
        assert type in ('stop', 'take_profit', 'trailing_stop')
        assert type not in ('stop', 'take_profit') or trigger_price is not None, \
            'Need trigger prices for stop losses and take profits'
        assert type not in ('trailing_stop',) or (trigger_price is None and trail_value is not None), \
            'Trailing stops need a trail value and cannot take a trigger price'

        return self._post(
            'conditional_orders', {
                'market': market,
                'side': side,
                'triggerPrice': trigger_price,
                'size': size,
                'reduceOnly': reduce_only,
                'type': type,
                'orderPrice': limit_price,
                'trailValue': trail_value,
                'retryUntilFilled': retry_until_filled
            })

    @authentication_required
    def cancel_order(self, order_id: str) -> dict:
        return self._delete(f'orders/{order_id}')

    @authentication_required
    def cancel_conditional_order(self, order_id: str) -> dict:
        return self._delete(f'conditional_orders/{order_id}')

    @authentication_required
    def cancel_orders(self,
                      market_name: Optional[str] = None,
                      conditional_orders: bool = False,
                      limit_orders: bool = False) -> dict:
        return self._delete(
            'orders', {
                'market': market_name,
                'conditionalOrdersOnly': conditional_orders,
                'limitOrdersOnly': limit_orders,
            })

    @authentication_required
    def get_lending_rates(self) -> dict:
        return self._get(f"spot_margin/lending_rates")

    @authentication_required
    def get_borrow_rates(self) -> dict:
        return self._get(f"spot_margin/borrow_rates")

    @authentication_required
    def get_borrow_summary(self) -> dict:
        return self._get(f"spot_margin/borrow_summary")

    @authentication_required
    def get_market_info(self, market_name: Optional[str] = None) -> dict:
        return self._get(f"spot_margin/market_info?market={market_name}")

    @authentication_required
    def get_fills(self,
                  start_time: Optional[float] = None,
                  end_time: Optional[float] = None,
                  order: Optional[float] = None,
                  orderId: Optional[float] = None) -> List[dict]:
        return self._get('fills', {
            'start_time': start_time,
            'end_time': end_time,
            'order': order,
            'orderId': orderId
        })

    @authentication_required
    def get_balances(self) -> List[dict]:
        return self._get('wallet/balances')

    @authentication_required
    def get_deposit_address(self,
                            ticker: str,
                            method: Optional[str] = None) -> dict:
        method = f'?method={method}' if method else ''
        return self._get(f'wallet/deposit_address/{ticker}{method}')

    @authentication_required
    def get_positions(self, show_avg_price: bool = False) -> List[dict]:
        return self._get('positions', {'showAvgPrice': show_avg_price})

    @authentication_required
    def get_position(self, name: str, show_avg_price: bool = False) -> dict:
        return next(
            filter(lambda x: x['future'] == name,
                   self.get_positions(show_avg_price)), None)

    @authentication_required
    def set_leverage(self, leverage):
        return self._post('account/leverage', {'leverage': leverage})

    @authentication_required
    def get_subaccounts(self) -> List[dict]:
        return self._get('subaccounts')

    @authentication_required
    def create_subaccounts(self, nickname) -> List[dict]:
        return self._post('subaccounts', {'nickname': nickname})

    @authentication_required
    def delete_subaccounts(self, nickname: Optional[str] = None) -> List[dict]:
        assert (nickname is not None) or (self._subaccount_name
                                          is not None), 'SubAccount not set'
        subaccount = nickname or self._subaccount_name
        return self._delete('subaccounts', {'nickname': subaccount})

    @authentication_required
    def get_subaccounts_balance(self, nickname=None) -> List[dict]:
        assert (nickname is not None) or (self._subaccount_name
                                          is not None), 'SubAccount not set'
        subaccount = nickname or self._subaccount_name
        return self._get(f'subaccounts/{subaccount}/balances',
                         {'nickname': subaccount})

    @authentication_required
    def request_quote(self, fromCoin, toCoin, size) -> List[dict]:
        return self._post('otc/quotes', {
            'fromCoin': fromCoin,
            'toCoin': toCoin,
            'size': size
        })

    @authentication_required
    def get_quote_details(self, quoteId):
        return self._get(f'otc/quotes/{quoteId}')

    @authentication_required
    def accept_quote(self, quoteId):
        return self._post(f'otc/quotes/{quoteId}/accept')

    @authentication_required
    def request_withdrawal(self,
                           coin: str,
                           size: float,
                           address: str,
                           tag: Optional[str] = None,
                           method: Optional[str] = None,
                           password: Optional[str] = None,
                           code: Optional[str] = None):
        assert (size > 0), 'Size must be greater than 0'
        return self._post('wallet/withdrawals', {
            'coin': coin,
            'size': size,
            'address': address,
            'tag': tag,
            'method': method,
            'password': password,
            'code': code
        })

    #
    # Public methods
    #

    def get_futures(self) -> List[dict]:
        return self._get('futures')

    def get_future(self, future_name: str) -> dict:
        return self._get(f'futures/{future_name}')

    def get_markets(self) -> List[dict]:
        return self._get('markets')

    def get_market(self, market: str) -> dict:
        return self._get(f'markets/{market}')

    def get_orderbook(self, market: str, depth: Optional[int] = None) -> dict:
        return self._get(f'markets/{market}/orderbook', {'depth': depth})

    def get_trades(self,
                   market: str,
                   limit: int = 100,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> dict:
        return self._get(f'markets/{market}/trades', {
            'limit': limit,
            'start_time': start_time,
            'end_time': end_time
        })

    def get_all_trades(self,
                       market: str,
                       start_time: Optional[float] = None,
                       end_time: Optional[float] = None) -> List:
        ids = set()
        limit = 100
        results = []
        while True:
            response = self._get(f'markets/{market}/trades', {
                'end_time': end_time,
                'start_time': start_time,
            })
            deduped_trades = [r for r in response if r['id'] not in ids]
            results.extend(deduped_trades)
            ids |= {r['id'] for r in deduped_trades}
            print(f'Adding {len(response)} trades with end time {end_time}')
            if len(response) == 0:
                break
            end_time = min(parse_datetime(t['time'])
                           for t in response).timestamp()
            if len(response) < limit:
                break
        return results

    def get_historical_data(self,
                            market_name: str,
                            resolution: int,
                            limit: int,
                            start_time: Optional[float] = None,
                            end_time: Optional[float] = None) -> dict:
        return self._get(
            f'markets/{market_name}/candles',
            dict(resolution=resolution,
                 limit=limit,
                 start_time=start_time,
                 end_time=end_time))

    def get_future_stats(self, future_name) -> List[dict]:
        return self._get(f'futures/{future_name}/stats',
                         {'future_name': future_name})

    def get_funding_rates(self, future: Optional[str] = None,
                                start_time: Optional[float] = None,
                                end_time: Optional[float] = None) -> List[dict]:
        return self._get('funding_rates',
            dict(future=future,
                start_time=start_time,
                end_time=end_time))

    # leveraged tokens

    def list_lts(self) -> List[dict]:
        return self._get(f'lt/tokens')

    def get_lt_info(self, market: str) -> dict:
        return self._get(f'lt/{market}')

    
