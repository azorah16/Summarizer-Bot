# This is the code for a bot that summarizes a conversation during a time period 
# used: huggingface, python, discord.py, os, datetime, time, re, json
import os

import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# client = discord.Client(intents=intents)
# Create the bot instance
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

async def fetch_messages(ctx, start_time: str, end_time: str):
    channel = ctx.channel
    start = datetime.strptime(start_time, '%m/%d/%Y %H:%M:%S', tzinfo=None)
    end = datetime.strptime(end_time, '%m/%d/%Y %H:%M:%S')
    print(start_time)

    messages = []
    async for message in channel.history(after=start,before=end,limit=300):
        messages.append(message.author.name + ": " + message.content)

    return messages


def summarize_messages(messages):
    summary = "\n".join(messages)
    return summary


# Define a command
@bot.command()
async def summary(ctx, arg1, arg2):
    
    await ctx.send('you are not {} and Alifia is {}'.format(arg1, arg2))
    messages = await fetch_messages(ctx, arg1, arg2)
    summary = summarize_messages(messages)
    await ctx.send(f"Messages from {arg1} to {arg2}:\n{summary}")

    
    
# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if message.content.startswith('!'):
#         await message.channel.send('Gandu bache')

#     await bot.process_commands(message)
    
try:
  token = os.getenv("TOKEN") or ""
  if token == "":
    raise Exception("Please add your token to the Secrets pane.")
  bot.run(token)
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
