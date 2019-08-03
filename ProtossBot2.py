import sc2,random
from sc2 import run_game,maps,Race,Difficulty
from sc2.player import Bot,Computer
from sc2.constants import *

class Main(sc2.BotAI):

    async def on_step(self,iteration):
        await self.distribute_workers()
        await self.train_probe()
        await self.build_pylon()
        await self.build_assimilator()
        await self.build_nexus()
        await self.build_gateway()
        await self.build_cyberneticscore()
        await self.build_stargate()
        await self.build_fleetbeacon()
        await self.train_voidray()
        await self.command_attack()
        await self.train_stalker()
        await self.train_zealot()

    async def train_probe(self):
        prope_limit = 75
        if self.can_afford(PROBE) and self.supply_left > 0:
            if self.units(PROBE).amount < prope_limit and self.units(NEXUS).ready.noqueue.exists:
                q = self.units(NEXUS).ready.noqueue.random
                await self.do(q.train(PROBE))

    async def build_pylon(self):
        if self.supply_left < 16 and self.already_pending(PYLON) < 2 and self.supply_cap != 200:
            if self.can_afford(PYLON) and self.units(NEXUS).exists:
                q = self.units(NEXUS).random
                await self.build(PYLON,near=q)

    async def build_assimilator(self):
        if self.can_afford(ASSIMILATOR) and self.units(PROBE).amount > 15:
            for q in self.units(NEXUS):
                geyser_count = self.state.vespene_geyser.closer_than(10,q)
                for q in geyser_count:
                    worker = self.select_build_worker(q.position)
                    if worker != None and not self.units(ASSIMILATOR).closer_than(1,q).exists:
                        if self.can_afford(ASSIMILATOR):
                            await self.do(worker.build(ASSIMILATOR,q))

    async def build_nexus(self):
        if self.units(VOIDRAY).amount > 4:
            nexus_limit = 5
        elif self.units(VOIDRAY).exists:
            nexus_limit = 4
        elif self.units(STARGATE).exists:
            nexus_limit = 3
        else:
            nexus_limit = 2

        if self.can_afford(NEXUS) and self.units(NEXUS).amount < nexus_limit:
            if not self.already_pending(NEXUS) and self.units(PROBE).amount > 16:
                await self.expand_now()

    async def build_gateway(self):
        nexus_count = self.units(NEXUS).amount
        gateway_limit = 1
        if nexus_count > 1 and self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
            if self.units(PYLON).ready.exists and self.units(GATEWAY).amount < gateway_limit:
                q = self.units(PYLON).ready.random
                if self.can_afford(GATEWAY):
                    await self.build(GATEWAY,near=q)

    async def build_cyberneticscore(self):
        nexus_count = self.units(NEXUS).amount
        if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE).exists and not self.already_pending(CYBERNETICSCORE):
            if self.units(PYLON).ready.exists and nexus_count > 1:
                q = self.units(PYLON).ready.random
                if self.can_afford(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE,near=q)

    async def build_stargate(self):
        nexus_count = self.units(NEXUS).amount
        stargate_limit = nexus_count
        if self.units(CYBERNETICSCORE).ready.exists and not self.already_pending(STARGATE):
            if self.can_afford(STARGATE) and self.units(STARGATE).amount < stargate_limit:
                if self.units(PYLON).ready.exists and self.units(STALKER).amount > 1:
                    q = self.units(PYLON).ready.random
                    if self.can_afford(STARGATE):
                        await self.build(STARGATE,near=q)

    async def build_fleetbeacon(self):
        if not self.units(FLEETBEACON).ready.exists and not self.already_pending(FLEETBEACON) and self.units(STARGATE).ready.exists:
            if self.can_afford(FLEETBEACON) and self.units(PYLON).ready.exists:
                q = self.units(PYLON).ready.random
                if self.can_afford(FLEETBEACON) and self.units(STARGATE).ready.exists:
                    await self.build(FLEETBEACON,near=q)

    async def train_zealot(self):
        if self.units(GATEWAY).ready.noqueue.exists:
            if self.can_afford(ZEALOT) and self.units(FLEETBEACON).exists:
                q = self.units(GATEWAY).ready.noqueue.random
                if self.can_afford(ZEALOT) and self.supply_left > 1:
                    await self.do(q.train(ZEALOT))
    """
    async def train_mothership(self):
        if not self.units(MOTHERSHIP).exists:
            if self.units(NEXUS).ready.exists and self.units(FLEETBEACON).ready.exists:
                q = self.units(NEXUS).ready.random
                if self.can_afford(MOTHERSHIP) and self.supply_left > 7:
                    await self.do(q.train(MOTHERSHIP))
    """
    async def train_voidray(self):
        if self.units(STARGATE).ready.noqueue.exists and self.units(FLEETBEACON).ready.exists:
            q = self.units(STARGATE).ready.noqueue.random
            if self.can_afford(VOIDRAY) and self.supply_left > 4:
                await self.do(q.train(VOIDRAY))

    async def train_stalker(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(STALKER):
            if self.units(GATEWAY).ready.noqueue.exists and self.units(STALKER).amount < 3:
                q = self.units(GATEWAY).ready.noqueue.random
                if self.can_afford(STALKER) and self.supply_left > 2:
                    await self.do(q.train(STALKER))

    async def command_attack(self):
        units = [VOIDRAY,MOTHERSHIP,STALKER,ZEALOT]
        for q in units:
            if len(self.known_enemy_units) > 0:
                EU = random.choice(self.known_enemy_units)
                for w in self.units(q).idle:
                    await self.do(w.attack(EU))
            elif len(self.known_enemy_structures) > 0:
                ES = random.choice(self.known_enemy_structures)
                for w in self.units(q).idle:
                    await self.do(w.attack(ES))
            elif self.supply_used > 190:
                for w in self.units(q).idle:
                    await self.do(w.attack(self.enemy_start_locations[0]))

run_game(maps.get("AbyssalReefLE"),[
    Bot(Race.Protoss,Main()),
    Computer(Race.Random,Difficulty.Medium)
    ], realtime=False)
