import os
import discord
from discord.ext import commands, tasks
import itertools

# ตั้งค่า Intent ของบอท
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------------------------------------
# ตั้งค่า ID สิทธิ์และช่องแจ้งเตือน
# ---------------------------------------------------------
OWNER_ID = 1505161074885001331         # User ID ของคุณ
ANNOUNCE_CHANNEL_ID = 1529818198516437053 # Channel ID ช่องแจ้งเตือน

# เก็บสถานะปัจจุบันของแต่ละระบบ
system_status = {
    "tr": "🟢 ใช้งานได้ปกติ",
    "unbanpiriya": "🟢 ใช้งานได้ปกติ"
}

# ตัวสลับข้อความใต้ชื่อบอท
status_cycle = itertools.cycle(["tr", "unbanpiriya"])

# ---------------------------------------------------------
# ระบบวนลูป (Tasks)
# ---------------------------------------------------------

# 1. สลับข้อความใต้ชื่อบอททุกๆ 10 วินาที
@tasks.loop(seconds=10)
async def update_presence():
    current = next(status_cycle)
    if current == "tr":
        await bot.change_presence(activity=discord.Game(f"TR: {system_status['tr']}"))
    else:
        await bot.change_presence(activity=discord.Game(f"Unbanpiriya: {system_status['unbanpiriya']}"))

# 2. ส่งการ์ดอัปเดตสถานะอัตโนมัติลงช่องที่กำหนดทุกๆ 24 ชั่วโมง
@tasks.loop(hours=24)
async def auto_daily_status():
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel:
        embed = build_status_embed("📢 สรุปสถานะระบบประจำวัน (24 ชม.)")
        await channel.send(embed=embed)

# Helper function สำหรับสร้าง Embed การ์ดสถานะสวยๆ
def build_status_embed(title_text):
    embed = discord.Embed(
        title=title_text, 
        color=0x2b2d31, # สีโทนเข้ม หรูหรา
        description="เช็กสถานะการทำงานของระบบแบบ Real-time"
    )
    
    # ใส่อีโมจิขยับได้อันแรก ตรงหน้าชื่อหัวข้อเล็กๆ (Author)
    embed.set_author(
        name="System Status Report",
        icon_url="https://cdn.discordapp.com/emojis/1506963593302638693.webp?size=32&animated=true"
    )
    
    embed.add_field(name="🔹 ระบบ TR", value=f"> **{system_status['tr']}**", inline=False)
    embed.add_field(name="🔹 ระบบ Unbanpiriya", value=f"> **{system_status['unbanpiriya']}**", inline=False)
    
    # ใส่อีโมจิขยับได้อันที่สอง ตรงมุมซ้ายล่างสุด (Footer)
    embed.set_footer(
        text="ระบบทำงานออนไลน์ตลอด 24 ชั่วโมง", 
        icon_url="https://cdn.discordapp.com/emojis/1437547680254529676.webp?size=128&animated=true"
    )
    return embed

@bot.event
async def on_ready():
    print(f"✅ ล็อกอินสำเร็จในชื่อ: {bot.user.name}")
    
    # เริ่มทำงานระบบ Loop
    if not update_presence.is_running():
        update_presence.start()
    if not auto_daily_status.is_running():
        auto_daily_status.start()

# ---------------------------------------------------------
# คำสั่งเปลี่ยนสถานะ (ผู้ดูแลเปลี่ยนได้คนเดียว)
# ---------------------------------------------------------

@bot.command()
async def set_tr(ctx, *, new_status: str):
    """เปลี่ยนสถานะ TR เช่น !set_tr 🔴 ปิดปรับปรุง"""
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้งานคำสั่งนี้ (เฉพาะเจ้าของบอทเท่านั้น)")
        return
        
    system_status["tr"] = new_status
    await ctx.send(f"✅ อัปเดตสถานะ **TR** เป็น: `{new_status}` เรียบร้อยแล้วครับ!")

@bot.command()
async def set_unban(ctx, *, new_status: str):
    """เปลี่ยนสถานะ Unbanpiriya เช่น !set_unban 🔴 ปิดปรับปรุง"""
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้งานคำสั่งนี้ (เฉพาะเจ้าของบอทเท่านั้น)")
        return
        
    system_status["unbanpiriya"] = new_status
    await ctx.send(f"✅ อัปเดตสถานะ **Unbanpiriya** เป็น: `{new_status}` เรียบร้อยแล้วครับ!")

# คำสั่งดูสถานะทั่วไป (ทุกคนพิมพ์ดูได้)
@bot.command()
async def status(ctx):
    embed = build_status_embed("📊 อัปเดตสถานะระบบ (System Status)")
    await ctx.send(embed=embed)

# ---------------------------------------------------------
# รันบอทผ่าน Render
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ Error: ไม่พบ DISCORD_TOKEN!")
else:
    bot.run(TOKEN)
