import discord
from discord.ext import commands
import time
import random
import datetime
import RPi.GPIO as GPIO
import asyncio
import Adafruit_DHT
from subprocess import call 
from picamera import PiCamera, Color

#Variabele voor token en channel_ID
TOKEN = 'PlaatsTokenHier'
CHANNEL_ID = PlaatsChannel_IdHier

#Toegang token voor discord server
description = '''IOT Workshop - Discord Bot'''
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Bot opgestart en ingelogd als:')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)
