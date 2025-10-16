import nextcord
from nextcord.ext import commands
import sys

# ตั้งค่า Intents
intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True

# สร้างบอท
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

# ตรวจสอบอาร์กิวเมนต์ที่ส่งมา
if len(sys.argv) < 4:
    print("Usage: python voice.py <BOT_TOKEN> <SERVER_ID> <CHANNEL_ID>")
    sys.exit(1)

token = sys.argv[1]       # Token ของบอทย่อย
serverid = int(sys.argv[2])  # Server ID
channelid = int(sys.argv[3])  # Channel ID


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

    guild = bot.get_guild(serverid)
    if guild is None:
        print(f"❌ Server ID {serverid} not found!")
        return

    vc = nextcord.utils.get(guild.channels, id=channelid)
    if vc is None:
        print(f"❌ Channel ID {channelid} not found!")
        return

    try:
        await vc.guild.change_voice_state(channel=vc, self_mute=True, self_deaf=True)
        print(f"🎧 Joined voice channel: {vc.name}")
    except Exception as e:
        print(f"⚠️ Failed to join voice channel: {e}")


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.self_stream:
        print(f'📺 {member.name} started streaming in {after.channel.name}.')


bot.run(token)