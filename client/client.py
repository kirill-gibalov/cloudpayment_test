import asyncio
import time
import random

from aiohttp import BasicAuth, ClientResponse
from typing import Any, Dict
from itertools import chain

from client.abstract_client import AbstractInteractionClient
from client.schema import UserCredential, UserCredentialDataClass, ChargeCard, Response


class Client(AbstractInteractionClient):

    CONNECTOR = None
    SERVICE = None
    BASE_URL = 'https://api.cloudpayments.ru/'

    def __init__(self):
        super().__init__()
        self.api_secret = None
        self.public_id = None

    def login(self, credentials: dict or UserCredential):
        if type(credentials) == dict:
            self.public_id = credentials.get('public_id')
            self.api_secret = credentials.get('api_secret')
        elif type(credentials) == UserCredentialDataClass:
            self.public_id = credentials.public_id
            self.api_secret = credentials.api_secret

    def _get_session_kwargs(self) -> Dict[str, Any]:
        """Returns kwargs necessary for creating a session instance."""
        kwargs = {
            'connector': self.CONNECTOR,
            'connector_owner': False,
            'trust_env': True,
        }
        if self.default_timeout:
            kwargs['timeout'] = self.default_timeout

        kwargs['auth'] = BasicAuth(self.public_id, self.api_secret)
        return kwargs

    async def _make_request(
            self,
            interaction_method: str,
            method: str,
            url: str,
            **kwargs: Any
    ) -> ClientResponse:
        """Wraps ClientSession.request allowing retries, updating metrics."""

        kwargs.setdefault('headers', {})

        response_time = 0.0
        response = exc = None
        for retry_number, retry_delay in enumerate(chain((0.0,), self.REQUEST_RETRY_TIMEOUTS)):
            if retry_delay:
                delay = retry_delay - response_time
                await asyncio.sleep(delay + random.uniform(-delay / 2, delay / 2))

            exc = None
            response = None
            before = time.monotonic()
            try:
                response = await self.session.request(method, url, auth=self.session.auth, **kwargs)

                assert response is not None
                success = True
                await self.session.connector.close()
                await self.session.close()
            except Exception as e:
                exc = e
                success = False

            response_time = time.monotonic() - before

            if success or isinstance(exc, asyncio.TimeoutError):
                break

        if exc:
            raise exc

        return response

    async def charge_card(self, charge_info: ChargeCard):
        params = {
            'Amount': charge_info.amount,
            'Currency': charge_info.currency,
            'IpAddress': charge_info.ip_address,
            'Name': charge_info.name,
            'CardCryptogramPacket': charge_info.cryptogram
        }
        if charge_info.invoice_id is not None:
            params['InvoiceId'] = charge_info.invoice_id
        if charge_info.description is not None:
            params['Description'] = charge_info.description
        if charge_info.account_id is not None:
            params['AccountId'] = charge_info.account_id
        if charge_info.email is not None:
            params['Email'] = charge_info.email
        if charge_info.service_fee is not None:
            params['PayerServiceFee'] = charge_info.service_fee
        if charge_info.data is not None:
            params['JsonData'] = charge_info.data

        endpoint = 'payments/cards/charge'
        response = await self.post(interaction_method='don`t know', url=self.BASE_URL + endpoint, data=params)
        return response
