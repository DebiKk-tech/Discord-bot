import asyncio
import datetime
from discord.utils import get

roles_income = {}


class EconomicsUser:
    def __init__(self, id, guild):
        self.money = 100
        self.id = id
        self.level = 1
        self.nextlevel = self.level * 200
        self.xp = 0
        self.last_time_earnings = datetime.datetime.now() - datetime.timedelta(10)
        self.items = []
        self.member = get(guild.members, id=self.id)
        self.banking = False
        self.banking_left = 0
        self.banking_summ = 0
        self.banking_per_day = 0
        self.last_work = self.last_time_earnings

    def get_balance(self):
        return self.money

    async def add_money(self, amount):
        if amount == 0:
            return
        self.money += amount
        await self.member.create_dm()
        await self.member.dm_channel.send(f'Ваш баланс изменился на {amount} рублей')

    def get_id(self):
        return self.id

    def check_level(self):
        if self.xp >= self.nextlevel:
            self.xp -= self.nextlevel
            self.level += 1
            self.nextlevel = self.level * 200
            self.add_money(200 * self.level)
            return True
        return False

    def add_xp(self, amount):
        self.xp += amount
        if self.check_level():
            return True
        return

    def get_income(self, roles_list):
        if datetime.datetime.now() - self.last_time_earnings < datetime.timedelta(1):
            print(f'Бабла не получил ведь время не прошло, осталось {datetime.timedelta(1) - (datetime.datetime.now() - self.last_time_earnings)}')
            print(f'В последний раз получал {self.last_time_earnings}')
            return False
        print(roles_list)
        for role in roles_list:
            if role.id in roles_income:
                self.add_money(roles_income[role.id])
        print('Доход получил')
        self.last_time_earnings = datetime.datetime.now()
        return True

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    async def start_banking(self, summ, time):
        self.banking = True
        percent = 0.05
        self.banking_summ, self.banking_left = summ, summ + summ * percent * time
        await self.add_money(self.banking_summ)
        self.banking_per_day = self.banking_left // time
        while self.banking_left > 0:
            self.banking_left -= self.banking_per_day
            await self.add_money(-self.banking_per_day)
            await asyncio.sleep(3600 * 24)
        self.banking = False
        self.banking_left = 0
        self.banking_summ = 0
        self.banking_per_day = 0
