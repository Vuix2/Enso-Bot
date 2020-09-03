# Ensō~Chan - A Multi Purpose Discord Bot That Has Everything Your Server Needs!
# Copyright (C) 2020  Hamothy

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import datetime
import os
import random

import asyncpg as asyncpg
import discord
from decouple import config
from discord import Colour, Embed
from discord.ext import commands, tasks
from discord.ext.commands import when_mentioned_or

from bot.libs.cache import MyCoolCache

counter = 0

# Get DB information from .env
password = config('DB_PASS')
host = config('DB_HOST')
user = config('DB_USER')
port = config('DB_PORT')
db = config('DB_NAME')

# Getting the bot token from environment variables
API_TOKEN = config('DISCORD_TOKEN')


class Bot(commands.Bot):
    def __init__(self, **options):

        async def get_prefix(bot, message):
            """Allow the commands to be used with mentioning the bot"""

            if message.guild is None:
                return "."
            return when_mentioned_or(self.get_prefix_for_guild(message.guild.id))(bot, message)

        super().__init__(command_prefix=get_prefix, case_insensitive=True, **options)
        self.db = None
        self.description = 'All current available commands within Ensō~Chan',
        self.owner_id = 154840866496839680  # Your unique User ID
        self.admin_colour = Colour(0x62167a)  # Admin Embed Colour
        self.version = "0.8.2"  # Version number of Ensō~Chan
        self.remove_command("help")  # Remove default help command

        # Instance variables for Enso
        self.hammyMention = '<@154840866496839680>'
        self.hammy_role_ID = "<@&715412394968350756>"
        self.blank_space = "\u200b"
        self.enso_embedmod_colours = Colour(0x62167a)
        self.enso_ensochancommands_Mention = "<#721449922838134876>"
        self.enso_ensochancommands_ID = 721449922838134876
        self.enso_verification_ID = 728034083678060594
        self.enso_selfroles_ID = 722347423913213992
        self.enso_guild_ID = 663651584399507476
        self.enso_newpeople_ID = 669771571337887765
        self.enso_modmail_ID = 728083016290926623
        self.enso_feedback_ID = 739807803438268427

        # Cross/Tick Emojis
        self.cross = "<:xMark:746834944629932032>"
        self.tick = "<:greenTick:746834932936212570>"

        # Instance variables for cache
        self.enso_cache = {}
        self.modmail_cache = {}
        self.starboard_cache = {}
        self.starboard_messages_cache = {}
        self.member_cache = MyCoolCache(100)

        async def create_connection():
            """Setting up connection using asyncpg"""

            self.db = await asyncpg.create_pool(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=db,
                loop=self.loop)

        async def startup_cache_log():
            """Store the guilds/modmail systems in cache from the database on startup"""

            # Setup up pool connection
            pool = self.db
            async with pool.acquire() as conn:

                # Query to get all records of guilds that the bot is in
                try:
                    results = await conn.fetch("""SELECT * FROM guilds""")

                    # Store the guilds information within cache
                    for row in results:
                        self.enso_cache[row["guild_id"]] = {"prefix": row["prefix"],
                                                            "modlogs": row["modlogs"],
                                                            "roles_persist": row["roles_persist"]}
                # Catch errors
                except asyncpg.PostgresError as e:
                    print("PostGres Error: Guild Records Could Not Be Loaded Into Cache On Startup", e)

                # Query to get all records of modmails within guilds
                try:
                    results = await conn.fetch("""SELECT * FROM moderatormail""")

                    # Store the information for modmail within cache
                    for row in results:
                        self.modmail_cache[row["guild_id"]] = {"modmail_channel_id": row["modmail_channel_id"],
                                                               "message_id": row["message_id"],
                                                               "modmail_logging_channel_id":
                                                                   row["modmail_logging_channel_id"]}
                # Catch errors
                except asyncpg.PostgresError as e:
                    print("PostGres Error: Modmail Records Could Not Be Loaded Into Cache On Startup", e)

                # Query to get all records of starboards within guilds
                try:
                    results = await conn.fetch("SELECT * FROM starboard")

                    # Store the information for starboard within cache
                    for row in results:
                        self.starboard_cache[row["guild_id"]] = {"channel_id": row["channel_id"],
                                                                 "min_stars": row["min_stars"]}

                # Catch errors
                except asyncpg.PostgresError as e:
                    print("PostGres Error: Starboard Records Could Not Be Loaded Into Cache On Startup", e)

                # Query to get all records of starboard messages within guilds
                try:
                    results = await conn.fetch("SELECT * FROM starboard_messages")

                    for row in results:
                        self.starboard_messages_cache[(row["root_message_id"], row["guild_id"])] = {
                            "star_message_id": row["star_message_id"],
                            "stars": row["stars"]}

                # Catch errors
                except asyncpg.PostgresError as e:
                    print("PostGres Error: Starboard Records Could Not Be Loaded Into Cache On Startup", e)

                # Release connection back to pool
                await pool.release(conn)

        # Establish Database Connection
        self.loop.run_until_complete(create_connection())
        # Load Information Into Cache
        self.loop.run_until_complete(startup_cache_log())

        @tasks.loop(minutes=2, reconnect=True)
        async def change_status():
            """Creating custom statuses as background task"""

            global counter
            # Waiting for the bot to ready
            await self.wait_until_ready()

            # Define array of statuses
            looping_statuses = [
                discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{len(self.users)} Weebs | {self.version}"),
                discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"Hamothy | Real Life | {self.version}"),
                discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"Hamothy Program | {self.version}"),
                discord.Game(name=f".help | {self.version}")
            ]

            # Check if the counter is at the end of the array
            if counter == (len(looping_statuses) - 1):
                # Reset the loop
                counter = 0
            else:
                # Increase the counter
                counter += 1

            # Display the next status in the loop
            await self.change_presence(activity=looping_statuses[counter])

        # Start the background task(s)
        change_status.start()

    # --------------------------------------------!Cache Section!-------------------------------------------------------

    def store_cache(self, guild_id, prefix, modlogs, roles_persist):
        """Storing guild information within cache"""

        self.enso_cache[guild_id] = {"prefix": prefix,
                                     "modlogs": modlogs,
                                     "roles_persist": roles_persist}

    def del_cache(self, guild_id):
        """Deleting the entry of the guild within the cache"""

        del self.enso_cache[guild_id]

    async def check_cache(self, member_id, guild_id):
        """Checks if member is in the member cache"""

        # Return key-value pair if member is already in the cache
        if (member_id, guild_id) in self.member_cache.cache:
            return self.member_cache.cache[member_id, guild_id]

        else:
            # Setup pool connection
            pool = self.db
            async with pool.acquire() as conn:

                # Get the author's/members row from the Members Table
                try:
                    select_query = """SELECT * FROM members WHERE member_id = $1 and guild_id = $2"""
                    result = await conn.fetchrow(select_query, member_id, guild_id)

                # Catch errors
                except asyncpg.PostgresError as e:
                    print(f"PostGres Error: Member {member_id} From Guild {guild_id}"
                          "Record Could Not Be Retrieved When Checking Cache", e)

                # Store it in cache
                else:
                    dict_items = {"married": result["married"],
                                  "married_date": result["married_date"],
                                  "muted_roles": result["muted_roles"],
                                  "roles": result["roles"]}
                    self.member_cache.store_cache((member_id, guild_id), dict_items)

                    return self.member_cache.cache[member_id, guild_id]

    # --------------------------------------------!End Cache Section!---------------------------------------------------

    # --------------------------------------------!Starboard Section!---------------------------------------------------

    def cache_store_starboard(self, guild_id, channel_id, min_stars):
        """Storing starboard within cache"""

        self.starboard_cache[guild_id] = {"channel_id": channel_id,
                                          "min_stars": min_stars}

    def get_starboard_channel(self, guild_id):
        """Returning the starboard channel of the guild"""

        starboard = self.starboard_cache.get(guild_id)
        return starboard.get("channel_id") if starboard else None

    def get_starboard_min_stars(self, guild_id):
        """Returning the starboard minimum stars of the guild"""

        starboard = self.starboard_cache.get(guild_id)
        return starboard.get("min_stars") if starboard else None

    def update_starboard_channel(self, guild_id, channel_id):
        """Update the starboard channel"""

        self.starboard_cache[guild_id]["channel_id"] = channel_id

    def update_starboard_min_stars(self, guild_id, min_stars):
        """Update the starboard minimum stars"""

        self.starboard_cache[guild_id]["min_stars"] = min_stars

    def delete_starboard(self, guild_id):
        """Deleting the starboard of the guild"""

        del self.starboard_cache[guild_id]

    def delete_starboard_messages(self, guild_id):

        # Array to store keys to be removed
        keys_to_remove = []

        # For every starboard message in cache
        for (root_msg_id, guild_id) in self.starboard_messages_cache:
            # if the guild_id passed in is equal to the guild_id within the cache
            if guild_id == guild_id:
                # Store key within array
                keys_to_remove.append((root_msg_id, guild_id))

        # Iterate through the array and then pop the keys from cache
        for key in keys_to_remove:
            self.starboard_messages_cache.pop(key)

    def cache_store_starboard_message(self, root_message_id, guild_id, star_message_id):
        """Store the starboard messages within cache"""

        self.starboard_messages_cache[root_message_id, guild_id] = {"star_message_id": star_message_id,
                                                                    "stars": 1}

    def update_starboard_message_stars(self, root_message_id, guild_id, star_message_id):
        """Store the starboard messages within cache"""

        self.starboard_messages_cache[root_message_id, guild_id] = {"star_message_id": star_message_id,
                                                                    "stars": 1}

    def update_starboard_message(self, root_message_id, guild_id, reactions):
        """Update the stored starboard message"""

        self.starboard_messages_cache[root_message_id, guild_id]["stars"] = reactions

    async def check_starboard_messages_cache(self, root_message_id, guild_id):
        """Check if the message is already in the cache"""

        # Return value if message is already in the cache
        if (root_message_id, guild_id) in self.starboard_messages_cache:
            return self.starboard_messages_cache[root_message_id, guild_id]["star_message_id"], \
                   self.starboard_messages_cache[root_message_id, guild_id]["stars"]

        else:
            # Setup pool connection
            pool = self.db
            async with pool.acquire() as conn:

                # Get the starboard row from the starboard_messages table
                try:
                    select_query = """SELECT * FROM starboard_messages WHERE root_message_id = $1 AND guild_id = $2"""
                    result = await conn.fetchrow(select_query, root_message_id, guild_id)

                # Catch errors
                except asyncpg.PostgresError as e:
                    print(e)

                # Store it in cache
                else:
                    if result:
                        self.starboard_messages_cache[root_message_id, guild_id] = {
                            "star_message_id": result["star_message_id"],
                            "stars": result["stars"]}

                        return self.starboard_messages_cache[root_message_id, guild_id]["star_message_id"], \
                               self.starboard_messages_cache[root_message_id, guild_id]["stars"]
                    else:
                        return None, 0

    # --------------------------------------------!EndStarboard Section!-------------------------------------------------

    # --------------------------------------------!Modmail Section!-----------------------------------------------------

    def cache_store_modmail(self, guild_id, modmail_channel, message, modmail_logging_channel):
        """Storing all modmail channels within cache"""

        self.modmail_cache[guild_id] = {"modmail_channel_id": modmail_channel,
                                        "message_id": message,
                                        "modmail_logging_channel_id": modmail_logging_channel}

    def get_modmail(self, guild_id):
        """Returning the modmail system of the guild"""

        return self.modmail_cache.get(guild_id)

    def update_modmail(self, guild_id, channel_id):
        """Update the modmail channel"""

        self.modmail_cache[guild_id]["modmail_logging_channel_id"] = channel_id

    def delete_modmail(self, guild_id):
        """Deleting the modmail system of the guild within the Cache"""

        del self.modmail_cache[guild_id]

    # --------------------------------------------!EndModmail Section!--------------------------------------------------

    # --------------------------------------------!RolePersist Section!-------------------------------------------------

    def get_roles_persist(self, guild_id):
        """Returning rolespersist value of the guild"""

        role_persist = self.enso_cache.get(guild_id)
        return role_persist.get("roles_persist") if role_persist else None

    async def update_role_persist(self, guild_id, value):
        """Update the rolepersist value of the guild (Enabled or Disabled)"""

        # Setup up pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Query for updating rolepersist values For guilds
            try:
                update_query = """UPDATE guilds SET roles_persist = $1 WHERE guild_id = $2"""
                await conn.execute(update_query, value, guild_id)

            # Catch error
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: RolePersist For Guild {guild_id} Could Not Be Updated", e)

            # Store in cache
            else:
                self.enso_cache[guild_id]["roles_persist"] = value

    # --------------------------------------------!End RolePersist Section!---------------------------------------------

    # --------------------------------------------!ModLogs Section!-----------------------------------------------------

    async def storage_modlog_for_guild(self, ctx, channel_id, setup):
        """Updating the modlog within the dict and database"""

        # Setup up pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Query to update modlogs within the database
            try:
                update_query = """UPDATE guilds SET modlogs = $1 WHERE guild_id = $2"""
                rowcount = await conn.execute(update_query, channel_id, ctx.guild.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print("PostGres Error: Modlogs Value In Guilds Table Could Not Be Updated/Setup", e)

            # Let the user know that modlogs channel has been updated/setup
            else:
                if setup:
                    print(rowcount, f"Modlog channel for guild {ctx.guild} has been Setup")
                    await self.generate_embed(ctx, desc=f"**Modlogs Channel** successfully setup in <#{channel_id}>" +
                                                        f"\nPlease refer to **{ctx.prefix}help** for any information")
                else:
                    print(rowcount, f"Modlog channel for guild {ctx.guild} has been Updated")
                    await self.generate_embed(ctx,
                                              desc=f"Modlog Channel for **{ctx.guild}** has been updated to <#{channel_id}>")

                # Store in cache
                self.enso_cache[ctx.guild.id]["modlogs"] = channel_id

    def remove_modlog_channel(self, guild_id):
        """Remove the value of modlog for the guild specified"""

        self.enso_cache[guild_id]["modlogs"] = None

    def get_modlog_for_guild(self, guild_id):
        """Get the modlog channel of the guild that the user is in"""

        modlogs = self.enso_cache.get(guild_id)
        return modlogs.get("modlogs") if modlogs else None

    # --------------------------------------------!End ModLogs Section!-------------------------------------------------

    # --------------------------------------------!Prefixes Section!----------------------------------------------------

    async def storage_prefix_for_guild(self, ctx, prefix):
        """Updating the prefix within the dict and database when the method is called"""

        # Setup up pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Query to update the existing prefix within the database
            try:
                update_query = """UPDATE guilds SET prefix = $1 WHERE guild_id = $2"""
                rowcount = await conn.execute(update_query, prefix, ctx.guild.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: Prefix For Guild {ctx.guild.id} Could Not Be Updated", e)

            # Let the user know that the guild prefix has been updated
            else:
                print(rowcount, f"Guild prefix has been updated for guild {ctx.guild}")
                await self.generate_embed(ctx, desc=f"Guild prefix has been updated to **{prefix}**")

                # Store in cache
                self.enso_cache[ctx.guild.id]["prefix"] = prefix

    def get_prefix_for_guild(self, guild_id):
        """Get the prefix of the guild that the user is in"""

        prefix = self.enso_cache[guild_id]["prefix"]
        if prefix:
            return prefix
        return "."

    # --------------------------------------------!End Prefixes Section!------------------------------------------------

    # --------------------------------------------!Roles/Colour/Embed Section!------------------------------------------

    @staticmethod
    def random_colour():
        """Generate a random hex colour"""

        return Colour(random.randint(0, 0xFFFFFF))

    async def generate_embed(self, ctx, desc):
        """Generate embed"""

        embed = Embed(description=desc,
                      colour=self.admin_colour)

        await ctx.send(embed=embed)

    async def store_roles(self, target, ctx, member):
        """Storing user roles within database"""

        role_ids = ", ".join([str(r.id) for r in target.roles])

        # Setup up pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Query to store existing roles of the member within the database
            try:
                update_query = """UPDATE members SET muted_roles = $1 WHERE guild_id = $2 AND member_id = $3"""
                rowcount = await conn.execute(update_query, role_ids, ctx.guild.id, member.id)
                result = await self.check_cache(member.id, member.guild.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: Roles Could Not Be Stored For Member {member.id} in Guild {member.guild.id}", e)

            # Print success
            # Update cache
            else:
                result["muted_roles"] = role_ids
                print(rowcount, f"Roles Added For User {member} in {ctx.guild}")

    async def clear_roles(self, member):
        """Clear the roles when the user has been unmuted"""

        # Setup up pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Query to clear the existing role of the member from the database
            try:
                update = """UPDATE members SET muted_roles = NULL WHERE guild_id = $1 AND member_id = $2"""
                rowcount = await conn.execute(update, member.guild.id, member.id)
                result = await self.check_cache(member.id, member.guild.id)

            # Catch error
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: Roles Could Not Be Cleared for Member {member.id} in Guild {member.guild.id}",
                      e)

            # Print success
            # Update cache
            else:
                result["muted_roles"] = None
                print(rowcount, f"Roles Cleared For User {member} in {member.guild.name}")

    # --------------------------------------------!End Roles/Colour/Embed Section!--------------------------------------

    # --------------------------------------------!Events Section!------------------------------------------------------

    async def on_message(self, message):
        """Make sure bot messages are not tracked"""

        # Ignoring messages that start with 2 ..
        if message.content.startswith("..") or message.author.bot:
            return

        # Processing the message
        await self.process_commands(message)

    async def on_ready(self):
        """Display startup message"""

        print("UvU Senpaiii I'm ready\n")

    async def on_guild_join(self, guild):
        """
        Store users in a database
        Store prefix/modlogs in the cache
        """

        # Store every single record into an array
        records = [(member.id, None, None, guild.id, None, None, None, 0) for member in guild.members]

        # Setup up pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Insert the guild information into guilds table
            try:
                insert = """INSERT INTO guilds VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id) DO NOTHING"""
                rowcount = await conn.execute(insert, guild.id, ".", None, 0)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: Guild {guild.id} Could Not Be Inserted Into Guilds Table", e)

            # Print success
            else:
                print(rowcount, f"Record(s) inserted successfully into {guild}")
                self.store_cache(guild.id, modlogs=None, prefix=".", roles_persist=0)

            # Query to insert all the member details to members table
            try:
                rowcount = await conn.copy_records_to_table("members", records=records)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: Members Could Not Be Inserted Into Members Table For Guild {guild.id}", e)

            # Store in cache
            else:
                print(rowcount, f"Record(s) inserted successfully into Members from {guild}")

            # Release connection back to pool
            await pool.release(conn)

    async def on_guild_remove(self, guild):
        """
        Remove users in the database for the guild
        Remove the modlogs/guild from the cache
        """

        # Setup pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Delete the guild information as the bot leaves the server
            try:
                delete = """DELETE FROM guilds WHERE guild_id = $1"""
                rowcount = await conn.execute(delete, guild.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: On Guild Remove Event Record Was Not Deleted For {guild.id}", e)

            # Delete the key - value pair for the guild
            else:
                print(rowcount, f"Record deleted successfully from Guild {guild}")
                self.del_cache(guild.id)

            # Delete all records of members from that guild
            try:
                delete = """DELETE FROM members WHERE guild_id = $1"""
                rowcount = await conn.execute(delete, guild.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: All Members Could Not Be Deleted From {guild.id}", e)

            # Print success
            else:
                print(rowcount, f"Record(s) deleted successfully from Members from {guild}")
                # Remove any/all members stored in cache from that guild
                self.member_cache.remove_many(guild.id)

            # Delete any starboard information upon leaving the guild
            try:
                delete = """DELETE FROM starboard WHERE guild_id = $1"""
                rowcount = await conn.execute(delete, guild.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(
                    f"PostGres Error: On Guild Remove Event Starboard/Starboard Messages Were Not Deleted For {guild.id}",
                    e)

            # Delete all information about the starboard and any messages stored
            else:
                print(rowcount, f"Starboard deleted successfully from Guild {guild}")
                if self.get_starboard_channel(guild.id):
                    self.delete_starboard(guild.id)
                    self.delete_starboard_messages(guild.id)

            # Release connection back to pool
            await pool.release(conn)

    async def on_member_join(self, member):
        """
        Bot event to insert new members into the database
        In the Enso guild, it will send an introduction embed
        """

        # Ignoring bots
        if member.bot: return

        # Get the guild and role persist value of the guild
        guild = member.guild
        role_persist = self.get_roles_persist(guild.id)

        # Setup pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Define the insert statement that will insert the user's information
            # On conflict, set the left values to null
            try:

                insert = """INSERT INTO members (guild_id, member_id) VALUES ($1, $2)
                ON CONFLICT (guild_id, member_id) DO UPDATE SET left_at = NULL, has_left = 0"""
                rowcount = await conn.execute(insert, member.guild.id, member.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(
                    f"PostGres Error: {member} | {member.id} was not be able to be added to {member.guild} | {member.guild.id}",
                    e)

            # Print success
            else:
                print(rowcount, f"{member} Joined {member.guild}, Record Inserted Into Members")
                print(rowcount, f"Roles Cleared For {member} in {member.guild}")

            # Get the roles of the user from the database
            try:
                select_query = """SELECT * FROM members WHERE guild_id = $1 AND member_id = $2"""

                user_joined = await conn.fetchrow(select_query, member.guild.id, member.id)
                role_ids = user_joined["roles"]

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: {member} | {member.id} Record Not Found", e)

            # Give roles back to the user if role persist is enabled
            else:
                if role_persist == 1:
                    # Get Enso Chan
                    bot = guild.get_member(self.user.id)
                    # Set flag for what value role_ids is
                    flag = role_ids

                    # Check permissions of Enso
                    if bot.guild_permissions.manage_roles and flag:
                        # Get all the roles of the user before they were muted from the database
                        roles = [member.guild.get_role(int(id_)) for id_ in role_ids.split(", ") if len(id_)]

                        # Give the member their roles back
                        await member.edit(roles=roles)
                        print(f"{member} Had Their Roles Given Back In {member.guild}")

                    # Don't give roles if user has no roles to be given
                    elif bot.guild_permissions.manage_roles and not flag:
                        print(f"Member {member} | {member.id} Had No Roles To Be Given")

                    # No permissions to give roles in the server
                    else:
                        print(
                            f"Insufficient Permissions to Add Roles to {member} | {member.id} in {member.guild} | {member.guild.id}")

            # Reset the roles entry for the database
            try:
                update_query = """UPDATE members SET roles = NULL WHERE guild_id = $1 AND member_id = $2"""
                rowcount = await conn.execute(update_query, member.guild.id, member.id)

            # Catch errors
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: Clearing Member {member.id} Roles in Guild {member.guild.id}", e)

            # Print success
            # Update cache
            else:
                print(rowcount, f"Roles Cleared For {member} in {member.guild}")

            # Release connection back to pool
            await pool.release(conn)

        # Make sure the guild is Enso and send welcoming embed to the server
        if guild.id == self.enso_guild_ID:
            new_people = guild.get_channel(self.enso_newpeople_ID)

            server_icon = guild.icon_url
            welcome_gif = "https://cdn.discordapp.com/attachments/669808733337157662/730186321913446521/NewPeople.gif"

            embed = Embed(title="\n**Welcome To Ensō!**",
                          colour=self.admin_colour,
                          timestamp=datetime.datetime.utcnow())

            embed.set_thumbnail(url=server_icon)
            embed.set_image(url=welcome_gif)
            embed.add_field(
                name=self.blank_space,
                value=f"Hello {member.mention}! We hope you enjoy your stay in this server!",
                inline=False)
            embed.add_field(
                name=self.blank_space,
                value=f"Be sure to check out our <#669815048658747392> channel to read the rules and <#683490529862090814> channel to get caught up with any changes! ",
                inline=False)
            embed.add_field(
                name=self.blank_space,
                value=f"Last but not least, feel free to go into <#669775971297132556> to introduce yourself!",
                inline=False)

            # Send embed to #newpeople
            await new_people.send(embed=embed)

    async def on_member_remove(self, member):
        """Storing member roles within the database when the member leaves"""

        # Ignoring bots
        if member.bot: return

        # Get the datetime of when the user left the guild
        left_at = datetime.datetime.utcnow()

        # Store member roles within a string to insert into database
        role_ids = ", ".join([str(r.id) for r in member.roles if not r.managed])

        # Setup pool connection
        pool = self.db
        async with pool.acquire() as conn:

            # Store member roles within the database
            try:
                update = """UPDATE members SET roles = $1, left_at = $2, has_left = 1
                                  WHERE guild_id = $3 AND member_id = $4"""
                rowcount = await conn.execute(update, role_ids, left_at, member.guild.id, member.id)

            # Catch Error
            except asyncpg.PostgresError as e:
                print(f"PostGres Error: Roles Could Not Be Added To {member} When Leaving {member.guild.id}", e)

            # Print success
            else:
                print(rowcount, f"{member} Left {member.guild.name}, Roles stored into Members")

    async def on_guild_channel_delete(self, channel):
        """Deleting modlogs/modmail channel if it's deleted in the guild"""

        # Get the modlogs channel (channel or none)
        modlogs = self.get_modlog_for_guild(channel.guild.id)
        # Get the starboard (record or none)
        starboard = self.get_starboard_channel(channel.guild.id)

        # Get the modmail record - (normal and logging channels)
        modmail_record = self.get_modmail(channel.guild.id)
        modmail_channel = modmail_record.get("modmail_channel_id") if modmail_record else None
        modmail_logging_channel = modmail_record.get("modmail_logging_channel_id") if modmail_record else None

        # Get pool
        pool = self.db

        # Delete the modlogs system from the database when modlogs channel is deleted
        if channel.id == modlogs:
            # Setup pool connection
            async with pool.acquire() as conn:

                # Set channel to none
                try:
                    update = """UPDATE guilds SET modlogs = NULL WHERE guild_id = $1"""
                    await conn.execute(update, channel.guild.id)

                # Catch errors
                except asyncpg.PostgresError as e:
                    print(f"PostGres Error: Guild Modlogs Could Not Be Deleted For {channel.guild.id}", e)

                # Delete channel from cache
                else:
                    self.remove_modlog_channel(channel.guild.id)

        # Delete all of the starboard information when the channel is deleted from the guild
        if channel.id == starboard:
            # Setup pool connection
            async with pool.acquire() as conn:

                # Delete any starboard information upon leaving the guild
                try:
                    delete = """DELETE FROM starboard WHERE guild_id = $1"""
                    rowcount = await conn.execute(delete, channel.guild.id)

                # Catch errors
                except asyncpg.PostgresError as e:
                    print(
                        f"PostGres Error: On Guild Remove Event Starboard/Starboard Messages Were Not Deleted For {channel.guild.id}",
                        e)

                # Delete all information about the starboard and any messages stored
                else:
                    print(rowcount, f"Starboard deleted successfully from Guild {channel.guild}")
                    if self.get_starboard_channel(channel.guild.id):
                        self.delete_starboard(channel.guild.id)
                        self.delete_starboard_messages(channel.guild.id)

                # Release connection back to pool
                await pool.release(conn)

        # If modmail channels are deleted, delete the entire system
        if channel.id == modmail_channel or channel.id == modmail_logging_channel:
            # Set up pool connection
            async with pool.acquire() as conn:

                # Remove the moderatormail record from the database
                try:
                    delete = """DELETE FROM moderatormail WHERE guild_id = $1"""
                    await conn.execute(delete, channel.guild.id)

                # Catch errors
                except asyncpg.PostgresError as e:
                    print(f"PostGres Error: ModeratorMail Record Could Not Be Deleted for Guild {channel.guild.id}", e)

                # Delete from cache
                else:
                    self.delete_modmail(channel.guild.id)

    # --------------------------------------------!End Events Section!--------------------------------------------------

    def execute(self):
        """Load the cogs and then run the bot"""

        for file in os.listdir(f'.{os.sep}cogs'):
            if file.endswith('.py'):
                self.load_extension(f"cogs.{file[:-3]}")

        # Run the bot, allowing it to come online
        try:
            self.run(API_TOKEN)
        except discord.errors.LoginFailure as e:
            print(e, "Login unsuccessful.")
