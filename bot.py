import discord
from discord.ext import commands
import psutil
import requests

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def check_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

@bot.event
async def on_ready():
    print(f'✅ บอทออนไลน์แล้วในชื่อ: {bot.user.name}')

@bot.command(name="status")
async def status(ctx):
    # 1. เช็กสถานะของ TR
    tr_is_running = check_process_running("tr_program.exe") # เปลี่ยนชื่อไฟล์โปรแกรม TR ของคุณ
    tr_status = "🟢 พร้อมใช้งาน (Online)" if tr_is_running else "🔴 กำลังปรับปรุง / ปิดอยู่ (Maintenance/Down)"

    # 2. เช็กสถานะของ Unbanpiriya
    try:
        response = requests.get("https://api.unbanpiriya.com", timeout=5) # เปลี่ยนเป็น URL ของ Unbanpiriya
        if response.status_code == 200:
            unban_status = "🟢 พร้อมใช้งาน (Online)"
        else:
            unban_status = f"🟡 กำลังปรับปรุง (Status: {response.status_code})"
    except requests.exceptions.ConnectionError:
        unban_status = "🔴 กำลังปรับปรุง / ออฟไลน์ (Offline)"

    # สร้างหน้าตากล่องข้อความแบบใช้งานง่าย
    embed = discord.Embed(
        title="📊 รายงานสถานะระบบ (TR & Unbanpiriya)",
        color=discord.Color.blue()
    )
    embed.add_field(name="🔹 Status TR", value=tr_status, inline=False)
    embed.add_field(name="🔹 Status Unbanpiriya", value=unban_status, inline=False)
    embed.set_footer(text="ระบบเช็กสถานะอัตโนมัติ 24 ชม.")

    await ctx.send(embed=embed)

bot.run("")