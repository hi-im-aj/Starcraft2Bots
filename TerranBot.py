import sc2
from sc2 import run_game,maps,Race,Difficulty
from sc2.player import Bot,Computer
from sc2.constants import *


class Main(sc2.BotAI):
    async def on_step(self,iteration):
        await self.distribute_workers()
        await self.train_workers()
        await self.build_supplydepot()
        await self.build_refinery()
        await self.expand1()
        await self.build_barracks()
        await self.que_units()

    async def train_workers(self):
        for commandcenter in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV) and self.units(SCV).amount < 44 and not self.already_pending(SCV):
                await self.do(commandcenter.train(SCV))

    async def build_supplydepot(self):
        if self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
            commandcenter = self.units(COMMANDCENTER).ready
            if commandcenter.exists:
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT,near=commandcenter.first)

    async def build_refinery(self):
        for commandcenter in self.units(COMMANDCENTER).ready:
            vaspeneLoc = self.state.vespene_geyser.closer_than(10,commandcenter)
            for vaspene in vaspeneLoc:
                if not self.can_afford(REFINERY):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(REFINERY).closer_than(1,vaspene).exists and self.units(BARRACKS).exists:
                    await self.do(worker.build(REFINERY,vaspene))

    async def expand1(self):
        if self.units(COMMANDCENTER).amount < 2 and self.can_afford(COMMANDCENTER) and self.units(REFINERY).exists:
            await self.expand_now()

    async def build_barracks(self):
        if self.units(SUPPLYDEPOT).ready.exists:
            supplydepotRand = self.units(SUPPLYDEPOT).ready.random
            if not self.units(BARRACKS).exists and not self.already_pending(BARRACKS):
                if self.units(SUPPLYDEPOT).exists and self.can_afford(BARRACKS):
                    await self.build(BARRACKS,near=supplydepotRand)
            elif self.units(BARRACKS).amount < 3 and self.units(COMMANDCENTER).amount >= 2:
                barracksRand = self.units(BARRACKS).ready.random
                if self.units(SUPPLYDEPOT).exists and self.can_afford(BARRACKS):
                    await self.build(BARRACKS,near=barracksRand)
            if self.units(BARRACKS).ready.exists:
                for q in self.units(BARRACKS).ready.noqueue:
                    await self.do(q.build(BARRACKSREACTOR))

    async def que_units(self):
        for q in self.units(BARRACKS).ready.noqueue:
            if self.can_afford(MARINE) and self.supply_left > 0 and self.units(BARRACKSREACTOR).amount >= 3:
                await self.do(q.train(MARINE))


run_game(maps.get("(2)DreamcatcherLE"),[
    Bot(Race.Terran,Main()),
    Computer(Race.Random,Difficulty.VeryEasy)
    ], realtime=False)
