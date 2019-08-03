import sc2,random
from sc2 import run_game,maps,Race,Difficulty
from sc2.player import Bot,Computer
from sc2.constants import *

class Main(sc2.BotAI):
    async def on_step(self,iteration):
        await self.distribute_workers()
        await self.chain()
        await self.chain_0()
        await self.chain_1()
        await self.command()

    async def chain(self):
        nexus_count = self.units(NEXUS).amount

        if self.units(TWILIGHTCOUNCIL).exists or self.units(STARGATE).exists or self.units(ROBOTICSFACILITY).exists:
            nexus_limit_0 = 4
        elif self.units(CYBERNETICSCORE).exists:
            nexus_limit_0 = 3
            pylon_build_limit_0 = 2
        else:
            nexus_limit_0 = 2
            pylon_build_limit_0 = 1

        nexus_limit = nexus_limit_0
        probe_limit = nexus_count * 18
        gateway_limit = 1 * nexus_count
        stargate_limit = 1 * nexus_count
        forge_limit = 1
        cyberneticscore_limit = 1

        if self.units(PROBE).amount < probe_limit and self.supply_left > 0 and self.units(NEXUS).ready.noqueue.exists:
            q = self.units(NEXUS).ready.noqueue.random
            if self.can_afford(PROBE):
                await self.do(q.train(PROBE))
        if self.units(GATEWAY).ready.noqueue.exists and self.units(CYBERNETICSCORE).ready.exists and self.supply_left >= 2:
            if self.units(VOIDRAY).amount > self.units(STALKER).amount:
                q = self.units(GATEWAY).ready.noqueue.random
                if self.can_afford(STALKER):
                    await self.do(q.train(STALKER))
        if self.units(STARGATE).ready.noqueue.exists and self.units(CYBERNETICSCORE).ready.exists and self.supply_left >= 4:
                q = self.units(STARGATE).ready.noqueue.random
                if self.can_afford(VOIDRAY):
                    await self.do(q.train(VOIDRAY))

        if self.units(NEXUS).amount < nexus_limit and not self.already_pending(NEXUS):
            if self.can_afford(NEXUS):
                await self.expand_now()
        elif self.units(GATEWAY).amount < gateway_limit and self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
            loc_0 = self.units(PYLON).ready.random
            await self.build(GATEWAY,near=loc_0)
        elif not self.units(FORGE).exists and self.can_afford(FORGE) and not self.already_pending(FORGE):
            loc_1 = self.units(PYLON).ready.random
            await self.build(FORGE,near=loc_1)
        elif not self.units(CYBERNETICSCORE).exists and self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
            loc_2 = self.units(PYLON).ready.random
            await self.build(CYBERNETICSCORE,near=loc_2)
        elif self.units(STARGATE).amount < stargate_limit and self.can_afford(STARGATE) and not self.already_pending(STARGATE) and self.units(CYBERNETICSCORE).exists:
            loc_3 = self.units(PYLON).ready.random
            await self.build(STARGATE,near=loc_3)

    async def chain_0(self):
        if self.can_afford(ASSIMILATOR):
            for q in self.units(NEXUS):
                geyser_count = self.state.vespene_geyser.closer_than(10,q)
                for q in geyser_count:
                    worker = self.select_build_worker(q.position)
                    if worker != None and not self.units(ASSIMILATOR).closer_than(1,q).exists:
                        if self.can_afford(ASSIMILATOR):
                            await self.do(worker.build(ASSIMILATOR,q))

    async def chain_1(self):
        if self.units(CYBERNETICSCORE).exists:
            pylon_build_limit_0 = 2
        else:
            pylon_build_limit_0 = 1

        pylon_build_limit = pylon_build_limit_0

        if not self.units(NEXUS).exists and self.can_afford(NEXUS):
            await self.expand_now()
        elif self.supply_left < 12 and not self.already_pending(PYLON) > pylon_build_limit:
            if self.can_afford(PYLON):
                loc = self.units(NEXUS).random
                await self.build(PYLON,near=loc)

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]
    async def command(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {STALKER: [15, 1],
                            VOIDRAY: [10, 1]}

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))

run_game(maps.get("(2)DreamcatcherLE"),[
    Bot(Race.Protoss,Main()),
    Computer(Race.Random,Difficulty.VeryHard)
    ], realtime=False)
