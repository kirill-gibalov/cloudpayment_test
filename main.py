import asyncio

from client.client import Client
from client.schema import UserCredentialDataClass, ChargeCard, Response


async def main():
    """Тестовые данные для вызова клиента"""
    charge_info = ChargeCard(cryptogram='yandex_crypto', amount=50, currency="Rub", name='name', ip_address='localhost')
    credentials = UserCredentialDataClass(public_id='user', api_secret='password')
    """Необходимо для работы из python кода"""
    client = Client()
    client.login(credentials)

    answer = await client.charge_card(charge_info)

    schema = Response()
    responce = schema.dump(answer.data)
    return responce


if __name__ == '__main__':
    asyncio.run(main())
