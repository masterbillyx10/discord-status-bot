import os
import discord
from discord.ext import commands, tasks

# ตั้งค่า Intent ของบอท
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------------------------------------
# ตั้งค่า ID ต่างๆ (สิทธิ์, ช่องแจ้งเตือน, ยศที่ต้องการแท็ก)
# ---------------------------------------------------------
OWNER_ID = 1505161074885001331            # User ID ของคุณ (น้องหวือ)
ANNOUNCE_CHANNEL_ID = 1529818198516437053 # Channel ID ช่องแจ้งเตือน
PING_ROLE_ID = 1519165358911787038        # Role ID ยศที่ต้องการแท็ก

# 🔴 ไอดี Emoji ขยับได้ 2 อันใหม่ 
# (ถ้าสลับกัน สามารถสลับเลข ID ด้านล่างนี้ได้เลยครับ)
EMOJI_ON = "<a:online:1529831651205709885>"   # สำหรับสถานะใช้งานได้ปกติ
EMOJI_OFF = "<a:offline:1529831624642924584>" # สำหรับสถานะปรับปรุง / มีปัญหา

# เก็บสถานะปัจจุบัน 
system_status = {
    "tr": {"text": "ใช้งานได้ปกติ", "is_online": True},
    "unbanpiriya": {"text": "ใช้งานได้ปกติ", "is_online": True}
}

# ---------------------------------------------------------
# ฟังก์ชันสร้างกล่องข้อความสถานะ
# ---------------------------------------------------------
def create_status_embed(title_text):
    # เช็กว่าระบบปกติทั้งคู่ไหม (ปกติ = เขียว, มีปัญหา = แดง)
    all_online = system_status["tr"]["is_online"] and system_status["unbanpiriya"]["is_online"]
    embed_color = 0x2ecc71 if all_online else 0xe74c3c 

    embed = discord.Embed(
        title=f"🌐 {title_text}",
        description="อัปเดตสถานะการทำงานของระบบแบบ Real-time\n━━━━━━━━━━━━━━━━━━━━━━",
        color=embed_color
    )
    
    # สลับอีโมจิตามสถานะ (on = ปกติ, off = ปรับปรุง)
    tr_emoji = EMOJI_ON if system_status["tr"]["is_online"] else EMOJI_OFF
    unban_emoji = EMOJI_ON if system_status["unbanpiriya"]["is_online"] else EMOJI_OFF

    # ใส่ข้อมูลแต่ละระบบ 
    embed.add_field(name="🔹 ระบบ TR", value=f"> {tr_emoji} **{system_status['tr']['text']}**\n", inline=False)
    embed.add_field(name="🔹 ระบบ Unbanpiriya", value=f"> {unban_emoji} **{system_status['unbanpiriya']['text']}**\n", inline=False)
    
    embed.set_footer(text="ระบบทำงานออนไลน์อัตโนมัติตลอด 24 ชั่วโมง")
    return embed

# ---------------------------------------------------------
# ระบบลูปแจ้งเตือนทุก 24 ชั่วโมง (พร้อมแท็กยศ)
# ---------------------------------------------------------
@tasks.loop(hours=24)
async def auto_daily_status():
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel:
        # ส่งข้อความแท็กยศ พร้อมกับกล่อง Embed
        await channel.send(
            content=f"<@&{PING_ROLE_ID}> 📢 **สรุปสถานะระบบประจำวันครับ!**", 
            embed=create_status_embed("สรุปสถานะระบบ (24 ชม.)")
        )

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user.name} ออนไลน์แล้ว!")
    if not auto_daily_status.is_running():
        auto_daily_status.start()

# ---------------------------------------------------------
# คำสั่งจัดการ (เปลี่ยนสถานะ พร้อมแท็กยศแจ้งเตือน)
# ---------------------------------------------------------

@bot.command()
async def set_tr(ctx, state: str, *, message: str):
    """วิธีใช้: !set_tr on ใช้งานได้ปกติ หรือ !set_tr off ปิดปรับปรุง"""
    if ctx.author.id != OWNER_ID:
        return
        
    is_online = state.lower() == "on"
    system_status["tr"] = {"text": message, "is_online": is_online}
    
    await ctx.send(
        content=f"<@&{PING_ROLE_ID}> ⚠️ **มีการอัปเดตสถานะระบบ TR!**", 
        embed=create_status_embed("อัปเดตสถานะ TR ล่าสุด")
    )

@bot.command()
async def set_unban(ctx, state: str, *, message: str):
    """วิธีใช้: !set_unban on ใช้งานได้ปกติ หรือ !set_unban off ปิดปรับปรุง"""
    if ctx.author.id != OWNER_ID:
        return
        
    is_online = state.lower() == "on"
    system_status["unbanpiriya"] = {"text": message, "is_online": is_online}
    
    await ctx.send(
        content=f"<@&{PING_ROLE_ID}> ⚠️ **มีการอัปเดตสถานะระบบ Unbanpiriya!**", 
        embed=create_status_embed("อัปเดตสถานะ Unbanpiriya ล่าสุด")
    )

@bot.command()
async def status(ctx):
    """พิมพ์ !status เพื่อเรียกดูหน้าต่างสถานะ (ไม่แท็กยศ)"""
    await ctx.send(embed=create_status_embed("System Status Report"))

# ---------------------------------------------------------
# รันบอท
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Error: ไม่พบ DISCORD_TOKEN!")
else:
    bot.run(TOKEN)
