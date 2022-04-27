import datetime
from discord.utils import get

roles_income = {
    966040422050857084: 1010
}


class EconomicsUser:
    def __init__(self, id, guild):
        self.money = 100
        self.id = id
        self.level = 1
        self.nextlevel = self.level * 100
        self.xp = 0
        self.last_time_earnings = datetime.datetime.now() - datetime.timedelta(10)
        self.items = []
        self.member = get(guild.members, id=self.id)

    def get_balance(self):
        return self.money

    def add_money(self, amount):
        self.money += amount

    def get_id(self):
        return self.id

    def check_level(self):
        if self.xp >= self.nextlevel:
            self.xp -= self.nextlevel
            self.level += 1
            self.nextlevel = self.level * 100
            self.add_money(100 * self.level)
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
