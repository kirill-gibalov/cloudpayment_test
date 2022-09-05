from dataclasses import dataclass
from typing import Any, Optional

from marshmallow import Schema, fields


class UserCredential(Schema):
    public_id = fields.Str()
    api_secret = fields.Str()


class Response(Schema):
    Success = fields.Bool()
    Message = fields.Str()


@dataclass
class UserCredentialDataClass:
    public_id: str
    api_secret: str


@dataclass
class ChargeCard:
    cryptogram: Any
    amount: int
    currency: str
    name: str
    ip_address: str
    invoice_id: Optional[str] = None
    description: Optional[str] = None
    account_id: Optional[str] = None
    email: Optional[str] = None
    data: Optional[str] = None
    service_fee: Optional[str] = None


@dataclass
class Response:
    success: str
    message: str
