import sc2
from sc2 import run_game,maps,Race,Difficulty
from sc2.player import Bot,Computer
from sc2.constants import *

q1 = 2
q2 = 39
q3 = 4
q4 = True
q5 = 3
q6 = 39 + 16

class Main(sc2.BotAI):
    async def on_step(self,iteration):
        await self.distribute_workers()
        await self.main_train()
        await self.main_build()
        await self.main_orders()

    async def main_train(self):
        larva = self.units(LARVA)
        if larva.exists:
            if self.supply_left < 8 and not self.already_pending(OVERLORD):
                for q in self.units(LARVA):
                    if self.can_afford(OVERLORD):
                        await self.do(q.train(OVERLORD))
            elif self.units(DRONE).amount <= q2 and self.supply_left > 0:
                for q in self.units(LARVA):
                    if self.can_afford(DRONE):
                        await self.do(q.train(DRONE))
            elif self.units(ZERGLING).amount <= q3 and self.units(SPAWNINGPOOL).exists and self.supply_left > 0:
                for q in self.units(LARVA):
                    if self.can_afford(ZERGLING):
                        await self.do(q.train(ZERGLING))
            elif self.units(DRONE).amount <= q6 and self.supply_left > 0 and self.units(HATCHERY).amount == q5:
                for q in self.units(LARVA):
                    if self.can_afford(DRONE):
                        await self.do(q.train(DRONE))

    async def main_build(self):
        if self.units(HATCHERY).amount == q1:
            for q in self.units(HATCHERY).ready:
                vaspenePos = self.state.vespene_geyser.closer_than(10,q)
                for q in vaspenePos:
                    worker = self.select_build_worker(q.position)
                    if worker is not None and self.can_afford(EXTRACTOR):
                        if not self.units(EXTRACTOR).closer_than(1,q).exists:
                            await self.do(worker.build(EXTRACTOR,q))
        if self.units(HATCHERY).amount < q1:
            if self.can_afford(HATCHERY):
                await self.expand_now()
        elif not self.units(SPAWNINGPOOL).exists:
            if self.can_afford(SPAWNINGPOOL) and self.units(EXTRACTOR).exists:
                extractorRand = self.units(EXTRACTOR).random
                await self.build(SPAWNINGPOOL,near=extractorRand)
        elif self.units(QUEEN).amount + self.already_pending(QUEEN) < q5 and self.units(SPAWNINGPOOL).ready.exists:
            for q in self.units(HATCHERY).ready.noqueue:
                if self.can_afford(QUEEN) and not self.already_pending(QUEEN):
                    await self.do(q.train(QUEEN))
        elif self.units(HATCHERY).amount + self.already_pending(HATCHERY) < q5 and self.units(QUEEN).exists:
            if self.can_afford(HATCHERY):
                await self.expand_now()

    async def main_orders(self):
        if self.units(ZERGLING).amount >= q3 and False:
            global q4
            if q4 == True:
                for q in self.units(ZERGLING):
                    await self.do(q.attack(self.enemy_start_locations[0]))
                    q4 = False

run_game(maps.get("(2)DreamcatcherLE"),[
    Bot(Race.Zerg,Main()),
    Computer(Race.Random,Difficulty.Easy)
    ], realtime=False)
