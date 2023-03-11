import sc2
from sc2.main import run_game
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId


class MyBot(BotAI):
    async def on_step(self, iteration: int):
        # print(f"This is my bot in iteration {iteration}, workers: {self.workers}, idle workers: {self.workers.idle}, supply: {self.supply_used}/{self.supply_cap}")
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount},", \
              f"minerals: {self.minerals}, gas: {self.vespene}, cannons: {self.structures(UnitTypeId.PHOTONCANNON).amount},", \
              f"pylons: {self.structures(UnitTypeId.PYLON).amount}, nexus: {self.structures(UnitTypeId.NEXUS).amount}", \
              f"gateways: {self.structures(UnitTypeId.GATEWAY).amount}, cybernetics cores: {self.structures(UnitTypeId.CYBERNETICSCORE).amount}", \
              f"stargates: {self.structures(UnitTypeId.STARGATE).amount}, voidrays: {self.units(UnitTypeId.VOIDRAY).amount}, supply: {self.supply_used}/{self.supply_cap}")

run_game(
    sc2.maps.get("AcropolisLE"),
    [Bot(Race.Zerg, MyBot()), Computer(Race.Zerg, Difficulty.Hard)],
    realtime=True,
)
