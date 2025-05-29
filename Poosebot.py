import asyncio
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import difflib

load_dotenv()

# Corrected line: Pass the environment variable name as a string
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) 
CISchanges = ""
intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def setup_hook(self):
        pass


async def print_hello_every_minute(channel):
    while True:
        global CISchanges
        getTimeTableChanges()
        with open('timetable_changes.txt', 'r') as file:
            lines = file.readlines()
        if CISchanges != "":   
            Sentmessage = CISchanges
            CISchanges = ""
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await channel.send(embed=embed)
        else: 
            print("No CIS changes found.")
        await asyncio.sleep(3600)  
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        client.loop.create_task(print_hello_every_minute(channel))
    else:
        print("Channel not found. Please check the CHANNEL_ID.")

def getScreenshotOfClass(url, id, outputfile):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, id))
        )
        element.screenshot(outputfile)
        print("Screenshot Taken")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
    finally:
        driver.quit()

def getTimeTableChanges():
    global CISchanges
    url = "https://www.ufv.ca/arfiles/includes/202509-timetable-changes.htm"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', id='table1')

        if table:
            rows = table.find_all('tr')
            new_data = []
            for row in rows:
                columns = row.find_all(['th', 'td'])
                row_data = [col.get_text(strip=True) for col in columns]
                new_data.append('\t'.join(row_data))
            with open('new_timetable_changes.txt', 'w') as new_file:
                new_file.write('\n'.join(new_data))
            try:
                with open('timetable_changes.txt', 'r') as old_file:
                    existing_data = old_file.read().splitlines()
            except FileNotFoundError:
                existing_data = []
            if new_data != existing_data:
                print("Differences detected (filtered by '- CIS '):")
                diff = difflib.unified_diff(existing_data, new_data, lineterm='', fromfile='Existing', tofile='New')
                CISchanges = ""
                for line in diff:
                    if "- CIS " in line:
                        CISchanges += line + '\n'
                        print(CISchanges)
                os.remove('timetable_changes.txt')  
                os.rename('new_timetable_changes.txt', 'timetable_changes.txt')  
                print("Timetable changes updated in 'timetable_changes.txt'")
            else:
                os.remove('new_timetable_changes.txt')
                print("No changes detected in the timetable.")
        else:
            print("Table with id='table1' not found on the page.")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")


Sentmessage = ""
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('!ping'):
        Sentmessage = 'pong'.format(message)
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)


    if message.content.lower().startswith('!timetable'):
        Sentmessage = "Fetching timetable changes..."
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)
        getTimeTableChanges()
        Sentmessage = "Timetable changes have been saved to 'timetable_changes.txt'"
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)
        with open('timetable_changes.txt', 'r') as file:
            lines = file.readlines()
        CISchanges = [line.strip() for line in lines if '- CIS ' in line]
        Sentmessage = '\n'.join(CISchanges) if CISchanges else "No CIS changes found."
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)


client.run(TOKEN)
