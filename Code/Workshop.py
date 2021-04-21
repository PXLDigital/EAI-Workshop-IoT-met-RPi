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
    channel = bot.get_channel(CHANNEL_ID) 
    msg_sent = False

    while True:
        try:
            if alarmActief == 1:
                time.sleep(0.1)
                current_state = GPIO.input(pir_sensor)
                if current_state == 1:
                    if not msg_sent:
                        await channel.send('Beweging gedetecteerd')
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
    print('Bot opgestart en ingelogd als:')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def foto(ctx):
    """Er wordt foto gemaakt en doorgestuurd."""
    camera.capture('/home/pi/Desktop/IOT_Workshop/image.jpg')
    await ctx.send(file=discord.File('/home/pi/Desktop/IOT_Workshop/image.jpg'))
    
@bot.command()
async def video(ctx):
    """Er wordt een video van 3 seconden gemaakt en doorgestuurd."""
    convert_video('/home/pi/Desktop/IOT_Workshop/video.h264', '/home/pi/Desktop/IOT_Workshop/video.mp4', 3)
    await ctx.send(file=discord.File('/home/pi/Desktop/IOT_Workshop/video.mp4'))
    commando = "rm " +"/home/pi/Desktop/IOT_Workshop/video.mp4"
    call([commando], shell=True)

@bot.command()
async def beveiliging(ctx, alarm : str):
    """Het alarm wordt aan en uit gezet (aan/uit)."""
    alarm = alarm.lower()
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
async def meting(ctx):
    """De temperatuur en luchtvochtigheid worden opgemeten."""
    await ctx.send('De temperatuur en luchtvochtigheid worden gemeten, even geduld. De resultaten worden zodadelijk verstuurd.')
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, gpio)
    if humidity is not None and temperature is not None:
        await ctx.send('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        await ctx.send('Ai, er ging iets mis bij het uitvoeren van de meting. Probeer het even opnieuw.')

@bot.command()
async def schakelaar(ctx, switch : str):
    """De relais wordt aan en uit gezet (gesloten/open)."""
    switch = switch.lower()
    global gesloten
    if switch == 'gesloten' and gesloten == 0:
        GPIO.output(gpio2,GPIO.HIGH)
        gesloten = 1
        await ctx.send('RELAIS Gesloten')
    elif switch == 'open' and gesloten == 1:
        GPIO.output(gpio2,GPIO.LOW)
        gesloten = 0
        await ctx.send("RELAIS Open")
    elif switch == 'gesloten' and gesloten == 1:
        await ctx.send('RELAIS Is Al Gesloten!')
    elif switch == 'open' and gesloten == 0:
        await ctx.send("RELAIS Is Al Open!")
    else:
        await ctx.send('Commando niet herkend: gebruik gesloten/open')

bot.loop.create_task(motionDetection())
bot.run(TOKEN)
