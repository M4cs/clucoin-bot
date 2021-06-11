import logging
import discord
import asyncio
from omegaconf import OmegaConf
from discord.ext.commands import Bot
from discord.ext import tasks
from web3 import Web3
from .constants import ABI
import requests
from logging import getLogger

logger = getLogger(__name__)

conf = OmegaConf.load('config.yaml')


class PriceHold:
    def __init__(self):
        self.last_price = -1

ph = PriceHold()

bot = Bot('-')
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
contract = w3.eth.contract(
    address="0x10ED43C718714eb63d5aA57B78B54704E256024E", abi=ABI
)


def get_change():
    res = requests.get('https://api.coingecko.com/api/v3/coins/clucoin').json()
    
    return float(res.get('market_data').get('price_change_percentage_24h'))

def get_7d_change():
    res = requests.get('https://api.coingecko.com/api/v3/coins/clucoin').json()
    
    return float(res.get('market_data').get('price_change_percentage_7d'))

def get_price():
    amounts = contract.functions.getAmountsOut(
        1000000000,
        [
            Web3.toChecksumAddress(x)
            for x in [
                "0x1162e2efce13f99ed259ffc24d99108aaa0ce935",
                "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
            ]
        ],
    ).call()
    usd = w3.fromWei(amounts[-1], "ether")
    return usd

@bot.event
async def on_ready():
    logger.warning('Started CluCoin Price Bot')
    bot.loop.create_task(update_price())
    price = f'{get_price():.12f}'
    change = get_change()
    higher = False
    if get_price() > ph.last_price:
        higher = True
    ph.last_price = get_price()
    await bot.change_presence(activity=discord.Activity(type=discord.activity.ActivityType.watching, name=f"24hr: {change:.2f}%"))
    await bot.get_guild(833793153131348046).get_member(bot.user.id).edit(nick=f"{'⬊' if not higher else '⬈'} {price[2:]}")
    roles = await bot.get_guild(833793153131348046).fetch_roles()
    role = None
    for r in roles:
        if r.id == 851219215230959617:
            role = r
            break
    if higher:
        await role.edit(server=bot.get_guild(833793153131348046), role=role, colour=0x00ff00)
    else:
        await role.edit(server=bot.get_guild(833793153131348046), role=role, colour=0xff0000)

@bot.command('price')
async def on_price(ctx):
    change = get_change()
    await bot.change_presence(activity=discord.Activity(type=discord.activity.ActivityType.watching, name=f"24hr: {change:.2f}% | -price"))
    price = get_price()
    strprice = f'{get_price():.12f}'
    color = 0xff0000
    higher = False
    if price > ph.last_price:
        higher = True
        color = 0x00ff00
    ph.last_price = get_price()
    await bot.get_guild(833793153131348046).get_member(bot.user.id).edit(nick=f"{'⬊' if not higher else '⬈'} {strprice[2:]}")
    embed = discord.Embed(name="Current Clu Price {'⬊' if not higher else '⬈'}", description=f"{get_price():.12f}", color=color)
    embed.add_field(name="24hr Change", value=f"{get_change():.2f}%")
    embed.add_field(name="7d Change", value=f"{get_7d_change():.2f}%")
    await ctx.reply(embed=embed)
    roles = await bot.get_guild(833793153131348046).fetch_roles()
    role = None
    for r in roles:
        if r.id == 851219215230959617:
            role = r
            break
    if higher:
        await role.edit(server=bot.get_guild(833793153131348046), role=role, colour=0x00ff00)
    else:
        await role.edit(server=bot.get_guild(833793153131348046), role=role, colour=0xff0000)
    

async def update_price():
    while True:
        logger.warning('Updating Price Information..')
        price = f'{get_price():.12f}'
        change = get_change()
        higher = False
        await bot.change_presence(activity=discord.Activity(type=discord.activity.ActivityType.watching, name=f"24hr: {change:.2f}% | -price"))
        if get_price() > ph.last_price:
            higher = True
        ph.last_price = get_price()
        await bot.get_guild(833793153131348046).get_member(bot.user.id).edit(nick=f"{'⬊' if not higher else '⬈'} {price[2:]}")
        # roles = await bot.get_guild(833793153131348046).fetch_roles()
        # role = None
        # for r in roles:
        #     if r.id == 851219215230959617:
        #         role = r
        #         break
        # if higher:
        #     await role.edit(server=bot.get_guild(833793153131348046), role=role, colour=0x00ff00)
        # else:
        #     await role.edit(server=bot.get_guild(833793153131348046), role=role, colour=0xff0000)
        logger.warning('We sleeping snore snore')
        await asyncio.sleep(60)

if __name__ == "__main__":
    bot.run(conf.token)