import discord
from discord.ext import commands
import random

client = discord.Client()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

users = {}


class Things(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_role_id = 966040422050857084

    @commands.command(name='test_role')
    async def test_role(self, ctx, role):
        author_roles = list(map(lambda x: x.id, ctx.author.roles)) # Получаю список айдишников ролей автора сообщения
        if self.admin_role_id in author_roles or not self.admin_role_id:
            role_id = role.lstrip('<@&').rstrip('>')
            self.admin_role_id = role_id
            await ctx.channel.send('Установлена новая роль администратора!')
        else:
            await ctx.channel.send(f'Увы, команда доступна только для <@&{self.admin_role_id}>')

    @commands.command(name='add_money')
    async def add_money(self, ctx, amount, target):
        author_roles = list(map(lambda x: x.id, ctx.author.roles))  # Получаю список айдишников ролей автора сообщения
        print(author_roles)
        if self.admin_role_id in author_roles or not self.admin_role_id:
            print(target)
            target = int(target.lstrip('<@').rstrip('>'))
            if target in users:
                users[target] += int(amount)
            else:
                users[target] = int(amount)
            await ctx.channel.send(f'Добавлено {amount} рублей пользователю <@{target}> \n Теперь у него {users[target]} рублей')
        else:
            await ctx.channel.send(f'Увы, команда доступна только для <@&{self.admin_role_id}>')

    @commands.command(name='balance')
    async def balance(self, ctx):
        id_need_to_check = int(ctx.author.id)
        if id_need_to_check in users:
            await ctx.channel.send(f'{ctx.author.mention}, ваш баланс составляет {users[id_need_to_check]} рублей')
        else:
            await ctx.channel.send('Перезайди на сервер, друже, тебя нет в базе данных')


@bot.event
async def on_message(message):
    print(message.content)
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    users[member.id] = 100
    await member.create_dm()
    await member.dm_channel.send(f'Привет, {member.name}! Добро пожаловать на сервер! Я начислил тебе 100 рублей, теперь они у тебя на счету!')


bot.add_cog(Things(bot))
TOKEN = "BOT_TOKEN"
bot.run(TOKEN)
