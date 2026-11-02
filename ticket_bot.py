import os

import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Сервер дээрх тохиргооны ID-ууд
PANEL_CHANNEL_ID = 1566402878560665600     # Панель байрлах суваг
LOG_CHANNEL_ID = 1566358811223138375       # Лог явах суваг
TICKET_CATEGORY_ID = 1561358461206528091   # Билет орох Категори

# 1. Билет хаах товчлуурын Class
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        guild = interaction.guild
        member = interaction.user

        # Log суваг руу мэдээлэх
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🔒 Ticket Closed",
                description=f"**Хаасан хэрэглэгч:** {member.mention}\n**Сувгийн нэр:** {channel.name}",
                color=discord.Color.red()
            )
            await log_channel.send(embed=log_embed)

        await interaction.response.send_message("Билет хаагдаж байна...", ephemeral=True)
        await asyncio.sleep(2)
        await channel.delete()

# 2. Сонголт хийх цэс (Clan Oroh / Gomdol)
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Clan Oroh", description="Clan-д элсэх хүсэлт илгээх", emoji="🎮"),
            discord.SelectOption(label="Gomdol", description="Гомдол, санал хүсэлт гаргах", emoji="⚠️")
        ]
        super().__init__(placeholder="Сонголт хийх...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        category = guild.get_channel(TICKET_CATEGORY_ID)
        selected_value = self.values[0]

        # Сувагт хандах эрхүүд
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Шинэ суваг үүсгэх (CategoryChannel шалгалтыг зөвөөр хийв)
        channel_name = f"ticket-{selected_value.lower().replace(' ', '-')}-{member.name}"
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category if isinstance(category, discord.CategoryChannel) else None,
            overwrites=overwrites
        )

        # Билет доторх угтах мессеж болон хаах товч
        close_view = CloseTicketView()
        embed = discord.Embed(
            title=f"🎫 Ticket: {selected_value}",
            description=f"Сайн байна уу {member.mention}? Та **{selected_value}** төрлөөр билет нээлээ. Энд асуудлаа дэлгэрэнгүй бичиж үлдгэнэ үү.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=close_view)

        # Log суваг руу мэдээлэх
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🎟️ Ticket Opened",
                description=f"**Үүсгэсэн хэрэглэгч:** {member.mention}\n**Төрөл:** {selected_value}\n**Нээгдсэн суваг:** {ticket_channel.mention}",
                color=discord.Color.green()
            )
            await log_channel.send(embed=log_embed)

        await interaction.response.send_message(f"Таны билет амжилттай нээгдлээ: {ticket_channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} амжилттай холбогдлоо!')

# Панелийг зориулалтын суваг руу илгээх команд
@bot.command()
@commands.has_permissions(administrator=True)
async def sendpanel(ctx):
    channel = bot.get_channel(PANEL_CHANNEL_ID)
    if channel:
        view = TicketView()
        embed = discord.Embed(
            title="ELITE Support Center",
            description="Доорх цэснээс сонголт хийж билет нээнэ үү.",
            color=discord.Color.gold()
        )
        await channel.send(embed=embed, view=view)
        await ctx.send("Панель амжилттай байршлаа!", ephemeral=True)
    else:
        await ctx.send("Суваг олдсонгүй! ID-гаа шалгана уу.", ephemeral=True)

# Ботоо асаах Token (Энд өөрийн ботаа хуулж тавина)
TOKEN = os.getenv("DISCORD_TOKEN")