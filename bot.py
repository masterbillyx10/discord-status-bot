import os
import discord
from discord.ext import commands, tasks
import itertools

# ตั้งค่า Intent ของบอท (เปิดใช้งาน message_content เพื่อให้อ่านข้อความได้)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------------------------------------
# ตั้งค่าข้อความสถานะ (Status) ที่ต้องการให้บอทสลับเปลี่ยน
# สามารถแก้ไขข้อความในฟันหนู ("...") ได้ตามต้องการเลยครับ
# ---------------------------------------------------------
statuses = itertools.cycle([
    "กำลังออนไลน์ 24 ชั่วโมง 🟢",
    "ดูแลเซิร์ฟเวอร์อยู่ครับ 🛡️",
    "พิมพ์ !ping เพื่อเช็กสถานะ 🚀"
])

# ตั้งเวลาให้สลับสถานะทุกๆ 10 วินาที
@tasks.loop(seconds=10)
async def change_status():
    # เปลี่ยนสถานะบอท (เปลี่ยนตรง discord.Game เป็น discord.Streaming หรือ discord.Activity ได้ถ้าต้องการ)
    await bot.change_presence(activity=discord.Game(next(statuses)))

@bot.event
async def on_ready():
    print(f"✅ ล็อกอินเข้าสู่ระบบสำเร็จในชื่อ: {bot.user.name} (ID: {bot.user.id})")
    print("🚀 บอทพร้อมทำงานออนไลน์ 24 ชั่วโมงบน Render แล้วครับ!")
    
    # สั่งให้ระบบสลับสถานะเริ่มทำงานตอนบอทออนไลน์
    if not change_status.is_running():
        change_status.start()

# คำสั่งสำหรับให้คนพิมพ์คุยกับบอท
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓 บอทออนไลน์และทำงานอยู่บนคลาวด์เรียบร้อยครับ!")

# ---------------------------------------------------------
# ระบบรันบอท (ดึง Token จาก Cloud ปลอดภัย 100%)
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ Error: ไม่พบ DISCORD_TOKEN! กรุณาตรวจสอบการตั้งค่า Environment Variables บนเว็บ Render")
else:
    bot.run(TOKEN)
