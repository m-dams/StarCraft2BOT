from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
import random
import numpy as np
import math
import cv2
import time
import os

SAVE_REPLAY = False
VISUALIZE = True

class FourGateBot(BotAI):
    def __init__(self):
        self.build_step = 0
        self.cyberneticscore = False
        self.proxy_pylon = False
        self.folder_name = f"{int(time.time())}"
        os.mkdir(f"input_data/{self.folder_name}")

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

        # END OF THE SCRYPTED PART

        # TO BE REPLACED BY SELECTIVE ACTIONS
        if all_supply_used >= 26 and self.build_step == 10:
            proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
            await self.warp_new_units(proxy)
            all_supply_used += 2

        supply_remaining = self.supply_cap - self.supply_used
        if supply_remaining < 8 and self.already_pending(UnitTypeId.PYLON) == 0:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)

        # PROXY PYLON
        # if not self.proxy_pylon and self.supply_used > 22:
        #     if self.can_afford(UnitTypeId.PYLON):
        #         await self.build(UnitTypeId.PYLON,
        #                          near=self.enemy_start_locations[0].towards(self.game_info.map_center, 30))
        #         self.proxy_pylon = True

        # ATTACK OPTIONS
        if self.units(UnitTypeId.STALKER).amount >= 10:
            if self.enemy_units:
                for st in self.units(UnitTypeId.STALKER).idle:
                    st.attack(random.choice(self.enemy_units))

            elif self.enemy_structures:
                for st in self.units(UnitTypeId.STALKER).idle:
                    st.attack(random.choice(self.enemy_structures))

            else:
                for st in self.units(UnitTypeId.STALKER).idle:
                    st.attack(self.enemy_start_locations[0])

        # DRAW MAP
        offset = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, -1], [-1, 1], [1, -1], [0, 0]]
        map_state = np.zeros((self.game_info.map_size[0], self.game_info.map_size[1], 3), dtype=np.uint8)
        base_buildings = [UnitTypeId.NEXUS, UnitTypeId.HATCHERY, UnitTypeId.COMMANDCENTER, UnitTypeId.LAIR,
                          UnitTypeId.HIVE]
        protoss_ground_units = [UnitTypeId.STALKER, UnitTypeId.ZEALOT, UnitTypeId.SENTRY]

        # draw the minerals:
        for mineral in self.mineral_field:
            pos = mineral.position
            c = [175, 255, 255]
            fraction = mineral.mineral_contents / 1800
            if mineral.is_visible:
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]
            else:
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [20, 75, 50]

        # draw the enemy start location:
        for enemy_start_location in self.enemy_start_locations:
            pos = enemy_start_location
            c = [0, 0, 255]
            map_state[math.ceil(pos.y)][math.ceil(pos.x)] = c

        # draw the enemy units:
        for enemy_unit in self.enemy_units:
            pos = enemy_unit.position
            c = [100, 0, 255]
            fraction = enemy_unit.health / enemy_unit.health_max if enemy_unit.health_max > 0 else 0.0001
            map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

        # draw the enemy structures:
        for enemy_structure in self.enemy_structures:
            if enemy_structure.type_id in base_buildings:
                pos = enemy_structure.position
                points = []
                for o in offset:
                    points.append((pos[0] + o[0], pos[1] + o[1]))
                c = [0, 100, 255]
                fraction = enemy_structure.health / enemy_structure.health_max if enemy_structure.health_max > 0 else 0.0001
                for p in points:
                    map_state[math.ceil(p[1])][math.ceil(p[0])] = [int(fraction * i) for i in c]

            else:
                pos = enemy_structure.position
                c = [0, 100, 255]
                fraction = enemy_structure.health / enemy_structure.health_max if enemy_structure.health_max > 0 else 0.0001
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

        # draw our structures:
        for our_structure in self.structures:
            if our_structure.type_id == UnitTypeId.NEXUS:
                pos = our_structure.position
                points = []
                for o in offset:
                    points.append((pos[0] + o[0], pos[1] + o[1]))
                c = [255, 255, 175]
                fraction = our_structure.health / our_structure.health_max if our_structure.health_max > 0 else 0.0001
                for p in points:
                    map_state[math.ceil(p[1])][math.ceil(p[0])] = [int(fraction * i) for i in c]

            else:
                pos = our_structure.position
                c = [0, 255, 175]
                fraction = our_structure.health / our_structure.health_max if our_structure.health_max > 0 else 0.0001
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

        # draw the vespene geysers:
        for vespene in self.vespene_geyser:
            pos = vespene.position
            c = [255, 175, 255]
            fraction = vespene.vespene_contents / 2250

            if vespene.is_visible:
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]
            else:
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [50, 20, 75]

        # draw our units:
        for our_unit in self.units:
            if our_unit.type_id in protoss_ground_units:
                pos = our_unit.position
                c = [255, 75, 75]
                fraction = our_unit.health / our_unit.health_max if our_unit.health_max > 0 else 0.0001
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

            else:
                pos = our_unit.position
                c = [175, 255, 0]
                fraction = our_unit.health / our_unit.health_max if our_unit.health_max > 0 else 0.0001
                map_state[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

        if VISUALIZE:
            # show map with opencv, resized to be larger:
            # horizontal flip:
            cv2.imshow('map', cv2.flip(cv2.resize(map_state, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST), 0))
            cv2.waitKey(1)

        if SAVE_REPLAY:
            # save map image into "replays dir"
            cv2.imwrite(f"input_data/{self.folder_name}/{int(time.time())}-{iteration}.png", map_state)

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
            pos = proxy.position.to2.random_on_distance(4)
            placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
            if placement is None:
                break
            warpgate.warp_in(UnitTypeId.STALKER, placement)

    # SELECTABLE ACTIONS
    # build new base or build probes
    def expand(self):
        pass

    # check how for the enemy is expanding
    def explore(self):
        pass

    # build more units/ buildings/ cannons
    def exploit(self):
        pass

    # attack starting location, expanded bases, military or defend
    def exterminate(self):
        pass

    # go back to base / proxy pylon
    def fall_back(self):
        pass


def main():
    # Human(Race.Protoss, "MKDMK", True),
    # Bot(Race.Protoss, FourGateBot(),
    # Computer(Race.Protoss, Difficulty.VeryHard),
    run_game(
        maps.get("AcropolisLE"),
        [Bot(Race.Protoss, FourGateBot()),
         Computer(Race.Zerg, Difficulty.Easy)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
