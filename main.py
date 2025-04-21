token = "Your Token"



import discord
from discord.ext import commands
from discord.ext import commands, tasks
from discord import app_commands
import json
import random
import asyncio
import datetime
import os

  






# تنظیمات ربات
intents = discord.Intents.all()
intents.guilds = True
intents.messages = True
intents.members = True
intents.message_content = True  # For message content access
intents.reactions = True  # For message reactions
#intents.guild_emojis_and_stickers = True  # Correct attribute for emoji and stickers
#intents.guild_roles = True  # For role updates
intents.voice_states = True  # For voice state updates

welcome_channels = {}  # Dictionary to store guild-specific welcome channels










bot = commands.Bot(command_prefix="!", intents=intents)

# ذخیره اطلاعات در فایل JSON
def save_data_to_json(data, file_name="data.json"):
    try:
        with open(file_name, "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}

    existing_data.update(data)
    with open(file_name, "w") as f:
        json.dump(existing_data, f, indent=4)

# دستور setgiveaway
@bot.tree.command(name="setgiveaway", description="Set up a giveaway")
@app_commands.describe(
    title="Title of the giveaway",
    description="Description of the giveaway",
    duration="Duration of the giveaway (e.g., 12h, 7d, 1m)"
)
async def setgiveaway(interaction: discord.Interaction, title: str, description: str, duration: str):
    # بررسی اینکه کاربر مدیر سرور باشد
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You must be an administrator to use this command.", ephemeral=True
        )
        return

    # بررسی و تبدیل مدت زمان
    try:
        duration_value = int(duration[:-1])
        duration_unit = duration[-1].lower()
        if duration_unit == "h":
            duration_seconds = duration_value * 3600
        elif duration_unit == "d":
            duration_seconds = duration_value * 86400
        elif duration_unit == "m":
            if duration_value > 1:
                await interaction.response.send_message("❌ Maximum duration is 1 month.", ephemeral=True)
                return
            duration_seconds = duration_value * 30 * 86400
        else:
            await interaction.response.send_message("❌ Invalid duration unit. Use `h`, `d`, or `m`.", ephemeral=True)
            return

        if duration_seconds > 30 * 86400:
            await interaction.response.send_message("❌ Maximum duration is 1 month.", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("❌ Invalid duration value. Please enter a valid number and unit.", ephemeral=True)
        return

    # ساخت embed گیوی
    embed = discord.Embed(
        title=title,
        description=f"**Description:** {description}\n**Duration:** {duration}",
        color=discord.Color.gold()
    )
    embed.set_author(name="🎉 New Giveaway 🎉")
    embed.set_footer(text="Click the button below to join the giveaway!")

    # دکمه جویین گیوی
    class JoinButton(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.entries = []

        @discord.ui.button(label="Join Giveaway", style=discord.ButtonStyle.green)
        async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id not in self.entries:
                self.entries.append(interaction.user.id)
                await interaction.response.send_message("✅ You have joined the giveaway!", ephemeral=True)
            else:
                await interaction.response.send_message("⚠️ You have already joined the giveaway.", ephemeral=True)

        async def pick_winner(self):
            if not self.entries:
                return None
            return random.choice(self.entries)

    view = JoinButton()

    # ارسال پیام گیوی
    await interaction.response.send_message(embed=embed, view=view)

    # صبر برای پایان گیوی
    await asyncio.sleep(duration_seconds)

    # انتخاب برنده
    winner_id = await view.pick_winner()
    if winner_id:
        winner = await bot.fetch_user(winner_id)
        await interaction.followup.send(f"🎉 The winner of the giveaway is: {winner.mention}!")
    else:
        await interaction.followup.send("❌ No participants, no winner.")

    # دکمه جویین گیوی
    class JoinButton(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.entries = []

        @discord.ui.button(label="Join Giveaway", style=discord.ButtonStyle.green)
        async def join_giveaway(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user.id not in self.entries:
                self.entries.append(interaction.user.id)
                await interaction.response.send_message("✅ You have joined the giveaway!", ephemeral=True)
            else:
                await interaction.response.send_message("⚠️ You have already joined the giveaway.", ephemeral=True)

        async def pick_winner(self):
            if not self.entries:
                return None
            return random.choice(self.entries)

    view = JoinButton()

    # ارسال پیام گیوی
    await interaction.response.send_message(embed=embed, view=view)

    # صبر برای پایان گیوی
    await asyncio.sleep(duration_seconds)

    # انتخاب برنده
    winner_id = await view.pick_winner()
    if winner_id:
        winner = await bot.fetch_user(winner_id)
        await interaction.followup.send(f"🎉 The winner of the giveaway is: {winner.mention}!")
    else:
        await interaction.followup.send("❌ No participants, no winner.")


# ذخیره اطلاعات در فایل JSON
def save_data_to_json(data, file_name="data.json"):
    try:
        with open(file_name, "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}

    existing_data.update(data)
    with open(file_name, "w") as f:
        json.dump(existing_data, f, indent=4)

# ذخیره تنظیمات لاگ در فایل JSON
def save_log_channel(guild_id, channel_id):
    try:
        with open("log_channels.json", "r") as f:
            log_channels = json.load(f)
    except FileNotFoundError:
        log_channels = {}

    log_channels[str(guild_id)] = channel_id

    with open("log_channels.json", "w") as f:
        json.dump(log_channels, f, indent=4)

# گرفتن چنل لاگ از فایل JSON
def get_log_channel(guild_id):
    try:
        with open("log_channels.json", "r") as f:
            log_channels = json.load(f)
        return log_channels.get(str(guild_id))
    except FileNotFoundError:
        return None

# ارسال لاگ‌ها به چنل مشخص
async def send_log_message(guild, message):
    channel_id = get_log_channel(guild.id)
    if channel_id:
        channel = guild.get_channel(int(channel_id))
        if channel:
            await channel.send(embed=message)

# کامند /serverlog برای تنظیم چنل لاگ
@bot.tree.command(name="serverlog", description="Set a channel for server logs")
@app_commands.describe(channel="Select a channel to store server logs")
async def serverlog(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must be an administrator to use this command.", ephemeral=True)
        return

    save_log_channel(interaction.guild.id, channel.id)
    await interaction.response.send_message(f"✅ Logs will now be sent to {channel.mention}.", ephemeral=True)

# Detailed log for deleted messages
@bot.event
async def on_message_delete(message):
    embed = discord.Embed(
        title="🗑️ Message Deleted",
        description=f"**User:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** {message.content or '[No Content]'}",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"Message ID: {message.id} • Author ID: {message.author.id}")
    await send_log_message(message.guild, embed)

# Detailed log for edited messages
@bot.event
async def on_message_edit(before, after):
    if before.content == after.content:
        return
    embed = discord.Embed(
        title="✏️ Message Edited",
        description=f"**User:** {before.author.mention}\n**Channel:** {before.channel.mention}",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.add_field(name="Before", value=before.content or "[No Content]", inline=False)
    embed.add_field(name="After", value=after.content or "[No Content]", inline=False)
    embed.set_footer(text=f"Message ID: {before.id} • Author ID: {before.author.id}")
    await send_log_message(before.guild, embed)

# Detailed log for member joining
@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title="👋 Member Joined",
        description=f"**User:** {member.mention}\n**Account Created:** {member.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        color=discord.Color.green(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"User ID: {member.id}")
    await send_log_message(member.guild, embed)

# Detailed log for member leaving
@bot.event
async def on_member_remove(member):
    embed = discord.Embed(
        title="🚪 Member Left",
        description=f"**User:** {member.mention}",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"User ID: {member.id}")
    await send_log_message(member.guild, embed)

# Detailed log for role updates (added/removed)
@bot.event
async def on_member_update(before, after):
    role_changes = []
    for role in before.roles:
        if role not in after.roles:
            role_changes.append(f"❌ Removed: {role.name}")
    for role in after.roles:
        if role not in before.roles:
            role_changes.append(f"✅ Added: {role.name}")
    
    if role_changes:
        embed = discord.Embed(
            title="🔄 Role Updated",
            description=f"**User:** {before.mention}\n" + "\n".join(role_changes),
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=f"User ID: {before.id}")
        await send_log_message(before.guild, embed)

# Detailed log for nickname changes
@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        embed = discord.Embed(
            title="🔄 Nickname Updated",
            description=f"**User:** {before.mention}\n**Old Nickname:** {before.nick or '[None]'}\n**New Nickname:** {after.nick or '[None]'}",
            color=discord.Color.purple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=f"User ID: {before.id}")
        await send_log_message(before.guild, embed)

# Detailed log for message reactions added or removed
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return  # Ignore bot reactions
    embed = discord.Embed(
        title="👍 Reaction Added",
        description=f"**User:** {user.mention}\n**Message:** {reaction.message.content[:100]}...\n**Emoji:** {reaction.emoji}",
        color=discord.Color.green(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"Message ID: {reaction.message.id}")
    await send_log_message(reaction.message.guild, embed)

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return  # Ignore bot reactions
    embed = discord.Embed(
        title="👎 Reaction Removed",
        description=f"**User:** {user.mention}\n**Message:** {reaction.message.content[:100]}...\n**Emoji:** {reaction.emoji}",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"Message ID: {reaction.message.id}")
    await send_log_message(reaction.message.guild, embed)

# Detailed log for emoji creation
@bot.event
async def on_guild_emojis_update(guild, before, after):
    added_emojis = [emoji for emoji in after if emoji not in before]
    removed_emojis = [emoji for emoji in before if emoji not in after]
    
    changes = []
    if added_emojis:
        changes.append(f"✅ Added Emojis: {', '.join([emoji.name for emoji in added_emojis])}")
    if removed_emojis:
        changes.append(f"❌ Removed Emojis: {', '.join([emoji.name for emoji in removed_emojis])}")

    if changes:
        embed = discord.Embed(
            title="🧑‍🎨 Emoji Update",
            description="\n".join(changes),
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await send_log_message(guild, embed)

# Detailed log for role creation, deletion, and updates
@bot.event
async def on_guild_role_create(role):
    embed = discord.Embed(
        title="🆕 Role Created",
        description=f"**Role:** {role.name}\n**Permissions:** {', '.join([perm[0] for perm in role.permissions if perm[1]])}",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"Role ID: {role.id}")
    await send_log_message(role.guild, embed)

@bot.event
async def on_guild_role_delete(role):
    embed = discord.Embed(
        title="❌ Role Deleted",
        description=f"**Role:** {role.name}",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"Role ID: {role.id}")
    await send_log_message(role.guild, embed)

@bot.event
async def on_guild_role_update(before, after):
    changes = []
    if before.name != after.name:
        changes.append(f"📝 Name changed from **{before.name}** to **{after.name}**")
    if before.permissions != after.permissions:
        changes.append(f"🔒 Permissions updated.")
    
    if changes:
        embed = discord.Embed(
            title="🔄 Role Updated",
            description=f"**Role:** {before.name}\n" + "\n".join(changes),
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=f"Role ID: {before.id}")
        await send_log_message(before.guild, embed)

# Detailed log for bans and unbans
@bot.event
async def on_member_ban(guild, user):
    embed = discord.Embed(
        title="🔨 Member Banned",
        description=f"**User:** {user.mention}\n**Reason:** {user.reason or '[No reason specified]'}",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"User ID: {user.id}")
    await send_log_message(guild, embed)

@bot.event
async def on_member_unban(guild, user):
    embed = discord.Embed(
        title="✅ Member Unbanned",
        description=f"**User:** {user.mention}",
        color=discord.Color.green(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text=f"User ID: {user.id}")
    await send_log_message(guild, embed)

# Detailed log for voice state updates
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        embed = discord.Embed(
            title="🎧 Voice State Updated",
            description=f"**User:** {member.mention}\n**From:** {before.channel.mention if before.channel else '[None]'}\n**To:** {after.channel.mention if after.channel else '[None]'}",
            color=discord.Color.purple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=f"User ID: {member.id}")
        await send_log_message(member.guild, embed)




# کامند /slowmode برای تنظیم حالت کند
@bot.tree.command(name="slowmode", description="Set the slowmode for a channel in seconds")
@app_commands.describe(
    seconds="Number of seconds to set for slowmode (0 to disable slowmode)"
)
async def slowmode(interaction: discord.Interaction, seconds: int):
    # بررسی اینکه کاربر مدیر سرور باشد
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            "❌ You need the 'Manage Channels' permission to use this command.",
            ephemeral=True
        )
        return

    # بررسی مقدار وارد شده برای زمان
    if seconds < 0:
        await interaction.response.send_message(
            "❌ Slowmode seconds cannot be negative.", ephemeral=True
        )
        return

    # تنظیم حالت کند برای کانال
    try:
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(
            f"✅ Slowmode for {interaction.channel.mention} set to {seconds} seconds."
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred while setting slowmode: {str(e)}", ephemeral=True
        )


# ذخیره اخطارهای کاربران
user_warnings = {}

# کامند /warn برای اخطار دادن به کاربر
@bot.tree.command(name="warn", description="Warn a user. If the user gets 3 warnings, they will be kicked.")
@app_commands.describe(
    member="The member to warn",
    reason="The reason for the warning"
)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    # بررسی دسترسی مدیر برای اخطار دادن
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message(
            "❌ You need the 'Kick Members' permission to use this command.",
            ephemeral=True
        )
        return

    # بررسی اینکه کاربر خود ربات را انتخاب نکرده باشد
    if member == interaction.guild.me:
        await interaction.response.send_message(
            "❌ You cannot warn the bot!", ephemeral=True
        )
        return

    # اضافه کردن اخطار به لیست اخطارها
    if member.id not in user_warnings:
        user_warnings[member.id] = []

    user_warnings[member.id].append(reason)
    warn_count = len(user_warnings[member.id])

    # ارسال پیام اخطار
    await interaction.response.send_message(
        f"⚠️ {member.mention} has been warned by {interaction.user.mention}.\nReason: {reason}\nThis is warning #{warn_count}."
    )

    # بررسی تعداد اخطارها و کیک کردن کاربر در صورت رسیدن به ۳
    if warn_count >= 3:
        try:
            await member.kick(reason="Reached 3 warnings.")
            del user_warnings[member.id]  # حذف اخطارها پس از کیک
            await interaction.followup.send(
                f"❌ {member.mention} has been kicked from the server for receiving 3 warnings."
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to kick {member.mention}: {str(e)}"
            )






# فرمان /kick
@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(member="The member to kick", reason="Reason for the kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    # بررسی دسترسی مدیر برای کیک کردن
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message(
            "❌ You need the 'Kick Members' permission to use this command.",
            ephemeral=True
        )
        return

    # بررسی اینکه کاربر خود ربات را انتخاب نکرده باشد
    if member == interaction.guild.me:
        await interaction.response.send_message(
            "❌ You cannot kick the bot!", ephemeral=True
        )
        return

    # انجام عمل کیک
    try:
        await member.kick(reason=reason)
        # ارسال پیام لاگ برای کیک
        embed = discord.Embed(
            title="👢 User Kicked",
            description=f"**User:** {member.mention}\n**Reason:** {reason}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=f"User ID: {member.id}")
        await send_log_message(interaction.guild, embed)

        await interaction.response.send_message(f"✅ {member.mention} has been kicked. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to kick {member.mention}: {str(e)}")

# فرمان /ban
@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(member="The member to ban", reason="Reason for the ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    # بررسی دسترسی مدیر برای بن کردن
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message(
            "❌ You need the 'Ban Members' permission to use this command.",
            ephemeral=True
        )
        return

    # بررسی اینکه کاربر خود ربات را انتخاب نکرده باشد
    if member == interaction.guild.me:
        await interaction.response.send_message(
            "❌ You cannot ban the bot!", ephemeral=True
        )
        return

    # انجام عمل بن
    try:
        await member.ban(reason=reason)
        # ارسال پیام لاگ برای بن
        embed = discord.Embed(
            title="🚫 User Banned",
            description=f"**User:** {member.mention}\n**Reason:** {reason}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=f"User ID: {member.id}")
        await send_log_message(interaction.guild, embed)

        await interaction.response.send_message(f"✅ {member.mention} has been banned. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to ban {member.mention}: {str(e)}")

# کامند /mute برای بی‌صدا کردن کاربر
@bot.tree.command(name="mute", description="Mute a user for a specified duration in seconds.")
@app_commands.describe(
    member="The member to mute",
    duration="Mute duration in seconds",
    reason="Reason for muting the user"
)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str):
    # بررسی دسترسی مدیر برای بی‌صدا کردن
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "❌ You need the 'Manage Roles' permission to use this command.",
            ephemeral=True
        )
        return

    # بررسی اینکه کاربر خود ربات را انتخاب نکرده باشد
    if member == interaction.guild.me:
        await interaction.response.send_message(
            "❌ You cannot mute the bot!", ephemeral=True
        )
        return

    # پیدا کردن یا ساختن رول "Muted"
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not mute_role:
        # ساختن رول Muted در صورت عدم وجود
        try:
            mute_role = await interaction.guild.create_role(
                name="Muted",
                permissions=discord.Permissions(send_messages=False, speak=False),
                reason="Role created for muting users."
            )
            # اعمال محدودیت برای همه کانال‌ها
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to create 'Muted' role: {str(e)}",
                ephemeral=True
            )
            return

    # اضافه کردن رول Muted به کاربر
    try:
        await member.add_roles(mute_role, reason=reason)
        await interaction.response.send_message(
            f"🔇 {member.mention} has been muted for {duration} seconds.\nReason: {reason}"
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed to mute {member.mention}: {str(e)}",
            ephemeral=True
        )
        return

    # زمان‌بندی برای برداشتن رول Muted
    await asyncio.sleep(duration)
    try:
        await member.remove_roles(mute_role, reason="Mute duration expired.")
        await interaction.followup.send(f"🔊 {member.mention} has been unmuted.")
    except Exception as e:
        await interaction.followup.send(
            f"❌ Failed to unmute {member.mention}: {str(e)}"
        )

# کامند /unmute برای برداشتن حالت بی‌صدا
@bot.tree.command(name="unmute", description="Unmute a user.")
@app_commands.describe(member="The member to unmute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    # بررسی دسترسی مدیر برای برداشتن بی‌صدا
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "❌ You need the 'Manage Roles' permission to use this command.",
            ephemeral=True
        )
        return

    # پیدا کردن رول "Muted"
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not mute_role:
        await interaction.response.send_message(
            "❌ The 'Muted' role does not exist in this server.",
            ephemeral=True
        )
        return

    # برداشتن رول Muted از کاربر
    try:
        await member.remove_roles(mute_role, reason="Unmute by an admin.")
        await interaction.response.send_message(
            f"🔊 {member.mention} has been unmuted."
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed to unmute {member.mention}: {str(e)}",
            ephemeral=True
        )

# کامند /removewarn برای حذف هشدار از کاربر
@bot.tree.command(name="removewarn", description="Remove a warning from a user.")
@app_commands.describe(member="The member to remove warning from", warn_count="Number of warning to remove")
async def removewarn(interaction: discord.Interaction, member: discord.Member, warn_count: int):
    # بررسی دسترسی مدیر برای حذف هشدار
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "❌ You need the 'Manage Server' permission to use this command.",
            ephemeral=True
        )
        return

    # ذخیره هشدارها در یک دیکشنری (می‌توانید از دیتابیس برای ذخیره استفاده کنید)
    if not hasattr(bot, 'warnings'):
        bot.warnings = {}

    # اگر کاربر هشدار دارد
    if member.id in bot.warnings and bot.warnings[member.id] >= warn_count:
        bot.warnings[member.id] -= warn_count
        await interaction.response.send_message(
            f"⚠️ {warn_count} warning(s) removed from {member.mention}. They now have {bot.warnings[member.id]} warning(s)."
        )
    else:
        await interaction.response.send_message(
            f"❌ {member.mention} does not have enough warnings to remove."
        )





@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error event: {event}")
    print(args)
    print(kwargs)




@bot.tree.command(name="setwelcome", description="Set the welcome channel for the server")
@app_commands.describe(channel="The channel where welcome messages will be sent")
async def set_welcome(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
        return

    welcome_channels[interaction.guild.id] = channel.id  # Save the welcome channel
    await interaction.response.send_message(
        f"✅ Welcome channel set to {channel.mention}", ephemeral=True
    )


@bot.event
async def on_member_join(member: discord.Member):
    # Get the welcome channel for the guild
    channel_id = welcome_channels.get(member.guild.id)
    if channel_id is None:
        return  # No welcome channel set

    channel = member.guild.get_channel(channel_id)
    if channel is None:
        return  # Channel doesn't exist

    # Create the embed message
    embed = discord.Embed(
        title="🎉 Welcome to the Server!",
        description=f"Hello {member.mention}, we're thrilled to have you here! 🎊\n\n"
                    "Make sure to check out the rules and have a fantastic time!",
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text="We're happy to see you!", icon_url=bot.user.avatar.url)

    # Send the embed to the welcome channel
    await channel.send(embed=embed)







# لیست دستورات
commands_list = {
    "setactivity": "Set a channel to monitor for inactivity",
    "slowmode": "Set the slowmode for a channel in seconds",
    "setwelcome": "Set the welcome channel for the server",
    "removewarn": "Remove a warning from a user.",
    "unmute": "Unmute a user.",
    "mute": "Mute a user for a specified duration in seconds.",
    "ban": "Ban a user from the server",
    "kick": "Kick a user from the server",
    "warn": "Warn a user. If the user gets 3 warnings, they will be kicked.",
    "serverlog": "Set a channel for server logs",
    "setgiveaway": "Set up a giveaway",
    "leaderboard": "leaderboard top money user's",
    "addbalance" : "admin only addbalance",
    "userinfo" : "user normal info",
    "serverinfo" : "this server info",
    "botinfo" : "this bot info",
    "give" : "give bots money for someone else"



    
}





# دستور /help
@bot.tree.command(name="help", description="help's about discord bot command's")
async def help_command(interaction: discord.Interaction):
    # ساخت Embed
    embed = discord.Embed(
        title="List Of Bot Command's",
        description="Here is List of command's",
        color=discord.Color.gold()
    )
    
    for command, description in commands_list.items():
        embed.add_field(name=f"/{command}", value=description, inline=False)
    
    embed.set_footer(text="Join Support server for more")
    
    # ارسال Embed
    await interaction.response.send_message(embed=embed)







# Store activity monitoring data
activity_monitor = {}

# Slash command to monitor channel activity
@bot.tree.command(name="setactivity", description="Set a channel to monitor for inactivity")
async def setactivity(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role, text: str = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    
    # Set default message if no text is provided
    activity_monitor[channel.id] = {
        "role": role.id,
        "text": text or "Let's keep this channel active! Share your thoughts or ask a question! 😊",
        "last_active": datetime.datetime.utcnow(),  # Store current UTC time
        "last_notified": None,  # Track last notification time
    }
    await interaction.response.send_message(f"Activity monitor set for {channel.mention} with role {role.mention}.", ephemeral=True)

# Event listener to track channel activity
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    # Update last active time for monitored channels
    if message.channel.id in activity_monitor:
        activity_monitor[message.channel.id]["last_active"] = datetime.datetime.utcnow()
    
    await bot.process_commands(message)

# Background task to check for inactivity
@tasks.loop(minutes=5)
async def check_inactivity():
    now = datetime.datetime.utcnow()
    for channel_id, monitor in activity_monitor.items():
        last_active = monitor["last_active"]
        last_notified = monitor["last_notified"]
        role_id = monitor["role"]
        text = monitor["text"]

        # Check if the channel is inactive for more than 1 hour
        if now - last_active > datetime.timedelta(hours=1):
            # If last notification was sent more than 12 hours ago, send the message
            if not last_notified or (now - last_notified > datetime.timedelta(hours=12)):
                channel = bot.get_channel(channel_id)
                role = discord.utils.get(channel.guild.roles, id=role_id)

                # Ensure channel and role are valid before sending the message
                if channel and role:
                    try:
                        await channel.send(f"{role.mention} {text}")
                        monitor["last_notified"] = now  # Update the last notified time
                    except discord.DiscordException as e:
                        print(f"Error sending message to {channel_id}: {e}")
                else:
                    print(f"Error: Could not find channel or role for channel {channel_id}")
        else:
            print(f"Channel {channel_id} is active. Skipping message.")


# دیتابیس موقتی برای سیستم اقتصادی
user_balances = {}

# شناسه کاربری که اجازه استفاده از /addbalance را دارد
ADMIN_USER_ID = 123456789012345678  # شناسه کاربر ادمین را اینجا قرار دهید




# تعریف Cogs
class AllCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # کامند اقتصادی: اضافه کردن موجودی
    @app_commands.command(name="addbalance", description="admin only addbalance")
    async def addbalance(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if interaction.user.id != ADMIN_USER_ID:
            await interaction.response.send_message("you are not bot admin.", ephemeral=True)
            return
        if amount <= 0:
            await interaction.response.send_message("money can not be 0.", ephemeral=True)
            return
        user_balances[member.id] = user_balances.get(member.id, 0) + amount
        await interaction.response.send_message(f"amount {amount} transformed to {member.mention}. you new balance is : {user_balances[member.id]} coin's")

    # کامند اقتصادی: نمایش موجودی حساب
    @app_commands.command(name="balance", description="user bot money balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        balance = user_balances.get(member.id, 0)
        await interaction.response.send_message(f"this user {member.mention}: {balance} coin's")



# اضافه کردن Cogs
async def setup(bot: commands.Bot):
    await bot.add_cog(AllCommands(bot))

# اجرای بات
async def main():
    async with bot:
        await setup(bot)
        await bot.start(token)




# رویداد آماده به کار شدن بات
@bot.event
async def on_ready():
    # سینک کردن کامندها
    await bot.tree.sync()
    print("bot command's are synced")

    # تنظیم وضعیت بات به Playing و Idle
    activity = discord.Activity(type=discord.ActivityType.playing, name="/help")
    await bot.change_presence(status=discord.Status.idle, activity=activity)

    print(f"bot is online : {bot.user}")

# تعریف Cogs
class AllCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # کامند اطلاعاتی: نمایش اطلاعات کاربر
    @app_commands.command(name="userinfo", description="user normal info")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(title=f"user info : {member.name}", color=discord.Color.blue())
        embed.add_field(name="username", value=member.name, inline=False)
        embed.add_field(name="id", value=member.id, inline=False)
        embed.add_field(name="join time", value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed)

    # کامند اطلاعاتی: نمایش اطلاعات سرور
    @app_commands.command(name="serverinfo", description="this server info")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"server info : {guild.name}", color=discord.Color.green())
        embed.add_field(name="server name", value=guild.name, inline=False)
        embed.add_field(name="server member's", value=guild.member_count, inline=False)
        embed.add_field(name="server role's", value=len(guild.roles), inline=False)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        await interaction.response.send_message(embed=embed)

    # کامند اطلاعاتی: نمایش اطلاعات بات
    @app_commands.command(name="botinfo", description="this bot info")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="bot info", color=discord.Color.gold())
        embed.add_field(name="bot name", value=self.bot.user.name, inline=False)
        embed.add_field(name="developer", value="HMC#0771", inline=False)
        embed.add_field(name="bot ping", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    # کامند اقتصادی: انتقال پول
    @app_commands.command(name="give", description="give bots money for someone else")
    async def give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("money need to be more then 0.", ephemeral=True)
            return
        giver_balance = user_balances.get(interaction.user.id, 0)
        if giver_balance < amount:
            await interaction.response.send_message("you don't have balance.", ephemeral=True)
            return
        user_balances[interaction.user.id] = giver_balance - amount
        user_balances[member.id] = user_balances.get(member.id, 0) + amount
        await interaction.response.send_message(f"this amount of money {amount} transformed to {member.mention} !")

    # کامند اقتصادی: نمایش جدول برترین کاربران
    @app_commands.command(name="leaderboard", description="leaderboard top money user's")
    async def leaderboard(self, interaction: discord.Interaction):
        sorted_balances = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="Top Money User's", color=discord.Color.purple())
        for rank, (user_id, balance) in enumerate(sorted_balances[:10], start=1):
            user = self.bot.get_user(user_id)
            embed.add_field(name=f"{rank}. {user.name if user else 'anonymous user'}", value=f"{balance} coin", inline=False)
        await interaction.response.send_message(embed=embed)




import asyncio
asyncio.run(main())