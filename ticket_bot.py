import os
import threading
from discord.ext import commands
import discord
from flask import Flask

# --- RENDER УНТАХААС ХАМГААЛАХ ВЭБ СЕРВЕР ---
app = Flask("")


@app.route("/")
def home():
  return "Bot is alive!"


def run_web():
  app.run(host="0.0.0.0", port=8080)


# Вэб серверийг тусдаа урсгалаар (thread) асаана
threading.Thread(target=run_web).start()


# --- DISCORD BOT ТОХИРГОО ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Панель байрлах сувгийн ID (Өөрийн сувгийн ID-гаар солино уу)
PANEL_CHANNEL_ID = 123456789012345678


class TicketView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.select(
      placeholder="Сонголт хийх...",
      options=[
          discord.SelectOption(
              label="Support Ticket", description="Тусламж авах"
          ),
          discord.SelectOption(label="Clan Join", description="Кландах орох"),
      ],
  )
  async def select_callback(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    await interaction.response.send_message(
        f"Таны сонголт: {select.values[0]}", ephemeral=True
    )


@bot.event
async def on_ready():
  print(f"Bot {bot.user.name} амжилттай холбогдлоо!")


@bot.command()
@commands.has_permissions(administrator=True)
async def sendpanel(ctx):
  channel = bot.get_channel(PANEL_CHANNEL_ID)
  if channel:
    view = TicketView()
    embed = discord.Embed(
        title="ELITE Support Center",
        description="Доорх цэснээс сонголт хийж билет нээнэ үү.",
        color=discord.Color.gold(),
    )
    await channel.send(embed=embed, view=view)
    await ctx.send("Панель амжилттай байршлаа!", ephemeral=True)
  else:
    await ctx.send("Суваг олдсонгүй! ID-гаа шалгана уу.", ephemeral=True)


# --- БОТЫГ АСААХ ХЭСЭГ ---
if __name__ == "__main__":
  TOKEN = os.getenv("DISCORD_TOKEN")
  bot.run(TOKEN)