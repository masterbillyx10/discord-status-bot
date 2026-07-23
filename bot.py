import os
import discord
from discord.ext import commands, tasks
import datetime

# ตั้งค่า Intent ของบอท
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------------------------------------
# ตั้งค่า ID ต่างๆ ที่น้องหวือกำหนด
# ---------------------------------------------------------
OWNER_ID = 1505161074885001331            # User ID น้องหวือ
ANNOUNCE_CHANNEL_ID = 1529818198516437053 # Channel ID ห้องแจ้งเตือนทั่วไป
CONTROL_CHANNEL_ID = 1529834562799276174  # Channel ID ห้องแอดมิน (Control)
PING_ROLE_ID = 1519165358911787038        # Role ID ยศที่ต้องการแท็ก

# ไอดี Emoji ขยับได้
EMOJI_ON = "<a:online:1529831651205709885>"
EMOJI_OFF = "<a:offline:1529831624642924584>"

# ---------------------------------------------------------
# ตัวแปรระบบ (เก็บสถานะ และ ID ข้อความล่าสุดเพื่อลบ)
# ---------------------------------------------------------
system_status = {
    "tr": {"text": "ใช้งานได้ปกติ", "is_online": True},
    "unbanpiriya": {"text": "ใช้งานได้ปกติ", "is_online": True}
}

last_announce_msg_id = None # จดจำ ID ข้อความล่าสุดเพื่อนำไปลบทิ้ง

# ---------------------------------------------------------
# ฟังก์ชันสร้างและส่งข้อความสถานะ (ลบของเก่า -> ลงของใหม่)
# ---------------------------------------------------------
def create_status_embed(title_text):
    all_online = system_status["tr"]["is_online"] and system_status["unbanpiriya"]["is_online"]
    embed_color = 0x2ecc71 if all_online else 0xe74c3c 

    embed = discord.Embed(
        title=f"🌐 {title_text}",
        description="อัปเดตสถานะการทำงานของระบบแบบ Real-time\n━━━━━━━━━━━━━━━━━━━━━━",
        color=embed_color
    )
    
    tr_emoji = EMOJI_ON if system_status["tr"]["is_online"] else EMOJI_OFF
    unban_emoji = EMOJI_ON if system_status["unbanpiriya"]["is_online"] else EMOJI_OFF

    embed.add_field(name="🔹 ระบบ TR", value=f"> {tr_emoji} **{system_status['tr']['text']}**\n", inline=False)
    embed.add_field(name="🔹 ระบบ Unbanpiriya", value=f"> {unban_emoji} **{system_status['unbanpiriya']['text']}**\n", inline=False)
    
    embed.set_footer(text="ระบบทำงานออนไลน์อัตโนมัติตลอด 24 ชั่วโมง")
    return embed

async def send_status_update(channel, title):
    global last_announce_msg_id
    
    # 1. วิ่งไปลบข้อความเก่า (ถ้ามี)
    if last_announce_msg_id:
        try:
            old_msg = await channel.fetch_message(last_announce_msg_id)
            await old_msg.delete()
        except:
            pass # ถ้าลบไม่ได้ (เช่นมีคนมือบอนลบไปแล้ว) ก็ให้ข้ามไป
            
    # 2. ส่งข้อความใหม่ พร้อมแท็กยศ
    embed = create_status_embed(title)
    content = f"<@&{PING_ROLE_ID}> 📢 **{title}**"
    
    new_msg = await channel.send(content=content, embed=embed)
    
    # 3. จำ ID ข้อความใหม่เอาไว้ใช้ลบรอบหน้า
    last_announce_msg_id = new_msg.id

# ---------------------------------------------------------
# ระบบปุ่มกด (แผงควบคุมแอดมิน)
# ---------------------------------------------------------
class ControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # ปุ่มอยู่ถาวร ไม่หมดเวลา
        
    # ล็อกสิทธิ์: ถ้าน้องหวือไม่ได้กด จะแจ้งเตือน
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้นะครับ!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="TR: ปกติ", style=discord.ButtonStyle.green, custom_id="tr_on")
    async def btn_tr_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        system_status["tr"] = {"text": "ใช้งานได้ปกติ", "is_online": True}
        await interaction.response.send_message("✅ อัปเดตสถานะ TR (ปกติ) เรียบร้อย", ephemeral=True)
        await send_status_update(bot.get_channel(ANNOUNCE_CHANNEL_ID), "อัปเดตสถานะระบบ TR!")

    @discord.ui.button(label="TR: ปรับปรุง", style=discord.ButtonStyle.red, custom_id="tr_off")
    async def btn_tr_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        system_status["tr"] = {"text": "ปิดปรับปรุงระบบชั่วคราว", "is_online": False}
        await interaction.response.send_message("🔴 อัปเดตสถานะ TR (ปรับปรุง) เรียบร้อย", ephemeral=True)
        await send_status_update(bot.get_channel(ANNOUNCE_CHANNEL_ID), "อัปเดตสถานะระบบ TR!")

    @discord.ui.button(label="Unban: ปกติ", style=discord.ButtonStyle.green, custom_id="unban_on")
    async def btn_unban_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        system_status["unbanpiriya"] = {"text": "ใช้งานได้ปกติ", "is_online": True}
        await interaction.response.send_message("✅ อัปเดตสถานะ Unban (ปกติ) เรียบร้อย", ephemeral=True)
        await send_status_update(bot.get_channel(ANNOUNCE_CHANNEL_ID), "อัปเดตสถานะระบบ Unbanpiriya!")

    @discord.ui.button(label="Unban: ปรับปรุง", style=discord.ButtonStyle.red, custom_id="unban_off")
    async def btn_unban_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        system_status["unbanpiriya"] = {"text": "ปิดปรับปรุงระบบชั่วคราว", "is_online": False}
        await interaction.response.send_message("🔴 อัปเดตสถานะ Unban (ปรับปรุง) เรียบร้อย", ephemeral=True)
        await send_status_update(bot.get_channel(ANNOUNCE_CHANNEL_ID), "อัปเดตสถานะระบบ Unbanpiriya!")

    @discord.ui.button(label="🔄 บังคับอัปเดตเดี๋ยวนี้", style=discord.ButtonStyle.blurple, custom_id="force_update")
    async def btn_update(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_status_update(bot.get_channel(ANNOUNCE_CHANNEL_ID), "สรุปสถานะระบบล่าสุด")
        await interaction.response.send_message("🔄 ส่งการ์ดแจ้งเตือนใบใหม่เรียบร้อย", ephemeral=True)

# ---------------------------------------------------------
# ระบบลูปแจ้งเตือน 06:00 น. อัตโนมัติ (เวลาประเทศไทย)
# ---------------------------------------------------------
# ตั้งค่าโซนเวลาเป็นไทย (UTC+7) และล็อกเวลา 6 โมงเช้า
tz_th = datetime.timezone(datetime.timedelta(hours=7))
time_6am = datetime.time(hour=6, minute=0, tzinfo=tz_th)

@tasks.loop(time=time_6am)
async def auto_daily_status():
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel:
        await send_status_update(channel, "สรุปสถานะระบบประจำวัน (06:00 น.)")

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user.name} ออนไลน์แล้ว!")
    bot.add_view(ControlPanel()) # ทำให้ปุ่มใช้งานได้ตลอดแม้รีสตาร์ทบอท
    if not auto_daily_status.is_running():
        auto_daily_status.start()

# ---------------------------------------------------------
# คำสั่งเรียกแผงควบคุมมาใช้งาน (ใช้ครั้งเดียวในห้อง Control)
# ---------------------------------------------------------
@bot.command()
async def setup(ctx):
    """เรียกแผงควบคุมบอท (พิมพ์ได้แค่ห้อง Control)"""
    if ctx.author.id != OWNER_ID:
        return
    if ctx.channel.id != CONTROL_CHANNEL_ID:
        await ctx.send("❌ รบกวนไปพิมพ์คำสั่งนี้ในห้อง Control Panel เท่านั้นครับ")
        return
        
    embed = discord.Embed(
        title="🎛️ แผงควบคุมสถานะบอท (Control Panel)",
        description="กดปุ่มด้านล่างเพื่อเปลี่ยนสถานะระบบได้เลยครับ\nเมื่อกดปุ่ม บอทจะไป **ลบข้อความแจ้งเตือนอันเก่าทิ้ง** แล้วส่งอันใหม่ล่าสุดให้ทันที!",
        color=0x2b2d31
    )
    await ctx.send(embed=embed, view=ControlPanel())

# ---------------------------------------------------------
# รันบอท
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Error: ไม่พบ DISCORD_TOKEN!")
else:
    bot.run(TOKEN)
