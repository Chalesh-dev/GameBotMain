from bson import json_util

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


# MULTI_TAP = [200, 500, 2000, 5000, 20_000, 75_000, 200_000, 300_000, 500_000, 750_000, 1_250_000, 2_500_000]
# SPEED = [200, 500, 2000, 5000, 20_000, 75_000, 200_000, 300_000, 500_000, 750_000, 1_250_000, 2_500_000]
# LIMIT = [200, 500, 2000, 5000, 20_000, 75_000, 200_000, 300_000, 500_000, 750_000, 1_250_000, 2_500_000]
# BOT = [200_000]

LEVELS = {
    "multi_tap": [200, 500, 2000, 5000, 20_000, 75_000, 200_000, 300_000, 500_000, 750_000, 1_250_000, 2_500_000],
    "limit": [200, 500, 2000, 5000, 20_000, 75_000, 200_000, 300_000, 500_000, 750_000, 1_250_000, 2_500_000],
    "speed": [1000, 20_000, 50_000, 125_000, 250_000],
    "bot": [200_000]

}

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
    ref_to: list[RefData]
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
            balance=1000000,
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

    a = users.insert_one(data)
    # print(a,"shah")


space.drop_collection(users)


# set_dummy_user_data(12)


def get_user_data(user_id: int) -> UserData:
    data = users.find_one({'user_id': user_id})
    # print(type(json.loads(json_util.dumps(data))))
    return json.loads(json_util.dumps(data))


def get_data(websocket: WebSocketServerProtocol) -> UserData:
    #todo: handle energy for the offline account
    uid = websocket.path[1:]
    user_data = get_user_data(uid)

    if user_data is not None:
        return user_data
    else:
        # todo: omit dummy data
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


async def tp_balance_emit(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.BALANCE, BalanceOutboundData(balance=user_data['balance']['balance'],
                                                               multi_tap=2, auto_bot=True, guru=False,
                                                               league=3), True)


async def tp_energy_emit(**kwargs: Unpack[TopicEmitter]):
    # todo: handle offline energy calculation
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    # pprint.pprint(user_data)
    await send_wss_msg(ws, Topics.ENERGY, EnergyOutboundData(energy=user_data["in_game"]["energy"],
                                                             max_energy=user_data['boost']["limit"] * 1000,
                                                             energy_speed=user_data['boost']["speed"]), True)


async def tp_bot_earning_emit(**kwargs: Unpack[TopicEmitter]):
    # todo: handle offline energy calculation and bot earning this is dummy data here
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.BOT_EARNING, BotEarningOutboundData(earning=1000), True)


async def tp_special_boost_emit(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.SPECIAL_BOOST,
                       SpecialBoosterOutboundData(max_special_boost=3,
                                                  guru_left=user_data["special_boost"]["guru"]["left"],
                                                  next_update=int((time.time() / 86400) + 1) * 86400,
                                                  full_tank_left=user_data["special_boost"]["refill"]["left"]), True)


async def tp_stats_emit(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.STATS,
                       StatsOutboundData(total_touches=100000,
                                         total_shares="76.2 T",
                                         total_players=2846128,
                                         online_players=2131247,
                                         daily_players=21421432), True)


async def tp_task_stat_emit(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    # todo: bot integration with this empty arrays - it is not in database!!!!! make its integration on mongodb
    await send_wss_msg(ws, Topics.TASKS_STATUS, TaskStatus(check=[], claim=[]), True)


async def tp_referral_emit(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.REFERRAL, ReferralOutboundData(
        invite_link=f"https://telegram.me/{BOT_USERNAME}?start={user_data['user_id']}",
        #todo: !!!
        # my_refs=user_data['referral']["ref_to"],
        my_refs=[RefData(
                            league=2,
                            name="Mahmud Ahmadi Nijad",
                            total_amount=45_500,
                            referrer_link="https://t.me/ahmadinejad"
                        )],
        ref_num=len(user_data['referral']["ref_to"])
    ), True)


async def tp_boost_emit(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    await send_wss_msg(ws, Topics.BOOST,
                       BoosterOutboundData(
                           multi_tap=BoosterDetailOutboundData(
                               level=user_data["boost"]["multi_tap"],
                               is_max=False,  # todo!
                               next_level_price=750  # todo !
                           ),
                           energy_limit=BoosterDetailOutboundData(
                               level=user_data["boost"]["limit"],
                               is_max=False,  # todo!
                               next_level_price=5000  # todo !
                           ),
                           recharging_speed=BoosterDetailOutboundData(
                               level=user_data["boost"]["speed"],
                               is_max=False,  # todo!
                               next_level_price=1500  # todo!
                           ),
                           tap_bot=BoosterDetailOutboundData(
                               level=user_data["boost"]["tap_bot"],
                               is_max=False,  # todo!
                               next_level_price=200_000  # todo!
                           )
                       ), True)


async def tp_tasks_emit(**kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    # print(REFERRALS[user_data["referral"]["current"]])
    await send_wss_msg(ws, Topics.TASKS, TasksOutboundData(
        special_tasks=[TasksSpecialOutboundData(
            title=x["title"],
            uuid=x["uuid"],
            link=x["link"],
            reward=x["reward"],
            status=True,
            claimed=TASKS.index(x) in user_data["special_task"]["claimed_tasks"]
        ) for x in TASKS],
        leagues=TasksLeagueOutboundData(
            unclaimed=[LEAGUES.index(x) for x in user_data["league_task"]["tasks"][:LEAGUES.index(user_data['in_game']['league'])]],
            claimed=user_data["league_task"]["claimed_tasks"],
            current=LEAGUES.index(user_data["in_game"]["league"]),
            total_amount=user_data["user"]["amount"]
        ),
        referral=TasksReferralOutboundData(
            unclaimed=[REFERRALS.index(x) for x in user_data["ref_task"]["tasks"]],
            claimed=[REFERRALS.index(x) for x in user_data["ref_task"]["claimed_tasks"]],
            current=user_data["referral"]["current"],
            total_referral=len(user_data["referral"]["ref_to"]),
        ),
    ), True)


async def tp_activate_callback(*args, **kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    # todo: db update or game instance update
    await send_wss_msg(ws, Topics.ACTIVATE, ActivateOutboundResponse(
        unit=args[0],
        new_left=user_data['special_boost'][args[0]]['left'] - 1,
        finish_time=user_data['special_boost'][args[0]]['next_update'],
        energy=user_data["in_game"]["energy"]
    ))


async def tp_upgrade_callback(*args, **kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    # todo: db update or game instance update and balance update
    if args[0] != "bot":
        new_level = user_data['boost'][args[0]]
        is_max = len(LEVELS[args[0]]) == new_level
        await send_wss_msg(ws, Topics.UPGRADE, UpgradeOutboundData(
            is_max=is_max,
            new_level=new_level,
            next_level_price=LEVELS[args[0]][new_level] if not is_max else 0,
            upgraded_unit=args[0],
            balance=user_data['balance']["balance"] - LEVELS[args[0]][new_level - 1]
        ))
    else:
        is_max = True
        await send_wss_msg(ws, Topics.UPGRADE, UpgradeOutboundData(
            is_max=is_max,
            new_level=1,
            next_level_price=0,
            upgraded_unit=args[0],
            balance=user_data['balance']["balance"] - LEVELS[args[0]][0]
        ))


async def tp_task_status_callback(*args, **kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    # todo: db update or game instance update and balance update
    await send_wss_msg(ws, Topics.TASKS_STATUS, TaskStatus(
        check=[],  # todo
        claim=[]  # todo
    ))


async def tp_tap_callback(*args, **kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    # todo: db update or game instance update and balance update
    await send_wss_msg(ws, Topics.TAP, TapOutboundResponse(
        balance=user_data['balance']["balance"] + 1,
        amount=user_data['user']['amount'] + 1,
        energy=user_data['in_game']["energy"]
    ))


async def tp_claim_callback(*args, **kwargs: Unpack[TopicEmitter]):
    ws = kwargs["ws"]
    user_data = kwargs["user_data"]
    type_of_claim = args[0]
    id_claim: int = args[1]
    # todo: db update or game instance update and balance update
    if type_of_claim == "league":
        user_data["league_task"]["claimed_tasks"].append(id_claim)
        unclaimed = list(range(0, len(LEAGUES)))
        for x in user_data["league_task"]["claimed_tasks"]:
            unclaimed.remove(x)
        await send_wss_msg(ws, Topics.CLAIM_LEAGUE, ClaimLeagueOutboundResponse(
            leagues=TasksLeagueOutboundData(
                unclaimed=unclaimed,
                claimed=[LEAGUES.index(x) for x in user_data["league_task"]["claimed_tasks"]],
                current=LEAGUES.index(user_data["in_game"]["league"]),
                total_amount=user_data['user']['amount'] + LEAGUES[id_claim]["reward"],
            ),
            balance=user_data['balance']['balance'] + LEAGUES[id_claim]["reward"],
            balance_up=LEAGUES[id_claim]["reward"]
        ))
    else: # todo whole section is wrong!!!!!
        await send_wss_msg(ws, Topics.TASKS, TasksOutboundData(
            balance_up=100231083, # todo
            balance = 2986489156, # todo
            special_tasks=[
                TasksSpecialOutboundData(
                    title="Join and Unlock The Impossible",
                    uuid=uuid.uuid4().__str__(),
                    link="https://google.com",
                    reward=100_000,
                    status=False,
                    claimed=True,
                ),
                TasksSpecialOutboundData(
                    title="Fap instead of Tap",
                    uuid=uuid.uuid4().__str__(),
                    link="https://xvideos.com",
                    reward=696969,
                    status=True,
                    claimed=True
                )
            ],
            leagues=TasksLeagueOutboundData(
                unclaimed=[0, 1],
                claimed=[3, 2],
                current=4,
                total_amount=500000
            ),
            referral=TasksReferralOutboundData(
                unclaimed=[0, 1, 4],
                claimed=[2, 3],
                current=5,
                total_referral=30,
            ),
        ),
                           status=True
                           )

async def handler(ws: WebSocketServerProtocol):
    user_data = get_data(ws)
    # pprint.pprint(user_data)
    if not user_data:
        logging.warning("user is not registered in the bot")
        return

    logging.info(f"user Connected! Telegram Id: {user_data["user_id"]} Client IP: {ws.remote_address[0]}")
    await tp_balance_emit(ws=ws, user_data=user_data)
    await tp_boost_emit(ws=ws, user_data=user_data)
    await tp_energy_emit(ws=ws, user_data=user_data)
    await tp_bot_earning_emit(ws=ws, user_data=user_data)
    await tp_special_boost_emit(ws=ws, user_data=user_data)
    await tp_stats_emit(ws=ws, user_data=user_data)
    await tp_tasks_emit(ws=ws, user_data=user_data)
    await tp_task_stat_emit(ws=ws, user_data=user_data)
    await tp_referral_emit(ws=ws, user_data=user_data)

    async for message in ws:
        data = json.loads(message)
        request = data["request"]
        topic = data["topic"]
        if topic == "activate":
            await tp_activate_callback(request, ws=ws, user_data=user_data)
        elif topic == "upgrade":
            await tp_upgrade_callback(request, ws=ws, user_data=user_data)
        elif topic == "tap":
            await tp_tap_callback(request, ws=ws, user_data=user_data)
        elif topic == "tasks status":
            await tp_task_status_callback(request, ws=ws, user_data=user_data)
        elif "claim" in topic:
            await tp_claim_callback(topic.replace("claim ",""), request, ws=ws, user_data=user_data)


async def main():
    async with serve(host=HOST, port=PORT, ws_handler=handler):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
