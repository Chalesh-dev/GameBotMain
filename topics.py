from typing import TypedDict, Literal
from enum import Enum


class Topics(Enum):
    ACTIVATE = "activate"
    ENERGY = 'energy'
    BALANCE = "balance"
    BOT_EARNING = "bot earning"
    STATS = "stats"
    SPECIAL_BOOST = "special boost"
    BOOST = "boost"
    TASKS = "tasks"
    REFERRAL = "referral"
    TASKS_STATUS = "task status"
    CLAIM_TASK = "claim task"


class EnergyOutboundData(TypedDict):
    energy: int
    max_energy: int
    energy_speed: int


class BalanceOutboundData(TypedDict):
    balance: int
    multi_tap: int
    guru: bool
    auto_bot: bool
    league: int


class BotEarningOutboundData(TypedDict):
    earning: int


class StatsOutboundData(TypedDict):
    total_touches: int
    total_shares: str
    total_players: int
    online_players: int
    daily_players: int


class SpecialBoosterOutboundData(TypedDict):
    max_special_boost: int
    guru_left: int
    full_tank_left: int
    next_update: int


class BoosterDetailOutboundData(TypedDict):
    level: int
    is_max: bool
    next_level_price: int


class BoosterOutboundData(TypedDict):
    multi_tap: BoosterDetailOutboundData
    energy_limit: BoosterDetailOutboundData
    recharging_speed: BoosterDetailOutboundData
    tap_bot: BoosterDetailOutboundData


class TasksSpecialOutboundData(TypedDict):
    uuid: str
    title: str
    reward: int
    link: str
    status: bool
    claimed: bool


class TasksLeagueOutboundData(TypedDict):
    unclaimed: list[int]
    claimed: list[int]
    current: int
    total_amount: int


class TasksReferralOutboundData(TypedDict):
    unclaimed: list[int]
    claimed: list[int]
    current: int
    total_referral: int


class TasksOutboundData(TypedDict):
    special_tasks: list[TasksSpecialOutboundData]
    leagues: TasksLeagueOutboundData
    referral: TasksReferralOutboundData


class RefData(TypedDict):
    name: str
    league: int
    total_amount: int
    referrer_link:str


class ReferralOutboundData(TypedDict):
    invite_link: str
    my_refs: list[RefData]
    ref_num: int



class UpgradeOutboundData(TypedDict):
    upgraded_unit: Literal["multi_tap", "tap_bot", "limit", "speed"]
    new_level: int
    is_max: bool
    next_level_price: int
    balance: int


class ActivateOutboundResponse(TypedDict):
    unit: Literal["guru", "refill"]
    new_left: int
    finish_time: int
    energy: int


class TapOutboundResponse(TypedDict):
    balance: int
    amount: int
    energy: int


class CheckTaskOutboundResponse(TypedDict):
    balance_up: int
    new_balance: int


class ClaimLeagueOutboundResponse(TypedDict):
    unclaimed: list[int]
    claimed: list[int]
    current: int
    total_amount: int
    balance: int
    balance_up: int


class ClaimReferralOutboundResponse(TypedDict):
    unclaimed: list[int]
    claimed: list[int]
    current: int
    total_referral: int
    balance: int
    balance_up: int


class OutboundData(TypedDict):
    topic: Topics
    result: object
    status: bool


class TaskStatus(TypedDict):
    claim: list[str]  # uuid to return
    check: list[str]  # uuid to return
