import datetime

import discord
from discord.ext import commands
import random

from economics_user import *
from shop_items import *

CASINO_ROULETTE_COLORS = {1: 'красный', 2: 'черный', 3: 'красный', 4: 'черный', 5: 'красный', 6: 'черный', 7: 'красный', 8: 'черный',
                          9: 'красный', 10: 'черный', 11: 'черный', 12: 'красный', 13: 'черный', 14: 'красный', 15: 'черный', 16: 'красный',
                          17: 'черный', 18: 'красный', 19: 'красный', 20: 'черный', 21: 'красный', 22: 'черный', 23: 'красный',
                          24: 'черный', 25: 'красный', 26: 'черный', 27: 'красный', 28: 'черный', 29: 'черный', 30: 'красный',
                          31: 'черный', 32: 'красный', 33: 'черный', 34: 'красный', 35: 'черный', 36: 'красный'}

client = discord.Client()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

users = {}
items = {}
work_cooldown = datetime.timedelta(hours=5)


class Things(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_if_admin(self, author):
        author_roles = list(map(lambda x: int(x.id), author.roles))
        if self.admin_role_id in author_roles or not self.admin_role_id:
            return True
        return False

    async def change_balance(self, user_id, amount):
        for user in users:
            if user == user_id:
                await users[user].add_money(amount)
                return

    @commands.command(name='добавить-предмет')
    async def create_item(self, ctx, name, price):
        if not self.check_if_admin(ctx.author):
            await ctx.channel.send(f'Это команда только для <@&{self.admin_role_id}>')
            return
        items[name] = ShopItem(int(price), name, ctx.guild)
        await ctx.channel.send(f'В магазин успешно добавлен предмет {name} по цене {price}')

    @commands.command(name='настроить-предмет')
    async def edit_item(self, ctx, name, parameter, value):
        if not self.check_if_admin(ctx.author):
            await ctx.channel.send(f'Это команда только для <@&{self.admin_role_id}>')
            return
        if parameter == 'роль-дана':
            role_id = value.lstrip('<@&').rstrip('>')
            items[name].role_given = int(role_id)
        elif parameter == 'роль-нужна':
            role_id = value.lstrip('<@&').rstrip('>')
            items[name].role_needed = int(role_id)
        elif parameter == 'роль-отобрана':
            role_id = value.lstrip('<@&').rstrip('>')
            items[name].role_taken = int(role_id)
        elif parameter == 'сообщение':
            items[name].message = value
        elif parameter == 'деньги':
            items[name].money_given = int(value)
        elif parameter == 'уровень':
            items[name].level_needed = int(value)

    @commands.command(name='убрать-предмет')
    async def delete_item(self, ctx, name):
        if not self.check_if_admin(ctx.author):
            await ctx.channel.send(f'Это команда только для <@&{self.admin_role_id}>')
            return
        if name in items:
            items.pop(name)
            await ctx.channel.send(f'Предмет {name} удален из магазина')

    @commands.command(name='поставить-роль-админа')
    async def set_admin_role(self, ctx, role):
        if self.check_if_admin(ctx.author):
            role_id = int(role.lstrip('<@&').rstrip('>'))
            self.admin_role_id = role_id
            await ctx.channel.send('Установлена новая роль администратора!')
        else:
            await ctx.channel.send(f'Увы, команда доступна только для <@&{self.admin_role_id}>')

    @commands.command(name='роль-админа')
    async def send_admin_role(self, ctx):
        if not self.check_if_admin(ctx.author):
            await ctx.channel.send(f'Команда доступна только для <@&{self.admin_role_id}>')
            return
        if self.admin_role_id:
            await ctx.channel.send(f'Текущая роль админа: <@&{self.admin_role_id}>')
        else:
            await ctx.channel.send('Нет сейчас админской роли. Небезопасно, поправить надо')

    @commands.command(name='дать-денег')
    async def add_money(self, ctx, target, amount=1000):
        if self.check_if_admin(ctx.author):
            target = int(target.lstrip('<@').rstrip('>'))
            await self.change_balance(target, amount)
            await ctx.channel.send(f'Добавлено {amount} рублей пользователю <@{target}> \n Теперь у него'
                                   f'{users[target].get_balance()} рублей')
        else:
            await ctx.channel.send(f'Увы, команда доступна только для <@&{self.admin_role_id}>')

    @commands.command(name='баланс')
    async def balance(self, ctx):
        id_need_to_check = int(ctx.author.id)
        if id_need_to_check in users:
            await ctx.channel.send(f'{ctx.author.mention}, ваш баланс составляет {users[id_need_to_check].get_balance()} рублей')
        else:
            await ctx.channel.send('Перезайди на сервер или обратись к админам, друже, тебя нет в базе данных!')

    @commands.command(name='казино')
    async def casino(self, ctx, game, number, bet):
        if bet.isdigit():
            bet = int(bet)
            if bet < 0 or bet > users[ctx.author.id].get_balance():
                await ctx.channel.send(f'Хорошая попытка. Но ваша ставка должна быть от 0 до {users[ctx.author.id].get_balance()}')
                return
        else:
            await ctx.channel.send('Ставка должна быть целым неотрицательным числом')
            return
        number = number.replace('ё', 'е')
        if number.isdigit():
            number = int(number)
        if game == 'кубик':
            if not 1 <= number <= 6:
                await ctx.channel.send('Если это шутка, то она не смешная. Нужно поставить на число от 1 до 6')
                return
            dice = random.randint(1, 6)
            await ctx.channel.send(f'На игральном кубике выпало число {dice}, вы ставили на {number}')
            if dice == number:
                await self.change_balance(ctx.author.id, bet * 2)
                await ctx.channel.send(f'Вы выиграли в кости и получили {bet * 2} рублей')
            else:
                await self.change_balance(ctx.author.id, -bet)
                await ctx.channel.send(f'Вы проиграли в кости и потеряли {bet} рублей')
        if game == 'рулетка':
            if not ('0' <= str(number) <= '36' or number in ['красный', 'черный', 'нечетный', 'четный']):
                await ctx.channel.send('На втором месте после названия игры должно идти число от 0 до 36 или ставки "четный", "нечетный", "красный", "черный"')
                return
            ball = random.randint(0, 36)
            color = False
            output = 'Выпал шарик: ' + str(ball)
            if ball:
                color = CASINO_ROULETTE_COLORS[ball]
                output = 'Выпал шарик: ' + color + ' ' + str(ball)
            if ball == number:
                await self.change_balance(ctx.author.id, bet * 34)
                output += f'\nВоу! Вы сорвали джекпот, поставив на {number}, ведь выпало {ball}! Вы получаете {bet * 34} рублей'
            elif color == number:
                await self.change_balance(ctx.author.id, bet)
                output += f'\nПоздравляем! Вы ставили на то, что выпадет мячик цвета {color}, и он выпал. Вы выиграли {bet} рублей'
            elif (number == 'нечетный' and ball % 2 == 1) or (number == 'четный' and ball % 2 == 0):
                await self.change_balance(ctx.author.id, bet)
                output += f'\nПоздравляем! Вы ставили на то, что выпадет {number} номер, и он выпал. Вы выиграли {bet} рублей'
            else:
                await self.change_balance(ctx.author.id, -bet)
                output += f'\nВы проиграли {bet} рублей'
            await ctx.channel.send(output)

    @commands.command(name='доход')
    async def income(self, ctx):
        if users[ctx.author.id].get_income(ctx.author.roles):
            await ctx.channel.send('Вы получили доход!')
        else:
            await ctx.channel.send('Вы пока не можете получить доход')

    @commands.command(name='магазин')
    async def shop(self, ctx, action=''):
        for item in items:
            if action == item:
                await items[item].bought(users[ctx.author.id], ctx.channel)
                return
            if not action:
                if not items:
                    await ctx.channel.send('Предметов пока нет')
                    return
                await ctx.channel.send(f'Предмет: {item}, стоит {items[item].price}')

    @commands.command(name='вещи')
    async def items(self, ctx):
        user = users[ctx.author.id]
        output = ''
        for item in user.items:
            output += item.name + ', '
        await ctx.channel.send('Ваши вещи: ' + output.rstrip(', '))

    @commands.command(name='использовать')
    async def activate_item(self, ctx, item_name):
        user = users[ctx.author.id]
        for item in user.items:
            if item.name == item_name:
                await item.activate(ctx.channel)
                return

    @commands.command(name='доход-роли')
    async def role_income(self, ctx, role, income):
        if not self.check_if_admin(ctx.author):
            await ctx.channel.send(f'Эта команда только для <@&{self.admin_role_id}>')
            return
        role_id = role.lstrip('<@&').rstrip('>')
        roles_income[int(role_id)] = int(income)

    @commands.command(name='передать-деньги')
    async def give_money(self, ctx, target, amount: int):
        if amount <= 0:
            await ctx.channel.send('Количество передаваемых денег должно быть больше нуля')
            return
        sender = users[ctx.author.id]
        if sender.money < amount:
            await ctx.channel.send('У вас недостаточно денег')
            return
        getter_id = int(target.lstrip('<@').rstrip('>'))
        if getter_id not in users:
            await ctx.channel.send('Получателя не существует')
            return
        await sender.change_balance(-amount)
        await users[getter_id].change_balance(amount)
        await ctx.channel.send(f'Отправлена сумма {amount} пользователю <@{getter_id}>')

    @commands.command(name='банк')
    async def bank(self, ctx, option, summa=0, time=0):
        user = users[ctx.author.id]
        if option == 'кредит':
            print('Зашел в иф')
            summa = int(summa)
            time = int(time)
            if not user.banking and summa > 0 and time >= 5 and summa % time == 0 and user.money > 0:
                print('Прошел проверку')
                await ctx.channel.send(f'Вы взяли кредит на сумму {summa}, на время {time}. Ежедневная выплата - {(summa + summa * 0.05 * time) // time}. Суммарная задолженность - {summa + summa * 0.05 * time}')
                await user.start_banking(summa, time)
        if option == 'инфо':
            if user.banking:
                await ctx.channel.send(f'У вас есть кредит на сумму {user.banking_summ}, ежедневная выплата - {user.banking_per_day}. Осталось выплатить {user.banking_left}')
            else:
                await ctx.channel.send('У вас нет кредитов!')

    @commands.command(name='работать')
    async def work(self, ctx):
        user = users[ctx.author.id]
        print(datetime.datetime.now() - user.last_work)
        print(work_cooldown)
        if datetime.datetime.now() - user.last_work > work_cooldown:
            user.last_work = datetime.datetime.now()
            money = random.randint(20, 200)
            await user.add_money(money)
            await ctx.channel.send(f'Вы заработали {money} рублей')
        else:
            await ctx.channel.send('Вам нужно подождать, прежде чем работать')

    @commands.command(name='поставить-перезарядку-работы')
    async def set_work_cooldown(self, ctx, hours=0, mins=0):
        global work_cooldown
        if not self.check_if_admin(ctx.author):
            await ctx.channel.send(f'Это команда только для <@&{self.admin_role_id}>')
            return
        hours = int(hours)
        mins = int(mins)
        work_cooldown = datetime.timedelta(hours=hours, minutes=mins)
        await ctx.channel.send('Перезарядка работы изменена')

    @commands.command(name='лидерборд')
    async def leaderboard(self, ctx):
        users_list = list(users.values())
        users_list.remove(users[bot.user.id])
        users_list = sorted(users_list, key=lambda x: x.get_balance(), reverse=True)
        output = ''
        for num, us in enumerate(users_list):
            if num > 19:
                break
            output += f'Место {num + 1} - <@{us.id}>, баланс {us.get_balance()}\n'
        await ctx.channel.send(output)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        members_list = guild.members
        for member in members_list:
            users[member.id] = EconomicsUser(member.id, member.guild)
    guilds_list = []  # bot.guilds
    for guild in guilds_list:
        for channel in guild.text_channels:
            await channel.send('Бот-экономика готов к работе')
    print(f'Ready!, activated: {datetime.datetime.now()}')


@bot.event
async def on_member_join(member):
    user = EconomicsUser(member.id, member.guild)
    users[member.id] = user
    await member.create_dm()
    await member.dm_channel.send(f'Привет, {member.name}! Добро пожаловать на сервер! Я начислил тебе 100 рублей,'
                                 'теперь они у тебя на счету!')


@bot.listen('on_message')
async def on_message(message):
    text = message.content.replace(' ', '')
    length = len(text)
    if users[message.author.id].add_xp(length):
        await message.author.create_dm()
        await message.author.dm_channel.send(f'У тебя новый уровень: {users[message.author.id].level}!\nЯ начислил тебе {users[message.author.id].level * 100} рублей!')


bot.add_cog(Things(bot))
TOKEN = "OTY2MzY3OTM2NTcyOTY5MDEw.YmAuRg.CEk7SaVIvUK9ZPvpEVE6nR9o3oU"
bot.run(TOKEN)
