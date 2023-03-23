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
import pickle
import sys

VISUALIZE = False
OLD_MAP = False
MODEL_PLAYING = True
HEIGHT = 168
WIDTH = 184


class FourGateBot(BotAI):
    def __init__(self):
        self.last_sent = 0
        self.build_step = -1
        self.cyberneticscore = False
        self.proxy_pylon = False
        self.folder_name = f"{int(time.time())}"
        self.model_decisions = False
        self.step_counter = 0

    async def on_step(self, iteration: int):
        self.step_counter += 1
        if self.step_counter % 10 != 0:
            return
        await self.distribute_workers()

        try:
            all_supply_used = self.supply_used + self.already_pending(UnitTypeId.PROBE)
            if self.already_pending(UnitTypeId.PROBE) != 0:
                all_supply_used -= 1
            nexus = self.townhalls.ready.random

            if OLD_MAP:
                if all_supply_used < 9:
                    if self.can_afford(UnitTypeId.PROBE):
                        nexus.train(UnitTypeId.PROBE)
                        all_supply_used += 1

                if all_supply_used == 9:
                    if self.can_afford(UnitTypeId.PYLON):
                        await self.build(UnitTypeId.PYLON,
                                         near=nexus.position.towards(self.game_info.map_center, 5))

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
                if 1 > self.already_pending_upgrade(
                        UpgradeId.WARPGATERESEARCH) > 0 and not self.cyberneticscore.has_buff(
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
                    self.model_decisions = True
                    print('Model is taking control of actions')
        except:
            print('Scrypt Exception')

        # END OF THE SCRYPTED PART
        if not MODEL_PLAYING:
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

            # PROXY PYLON
            if not self.proxy_pylon and self.supply_used > 22:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON,
                                     near=self.enemy_start_locations[0].towards(self.game_info.map_center, 30))
                    self.proxy_pylon = True

            # ATTACK OPTIONS
            if self.units(UnitTypeId.STALKER).amount + self.units(UnitTypeId.ZEALOT).amount >= 10:
                attack_units =  self.units(UnitTypeId.STALKER) + self.units(UnitTypeId.ZEALOT)
                if self.enemy_units:
                    for st in attack_units.idle:
                        st.attack(random.choice(self.enemy_units))

                elif self.enemy_structures:
                    for st in attack_units.idle:
                        st.attack(random.choice(self.enemy_structures))

                else:
                    for st in attack_units.idle:
                        st.attack(self.enemy_start_locations[0])

        if self.model_decisions:
            no_action = True
            while no_action:
                try:
                    with open('state_rwd_action.pkl', 'rb') as f:
                        state_rwd_action = pickle.load(f)

                        if state_rwd_action['action'] is None:
                            # print("No action yet")
                            no_action = True
                        else:
                            # print(f"Action found - {state_rwd_action['action']}")
                            no_action = False
                except:
                    pass

            action = state_rwd_action['action']
            if action == 0:
                await self.expand()
            elif action == 1:
                await self.build_warpgates()
            elif action == 2:
                await self.train()
            elif action == 3:
                await self.explore(iteration)
            elif action == 4:
                await self.exterminate()
            elif action == 5:
                await self.group_units()

        # DRAW MAP
        offset = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, -1], [-1, 1], [1, -1], [0, 0]]
        map_state = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), dtype=np.uint8)
        base_buildings = [UnitTypeId.NEXUS, UnitTypeId.HATCHERY, UnitTypeId.COMMANDCENTER, UnitTypeId.LAIR,
                          UnitTypeId.HIVE]
        protoss_ground_units = [UnitTypeId.STALKER, UnitTypeId.ZEALOT, UnitTypeId.SENTRY]
        # print(self.game_info.map_size[1])
        # print(self.game_info.map_size[0])

        # draw the minerals:
        for mineral in self.mineral_field:
            pos = mineral.position
            c = [175, 255, 255]
            if OLD_MAP:
                fraction = mineral.mineral_contents / 1500
            else:
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
            if OLD_MAP:
                fraction = vespene.vespene_contents / 2500
            else:
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
            cv2.imshow('map', cv2.flip(cv2.resize(map_state, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST), 0))
            cv2.waitKey(1)

        reward = 0

        try:
            attack_count = 0
            attack_units = self.units(UnitTypeId.STALKER) + self.units(UnitTypeId.ZEALOT)
            for unit in attack_units:
                # if unit is attacking and is in range of enemy unit:
                if unit.is_attacking and unit.target_in_range:
                    if self.enemy_units.closer_than(12, unit) or self.enemy_structures.closer_than(12, unit):
                        # reward += 0.005 # original was 0.005, decent results, but let's 3x it.
                        reward += 0.015
                        attack_count += 1

        except Exception as e:
            print("reward", e)
            reward = 0

        if iteration % 100 == 0:
            print(f"Iter: {iteration}. RWD: {reward}. VR: {self.units(UnitTypeId.VOIDRAY).amount}")

        # write the file:
        data = {"state": map_state, "reward": reward, "action": None,
                "done": False}  # empty action waiting for the next one!

        with open('state_rwd_action.pkl', 'wb') as f:
            pickle.dump(data, f)

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
            unit_type = random.randint(0, 1)
            pos = proxy.position.to2.random_on_distance(4)
            if unit_type == 1:
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    break
                warpgate.warp_in(UnitTypeId.STALKER, placement)
            elif unit_type == 0:
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, pos, placement_step=1)
                if placement is None:
                    break
                warpgate.warp_in(UnitTypeId.ZEALOT, placement)

    # SELECTABLE ACTIONS
    # build new base or build probes
    async def expand(self):
        try:
            found_something = False
            if self.supply_left < 4:
                if self.already_pending(UnitTypeId.PYLON) == 0:
                    if self.can_afford(UnitTypeId.PYLON):
                        await self.build(UnitTypeId.PYLON, near=random.choice(self.townhalls))
                        found_something = True

            if not found_something:

                for nexus in self.townhalls:
                    worker_count = len(self.workers.closer_than(10, nexus))
                    if worker_count < 22:
                        if nexus.is_idle and self.can_afford(UnitTypeId.PROBE):
                            nexus.train(UnitTypeId.PROBE)
                            found_something = True

                    for geyser in self.vespene_geyser.closer_than(10, nexus):
                        if not self.can_afford(UnitTypeId.ASSIMILATOR):
                            break
                        if not self.structures(UnitTypeId.ASSIMILATOR).closer_than(2.0, geyser).exists:
                            await self.build(UnitTypeId.ASSIMILATOR, geyser)
                            found_something = True

            if not found_something:
                if self.already_pending(UnitTypeId.NEXUS) == 0 and self.can_afford(UnitTypeId.NEXUS):
                    await self.expand_now()

        except Exception as e:
            print(e)

    # check how far the enemy is expanding
    async def explore(self, iteration):
        try:
            self.last_sent
        except:
            self.last_sent = 0

        if (iteration - self.last_sent) > 200:
            try:
                if self.units(UnitTypeId.PROBE).exists:
                    probe = random.choice(self.units(UnitTypeId.PROBE))
                # send probe towards enemy base:
                probe.attack(random.choice(self.expansion_locations_list))
                self.last_sent = iteration

            except Exception as e:
                pass

    # build more warpgates
    async def build_warpgates(self):
        try:
            for nexus in self.townhalls:
                if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
                    if self.can_afford(UnitTypeId.CYBERNETICSCORE) and self.already_pending(
                            UnitTypeId.CYBERNETICSCORE) == 0 and self.structures(UnitTypeId.GATEWAY).exists:
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=nexus)

                if not self.structures(UnitTypeId.GATEWAY).closer_than(10, nexus).exists:
                    if self.can_afford(UnitTypeId.GATEWAY) and self.already_pending(UnitTypeId.GATEWAY) == 0:
                        await self.build(UnitTypeId.GATEWAY, near=nexus)

        except Exception as e:
            print(e)

    # train more army
    async def train(self):
        try:
            proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
            await self.warp_new_units(proxy)

        except Exception as e:
            print(e)

    # attack starting location, expanded bases, military or defend
    async def exterminate(self):
        try:
            attack_units = self.units(UnitTypeId.STALKER) + self.units(UnitTypeId.ZEALOT)
            for stalker in attack_units.idle:
                if self.enemy_units.closer_than(10, stalker):
                    stalker.attack(random.choice(self.enemy_units.closer_than(10, stalker)))

                elif self.enemy_structures.closer_than(10, stalker):
                    stalker.attack(random.choice(self.enemy_structures.closer_than(10, stalker)))

                elif self.enemy_units:
                    stalker.attack(random.choice(self.enemy_units))

                elif self.enemy_structures:
                    if self.units(UnitTypeId.STALKER).amount >= 10:
                        struct = random.choice(self.enemy_structures)
                        pos = struct.position
                        stalker.attack(pos)

                elif self.enemy_start_locations:
                    if self.units(UnitTypeId.STALKER).amount >= 10:
                        pos = self.enemy_start_locations[0].position
                        stalker.attack(pos)

        except Exception as e:
            print(e)

    # group units
    async def group_units(self):
        attack_units = self.units(UnitTypeId.STALKER) + self.units(UnitTypeId.ZEALOT)
        if attack_units.amount > 0:
            if self.townhalls:
                nexus = self.townhalls[-1]
                pos = nexus.position.towards(self.game_info.map_center, 10)
                for stalker in attack_units.idle:
                    stalker.attack(pos)


def main():
    # Human(Race.Protoss, "MKDMK", True),
    # Bot(Race.Protoss, FourGateBot(),
    # Computer(Race.Protoss, Difficulty.VeryHard),
    result = run_game(
        maps.get("BlackburnAIE"),
        [Bot(Race.Protoss, FourGateBot()),
         Computer(Race.Terran, Difficulty.Hard)],
        realtime=False,
    )

    if str(result) == "Result.Victory":
        rwd = 500
    else:
        rwd = -500

    with open("results.txt", "a") as f:
        f.write(f"{result}\n")

    map_state = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    data = {"state": map_state, "reward": rwd, "action": None, "done": True}  # empty action waiting for the next one!
    with open('state_rwd_action.pkl', 'wb') as f:
        pickle.dump(data, f)

    cv2.destroyAllWindows()
    cv2.waitKey(1)
    time.sleep(3)
    sys.exit()


if __name__ == "__main__":
    main()
