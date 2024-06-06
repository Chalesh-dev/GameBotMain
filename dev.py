import asyncio
import json
import logging
import os
import pathlib
import random
import time
import uuid
import ssl
from dotenv import load_dotenv
from websockets import serve, WebSocketServerProtocol

from topics import *

logging.basicConfig(
    format="%(asctime)s --- ChaleshSoft --- %(message)s",
    level=logging.INFO,
)

load_dotenv()

PORT = os.getenv('PORT')
HOST = os.getenv('HOST')

b = uuid.uuid4().__str__()
d = uuid.uuid4().__str__()
# todo: pend?!?!?!
pend = False


async def handler(websocket: WebSocketServerProtocol):
    global pend

    user_id = int(websocket.path[1:])
    print(user_id)
    logging.info(f"user Connected! Telegram Id: {user_id} Client IP: {websocket.remote_address[0]}")

    await websocket.send(
        json.dumps(
            OutboundData(
                topic="balance",
                result=BalanceOutboundData(
                    balance=1000000000,
                    multi_tap=2,
                    auto_bot=True,
                    guru=False,
                    league=3
                ),
                status=True
            )
        )
    )
    await websocket.send(
        json.dumps(
            OutboundData(
                topic="energy",
                result=EnergyOutboundData(
                    energy=1515,
                    max_energy=7523,
                    energy_speed=158
                ),
                status=True
            )
        )
    )
    await websocket.send(
        json.dumps(
            OutboundData(
                topic="bot earning",
                result=BotEarningOutboundData(
                    earning=6969
                ),
                status=True
            )
        )
    )

    await websocket.send(
        json.dumps(
            OutboundData(
                topic="special boost",
                result=SpecialBoosterOutboundData(
                    max_special_boost=3,
                    guru_left=1,
                    next_update=int((time.time() / 86400) + 1) * 86400,
                    full_tank_left=3,
                ),
                status=True
            )
        )
    )
    await websocket.send(
        json.dumps(
            OutboundData(
                topic="stats",
                result=StatsOutboundData(
                    total_touches=100000,
                    total_shares="76.2 T",
                    total_players=2846128,
                    online_players=2131247,
                    daily_players=21421432
                ),
                status=True
            )
        )
    )
    await websocket.send(
        json.dumps(
            OutboundData(
                topic="boost",
                result=BoosterOutboundData(
                    multi_tap=BoosterDetailOutboundData(
                        level=2,
                        is_max=False,
                        next_level_price=750
                    ),
                    energy_limit=BoosterDetailOutboundData(
                        level=2,
                        is_max=False,
                        next_level_price=225
                    ),
                    recharging_speed=BoosterDetailOutboundData(
                        level=2,
                        is_max=False,
                        next_level_price=650
                    ),
                    tap_bot=BoosterDetailOutboundData(
                        level=1,
                        is_max=False,
                        next_level_price=200_000
                    )
                ),
                status=True
            )
        )
    )

    await websocket.send(
        json.dumps(
            OutboundData(
                topic="tasks",
                result=TasksOutboundData(
                    special_tasks=[
                        TasksSpecialOutboundData(
                            title="Join and Unlock The Impossible",
                            uuid=b,
                            link="https://google.com",
                            reward=100_000,
                            status=False,
                            claimed=False,
                        ),
                        TasksSpecialOutboundData(
                            title="Fap instead of Tap",
                            uuid=d,
                            link="https://xvideos.com",
                            reward=696969,
                            status=True,
                            claimed=True
                        )
                    ],
                    leagues=TasksLeagueOutboundData(
                        unclaimed=[0,1,2],
                        claimed=[3],
                        current=4,
                        total_amount=22000
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
        )
    )

    # todo : on app render
    await websocket.send(
        json.dumps(
            OutboundData(
                topic="tasks status",
                status=True,
                result=TaskStatus(
                    check=[],
                    claim=[d, b]
                ),
            )
        )
    )

    await websocket.send(
        json.dumps(
            OutboundData(
                topic="referral",
                result=ReferralOutboundData(
                    invite_link="https://t.me/invite_link",
                    my_refs=[
                        RefData(
                            league=2,
                            name="Mahmud Ahmadi Nijad",
                            total_amount=45_500,
                            referrer_link="https://t.me/ahmadinejad"
                        ),
                        RefData(
                            league=2,
                            name="Ebram raisi",
                            total_amount=85_000,
                            referrer_link="https://t.me/raisi"

                        )
                    ],
                    ref_num=1
                ),
                status=True
            )
        )
    )

    async for message in websocket:
        data = json.loads(message)
        request = data["request"]
        topic = data["topic"]
        if topic == "activate":
            # todo: validation
            if request == "guru":
                await websocket.send(
                    json.dumps(
                        OutboundData(
                            topic=topic,
                            result=ActivateOutboundResponse(
                                unit=request,
                                new_left=0,
                                finish_time=1727579000,
                                energy=1234),
                            status=True
                        )
                    )
                )
            elif request == "refill":
                # todo: validation
                await websocket.send(
                    json.dumps(
                        OutboundData(
                            topic=topic,
                            result=ActivateOutboundResponse(
                                unit=request,
                                new_left=0,
                                finish_time=1777777777,
                                energy=4999),
                            status=True
                        )
                    )
                )
            else:
                print("error activating! False unit!")
        elif topic == "upgrade":
            # todo: handling different
            await websocket.send(
                json.dumps(
                    OutboundData(
                        topic=topic,
                        status=True,
                        result=UpgradeOutboundData(
                            is_max=True,
                            new_level=random.randint(1, 10),
                            next_level_price=random.randint(1000, 500000),
                            upgraded_unit=request,
                            balance=random.randint(0, 10000000000)
                        )
                    )
                )
            )
        elif topic == "tap":
            await websocket.send(
                json.dumps(
                    OutboundData(
                        topic=topic,
                        status=True,
                        result=TapOutboundResponse(
                            balance=random.randint(29999999, 40000000),
                            amount=random.randint(2, 9009090),
                            energy=random.randint(0, 5000)
                        )
                    )
                )
            )
        elif topic == "tasks status":
            await websocket.send(
                json.dumps(
                    OutboundData(
                        topic=topic,
                        status=True,
                        result=TaskStatus(
                            check=[d],
                            claim=[]
                        ),
                    )
                )
            )
            pend = True

        #todo handle task pending before check
        elif topic == "task status":
            await websocket.send(
                json.dumps(
                    OutboundData(
                        topic=topic,
                        status=True,
                        result=TaskStatus(
                            check=[d],
                            claim=[b]
                        ),
                    )
                )
            )
        elif topic == "referral":
            refs = [
                {
                    "name": "ali",
                    "league": 4,
                    "total_amount": 580851
                },
                {
                    "name": "mina",
                    "league": 10,
                    "total_amount": 12423143253
                }
            ]
            await websocket.send(
                json.dumps(
                    OutboundData(
                        topic=topic,
                        status=True,
                        result=ReferralOutboundData(
                            invite_link="https://telegram.me/test_spx_bot?start=123",
                            my_refs=refs,
                            ref_num=len(refs),
                        ),
                    )
                )
            )



        elif topic == "claim task":
            # request is uuid
            # send balance also !!!!!
            # todo: this a is to set state of global a to reverse
            await websocket.send(json.dumps(
                OutboundData(
                    topic="tasks",
                    result=TasksOutboundData(
                        special_tasks=[
                            TasksSpecialOutboundData(
                                title="Join and Unlock The Impossible",
                                uuid=b,
                                link="https://google.com",
                                reward=100_000,
                                status=False,
                                claimed=True,
                            ),
                            TasksSpecialOutboundData(
                                title="Fap instead of Tap",
                                uuid=d,
                                link="https://xvideos.com",
                                reward=696969,
                                status=True,
                                claimed=True
                            )
                        ],
                        leagues=TasksLeagueOutboundData(
                            unclaimed=[0,1,2],
                            claimed=[],
                            current=3,
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
            ))

#
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# #
# localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# #
# ssl_context.load_cert_chain(localhost_pem)


async def main():
    async with serve(host=HOST, port=PORT, ws_handler=handler): # , ssl=ssl_context
        print(f"WebSocket is Serving on wss://{HOST}:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
