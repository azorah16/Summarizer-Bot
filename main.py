# This is the code for a bot that summarizes a conversation during a time period 
# used: huggingface, python, discord.py, os, datetime, time, re, json
# implement a command which allows user to set their timezone. give appropriate 
# message that they have to set their timezone if not in 'US/Central'.

# Maybe implement a database that stores the timezones of users.

import os
import discord
from discord.ext import commands
from datetime import datetime
import pytz
from pytz import timezone
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Create the bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


async def fetch_messages(ctx, start_time: str, end_time: str, t_z= "US/Central"):
    try:
        channel = ctx.channel
        utc = pytz.UTC
        zone = timezone(t_z)
        
        fmt='%m/%d/%Y %H:%M:%S'
        naive_start = datetime.strptime(start_time, fmt)
        naive_end = datetime.strptime(end_time, fmt)
        print(f"Not Parsed start_time: {naive_start}, end_time: {naive_end}")
        
        local_start = zone.localize(naive_start)
        local_end = zone.localize(naive_end)
        print(f"Local start_time: {local_start}, end_time: {local_end}")
        
        utc_start= local_start.astimezone(utc)
        utc_end= local_end.astimezone(utc)
        print(f"UTC start_time: {utc_start}, end_time: {utc_end}")
        
        messages = []
        async for message in channel.history(
            after=utc_start,before=utc_end,
            limit=300, oldest_first=True):
            
            if message.author != bot.user: #and message.startswith("/summary") == False:
                # print(message.content)
                messages.append(f'{message.author.name}: {message.content}')
                
        return messages
        
    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise

def summarize_messages():

    model_name = "t5-base"
    tokenizer = T5Tokenizer.from_pretrained(model_name, legacy = False)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # print(type(tokenizer))
    # print(type(model))
    
    convo = """
    summarize: 
    Person A: "Hello, my name is Ali Asghar."
    Person B: "Hey, Ali. Nice to meet you. I am Ahmed. Where do you study?"
    Person A: "I am studying at the University of Illinois Urbana Champaign."
    Person B: "Awesome! I am studying at the Mansehra Institute of Technology."
    """
# "\n".join(messages)

    input_text = convo
    input_ids = tokenizer.encode(
        input_text, return_tensors="pt",
        max_length=512, truncation=True)

    summary_ids = model.generate(
        input_ids, max_length=100, min_length=5,
        length_penalty=1.0, num_beams=4, early_stopping=True)
    
    summary = tokenizer.decode(
        summary_ids[0], skip_special_tokens=True)
    
    return summary

summary = summarize_messages()
print("Generated Summary:")
print(summary)


Define a command
@bot.command()
async def summary(ctx, start_time, end_time, t_z = "US/Central"):
    try:
        await ctx.send('command works')
        messages = await fetch_messages(ctx, start_time, end_time, t_z)
        summary = summarize_messages(messages)
        await ctx.send(f"Messages from {start_time} to {end_time}:\n{summary}")
        print(summary)
    except  Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"An error occurred: {e}")
    
    
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
