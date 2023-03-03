import sc2
from sc2.main import run_game
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.data import Difficulty, Race


class MyBot(BotAI):
    async def on_step(self, iteration: int):
        print(f"This is my bot in iteration {iteration}!")


run_game(
    sc2.maps.get("AcropolisLE"),
    [Bot(Race.Zerg, MyBot()), Computer(Race.Zerg, Difficulty.Hard)],
    realtime=False,
)
