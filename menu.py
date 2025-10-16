import nextcord
from nextcord.ext import commands
from nextcord import Interaction, TextInputStyle, ButtonStyle
from nextcord.ui import Button, View, Modal, TextInput
import subprocess
import json
import os

# ⚙️ ตั้งค่า
TOKEN = "MTMzOTkxNjM0MDAzODk5MTg3Mg.GuN372.cQJCWeQEK2BVUpH0SyvVBRgl9Br1N2Jal4Cwkw"
LOG_CHANNEL_ID = 1422222170267848807 # ช่อง Log ที่จะให้บอทส่งข้อความ
TOKENS_FILE = "tokens.json"

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())


# ======================= ฟังก์ชันบันทึก/โหลดโทเคน =======================
def save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    return {}


# ======================= Modal สำหรับตั้งค่า =======================
class BotOnModal(Modal):
    def __init__(self):
        super().__init__("ตั้งค่าบอทออนช่องเสียง")
        self.add_item(TextInput(label="โทเคนบอท", style=TextInputStyle.paragraph, required=True))
        self.add_item(TextInput(label="Server ID", style=TextInputStyle.short, required=True))
        self.add_item(TextInput(label="Channel ID", style=TextInputStyle.short, required=True))

    async def callback(self, interaction: nextcord.Interaction):
        token = self.children[0].value.strip()
        server_id = self.children[1].value.strip()
        channel_id = self.children[2].value.strip()

        try:
            tokens = load_tokens()
            tokens[str(interaction.user.id)] = {
                "token": token,
                "server_id": server_id,
                "channel_id": channel_id,
            }
            save_tokens(tokens)

            # 🔄 รัน voice.py เป็น Process แยก
            subprocess.Popen(["python", "voice.py", token, server_id, channel_id])

            await interaction.response.send_message("> ✅ บอทกำลังเข้า Voice Channel แล้ว", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ เกิดข้อผิดพลาด: {e}", ephemeral=True)

        # 🔔 ส่ง Log
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="📢 บอทออนช่องเสียง",
                description=f"👤 ผู้ใช้: {interaction.user.mention}\n"
                            f"🆔 Server: `{server_id}`\n"
                            f"🎧 Channel: `{channel_id}`",
                color=nextcord.Color.blue()
            )
            await log_channel.send(embed=log_embed)


# ======================= View ปุ่มหลัก =======================
class BotControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="ตั้งค่าออนช่อง", emoji="🎧", style=ButtonStyle.secondary)
    async def bot_on(self, button: Button, interaction: Interaction):
        modal = BotOnModal()
        await interaction.response.send_modal(modal)

    @nextcord.ui.button(label="ล้างโทเคน", emoji="🗑️", style=ButtonStyle.red)
    async def clear_token(self, button: Button, interaction: Interaction):
        tokens = load_tokens()
        user_data = tokens.pop(str(interaction.user.id), None)

        if user_data:
            save_tokens(tokens)
            await interaction.response.send_message("> 🧹 ล้างโทเคนเรียบร้อยแล้ว", ephemeral=True)
        else:
            await interaction.response.send_message("> ❌ ไม่พบโทเคนของคุณในระบบ", ephemeral=True)


# ======================= คำสั่ง !semenu =======================
@bot.command(name="semenu")
async def semenu(ctx):
    embed = nextcord.Embed(
        title="🎶 ระบบออนช่องเสียง",
        description="เลือกการดำเนินการจากปุ่มด้านล่าง",
        color=nextcord.Color.purple()
    )
    embed.set_footer(text="By Big_natanon")
    view = BotControlView()
    await ctx.send(embed=embed, view=view)


# ======================= เริ่มรันบอทหลัก =======================
bot.run(TOKEN)