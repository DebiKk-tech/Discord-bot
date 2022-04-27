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


class Things(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_role_id = 966040422050857084

    def check_if_admin(self, author):
        author_roles = list(map(lambda x: int(x.id), author.roles))
        if self.admin_role_id in author_roles or not self.admin_role_id:
            return True
        return False

    def change_balance(self, user_id, amount):
        for user in users:
            if user == user_id:
                users[user].add_money(amount)
                return

    @commands.command(name='добавить-предмет')
    async def create_item(self, ctx, name, price):
        items[name] = ShopItem(int(price), name, ctx.guild)
        await ctx.channel.send(f'В магазин успешно добавлен предмет {name} по цене {price}')

    @commands.command(name='настроить-предмет')
    async def edit_item(self, ctx, name, parameter, value):
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
            self.change_balance(target, amount)
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
                self.change_balance(ctx.author.id, bet * 2)
                await ctx.channel.send(f'Вы выиграли в кости и получили {bet * 2} рублей')
            else:
                self.change_balance(ctx.author.id, -bet)
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
                self.change_balance(ctx.author.id, bet * 34)
                output += f'\nВоу! Вы сорвали джекпот, поставив на {number}, ведь выпало {ball}! Вы получаете {bet * 34} рублей'
            elif color == number:
                self.change_balance(ctx.author.id, bet)
                output += f'\nПоздравляем! Вы ставили на то, что выпадет мячик цвета {color}, и он выпал. Вы выиграли {bet} рублей'
            elif (number == 'нечетный' and ball % 2 == 1) or (number == 'четный' and ball % 2 == 0):
                self.change_balance(ctx.author.id, bet)
                output += f'\nПоздравляем! Вы ставили на то, что выпадет {number} номер, и он выпал. Вы выиграли {bet} рублей'
            else:
                self.change_balance(ctx.author.id, -bet)
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
        role_id = role.lstrip('<@&').rstrip('>')
        roles_income[int(role_id)] = int(income)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        members_list = guild.members
        for member in members_list:
            users[member.id] = EconomicsUser(member.id, member.guild)
    guilds_list = bot.guilds
    for guild in []:  # guilds_list:
        for channel in guild.text_channels:
            await channel.send('Бот-экономика готов к работе')
    print('Ready!')


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
TOKEN = "TOKEN"
bot.run(TOKEN)
