import sc2
from sc2 import run_game,maps,Race,Difficulty
from sc2.player import Bot,Computer
from sc2.constants import *
import random

class Main(sc2.BotAI):
    async def on_step(self,iteration):
        await self.distribute_workers()
        await self.dist_geyser()
        await self.build_order()
        await self.train_units()
        await self.commands()

    async def dist_geyser(self):
        for q in self.units(COMMANDCENTER).ready:
            geyserAmount = self.state.vespene_geyser.closer_than(10,q)
            for q in geyserAmount:
                worker = self.select_build_worker(q.position)
                if self.can_afford(REFINERY) and self.units(BARRACKS).exists:
                    if worker is not None and not self.units(REFINERY).closer_than(1,q).exists:
                        await self.do(worker.build(REFINERY,q))

    async def build_order(self):
        global cmdcAmount,targetScvAmount,targetBarracksAmount
        cmdcAmount = self.units(COMMANDCENTER).amount
        targetScvAmount = cmdcAmount * 20
        targetBarracksAmount = cmdcAmount * 2
        if not self.units(COMMANDCENTER).exists and self.can_afford(COMMANDCENTER):
            await self.expand_now()
        elif self.supply_left < 8 and not self.already_pending(SUPPLYDEPOT):
            if self.can_afford(SUPPLYDEPOT):
                cmdcRand = self.units(COMMANDCENTER).ready.random
                await self.build(SUPPLYDEPOT,near=cmdcRand)
        elif self.units(SCV).amount < targetScvAmount:
                for q in self.units(COMMANDCENTER).ready.noqueue:
                    if self.can_afford(SCV):
                        await self.do(q.train(SCV))
        elif self.units(BARRACKS).amount <= targetBarracksAmount and not self.already_pending(BARRACKS):
            if self.can_afford(BARRACKS):
                sdRand = self.units(SUPPLYDEPOT).ready.random
                await self.build(BARRACKS,near=sdRand)
        elif cmdcAmount < 2 and not self.already_pending(COMMANDCENTER) and not self.already_pending(BARRACKS):
            await self.expand_now()
        elif not self.units(ENGINEERINGBAY).exists and not self.already_pending(ENGINEERINGBAY):
            sdRand = self.units(SUPPLYDEPOT).ready.random
            await self.build(ENGINEERINGBAY,near=sdRand)

    async def train_units(self):
        if self.units(BARRACKS).ready.noqueue.exists:
            for q in self.units(BARRACKS).ready.noqueue:
                if self.can_afford(MARINE) and self.supply_left > 0:
                    await self.do(q.train(MARINE))

    async def commands(self):
        if self.units(MARINE).idle and self.units(MARINE).idle.amount > 10 and len(self.known_enemy_units) > 0:
            for q in self.units(MARINE):
                await self.do(q.attack(random.choice(self.known_enemy_units)))
        elif self.units(MARINE).idle and self.units(MARINE).idle.amount > 40 and len(self.known_enemy_structures) > 0:
            for q in self.units(MARINE):
                await self.do(q.attack(random.choice(self.known_enemy_structures)))
        elif self.units(MARINE).idle and self.units(MARINE).idle.amount > 40:
            for q in self.units(MARINE):
                await self.do(q.attack(self.enemy_start_locations[0]))

run_game(maps.get("(2)DreamcatcherLE"),[
    Bot(Race.Terran,Main()),
    Computer(Race.Random,Difficulty.Easy)
    ], realtime=False)
