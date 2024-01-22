import ssl
from flask import Flask, request, Response, render_template
from discord import *
import aiohttp
import json
import asyncio
import os
import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError
from discordbot_utils import *
from makeEmbeds import *
from discord.ext import commands


app = Flask(__name__)

# https://discord.com/api/oauth2/authorize?client_id=1114908829713436672&permissions=268855376&scope=bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True
intents.moderation = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

invites = {}

with open("cred.json") as tokenfile:
    credential = json.load(tokenfile)
checkperms_roles = ["Justicar", "Defender"]

#pushing the Changes in form of the changelog into #changelog
async def pushChanges(change_what, change_where, change_why, change_note, authorAvatar, author):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(credential["webhook_changelog"], session=session)
        response = await webhook.send(embed=makeEmbeddedChangelog(change_what, change_where, change_why, change_note, authorAvatar, author), username='Servant of the 9th', avatar_url='https://cdn.discordapp.com/emojis/1113817526984515624.webp?size=96&quality=lossless', wait=True)
        message_id = str(response.id)
        channel_id = str(response.channel.id)

        return message_id, channel_id

async def pushEventPreview(data, authorAvatar, eventAuthor):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(credential["webhook_create_event"], session=session)
        response = await webhook.send(embed=makeEmbeddedEventPreview(data["event_name"], data["event_description"], data["event_time"], data["event_max_participants"], data["picture"], data["event_id"], authorAvatar, eventAuthor), username='Servant of the 9th', avatar_url='https://cdn.discordapp.com/emojis/1113817526984515624.webp?size=96&quality=lossless', wait=True)
        message_id = str(response.id)
        channel_id = str(response.channel.id)

        return message_id, channel_id

async def pushEventToEvents(newEventChannelID, data, authorAvatar, eventAuthor):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(credential["webhook_events"], session=session)
        response = await webhook.send(embed=makeEmbeddedEventPublic(newEventChannelID, data["event_name"], data["event_description"], data["event_time"], data["event_max_participants"], data["picture"], data["event_id"], authorAvatar, eventAuthor), username='Servant of the 9th', avatar_url='https://cdn.discordapp.com/emojis/1113817526984515624.webp?size=96&quality=lossless', wait=True)
        message_id = str(response.id)
        channel_id = str(response.channel.id)

        return message_id, channel_id

async def editEventPreview(data, authorAvatar, eventAuthor):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(credential["webhook_create_event"], session=session)
        previewMessageID = data["preview_message_id"]
        await webhook.edit_message(message_id=previewMessageID, embed=makeEmbeddedEventPreview(data["event_name"], data["event_description"], data["event_time"], data["event_max_participants"], data["picture"], data["event_id"], authorAvatar, eventAuthor))

async def editEventPublic(data, authorAvatar, eventAuthor):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(credential["webhook_events"], session=session)
        players = ""
        for i in range(len(data["signups"])):
            if data["signups"][i]["player" + str(i)] != "":
                playerToAdd = data["signups"][i]["player" + str(i)]
                players = players + "\n" + playerToAdd

        published_message_id = data["published_message_id"]
        await webhook.edit_message(message_id=published_message_id, embed=editEmbeddedEventPublic(data["newEventChannelID"], data["event_name"], data["event_description"], data["event_time"], data["event_max_participants"], players, data["picture"], data["event_id"], authorAvatar, eventAuthor))


async def sendAutomodPlayerAction(member, action, actionBy = None, reason = None, unix_timedoutUntil = None):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(credential["webhook_automod"], session=session)

        member_id = member.id
        member_profile_picture = member.display_avatar.url
        member_name = member.name

        if action == "leave":
            await webhook.send(embed=makeEmbeddedPlayerLeft(member_id, member_profile_picture, member_name), username='Servant of the 9th', avatar_url='https://cdn.discordapp.com/emojis/1113817526984515624.webp?size=96&quality=lossless')
        if action == "kick":
            await webhook.send(embed=makeEmbeddedPlayerKicked(member_id, member_profile_picture, member_name, actionBy, reason), username='Servant of the 9th', avatar_url='https://cdn.discordapp.com/emojis/1113817526984515624.webp?size=96&quality=lossless')
        if action == "ban":
            await webhook.send(embed=makeEmbeddedPlayerKicked(member_id, member_profile_picture, member_name, actionBy, reason), username='Servant of the 9th', avatar_url='https://cdn.discordapp.com/emojis/1113817526984515624.webp?size=96&quality=lossless')
        if action == "timeout":
            await webhook.send(embed=makeEmbeddedPlayerTimeout(member_id, member_profile_picture, member_name, actionBy, reason, unix_timedoutUntil), username='Servant of the 9th', avatar_url='https://cdn.discordapp.com/emojis/1113817526984515624.webp?size=96&quality=lossless')


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    activity = discord.Activity(
        name="The Order",
        type=discord.ActivityType.watching,
        details="Praying for EA",
        state="Believing in the 9th",
        start=datetime.datetime.utcnow(),
        large_image="chapel",
        large_text="Order of the 9th"
    )
    
    await client.change_presence(activity=activity, status=discord.Status.online)

@tree.command(name="hello")
async def hello(interaction):
    await interaction.response.send_message("Hello")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
@client.event
async def on_message(message):

    if message.channel.id == 1123314997901152299:
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        
    if message.author.id != client.user.id and message.channel.id == 1121034776497897482: #moderation
        if message.content == None or message.content == "":
            return
        else:
            await message.delete()

    if not message.content.startswith("Vote") and message.channel.id == 1123314997901152299: #moderation-votes
        await message.delete()

    if message.author.id != client.user.id and message.channel.id == 1119244292335079588 and not message.content.startswith('!cases ') and not message.content.startswith('!getwarnings ') and not message.content.startswith('!addwarning ') and not message.content.startswith('!removewarning '):
        await message.delete()

    if message.author.id != client.user.id and message.channel.id == 1127648406219804804:
        await message.delete()

    if message.content.startswith('!cases ') and message.channel.id == 1119244292335079588: #warning-cases channel
        userid = message.content[7:]
        if isInt(userid) == False:
            mustBeInt = await message.reply('User-ID must be an integer!')
            await mustBeInt.delete(delay=5)
        else:
            guild = message.guild
            user = guild.get_member(int(userid))
        
            if user is None:
                notFoundMessage = await message.reply('User not found.')
                await notFoundMessage.delete(delay=5)
                await message.delete(delay=5)
                return
            else:
                getWarningsData = getWarnings(int(userid))
                await message.add_reaction('✅')
                embed1 = discord.Embed(
                title='Cases for ' + user.name,
                description='User-ID: ' + str(user.id),
                color=discord.Color.yellow()
            )
                embed = embed1
                field_count = 0
                async for entry in guild.audit_logs(limit=100):
                        action = ''
                        if entry.target.id == user.id and entry.action in [discord.AuditLogAction.kick, discord.AuditLogAction.ban, discord.AuditLogAction.unban, discord.AuditLogAction.member_update]:
                            if entry.action == discord.AuditLogAction.kick:
                                action = "Kick"
                                timestamp = entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                reason = entry.reason
                                moderator = "<@" + str(entry.user.id) + ">"
                            if entry.action == discord.AuditLogAction.ban:
                                action = "Ban"
                                timestamp = entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                reason = entry.reason
                                moderator = "<@" + str(entry.user.id) + ">"
                            if entry.action == discord.AuditLogAction.unban:
                                action = "Unban"
                                timestamp = entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                reason = entry.reason
                                moderator = "<@" + str(entry.user.id) + ">"
                            if entry.action == discord.AuditLogAction.member_update and entry.user.id != entry.target.id:
                                action = "Timeout"
                                timestamp = entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                reason = entry.reason
                                moderator = "<@" + str(entry.user.id) + ">"
                            if action != '':
                                timestamp = entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                reason = entry.reason
                                moderator = "<@" + str(entry.user.id) + ">"
                                if field_count == 24:
                                    embed2 = discord.Embed(
                                    title='',
                                    description='',
                                    color=discord.Color.yellow()
                                )
                                    embed = embed2
                                if reason == None:
                                    embed.add_field(name=action, value='Reason: not given')
                                else:
                                    embed.add_field(name=action, value='Reason: ' + reason)
                                embed.add_field(name='Time', value=timestamp, inline=True)
                                embed.add_field(name="Made by", value=moderator, inline=True)
                                field_count = field_count + 3
                                embed.set_thumbnail(url=user.display_avatar.url)
                if not embed.fields:
                    embed.add_field(name='No actions found for this user', value='')
                    embed.set_thumbnail(url=user.display_avatar.url)
                                

                embed.set_footer(text='Bot created by \nniclas01', icon_url='https://cdn.discordapp.com/emojis/1115655349966479440.gif?size=96&quality=lossless')
                if field_count >= 24:
                    await message.channel.send(embed=embed1)
                    await message.channel.send(embed=embed2)
                else:
                    await message.channel.send(embed=embed1)
                await message.channel.send(embed=makeEmbeddedWarnings(getWarningsData))
                await message.delete(delay=5)

    if message.content.lower() == "goodnight" and client.user.id != message.author.id or message.content.lower() =="gn" and client.user.id != message.author.id or message.content.lower() =="gn guys" and client.user.id != message.author.id or message.content.lower() =="goodnight guys" and client.user.id != message.author.id:
        await message.reply("Goodnight! <3")
    if message.mentions:
        mentioned_users = message.mentions
        dontPingUser = 137654101692383233
        for user in mentioned_users:
            if user.id == dontPingUser and message.author.id != dontPingUser:
                await message.reply(embed=makeEmbeddedGraysunPing())
                channel_warning = client.get_channel(1119244292335079588)
                await channel_warning.send("!addwarning " + str(message.author.id) + " Broke Rule [9] by pinging Graysun")
                await message.author.timeout(datetime.timedelta(hours=1), "Broke Rule [9] by pinging Graysun")

    if message.content.startswith('!checkperms '):
        checked_role, hasPerm = checkPermissions(message.author, checkperms_roles, "checkperms")
        if hasPerm == False:
            await message.add_reaction('❌')
            await message.delete(delay=5)
            checkperms_error0 = await message.reply("**You don't have permissions to do that!**")
            await checkperms_error0.delete(delay=5)

        if hasPerm == True:
            role = message.content[12:]
            perms = getPermissions(role)
            if perms == False:
                await message.add_reaction('❌')
                await message.delete(delay=5)
                checkperms_error1 = await message.reply("**Role not found. Make sure it is the correct role id or role name.**")
                await checkperms_error1.delete(delay=5)
            else:
                await message.add_reaction('✅')
                await message.delete(delay=5)
                await message.channel.send(embed=makeEmbeddedCheckperms(perms))

                


    if message.content.startswith('!checkroles ') and message.channel.id == 1121034776497897482: #moderation
        desired_roles = ["Templar", "Defender"]  # List of desired role names
        
        # Get the user's member object
        user_id = message.content[12:]
        guild = message.guild
        if isInt(user_id) == True:
            # Find the entries in the audit log for adding the desired roles to the user
            matching_entries = []
            async for entry in guild.audit_logs(limit=None):
                if entry.action == discord.AuditLogAction.member_role_update and entry.target.id == int(user_id):
                    for role in entry.after.roles:
                        if role.name in desired_roles:
                            matching_entries.append(entry)
                            break
            if matching_entries: #and isInt(user_id) == True:
                user_id = int(user_id)
                await message.add_reaction('✅')
                await message.delete(delay=5)
                await message.channel.send(embed=makeEmbeddedCheckrolesMessage(matching_entries, user_id, desired_roles))
            if matching_entries == []:
                checkroles_reply = await message.reply("**User does not have any special roles**")  
                await message.add_reaction('❌')
                await message.delete(delay=5)
                await checkroles_reply.delete(delay=8)
        else:
            checkroles_reply = await message.reply("**User-ID must be a number!**")  
            await message.add_reaction('❌')
            await message.delete(delay=5)
            await checkroles_reply.delete(delay=8)

    if message.content.startswith('!getwarnings ') and message.channel.id == 1119244292335079588: #channel_id
        checked_role, hasPerm = checkPermissions(message.author, checkperms_roles, "checkwarning")
        if hasPerm == True:
            message_content = message.content[13:]
            getWarningsData = getWarnings(int(message_content))
            await message.add_reaction('✅')
            await message.channel.send(embed=makeEmbeddedWarnings(getWarningsData))
            await message.delete(delay=5)
        else:
            await message.add_reaction('❌')
            await message.delete(delay=5)
            perms_error = await message.reply("**You don't have permissions to do that!**")
            await perms_error.delete(delay=5)
    
    if message.content.startswith('!addwarning ') and message.channel.id == 1119244292335079588:
        checked_role, hasPerm = checkPermissions(message.author, checkperms_roles, "addwarning")
        if hasPerm == True:
            image_url = None
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    image_url = attachment.url
                    filename = download_image(image_url)
                    guild = message.guild.id
                    archiveChannel = client.get_channel(1131194745998282823)
                    with open("img/" + filename, "rb") as pic:
                        proof = await archiveChannel.send(file=discord.File(pic))
                    break
                for pictures in proof.attachments:
                    image_url = pictures.url

            message_content1 = message.content[12:]
            message_content1 = message_content1.split(" ", 1)
            newWarning = addNewWarning(int(message_content1[0]), message_content1[1], message.author.id, image_url)
            await message.add_reaction('✅')
            userToDM = await client.fetch_user(int(message_content1[0]))
            await userToDM.send(embed=makeEmbeddedAddedWarningDM(newWarning))
            getWarningsData = getWarnings(int(message_content1[0]))
            await message.channel.send(embed=makeEmbeddedWarnings(getWarningsData))
            await message.delete(delay=3)
        else:
            await message.add_reaction('❌')
            await message.delete(delay=5)
            perms_error = await message.reply("**You don't have permissions to do that!**")
            await perms_error.delete(delay=5)

    if message.content.startswith('!removewarning ') and message.channel.id == 1119244292335079588:
        checked_role, hasPerm = checkPermissions(message.author, checkperms_roles, "removewarning")
        if hasPerm == True:
            message_content2 = message.content[15:]
            message_content2 = message_content2.split(" ", 1)
            removedWarning = removeWarning(int(message_content2[0]), int(message_content2[1]))
            if removedWarning == False:
                await message.add_reaction('❌')
                bot_message1 = await message.channel.send("No warnings with ID " + str(message_content2[1]) + " were found")
                await bot_message1.delete(delay=5)
                await message.delete(delay=5)
            else: 
                userToDM1 = await client.fetch_user(int(message_content2[0]))
                await userToDM1.send(embed=makeEmbeddedRemovedWarningDM(removedWarning, message.author.id))
                await message.delete(delay=5)
                getWarningsData = getWarnings(int(message_content2[0]))
                await message.add_reaction('✅')
                await message.channel.send(embed=makeEmbeddedWarnings(getWarningsData))
        else:
            await message.add_reaction('❌')
            await message.delete(delay=5)
            perms_error = await message.reply("**You don't have permissions to do that!**")
            await perms_error.delete(delay=5)

    #changelog message
    if message.content.startswith('What changed:') and message.channel.id == credential["channel_changelog"]:
        guild_id = str(message.guild.id)
        await message.add_reaction('✅')
        #getting userinfos
        messageByUser, avatarOfUser, author = getUserInfo(message)

        #saving and splitting messageByUser
        c_what, c_where, c_why, c_note = editChangelogMessage(messageByUser)

        #pushing the changes with a bot message and deleting the original message
        message_id, channel_id = await pushChanges(change_what=c_what, change_where=c_where, change_why=c_why, change_note=c_note, authorAvatar=avatarOfUser, author=author)
        await message.delete(delay=3)

        #Archive message
        await message.author.send(embed=makeEmbeddedArchiveDM(messageByUser, guild_id, channel_id, message_id))
    
    #creating event
    if message.content.startswith('Event name:') and message.channel.id == credential["channel_create_event"]:
        messageToEvent, avatarOfEventAuthor, eventAuthor = getUserInfo(message)
        message_user  = message

        event_name, event_description, event_time, event_max_participants, event_picture = preparingEventMessage(messageToEvent)
        if event_max_participants == False:
            message_bot3 = await message.reply("**Error:** Max participants can only be **one** number.\nPlease delete your message and repost it.")
            await message_bot3.delete(delay=10)
            await message.add_reaction('❌')
        else:
            event_data = makeNewEventInJson(event_name, event_description, event_time, event_max_participants, event_picture, eventAuthor)
            message_id, channel_id = await pushEventPreview(event_data, avatarOfEventAuthor, eventAuthor)
            channel = client.get_channel(int(channel_id))
            message_bot = await channel.fetch_message(message_id)
            savetoEventsJson(event_data["event_id"],"preview_message_id", message_id)
            savetoEventsJson(event_data["event_id"],"creator_message_id", message.id)


            await message_bot.add_reaction('✅')

            #wait for user's reaction
            def check(reaction, user):
                return user == message.author and reaction.message.id == message_bot.id and str(reaction.emoji) == '✅'

            try:
                reaction, user = await client.wait_for("reaction_add", timeout=600, check=check)
            except asyncio.TimeoutError:
                await message_bot.delete()
                await message_user.delete()
                #messageData = getMessageInfo(message_bot.id)
                #deleteEventEntry(messageData["event_id"])
            else:
                await message_user.add_reaction('✅')
                await message_user.delete(delay=3)
                await message_bot.delete(delay=3)

                category_id = 1117510149318389892
                guild = client.get_guild(message.guild.id)
                category = guild.get_channel(category_id)
                channel_name = event_data["event_name"]
                role_justicar = guild.get_role(1110118558064705556)
                eventCreator = guild.get_member(message.author.id)

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    eventCreator: discord.PermissionOverwrite(read_messages=True, manage_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }

                for role in guild.roles:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=False)

                eventTextChannel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
                await eventTextChannel.set_permissions(role_justicar, read_messages=True)
                
                newEventChannelID = eventTextChannel.id
                savetoEventsJson(event_data["event_id"], "newEventChannelID", int(newEventChannelID))
                message_public_id, channel_public_id = await pushEventToEvents(newEventChannelID, event_data, message.author.avatar, message.author)
                channel = client.get_channel(int(channel_public_id))
                message_bot = await channel.fetch_message(message_public_id)

                savetoEventsJson(event_data["event_id"], "published_message_id", int(message_public_id))
                messageData = getMessageInfo(int(message_public_id))
                print(messageData)
                addPlayerEntries(messageData["event_max_participants"], messageData["event_id"])

                await message_bot.add_reaction('📝')
                await message_bot.add_reaction('❌')
                await message_bot.add_reaction('🗑️')
                await message.author.send(embed=makeEmbeddedEventCreatedDM(messageToEvent, message.guild.id, int(channel_public_id), message_bot.id, newEventChannelID))
    
    if message.content.startswith('!changetime '):
        event_id = getEventIDByEventChannelID(message.channel.id)
        data = getMessageInfobyEventID(event_id)
        if message.author.id == int(data["creator"]):
            eventAuthor = message.author
            avatarOfEventAuthor = message.author.avatar
            message_command_time = message.content[12:]
            savetoEventsJson(event_id, "event_time", str(message_command_time))
            data = getMessageInfobyEventID(event_id)
            await editEventPublic(data, avatarOfEventAuthor, eventAuthor)
            await message.add_reaction('✅')
            await message.delete(delay=3)

    if message.content.startswith('!changedesc '):
        event_id = getEventIDByEventChannelID(message.channel.id)
        data = getMessageInfobyEventID(event_id)
        if message.author.id == int(data["creator"]):
            eventAuthor = message.author
            avatarOfEventAuthor = message.author.avatar
            message_command_desc = message.content[12:]
            savetoEventsJson(event_id, "event_description", str(message_command_desc))
            data = getMessageInfobyEventID(event_id)
            await editEventPublic(data, avatarOfEventAuthor, eventAuthor)
            await message.add_reaction('✅')
            await message.delete(delay=3)


@client.event
async def on_message_delete(message):
    if message.author.id != client.user.id and message.channel.id != 1116144039394279454 and message.channel.id != 1110315336730935327 and message.channel.id != 1119244292335079588 and message.channel.id != 1115217957660917800 and message.channel.id != 1119244292335079588 and message.channel.id != 1123314997901152299 and message.channel.id != 1121034776497897482 and message.channel.id != 1117510275516600491 and message.channel.id != 1117530368124395741 and message.channel.id != 1127648406219804804 and message.channel.id != 1131194745998282823: #ignore justichat and holding-room and defenderchat and changelog and warnings-cases and moderationvotes and moderation and create-event and events
        guild = message.guild
        hasImages = False
        deleter = message.author.name
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            if entry.target.id == message.author.id:
                deleter = entry.user.name
                break

        if client.user.name != deleter:
            message_logs_channel = client.get_channel(1127648406219804804) #message-logs
            if (len(message.embeds) > 0) or (len(message.attachments) > 0):
                hasImages = True

            await message_logs_channel.send(embed=makeEmbeddedDeletedMessage(message.author.avatar, message.author, message.author.id, deleter, message.content, hasImages, message.channel.id))
"""            if hasImages == True:
                for embed in message.embeds:
                    if embed.image:
                        try:
                            picture_url = embed.image.proxy_url
                            parsed_url = urlparse(picture_url)
                            file_extension = os.path.splitext(parsed_url.path)[1]
                            filename = "picture" + file_extension
                            urllib.request.urlretrieve(picture_url, filename)
                            await message_logs_channel.send(file=filename)
                        except HTTPError as e:
                                await message_logs_channel.send("Couldn't get image from url.")

            # Check if the deleted message has attachments
            if hasImages == True:
                for attachment in message.attachments:
                    try:
                        picture_url = attachment.proxy_url
                        parsed_url = urlparse(picture_url)
                        file_extension = os.path.splitext(parsed_url.path)[1]
                        filename = "picture" + file_extension
                        urllib.request.urlretrieve(picture_url, filename)
                        await message_logs_channel.send(file=filename)
                        print(picture_url)
                    except HTTPError as e:
                            await message_logs_channel.send("Couldn't get attachments from url.")
"""
@client.event
async def on_raw_message_edit(payload):
    channelID = payload.channel_id
    messageID = payload.message_id
    data = payload.data
    channel = client.get_channel(channelID)
    editedEventMessage = await channel.fetch_message(messageID)
    eventAuthor =  editedEventMessage.author
    if eventAuthor.id != 1116029608555450459 and channelID == credential["channel_create_event"] and editedEventMessage.content.startswith("Event name:"):
        editedEventContent = data['content']
        avatarOfEventAuthor = eventAuthor.avatar
        event_name, event_description, event_time, event_max_participants, event_picture = preparingEventMessage(editedEventContent)
        edited_data = editExistingData(event_name, event_description, event_time, event_max_participants, event_picture, messageID)
        await editEventPreview(edited_data, avatarOfEventAuthor, eventAuthor)

@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(payload.guild_id)

    if payload.user_id == client.user.id:
        return
    
    if payload.user_id != client.user.id and str(payload.emoji) == '📝' and payload.channel_id == credential["channel_events"]:
        addResponse = addPlayerToEvent(payload.user_id, payload.message_id)
        eventReactor = await client.fetch_user(payload.user_id)
        if addResponse != False:
            addResponse = addResponse[1]
            eventAuthor = await client.fetch_user(addResponse["creator"])
            authorAvatar = eventAuthor.avatar
            await editEventPublic(addResponse, authorAvatar, eventAuthor)
            channelToAddto = guild.get_channel(addResponse["newEventChannelID"])
            signedupUser = guild.get_member(payload.user_id)
            await channelToAddto.set_permissions(signedupUser, read_messages=True)
            await eventReactor.send(embed=makeEmbeddedEventJoinedDM(payload.guild_id, payload.channel_id, payload.message_id, addResponse["newEventChannelID"]))
        
        if addResponse == False:
            await eventReactor.send(embed=makeEmbeddedEventFullDM())

    if payload.user_id != client.user.id and str(payload.emoji) == "❌" and payload.channel_id == credential["channel_events"]:
        messageData = getMessageInfo(payload.message_id)
        removeResponse = removePlayerFromEvent(payload.user_id, messageData["published_message_id"])
        if removeResponse != False:
            removeResponse = removeResponse[1]
            eventAuthor = await client.fetch_user(int(messageData["creator"]))
            authorAvatar = eventAuthor.avatar
            await editEventPublic(removeResponse, authorAvatar, eventAuthor)
            channelToRemoveFrom = guild.get_channel(removeResponse["newEventChannelID"])
            signedOutUser = guild.get_member(payload.user_id)
            role_justicar = guild.get_role(1110118558064705556)
            if role_justicar in signedOutUser.roles:
                print("Ignoring Justicar")
            else:
                await channelToRemoveFrom.set_permissions(signedOutUser, read_messages=False)
            eventReactor = await client.fetch_user(payload.user_id)
            await eventReactor.send(embed=makeEmbeddedEventLeftDM(payload.guild_id, payload.channel_id, payload.message_id))

    if payload.user_id != client.user.id and str(payload.emoji) == "🗑️" and payload.channel_id == credential["channel_events"]:
        messageData = getMessageInfo(payload.message_id)
        if int(messageData["creator"]) == payload.user_id:
            channelToDelete = client.get_channel(messageData["newEventChannelID"])
            await channelToDelete.delete()
            eventChannel = client.get_channel(payload.channel_id)
            messageToDelete = await eventChannel.fetch_message(int(messageData["published_message_id"]))
            await messageToDelete.delete()
            #deleteEventEntry(messageData["event_id"])


@client.event
async def on_member_remove(member):
    guild = member.guild

    if guild.id == 1104622211068854363:
        ban_entry = None

        async for entry in guild.audit_logs(limit=1):
            if entry.target == member and entry.action in [discord.AuditLogAction.kick, discord.AuditLogAction.ban]:
                ban_entry = entry
                break

        if ban_entry is not None:
            if ban_entry.action == discord.AuditLogAction.kick:
                await sendAutomodPlayerAction(member, action="kick", actionBy=entry.user_id, reason=entry.reason)
            elif ban_entry.action == discord.AuditLogAction.ban:
                await sendAutomodPlayerAction(member, action="ban", actionBy=entry.user_id, reason=entry.reason)
        else:
            await sendAutomodPlayerAction(member=member, action="leave")

def fetch_audit_logs(guild, limit):
    auditlog_entries = guild.audit_logs(limit=limit)
    return auditlog_entries

@client.event
async def on_member_update(before, after):
    guild = before.guild
    async for entry in fetch_audit_logs(guild, 1):
        if entry.target == before and entry.user != entry.target:
            if isinstance(entry.target, discord.Member) and hasattr(entry.target, 'timed_out_until') and entry.target.timed_out_until != None and before.roles == after.roles:
                # Check if the target member has the 'timed_out_until' attribute
                discordUnixTime = datestrToDateUnix(str(entry.target.timed_out_until))
                await sendAutomodPlayerAction(member=entry.target, action="timeout", actionBy=entry.user_id, reason=str(entry.reason), unix_timedoutUntil=discordUnixTime)
                await before.send(embed=makeEmbeddedTimeOutDM(str(entry.reason)))
            break  # Exit the loop after processing the entry
        
        #send DM on receiving templar-role
    desired_role = discord.utils.get(after.roles, name="Templar")
    if desired_role and desired_role not in before.roles and desired_role in after.roles:
        # User received the desired role, send them a DM
        user = after  # The user who received the role
        await after.send(embed=makeEmbeddedTemplarDM())
    defender_role = discord.utils.get(after.roles, name="Defender")
    if defender_role and defender_role not in before.roles and defender_role in after.roles:
        # User received the desired role, send them a DM
        user = after  # The user who received the role
        await after.send(embed=makeEmbeddedDefenderDM())

    


@app.route("/webhooks/3f76b73c-0fea-45cc-b8dd-94185834c5e9/", methods=["POST"])
def respond():
    
    court_data = request.json  # Get the event data from the webhook payload
    court_channel = client.get_channel(1111723093019328574)
    coro = court_channel.send(embed=makeEmbeddedCourtFiling(court_data))
    asyncio.run_coroutine_threadsafe(coro, client.loop)
    #loop.run_until_complete(court_channel.send(court_data["payload"]["results"][0]["description"]))
    return Response(status=200)

@app.route("/webhooks/3f76b73c-0fea-45cc-b8dd-123daww1ddw1f12e/", methods=["POST"])
def respond_update():
    
    domain_update = request.json  # Get the event data from the webhook payload
    court_channel = client.get_channel(1111723093019328574)
    coro = court_channel.send("**Domain has been updated:** \nhttps://who.is/whois/darkanddarker.com")
    asyncio.run_coroutine_threadsafe(coro, client.loop)
    #loop.run_until_complete(court_channel.send(court_data["payload"]["results"][0]["description"]))
    return Response(status=200)



# Flask route for serving index.html
@app.route("/index/")
def index():
    return render_template("index.html")

# Configure SSL context


# Start the Flask app
def run_flask():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain("/etc/letsencrypt/live/hiddenace.net/fullchain.pem", "/etc/letsencrypt/live/hiddenace.net/privkey.pem")
    app.run(host="0.0.0.0", port=443, ssl_context=context)


if __name__ == "__main__":
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Run the Discord bot in the main thread
    client.run(credential["token"])

    # Wait for the Flask thread to finish
    flask_thread.join()
    

