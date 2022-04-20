import discord
from discord.ext import commands
import random

client = discord.Client()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


class Things(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_role_id = False

    @commands.command(name='test_role')
    async def test_role(self, ctx, role):
        author_roles = list(map(lambda x: x.id, ctx.author.roles)) # Получаю список айдишников ролей автора сообщения
        if self.admin_role_id in author_roles or not self.admin_role_id:
            role_id = role.lstrip('<@&').rstrip('>')
            self.admin_role_id = role_id
            await ctx.channel.send('Установлена новая роль администратора!')
        else:
            await ctx.channel.send(f'Увы, команда доступна только для <@&{self.admin_role_id}>')


@bot.event
async def on_message(message):
    print(message.content)
    await bot.process_commands(message)


bot.add_cog(Things(bot))
TOKEN = "OTY2MzY3OTM2NTcyOTY5MDEw.YmAuRg.wLyCwPRv2Ji7_XP5rOd51yfG_LU"
bot.run(TOKEN)
