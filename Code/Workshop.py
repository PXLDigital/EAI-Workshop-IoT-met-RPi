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

#Toegang token voor discord server
TOKEN = 'ODIzMjA4NDc4MjU5NTQ0MDg0.YFdeow.Z54zEz5Gv09vQXruzKEz7XdOtT8'
description = '''IOT Workshop - Discord Bot'''
bot = commands.Bot(command_prefix='?', description=description, help_command=None)
#bot = commands.Bot(command_prefix='?', description=description)
pfp_path = "avatar.jpg"
fp = open(pfp_path, 'rb')
pfp = fp.read()

#DHT declareren
dht_sensor = Adafruit_DHT.DHT11
gpio = 18 #GPIO voor dht sensor

#PIR declareren
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pir_sensor = 24 #GPIO voor pir sensor
GPIO.setup(pir_sensor, GPIO.IN, GPIO.PUD_DOWN) #voor ruis weg te werken
current_state = 0
alarmActief = 0

#RELAIS declareren
gpio2 = 21
gesloten = 0
GPIO.setup(gpio2,GPIO.OUT)
GPIO.output(gpio2,GPIO.LOW)

#CAMERA declaren + functie
camera = PiCamera()
camera.resolution = (640,480)
def convert_video(file_h264, file_mp4, lengteVideo):
    # Opnemen gekozen lengte (lengteVideo)
    camera.start_recording(file_h264)
    time.sleep(lengteVideo)
    camera.stop_recording()
    # Omzetten h264 formaat naa mp4 formaat
    command = "MP4Box -add " + file_h264 + " " + file_mp4
    call([command], shell=True)


#Stuurt "motion detected" bij beweging
async def motionDetection():
    await bot.wait_until_ready()
    channel = discord.utils.get(bot.get_all_channels(), name="algemeen")
    #print(channel.id)
    #channel = bot.get_channel(829712542741692457) # replace with channel ID that you want to send to
    msg_sent = False

    while True:
        try:
            if alarmActief == 1:
                time.sleep(0.1)
                current_state = GPIO.input(pir_sensor)
                if current_state == 1:
                    if not msg_sent:
                        await channel.send('Beweging gedetecteerd')
                        print('beweging')
                        convert_video('/home/pi/Desktop/IOT_Workshop/video.h264', '/home/pi/Desktop/IOT_Workshop/video.mp4', 5)
                        await channel.send(file=discord.File('/home/pi/Desktop/IOT_Workshop/video.mp4'))
                        commando = "rm " +"/home/pi/Desktop/IOT_Workshop/video.mp4"
                        call([commando], shell=True)
                        msg_sent = True
                    else:
                        msg_sent = False
                    #print("GPIO pin %s is %s" % (pir_sensor, current_state)) # motion detected
                    time.sleep(4) # wait 4 seconds for PIR to reset.
        except KeyboardInterrupt:
            GPIO.cleanup()
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    #await bot.user.edit(avatar = pfp)
    print('Bot opgestart en ingelogd als:')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.group(invoke_witout_command=True)
async def help(ctx):
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title = "Help", description = "Uitleg van comando's. gebruik ?help [commando] voor extra uitleg \n <> betekend moet gebruikt worden, [] betekend mag gebuikt worden", color = discord.Colour.blue())
    embed.add_field(name="?purge <x>", value="verwijderen van x aanal berichten",  inline=False)
    embed.add_field(name="?help", value="laat dit scherm",  inline=False)
    embed.add_field(name="?foto", value="Er wordt foto gemaakt en doorgestuurd.",  inline=False)
    embed.add_field(name="?video [x]", value="Er wordt een video van x seconden gemaakt en doorgestuurd\nAls er niks wordt megegeven wordt er een video van 3 seconden gemaakt",  inline=False)
    embed.add_field(name="?beveiliging <x>", value="De beveiliging wordt aan of uit gezet \nGebruik Aan of Uit op de plaats van x",  inline=False)
    embed.add_field(name="?meting", value="De temperatuur en luchtvochtigheid worden opgemeten.",  inline=False)
    embed.add_field(name="?schakelaar <x>", value="De relais wordt aan en uit gezet.\nGebruik Aan of Uit op de plaats van x",  inline=False)

    await ctx.send(embed = embed)

@bot.command()
async def purge(ctx, number):
    """verwijderen van x aantal  berichten"""
    await ctx.channel.purge(limit=1)
    number = int(number) #aantal berichten om te verwijderen
    await ctx.channel.purge(limit=number)

@bot.command()
async def foto(ctx):
    """Er wordt foto gemaakt en doorgestuurd."""
    await ctx.channel.purge(limit=1)
    camera.capture('/home/pi/Desktop/IOT_Workshop/image.jpg')
    await ctx.send(file=discord.File('/home/pi/Desktop/IOT_Workshop/image.jpg'))
    
@bot.command()
async def video(ctx,lenght : int=3):
    """Er wordt een video van x seconden gemaakt en doorgestuurd.(als er niks wordt megegeven is het 3 seconden )"""
    convert_video('/home/pi/Desktop/IOT_Workshop/video.h264', '/home/pi/Desktop/IOT_Workshop/video.mp4', lenght)
    await ctx.channel.purge(limit=1)
    await ctx.send(file=discord.File('/home/pi/Desktop/IOT_Workshop/video.mp4'))
    commando = "rm " +"/home/pi/Desktop/IOT_Workshop/video.mp4"
    call([commando], shell=True)

@bot.command()
async def beveiliging(ctx, alarm : str):
    """Het alarm wordt aan en uit gezet."""
    await ctx.channel.purge(limit=1)
    global alarmActief
    if alarm == 'aan' and alarmActief == 0:
        alarmActief = 1
        await ctx.send('Alarm wordt ingeschakeld')
    elif alarm == 'uit' and alarmActief == 1:
        alarmActief = 0
        await ctx.send("Alarm wordt uitgeschakeld")
    elif alarm == 'aan' and alarmActief == 1:
        await ctx.send('Alarm is al ingeschakeld')
    elif alarm == 'uit' and alarmActief == 0:
        await ctx.send('Alarm is al uitgeschakeld')
    else:
        await ctx.send('Commando niet herkend: gebruik aan/uit')

@bot.command()
async def spam(ctx, number: int = 100):
    """"voor bart."""
    await ctx.channel.purge(limit=1)
    for count in range(number):
        await ctx.send('spammen')
        time.sleep(0.5)
        print(count)
    time.sleep(5)
    await ctx.channel.purge(limit=number)

@bot.command()
async def meting(ctx):
    """De temperatuur en luchtvochtigheid worden opgemeten."""
    await ctx.channel.purge(limit=1)
    await ctx.send('De temperatuur en luchtvochtigheid worden gemeten, even geduld. De resultaten worden zodadelijk verstuurd')
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, gpio)
    await ctx.channel.purge(limit=1)
    if humidity is not None and temperature is not None:
        await ctx.send('Temp={0:0.1f}°C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        await ctx.send('Ai, er ging iets mis bij het uitvoeren van de meting. Probeer het even opnieuw.')

@bot.command()
async def schakelaar(ctx, switch : str):
    """De relais wordt aan en uit gezet."""
    await ctx.channel.purge(limit=1)
    global gesloten
    if switch == 'aan' and gesloten == 0:
        GPIO.output(gpio2,GPIO.HIGH)
        gesloten = 1
        await ctx.send("RELAIS Gesloten")
    elif switch == 'uit' and gesloten == 1:
        GPIO.output(gpio2,GPIO.LOW)
        gesloten = 0
        await ctx.send("RELAIS Open")
    elif switch == 'aan' and gesloten == 1:
        await ctx.send("RELAIS Is Al Gesloten!")
    elif switch == 'uit' and gesloten == 0:
        await ctx.send("RELAIS Is Al Open!")
    else:
        await ctx.send('Commando niet herkend: gebruik aan/uit')

@bot.command()
async def test(ctx):
    await ctx.channel.purge(limit=1)
    await ctx.send("test wordt gestart")
    time.sleep(1)
    await ctx.send("test RELAIS")
    global gesloten
    if gesloten == 1:
        GPIO.output(gpio2,GPIO.LOW)
        await ctx.send("RELAIS Open")
        time.sleep(5)
        GPIO.output(gpio2,GPIO.HIGH)
        await ctx.send("RELAIS Gesloten")
    else:
        GPIO.output(gpio2,GPIO.HIGH)
        await ctx.send("RELAIS Gesloten")
        time.sleep(5)
        GPIO.output(gpio2,GPIO.LOW)
        await ctx.send("RELAIS Open")
    time.sleep(1)
    await ctx.send("test camera foto")
    camera.capture('/home/pi/Desktop/IOT_Workshop/image.jpg')
    await ctx.send(file=discord.File('/home/pi/Desktop/IOT_Workshop/image.jpg'))
    time.sleep(1)
    await ctx.send("test camera Video")
    convert_video('/home/pi/Desktop/IOT_Workshop/video.h264', '/home/pi/Desktop/IOT_Workshop/video.mp4', 3)
    await ctx.send(file=discord.File('/home/pi/Desktop/IOT_Workshop/video.mp4'))
    commando = "rm " +"/home/pi/Desktop/IOT_Workshop/video.mp4"
    call([commando], shell=True)
    time.sleep(1)
    await ctx.send("test DHT Sensor")
    await ctx.send('De temperatuur en luchtvochtigheid worden gemeten, even geduld. De resultaten worden zodadelijk verstuurd')
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, gpio)
    await ctx.channel.purge(limit=1)
    if humidity is not None and temperature is not None:
        await ctx.send('Temp={0:0.1f}°C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        await ctx.send('Ai, er ging iets mis bij het uitvoeren van de meting. Probeer het even opnieuw.')
    time.sleep(1)
    await ctx.send("test motion detector")
    current_state = 0
    while current_state == 0:
        current_state = GPIO.input(pir_sensor)
        time.sleep(1)
    await ctx.send("motion detected")
    await ctx.send("test compleet")
bot.loop.create_task(motionDetection())
bot.run(TOKEN)
