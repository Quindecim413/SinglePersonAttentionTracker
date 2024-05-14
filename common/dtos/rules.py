from datetime import datetime
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

from common.dtos.utils import AttentionRuleId, BaseConfig


@dataclass(frozen=True, config=BaseConfig)
class RuleRefreshInfo:
    id:AttentionRuleId
    refresh_time:datetime

RuleRefreshInfoAdapter = TypeAdapter(RuleRefreshInfo)
RulesRefreshInfoListAdapter = TypeAdapter(list[RuleRefreshInfo])