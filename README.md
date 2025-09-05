<div align="center">
<img src="https://img.icons8.com/fluency/48/000000/api-settings.png" alt="API Icon"/>
<h1>Steam-Trader API Wrapper</h1>
</div>

<p align="center">
Добро пожаловать в документацию по асинхронному API врапперу для сайта <i>Steam-Trader.com</i>.
<br>
Эта библиотека была создана, чтобы максимально упростить взаимодействие с API, спрятав всю сложную логику запросов и обработки ошибок "под капот".
</p>

---

## ✨ Основные преимущества
* **Простота:** Забудьте о ручном формировании URL и разборе JSON. Просто вызывайте понятные методы.
* **Асинхронность:** Построен на `aiohttp`, что делает его неблокирующим и идеальным для современных ботов.
* **Надежность:** Встроенная обработка таймаутов, сетевых ошибок и неудачных ответов от API.

---

## ⚙️ Начало работы
### 1. Установка
Для работы враппера требуется только одна библиотека — `aiohttp`.
```shell
pip install aiohttp
```
### 2. Подключение
Скопируйте файл steam_trader_wrapper.py в папку с вашим проектом и импортируйте основной класс в свой главный 
```python
from steam_trader_wrapper import SteamTraderClient
```
## 📖 Примеры использования
Все примеры предполагают, что вы работаете внутри асинхронной функции.

### 1. Инициализация клиента
Это первый и самый важный шаг. Клиент создаётся один раз и используется для всех дальнейших запросов

```python
import asyncio

async def main():
    API_KEY = "ВАШ_СЕКРЕТНЫЙ_КЛЮЧ"
    client = SteamTraderClient(apikey=API_KEY)

    # ... здесь будет ваш код ...

    # В конце работы обязательно закрываем сессию
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```
### 2. Проверка баланса
Простой запрос для получения текущего баланса.

```python
balance_data = await client.get_balance()
if balance_data and balance_data.get('success'):
    balance = float(balance_data['balance'])
    print(f"💰 Ваш баланс: {balance:.2f} ₽")
```
### 3. Создание ордера на покупку
Выставляем заявку на покупку 5 штук Refined Metal (GID 1226) по цене 2.60 ₽.
```python
gid_to_buy = 1226
price_to_buy = 2.60
quantity = 5

result = await client.create_buy_order(gid=gid_to_buy, price=price_to_buy, count=quantity)

if result and result.get('success'):
    placed_count = result.get('placed', 0)
    print(f"✅ Успешно выставлено {placed_count} ордеров на покупку.")
```
### 4. Выставление предмета на продажу
Продаём предмет, используя его assetid и itemid (их можно получить из инвентаря).

```python
assetid_to_sell = 1234567890  # Пример
itemid_to_sell = 98765     # Пример
price_to_sell = 2.88

result = await client.list_item_for_sale(
    assetid=assetid_to_sell,
    itemid=itemid_to_sell,
    price=price_to_sell
)

if result and result.get('success'):
    sale_id = result.get('id')
    print(f"✅ Предмет успешно выставлен на продажу! ID продажи: {sale_id}")
```

### 5. Получение списка своих лотов на продаже
Запрашиваем инвентарь со статусом 0 (В продаже).

```python
# Для TF2 game_id = 440
# Статус 0 = "В продаже"
sell_orders_data = await client.get_inventory(game_id=440, status=0)

if sell_orders_data and sell_orders_data.get('success'):
    items_on_sale = sell_orders_data.get('items', [])
    print(f"У вас на продаже {len(items_on_sale)} предметов.")
    for item in items_on_sale:
        print(f"  - ID продажи: {item.get('id')}, GID: {item.get('gid')}, Цена: {item.get('price')} ₽")
```
### 6. Изменение цены существующего ордера
Если нужно "подрезать" цену конкурента, используем этот метод.

```python
# ID ордера, который нужно изменить (например, ID продажи из примера выше)
order_id_to_edit = 12345678
new_competitive_price = 2.87

result = await client.edit_price(orderid=order_id_to_edit, new_price=new_competitive_price)

if result and result.get('success'):
    print(f"✅ Цена для ордера {order_id_to_edit} успешно изменена!")
```


