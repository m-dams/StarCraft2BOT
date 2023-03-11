from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
from examples.zerg import hydralisk_push, zerg_rush, onebase_broodlord
import random


class FourGateBot(BotAI):
    def __init__(self):
        self.build_step = 0
        self.cyberneticscore = False
        self.proxy_built = False

    async def on_step(self, iteration: int):
        await self.distribute_workers()
        all_supply_used = self.supply_used + self.already_pending(UnitTypeId.PROBE)
        if self.already_pending(UnitTypeId.PROBE) != 0:
            all_supply_used -= 1
        # print(all_supply_used)
        # workers_count = self.workers.amount + self.already_pending(UnitTypeId.PROBE)
        if iteration == 0:
            await self.chat_send("4-gate scrypted bot")
        nexus = self.townhalls.ready.random

        # if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
        #     nexuses = self.structures(UnitTypeId.NEXUS)
        #     abilities = await self.get_available_abilities(nexuses)
        #     for loop_nexus, abilities_nexus in zip(nexuses, abilities):
        #         if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
        #             loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
        #             break

        if all_supply_used < 14:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
                all_supply_used += 1

        if all_supply_used == 14:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON,
                                 near=nexus.position.towards(self.game_info.map_center, 5))
                self.build_step = 1

        if 14 <= all_supply_used < 16 and self.build_step == 1:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
                all_supply_used += 1

        if all_supply_used == 16 and self.build_step == 1:
            if self.can_afford(UnitTypeId.GATEWAY):
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.GATEWAY,
                                 near=pylon)
                self.build_step = 2

        if all_supply_used == 16 and self.build_step == 2:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
                all_supply_used += 1

        if all_supply_used == 17 and self.build_step == 2:
            for nexus in self.structures(UnitTypeId.NEXUS):
                vespenes = self.vespene_geyser.closer_than(15, nexus)
                for vespene in vespenes:
                    if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.already_pending(UnitTypeId.ASSIMILATOR):
                        await self.build(UnitTypeId.ASSIMILATOR, vespene)
                        self.build_step = 3

        if all_supply_used < 19 and self.build_step == 3:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
                all_supply_used += 1

        if all_supply_used == 19 and self.build_step == 3:
            if self.can_afford(UnitTypeId.GATEWAY):
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.GATEWAY,
                                 near=pylon)
                self.build_step = 4

        if all_supply_used < 22 and self.build_step == 4:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
                all_supply_used += 1

        if all_supply_used == 22 and self.build_step == 4:
            if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.CYBERNETICSCORE,
                                 near=pylon)

        if all_supply_used == 22 and self.already_pending(UnitTypeId.CYBERNETICSCORE) and self.build_step == 4:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON,
                                 near=nexus.position.towards(self.game_info.map_center, 12))
                self.build_step = 5

        if all_supply_used == 22 and self.build_step == 5:
            for nexus in self.structures(UnitTypeId.NEXUS):
                vespenes = self.vespene_geyser.closer_than(15, nexus)
                for vespene in vespenes:
                    if self.can_afford(UnitTypeId.ASSIMILATOR):
                        await self.build(UnitTypeId.ASSIMILATOR, vespene)
                if self.already_pending(UnitTypeId.ASSIMILATOR):
                    self.build_step = 6

        if all_supply_used == 22 and self.build_step == 6:
            if self.can_afford(UnitTypeId.GATEWAY):
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.GATEWAY,
                                 near=pylon)
                self.build_step = 7

        if self.already_pending_upgrade(
                UpgradeId.WARPGATERESEARCH) == 0 and self.build_step == 7:
            if self.can_afford(UpgradeId.WARPGATERESEARCH):
                cyberneticscore_ready = self.structures(UnitTypeId.CYBERNETICSCORE).ready
                if cyberneticscore_ready:
                    self.research(UpgradeId.WARPGATERESEARCH)
                    self.cyberneticscore = self.structures(UnitTypeId.CYBERNETICSCORE)[0]
                    await self.activate_chronoboost(self.cyberneticscore)
                    self.build_step = 8

        if self.cyberneticscore:
            if 1 > self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) > 0 and not self.cyberneticscore.has_buff(
                    BuffId.CHRONOBOOSTENERGYCOST):
                await self.activate_chronoboost(self.cyberneticscore)

        if all_supply_used < 26 and self.build_step == 8:
            for sg in self.structures(UnitTypeId.GATEWAY).ready.idle:
                if self.can_afford(UnitTypeId.STALKER):
                    sg.train(UnitTypeId.STALKER)
                    all_supply_used += 2

        if all_supply_used == 26 and self.build_step == 8:
            if self.can_afford(UnitTypeId.GATEWAY):
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.GATEWAY,
                                 near=pylon)
                self.build_step = 9

        if all_supply_used == 26 and self.build_step == 9:
            if self.can_afford(UnitTypeId.PYLON):
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.PYLON,
                                 near=pylon)
                self.build_step = 10

        if all_supply_used >= 26 and self.build_step == 10:
            for gw in self.structures(UnitTypeId.GATEWAY).ready.idle:
                gateways = self.structures(UnitTypeId.GATEWAY).ready.idle
                if self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 1:
                    abilities = await self.get_available_abilities(gateways)
                    if AbilityId.MORPH_WARPGATE in abilities:
                        for loop_nexus, abilities_nexus in zip(gateways, abilities):
                            if AbilityId.MORPH_WARPGATE in abilities_nexus:
                                loop_nexus(AbilityId.MORPH_WARPGATE, gw)
                                break
                elif self.can_afford(UnitTypeId.STALKER):
                    gw.train(UnitTypeId.STALKER)
                    all_supply_used += 2

        if all_supply_used >= 26 and self.build_step == 10:
            proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
            await self.warp_new_units(proxy)
            all_supply_used += 2

        supply_remaining = self.supply_cap - self.supply_used
        if supply_remaining < 8 and self.already_pending(UnitTypeId.PYLON) == 0:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)

        # if we have more than 3 STALKERS, let's attack!
        if self.units(UnitTypeId.STALKER).amount >= 10:
            if self.enemy_units:
                for st in self.units(UnitTypeId.STALKER).idle:
                    st.attack(random.choice(self.enemy_units))

            elif self.enemy_structures:
                for st in self.units(UnitTypeId.STALKER).idle:
                    st.attack(random.choice(self.enemy_structures))

            # otherwise attack enemy starting position
            else:
                for st in self.units(UnitTypeId.STALKER).idle:
                    st.attack(self.enemy_start_locations[0])

    async def activate_chronoboost(self, target):
        if not target.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            nexuses = self.structures(UnitTypeId.NEXUS)
            abilities = await self.get_available_abilities(nexuses)
            for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                    loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, target)
                    break

    async def warp_new_units(self, proxy):
        warpgates = self.structures(UnitTypeId.WARPGATE).ready
        for warpgate in warpgates:
            abilities = await self.get_available_abilities(warpgates)
            # all the units have the same cooldown anyway so let's just look at ZEALOT
            if AbilityId.WARPGATETRAIN_STALKER in abilities:
                pos = proxy.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    return
                warpgate.warp_in(UnitTypeId.STALKER, placement)

def main():
    # Human(Race.Protoss, "MKDMK", True),
    run_game(
        maps.get("AcropolisLE"),
        [Bot(Race.Protoss, FourGateBot()),
         Computer(Race.Zerg, Difficulty.Hard)],
        realtime=False,
    )


if __name__ == "__main__":
    main()

#   14	  0:18	  Pylon
#   16	  0:46	  Gateway
#   17	  0:53	  Assimilator
#   19	  1:11	  Gateway
#   22	  1:33	  Cybernetics Core
#   22	  1:35	  Pylon
#   22	  1:37	  Assimilator
#   22	  1:51	  Gateway
#   22	  2:05	  Warp Gate (Chrono Boost)
#   22	  2:11	  Stalker x2
#   26	  2:21	  Gateway
#   26	  2:27	  Pylon
#   26	  2:38	  Stalker x2
#   30	  2:49	  Sentry
#   32	  3:08	  Stalker x3
#   38	  3:45	  Pylon x2
#   38	  4:05	  Stalker x4
#   46	  4:12	  Pylon
#   46	  4:31	  Stalker x2
#   46	  4:33	  Sentry
#   46	  4:36	  Stalker
#   54	  4:54	  Pylon
#   54	  4:59	  Stalker x3
#   60	  5:12	  Stalker
#   60	  5:23	  Stalker
#   62	  5:29	  Stalker
#   64	  5:40	  Stalker
#   66	  5:48	  Stalker
#   62	  6:09	  Stalker x2
#   64	  6:17	  Stalker
#   66	  6:27	  Stalker
#   68	  6:45	  Stalker
#   70	  6:55	  Nexus
#   70	  6:57	  Pylon
#   70	  7:56	  Stalker x4
#   78	  8:03	  Pylon x2
