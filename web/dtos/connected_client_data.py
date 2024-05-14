from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

from common.dtos.utils import BaseConfig



@dataclass(frozen=True, config=BaseConfig)
class ConnectedClientData:
    sid:str

ConnectedClientDataAdapter = TypeAdapter(ConnectedClientData)

