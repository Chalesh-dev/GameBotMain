import pprint
from typing import TypedDict, Unpack, Required, NotRequired
import asyncio
import json
import logging
import os
import random
import time
import uuid
from functools import cache
from pymongo import MongoClient
from dotenv import load_dotenv
from websockets import serve, WebSocketServerProtocol

from topics import *

# from topics import Topics
logging.basicConfig(
    format="%(asctime)s --- SpaceX Swap --- %(message)s",
    level=logging.INFO,
)

load_dotenv()

PORT = os.getenv('PORT')
HOST = os.getenv('HOST')
BOT_USERNAME = os.getenv("BOT_USERNAME")

client = MongoClient("localhost", 27017)
space = client["space-x-bot"]
users = space["users"]


# space.drop_collection(users)

class ReferralLeagueData(TypedDict):
    title: str
    reward: int
    threshold: int


REFERRALS = [
    ReferralLeagueData(title="invite 1 friends", reward=25_000, threshold=1),
    ReferralLeagueData(title="invite 3 friends", reward=50_000, threshold=3),
    ReferralLeagueData(title="invite 10 friends", reward=200_000, threshold=10),
    ReferralLeagueData(title="invite 25 friends", reward=250_000, threshold=25),
    ReferralLeagueData(title="invite 50 friends", reward=300_000, threshold=50),
    ReferralLeagueData(title="invite 100 friends", reward=500_000, threshold=100),
    ReferralLeagueData(title="invite 500 friends", reward=2_000000, threshold=500),
    ReferralLeagueData(title="invite 1000 friends", reward=2_500000, threshold=1000),
    ReferralLeagueData(title="invite 10000 friends", reward=10_000000, threshold=10000),
    ReferralLeagueData(title="invite 100000 friends", reward=100_000000, threshold=100000),
]

LEAGUES = [
    ReferralLeagueData(title="Wooden League", reward=500, threshold=0),
    ReferralLeagueData(title="Bronze League", reward=1000, threshold=1),
    ReferralLeagueData(title="Silver League", reward=5000, threshold=5000),
    ReferralLeagueData(title="Gold League", reward=10000, threshold=50000),
    ReferralLeagueData(title="Platinum League", reward=25000, threshold=250000),
]


class TaskData(TypedDict):
    title: str
    uuid: str
    link: str
    reward: int


TASKS = [
    TaskData(title="Google", reward=500, link="https://google.com", uuid=uuid.uuid4().__str__()),
    TaskData(title="Ice me Out", reward=50000, link="https://fbi.gov", uuid=uuid.uuid4().__str__()),
    TaskData(title="Intelligence", reward=500554, link="https://cia.gov", uuid=uuid.uuid4().__str__()),
]


class BaseUserRef(TypedDict):
    user_id: int
    name: str
    link: str
    amount: int


class BaseUser(TypedDict):
    name: str
    username: str
    ip: str
    amount: int


class UserReferralData(TypedDict):
    ref_from: BaseUserRef
    ref_to: list[BaseUser]
    ref_link: str
    current: int


class UserReferralTaskData(TypedDict):
    claimed_tasks: list[ReferralLeagueData]
    tasks: list[ReferralLeagueData]


class UserLeagueData(TypedDict):
    claimed_tasks: list[ReferralLeagueData]
    tasks: list[ReferralLeagueData]


class UserTaskData(TypedDict):
    claimed_tasks: list[TaskData]
    tasks: list[TaskData]


class UserBalance(TypedDict):
    balance: int
    total_click: int
    rewards: int
    ref_direct_rewards: int


class UserBoosts(TypedDict):
    multi_tap: int
    limit: int
    speed: int
    tap_bot: bool


class SpecialPerks(TypedDict):
    left: int
    next_update: int


class UserSpecialBoost(TypedDict):
    guru: SpecialPerks
    refill: SpecialPerks


class UserInGameData(TypedDict):
    last_click: int
    league: ReferralLeagueData
    energy: int
    last_online: int


class UserData(TypedDict):
    _id: NotRequired[str]
    user_id: int
    user: BaseUser
    referral: UserReferralData
    ref_task: UserReferralTaskData
    special_task: UserTaskData
    league_task: UserLeagueData
    in_game: UserInGameData
    special_boost: UserSpecialBoost
    boost: UserBoosts
    balance: UserBalance


def set_dummy_user_data(user_id: int):
    claimed_ref_tasks = [REFERRALS[0]]
    claimed_league_tasks = [LEAGUES[0]]
    claimed_special_tasks = [TASKS[0]]
    data = UserData(
        user_id=user_id,
        user=BaseUser(
            name="Ali",
            username="@bor420",
            ip="1.1.1.1",
            amount=0,
        ),
        in_game=UserInGameData(
            last_click=int(time.time()),
            league=LEAGUES[2],
            energy=1000,
            last_online=int(time.time()),
        ),
        league_task=UserLeagueData(
            claimed_tasks=claimed_league_tasks,
            tasks=[x for x in LEAGUES if x not in claimed_league_tasks]
        ),
        ref_task=UserReferralTaskData(
            claimed_tasks=claimed_ref_tasks,
            tasks=[x for x in REFERRALS if x not in claimed_ref_tasks]
        ),
        special_task=UserTaskData(
            claimed_tasks=claimed_special_tasks,
            tasks=[x for x in TASKS if x not in claimed_special_tasks]
        ),
        boost=UserBoosts(
            multi_tap=1,
            limit=1,
            speed=1,
            tap_bot=False
        ),
        balance=UserBalance(
            balance=0,
            total_click=0,
            rewards=0,
            ref_direct_rewards=0,
        ),
        special_boost=UserSpecialBoost(
            guru=SpecialPerks(
                left=3,
                next_update=(int(time.time() / 86400) + 1) * 86400,
            ),
            refill=SpecialPerks(
                left=3,
                next_update=(int(time.time() / 86400) + 1) * 86400,
            ),
        ),
        referral=UserReferralData(
            ref_from=BaseUserRef(
                link="https://t.me/bor420",
                user_id=10,
                name="Ali",
                amount=0
            ),
            ref_to=[],
            ref_link=f"https://telegram.me/{BOT_USERNAME}?start={user_id}",
            current=2
        )
    )
    pprint.pprint(data)
    users.insert_one(data)


space.drop_collection(users)
set_dummy_user_data(12)


def get_user_data(user_id: int) -> UserData:
    data: UserData = users.find_one({'user_id': user_id})
    return data


def get_data(websocket: WebSocketServerProtocol) -> UserData:
    #todo: handle energy for the offline account
    uid = websocket.path[1:]
    user_data = get_user_data(uid)
    if user_data is not None:
        return user_data
    else:
        set_dummy_user_data(uid)
        user_data = get_user_data(uid)
        return user_data


async def send_wss_msg(websocket: WebSocketServerProtocol, topic: Topics, result: dict, status: bool = True) -> bool:
    await websocket.send(
        json.dumps(
            OutboundData(
                topic=topic.value,
                status=status,
                result=result,
            )
        )
    )
    return True


class TopicEmitter(TypedDict):
    ws: Required[WebSocketServerProtocol]
    user_data: Required[UserData]


async def topic_balance_emitter(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.BALANCE, BalanceOutboundData(balance=user_data['balance']['balance'],
                                                               multi_tap=2, auto_bot=True, guru=False,
                                                               league=3), True)


async def topic_energy_emitter(**kwargs: Unpack[TopicEmitter]):
    # todo: handle offline energy calculation
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.ENERGY, EnergyOutboundData(energy=user_data.in_game.energy,
                                                             max_energy=user_data.boost.limit * 500,
                                                             energy_speed=user_data.boost.energy), True)


async def topic_bot_earning_emitter(**kwargs: Unpack[TopicEmitter]):
    # todo: handle offline energy calculation and bot earning this is dummy data here
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.BOT_EARNING, BotEarningOutboundData(earning=1000), True)


async def topic_special_boost_emitter(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.SPECIAL_BOOST,
                       SpecialBoosterOutboundData(max_special_boost=3, guru_left=user_data.special_boost.guru.left,
                                                  next_update=int((time.time() / 86400) + 1) * 86400,
                                                  full_tank_left=user_data.special_boost.refill.left), True)


async def topic_stats_emitter(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.STATS,
                       StatsOutboundData(total_touches=100000,
                                         total_shares="76.2 T",
                                         total_players=2846128,
                                         online_players=2131247,
                                         daily_players=21421432), True)


async def topic_boost_emitter(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.BOOST,
                       BoosterOutboundData(
                           multi_tap=BoosterDetailOutboundData(
                               level=user_data.boost.multi_tap,
                               is_max=False,  # todo!
                               next_level_price=750  # todo !
                           ),
                           energy_limit=BoosterDetailOutboundData(
                               level=user_data.boost.limit,
                               is_max=False,  # todo!
                               next_level_price=5000  # todo !
                           ),
                           recharging_speed=BoosterDetailOutboundData(
                               level=user_data.boost.speed,
                               is_max=False,  # todo!
                               next_level_price=1500  # todo!
                           ),
                           tap_bot=BoosterDetailOutboundData(
                               level=user_data.boost.tap_bot,
                               is_max=False,  # todo!
                               next_level_price=200_000  # todo!
                           )
                       ), True)


async def topic_tasks_emitter(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.TASKS, TasksOutboundData(
        special_tasks=[TasksSpecialOutboundData(
            title=x.title,
            uuid=x.uuid,
            link=x.link,
            reward=x.reward,
            status=True,
            claimed=TASKS.index(x) in user_data.special_task.claimed_tasks
        ) for x in TASKS],
        leagues=TasksLeagueOutboundData(
            unclaimed=[x for x in user_data.league_task.tasks[:user_data.in_game.league]],
            claimed=user_data.league_task.claimed_tasks,
            current=user_data.in_game.league,
            total_amount=user_data.user.amount
        ),
        referral=TasksReferralOutboundData(
            unclaimed=[x for x in user_data.ref_task.tasks],
            claimed=user_data.ref_task.claimed_tasks,
            current=user_data.referral.current,
            total_referral=len(user_data.referral.ref_to),
        ),
    ), True)


async def

async def handler(ws: WebSocketServerProtocol):
    user_data = get_data(ws)
    if not user_data:
        logging.warning("user is not registered in the bot")
    else:
        logging.info(f"user Connected! Telegram Id: {user_data["user_id"]} Client IP: {ws.remote_address[0]}")
        await topic_balance_emitter(ws=ws, user_data=user_data)
        await topic_energy_emitter(ws=ws, user_data=user_data)
        await topic_bot_earning_emitter(ws=ws, user_data=user_data)
        await topic_special_boost_emitter(ws=ws, user_data=user_data)
        await topic_stats_emitter(ws=ws, user_data=user_data)
        await topic_tasks_emitter(ws=ws, user_data=user_data)


async def main():
    async with serve(host=HOST, port=PORT, ws_handler=handler):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
