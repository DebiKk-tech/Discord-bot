from discord.utils import get


class ShopItem:
    def __init__(self, price, name, guild, role_given=False, money_given=False, message=False, role_taken=False, role_needed=False):
        self.price = price
        self.owner = False
        self.name = name
        self.guild = guild
        self.role_given = role_given
        self.money_given = money_given
        self.message = message
        self.role_needed = role_needed
        self.role_taken = role_taken

    async def bought(self, buyer, channel):
        if buyer.get_balance() >= self.price:
            buyer.add_money(-self.price)
            buyer.add_item(self)
            self.owner = buyer
            await channel.send(f'Вы купили предмет: {self.name} за {self.price} рублей')

    async def activate(self, channel):
        if self.role_needed and get(self.guild.roles, id=self.role_needed) not in self.owner.member.roles:
            await channel.send(f'Вам нужна роль <@&{self.role_needed}> чтобы использовать {self.name}')
            return
        self.owner.remove_item(self)
        await channel.send(f'Вы использовали: {self.name}')
        if self.message:
            await channel.send(self.message)
        if self.role_given:
            role_given = get(self.guild.roles, id=self.role_given)
            await self.owner.member.add_roles(role_given)
        if self.money_given:
            self.owner.add_money(self.money_given)
        role_taken = get(self.guild.roles, id=self.role_taken)
        if self.role_taken and role_taken in self.owner.member.roles:
            await self.owner.member.remove_roles(role_taken)
