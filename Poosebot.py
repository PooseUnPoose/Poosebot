import asyncio
import discord
from discord.ext import commands
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()

# Corrected line: Pass the environment variable name as a string
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

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

    #Balance & help commands
    if message.content.lower().startswith('!register'):
        StartingBalance = 1000
        try:
            with open('Users.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
            with open('Users.json', 'w') as file:
                json.dump(data, file)
        nickname = str(message.author.nick)
        if nickname in data:
            Sentmessage = "You are already registered"
        else:
            Sentmessage = "Registering {0.author.mention}".format(message)
            print(Sentmessage)
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await message.channel.send(embed=embed)
            Sentmessage = "You have a starting Balance of " + str(StartingBalance)
            data[nickname] = StartingBalance
            with open('Users.json', 'w') as file:
                json.dump(data, file)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)

    if message.content.lower().startswith('!balance'):
        with open('Users.json', 'r') as file:
            data = json.load(file)
        user = str(message.author.nick)
        if user in data:
            balance = data[user]
            Sentmessage = f"Your balance is {balance}"
        else:
            Sentmessage = "You are not registered"
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)

    if message.content.lower().startswith('!leaderboard'):
        with open('Users.json', 'r') as file:
            data = json.load(file)
        data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        Sentmessage = "Leaderboard\n"
        for key, value in data.items():
            Sentmessage += f"{key} : {value}\n"
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)

    if message.content.lower().startswith('!welfare'):
        with open('Users.json', 'r') as file:
            data = json.load(file)
        user = str(message.author)
        if user in data:
            balance = data[user]
            if balance < 10:
                new_balance = balance + 10
                Sentmessage = f"You received 10 welfare points. Your new balance is {new_balance}"
                data[user] = new_balance
                with open('Users.json', 'w') as file:
                    json.dump(data, file)
            else:
                Sentmessage = "You already have enough balance"
        else:
            Sentmessage = "You are not registered"
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)

    if message.content.lower().startswith('!help'):
        Sentmessage = "Commands:\n!register: Register your self \n!balance: Check your balance\n!deathroll [bet]: Roll down with the computer, first to 1 loses\n!deathrollvs [Opponent] [Bet] \n!leaderboard: List the richest users\n!welfare: gives you some welfare if you're broke\n!help"
        print(Sentmessage)
        embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
        await message.channel.send(embed=embed)

    #Games
    if message.content.lower().startswith('!roll '):
        roll_amount = int(message.content.split()[1])
        with open('Users.json', 'r') as file:
            data = json.load(file)
        user = str(message.author.nick)
        if user in data:
            balance = data[user]
            if roll_amount <= balance:
                PlayerRollValue = 0
                ComputerRollValue = 0
                Sentmessage =""
                RollMax = roll_amount
                while (PlayerRollValue != 1) | (ComputerRollValue != 1):                
                    PlayerRollValue = random.randint(1, RollMax)
                    RollMax = PlayerRollValue
                    Sentmessage += f"You rolled {PlayerRollValue}\n "
                    if PlayerRollValue == 1:
                        new_balance = balance - roll_amount
                        Sentmessage += f"You Lose! Your new balance is {new_balance}"
                        data[user] = new_balance
                        with open('Users.json', 'w') as file:
                            json.dump(data, file)
                        embed = discord.Embed(title=str(message.author)+"'s Roll Result",description=Sentmessage, color=discord.Color.green())
                        await message.channel.send(embed=embed)
                        break
                    else:
                        ComputerRollValue = random.randint(1, RollMax)
                        Sentmessage += f"Computer rolled {ComputerRollValue}\n "
                        RollMax = ComputerRollValue
                        if ComputerRollValue == 1:
                            new_balance = balance + roll_amount
                            Sentmessage += f"You Win! Your new balance is {new_balance}"
                            data[user] = new_balance
                            with open('Users.json', 'w') as file:
                                json.dump(data, file)
                            embed = discord.Embed(title=str(message.author)+"'s Roll Result", description=Sentmessage, color=discord.Color.green())
                            await message.channel.send(embed=embed)
                            break
            else:
                Sentmessage = "Insufficient balance for deathroll that ammount"
                embed = discord.Embed(title=str(message.author)+" is poor", description=Sentmessage, color=discord.Color.green())
                await message.channel.send(embed=embed)

                
        else:
            Sentmessage = "You are not registered"
        print(Sentmessage)
    
    if message.content.lower().startswith('!deathrollvs '):
        roll_amount = int(message.content.split()[2])
        with open('Users.json', 'r') as file:
            data = json.load(file)
        user1 = str(message.author.nick)
        user2 = str(message.content.split()[1])
        if user1 in data and user2 in data:
            balance1 = data[user1]
            balance2 = data[user2]
            if roll_amount <= balance1 and roll_amount <= balance2:
                await message.channel.send(f"{user2}, do you accept the deathroll challenge from {user1}? Type '!accept' to proceed.")
                def check_acceptance(m):
                    return m.author.nick == user2 and m.content.lower() == '!accept'
                try:
                    acceptance_message = await client.wait_for('message', check=check_acceptance, timeout=60)
                except asyncio.TimeoutError:
                    Sentmessage = f"{user2} did not accept the deathroll challenge."
                    embed = discord.Embed(title="Deathroll Challenge", description=Sentmessage, color=discord.Color.green())
                    await message.channel.send(embed=embed)
                    return
                else:
                    Sentmessage = f"{user2} accepted the deathroll challenge!"
                    embed = discord.Embed(title="Deathroll Challenge", description=Sentmessage, color=discord.Color.green())
                    await message.channel.send(embed=embed)

                Player1RollValue = 0
                Player2RollValue = 0
                Sentmessage = ""
                RollMax = roll_amount
                while (Player1RollValue != 1) and (Player2RollValue != 1):
                    Player1RollValue = random.randint(1, RollMax)
                    RollMax = Player1RollValue
                    Sentmessage += f"{user1} rolled {Player1RollValue}\n"
                    if Player1RollValue == 1:
                        new_balance1 = balance1 - roll_amount
                        new_balance2 = balance2 + roll_amount
                        Sentmessage += f"{user1} loses! {user1}'s new balance is {new_balance1}\n"
                        Sentmessage += f"{user2} wins! {user2}'s new balance is {new_balance2}"
                        data[user1] = new_balance1
                        data[user2] = new_balance2
                        with open('Users.json', 'w') as file:
                            json.dump(data, file)
                        embed = discord.Embed(title="Deathroll Result", description=Sentmessage, color=discord.Color.green())
                        await message.channel.send(embed=embed)
                        break
                    else:
                        Player2RollValue = random.randint(1, RollMax)
                        Sentmessage += f"{user2} rolled {Player2RollValue}\n"
                        RollMax = Player2RollValue
                        if Player2RollValue == 1:
                            new_balance1 = balance1 + roll_amount
                            new_balance2 = balance2 - roll_amount
                            Sentmessage += f"{user1} wins! {user1}'s new balance is {new_balance1}\n"
                            Sentmessage += f"{user2} loses! {user2}'s new balance is {new_balance2}"
                            data[user1] = new_balance1
                            data[user2] = new_balance2
                            with open('Users.json', 'w') as file:
                                json.dump(data, file)
                            embed = discord.Embed(title=f"{user1} Vs {user2}", description=Sentmessage, color=discord.Color.green())
                            await message.channel.send(embed=embed)
                            break
            else:
                Sentmessage = "Insufficient balance for deathroll that amount"
                embed = discord.Embed(title="Insufficient Balance", description=Sentmessage, color=discord.Color.green())
                await message.channel.send(embed=embed)
        else:
            Sentmessage = "One or both users are not registered"
            embed = discord.Embed(title="User Not Registered", description=Sentmessage, color=discord.Color.green())
            await message.channel.send(embed=embed)

    if message.content.lower().startswith('!poose') or message.content.lower().startswith('!pt'):
        print('Taking Screenshot')
        getScreenshotOfClass('https://classicwowarmory.com/character/us/doomhowl/Poosehunt', 'extra', 'pooselevel.png')
        await message.channel.send(file=discord.File('pooselevel.png'))
        os.remove('pooselevel.png')

#-------------------------------------------------------------------------------------
    #Admin commands
    if message.content.lower().startswith('!admingive '):
        if str(message.author) != "pooseunpoose":
            Sentmessage = "You are not authorized to use this command"
            print(Sentmessage)
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await message.channel.send(embed=embed)
        else:
            with open('Users.json', 'r') as file:
                data = json.load(file)
            user = str(message.content.split()[1])
            amount = int(message.content.split()[2])
            if user in data:
                balance = data[user]
                new_balance = balance + amount
                Sentmessage = f"{user} received {amount} points. Their new balance is {new_balance}"
                data[user] = new_balance
                with open('Users.json', 'w') as file:
                    json.dump(data, file)
            else:
                Sentmessage = "User is not registered"
            print(Sentmessage)
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await message.channel.send(embed=embed)

    if message.content.lower().startswith('!admintax '):
        if str(message.author) != "pooseunpoose":
            Sentmessage = "You are not authorized to use this command"
            print(Sentmessage)
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await message.channel.send(embed=embed)
        else:
            with open('Users.json', 'r') as file:
                data = json.load(file)
            user = str(message.content.split()[1])
            amount = int(message.content.split()[2])
            if user in data:
                balance = data[user]
                new_balance = balance - amount
                Sentmessage = f"{user} lost {amount} points. Their new balance is {new_balance}"
                data[user] = new_balance
                with open('Users.json', 'w') as file:
                    json.dump(data, file)
            else:
                Sentmessage = "User is not registered"
            print(Sentmessage)
            embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
            await message.channel.send(embed=embed)

    # if message.content.lower().startswith('!nuke'):
    #     if str(message.author) != "pooseunpoose":
    #         Sentmessage = "You are not authorized to use this command"
    #         print(Sentmessage)
    #         embed = discord.Embed(description=Sentmessage, color=discord.Color.green())
    #         await message.channel.send(embed=embed)
    #     else:
    #         await message.channel.purge()
    #         Sentmessage = "Meganuke has been activated"
    #         print(Sentmessage)
        


client.run(TOKEN)
