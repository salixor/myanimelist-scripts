import discord
import asyncio

import csv
import urllib.request
import codecs

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as', flush=True)
    print(client.user.name, flush=True)
    print(client.user.id, flush=True)
    print('------', flush=True)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('!anime_stats') or message.content.lower().startswith('!manga_stats'):
        if message.content.lower().startswith('!anime_stats'):
            worktype = 'anime'
        elif message.content.lower().startswith('!manga_stats'):
            worktype = 'manga'
        else:
            return

        message_split = message.content.split(" ")

        if len(message_split) <= 1:
            await client.send_message(message.channel, 'Please type `!{}_stats <id>`.'.format(worktype))
        else:
            search_id = message_split[1]

            if not search_id.isnumeric():
                await client.send_message(message.channel, 'Please type `!{}_stats <id>`.'.format(worktype))
            else:
                search_id = int(search_id)

                url = 'http://cocchi.iiens.net/MALUpdater/shared_works_' + worktype + '.csv'
                req = urllib.request.urlopen(url)

                csvfile = csv.reader(codecs.iterdecode(req, 'utf-8'), delimiter='|')
                line_match = []

                for index, line in enumerate(csvfile):
                    if index == 0:
                        pseudos = [pseudo for pseudo in line]
                    else:
                        id = int(line[0])
                        if id == search_id:
                            line_match = line
                            break

                if line_match != []:
                    title = line_match[1]
                    poster_url = line_match[3]
                    mal_url = "https://myanimelist.net/{}/{}".format(worktype, search_id)

                    result = discord.Embed(title=title, url=mal_url, color=0xf7ed3b)
                    result.set_footer(text=worktype.capitalize(), icon_url="https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png")
                    result.set_thumbnail(url=poster_url)

                    statuses_scores = [s for s in line_match[4:4+len(pseudos)]]

                    for index, pseudo in enumerate(pseudos):
                        if statuses_scores[index] == 'O':
                            result.add_field(name=pseudo, value="On-hold")
                        elif statuses_scores[index] == 'D':
                            result.add_field(name=pseudo, value="Dropped")
                        elif statuses_scores[index] == 'P' and worktype == "anime":
                            result.add_field(name=pseudo, value="Plan to watch")
                        elif statuses_scores[index] == 'P' and worktype == "manga":
                            result.add_field(name=pseudo, value="Plan to read")
                        elif statuses_scores[index].isnumeric():
                            if int(statuses_scores[index]) == 0:
                                result.add_field(name=pseudo, value="Not yet rated")
                            else:
                                result.add_field(name=pseudo, value="Score : " + statuses_scores[index])
                        else:
                            result.add_field(name=pseudo, value="Not in list")

                    await client.send_message(message.channel, embed=result)
                else:
                    await client.send_message(message.channel, 'No such anime was found.')


client.run('MzIzMjExNTQzNzQxNDY0NTc4.DB34RA.bdVDgEe9KXHKiBhwoRoYtojfHGY')
