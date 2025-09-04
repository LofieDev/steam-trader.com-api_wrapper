# steam_trader_wrapper
import asyncio
import logging
import aiohttp

class SteamTraderClient:
    """
    Асинхронный API Wrapper для сайта steam-trader.com.
    Упрощает взаимодействие с API, обрабатывает ошибки и управляет сессией.
    """
    BASE_URL = "https://api.steam-trader.com"

    def __init__(self, api_key: str, session: aiohttp.ClientSession = None):
        if not api_key:
            raise ValueError("API ключ не может быть пустым.")
            
        self.api_key = api_key
        self._session = session
        self._owner_session = False
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._owner_session = True

    async def _api_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict | None:
        """Базовый метод для выполнения всех запросов к API."""
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Добавляем API ключ во все запросы
        payload = {'key': self.api_key}
        if params:
            payload.update(params)
        if data:
            payload.update(data)
        
        try:
            async with self._session.request(method, url, 
                                             params=payload if method.upper() == 'GET' else None,
                                             data=payload if method.upper() == 'POST' else None,
                                             timeout=15) as response:
                response.raise_for_status()
                json_response = await response.json()
                
                if not json_response.get("success"):
                    logging.error(f"[Wrapper] API {endpoint} вернул ошибку: {json_response.get('error', 'Нет деталей')}")
                    return json_response
                
                return json_response

        except asyncio.TimeoutError:
            logging.error(f"[Wrapper] Таймаут при запросе к {endpoint}")
        except aiohttp.ClientError as e:
            logging.error(f"[Wrapper] Сетевая ошибка при запросе к {endpoint}: {e}")
        except Exception as e:
            logging.error(f"[Wrapper] Непредвиденная ошибка при запросе к {endpoint}: {e}", exc_info=True)
            
        return None

    async def get_min_prices(self, gid: int) -> dict | None:
        """Возвращает минимальные/максимальные цены предмета."""
        return await self._api_request("GET", "getminprices/", params={'gid': gid, 'currency': 1})

    async def get_order_book(self, gid: int) -> dict | None:
        """Возвращает стакан ордеров для предмета."""
        return await self._api_request("GET", "orderbook/", params={'gid': gid, 'limit': 5})
        
    async def get_inventory(self, game_id: int, status: int) -> dict | None:
        """Получает инвентарь пользователя с определённым статусом."""
        params = {'gameid': game_id, f'status[0]': status}
        return await self._api_request("GET", "getinventory/", params=params)

    async def create_buy_order(self, gid: int, price: float, count: int = 1) -> dict | None:
        """Создаёт ордер на покупку."""
        data = {'gid': gid, 'price': price, 'count': count}
        return await self._api_request("POST", "createbuyorder/", data=data)

    async def buy_item(self, gid: int, price: float) -> dict | None:
        """Моментально покупает самый дешёвый предмет (Commodity)."""
        data = {'id': gid, 'type': 1, 'price': price, 'currency': 1}
        return await self._api_request("POST", "buy/", data=data)
        
    async def list_item_for_sale(self, asset_id: int, item_id: int, price: float) -> dict | None:
        """Выставляет предмет на продажу."""
        data = {'assetid': asset_id, 'itemid': item_id, 'price': price}
        return await self._api_request("POST", "sale/", data=data)

    async def edit_price(self, order_id: int, new_price: float) -> dict | None:
        """Изменяет цену существующего ордера."""
        return await self._api_request("POST", "editprice/", data={'id': order_id, 'price': new_price})

    async def get_ws_token(self) -> dict | None:
        """Получает токен для WebSocket."""
        return await self._api_request("GET", "getwstoken/")


    async def get_balance(self) -> dict | None:
        """Возвращает баланс пользователя."""
        return await self._api_request("GET", "getbalance/")

    async def check_and_accept_trades(self) -> dict | None:
        """Проверяет и получает информацию о готовом обмене."""
        return await self._api_request("GET", "exchange/")

    async def get_discounts(self) -> dict | None:
        """Возвращает комиссию/скидку и оборот на сайте."""
        return await self._api_request("GET", "getdiscounts/")

    async def set_trade_link(self, trade_link: str) -> dict | None:
        """Устанавливает ссылку для обмена."""
        return await self._api_request("POST", "settradelink/", data={'trade_link': trade_link})

    async def close(self):
        """Закрывает сессию aiohttp, если она была создана враппером."""
        if self._session and not self._session.closed and self._owner_session:
            await self._session.close()
            logging.info("[Wrapper] Сессия успешно закрыта.")