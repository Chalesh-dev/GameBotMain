from typing_extensions import TypedDict, NotRequired


class UserData(TypedDict):
    user_id: int
    energy: int
    balance: int
    total_amount: int
    total_clicks: int
    last_clicks: int
    limit_level: int
    speed_level: int
    multi_tap_level: int
    auto_bot: bool
    guru_used: int
    refill_used: int
    claimed_tasks: list[int]
    claimed_leagues: list[int]
    claimed_ref: list[int]
    referrals: list[int]
    last_update: int
    tap_bot_earning: int