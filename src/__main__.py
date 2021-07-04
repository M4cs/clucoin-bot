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

def get_info():
    res = requests.get('https://api.coingecko.com/api/v3/coins/clucoin').json()
    res1 = requests.get('https://api.clucoin.com/v1/data').json()
    print(res1)
    price = get_price()
    return {
        '24hr_change': float(res.get('market_data').get('price_change_percentage_24h')),
        '7d_change': float(res.get('market_data').get('price_change_percentage_7d')),
        'ath': float(res.get('market_data').get('ath').get('usd')),
        'market_cap': float(res1.get('data').get('market_cap')),
        'supply': float(res1.get('data').get('supply')),
        'total_burnt': float(res1.get('data').get('supply')),
        'price': f'{price:.12f}'
    }


@bot.event
async def on_ready():
    logger.warning('Started CluCoin Price Bot')
    bot.loop.create_task(update_price())
    info = get_info()
    higher = False
    if float(info['price']) > ph.last_price:
        higher = True
    ph.last_price = float(info['price'])
    await bot.change_presence(activity=discord.Activity(type=discord.activity.ActivityType.watching, name=f"24hr: {info['24hr_change']:.2f}%"))
    await bot.get_guild(833793153131348046).get_member(bot.user.id).edit(nick=f"{'⬊' if not higher else '⬈'} {info['price'][2:]}")

@bot.command('price')
async def on_price(ctx):
    info = get_info()
    higher = False
    color = 0xff0000
    if float(info['price']) > ph.last_price:
        higher = True
        color = 0x00ff00
    ph.last_price = float(info['price'])
    await bot.get_guild(833793153131348046).get_member(bot.user.id).edit(nick=f"{'⬊' if not higher else '⬈'} {info['price'][2:]}")
    embed = discord.Embed(title="CluCoin Price Info", description=f"{float(info['price']):.12f}", color=color)
    embed.add_field(name="💸 Price:", value=f"{info['price']}")
    embed.add_field(name="💱 24hr Change:", value=f"{info['24hr_change']:,}")
    embed.add_field(name="📆 Weekly Change:", value=f"{info['7d_change']:,}")
    embed.add_field(name="📈 ATH:", value=f"{info['ath']:,}")
    embed.add_field(name="💰 Market Cap:", value=f"{info['market_cap']:,}")
    embed.add_field(name="💵 Total Supply:", value=f"{info['supply']:,}")
    embed.add_field(name="🔥 Total Burnt:", value=f"{info['total_burnt']:,}")
    await ctx.reply(embed=embed)

async def update_price():
    while True:
        logger.warning('Updating Price Information..')
        info = get_info()
        higher = False
        if float(info['price']) > float(ph.last_price):
            higher = True
        ph.last_price = float(info['price'])
        await bot.change_presence(activity=discord.Activity(type=discord.activity.ActivityType.watching, name=f"24hr: {info['24hr_change']:.2f}%"))
        await bot.get_guild(833793153131348046).get_member(bot.user.id).edit(nick=f"{'⬊' if not higher else '⬈'} {info['price'][2:]}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    bot.run(conf.token)