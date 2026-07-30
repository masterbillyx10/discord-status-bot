import os
import asyncio
import discord
from discord.ext import commands, tasks
import datetime
from aiohttp import web
from deep_translator import GoogleTranslator

# ---------------------------------------------------------
# ตั้งค่า ID ต่างๆ (ของพาร์ตเนอร์ และ ดิสคอร์ดเรา)
# ---------------------------------------------------------
OWNER_ID = 1505161074885001331            # User ID น้องหวือ
ANNOUNCE_CHANNEL_ID = 1529818198516437053 # Channel ID ห้องแจ้งเตือนทั่วไป
CONTROL_CHANNEL_ID = 1529834562799276174  # Channel ID ห้องแอดมิน (Control)
PING_ROLE_ID = 1519165358911787038        # Role ID ยศ @WarZ ที่ต้องการแท็ก

# 🔴 ไอดีห้องดึงข่าวสารพาร์ตเนอร์ & ห้องประกาศแปลไทยของเรา
PARTNER_CHANNEL_ID = 1525847194794594384   # ห้อง #cheat-updates พาร์ตเนอร์
MY_UPDATE_CHANNEL_ID = 1507056687612301332 # ห้อง 📜 Update ในดิสคอร์ดเรา

EMOJI_ON_ID = 1529831651205709885   
EMOJI_OFF_ID = 1529831624642924584  

# ---------------------------------------------------------
# Web Server แบบ Async (aiohttp) ป้องกัน 502 Bad Gateway
# ---------------------------------------------------------
async def handle_ping(request):
    return web.Response(text="Bot is alive and running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_head('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web Server started on port {port}")

# ---------------------------------------------------------
# ตั้งค่า บอท Discord หลัก
# ---------------------------------------------------------
class MyBot(commands.Bot):
    async def setup_hook(self):
        # รัน Web Server แบบ Background Task ไม่ให้บล็อกบอท
        self.loop.create_task(start_web_server())

intents = discord.Intents.default()
intents.message_content = True
bot = MyBot(command_prefix="!", intents=intents)

system_status = {
    "tr": {"text": "ใช้งานได้ปกติ", "is_online": True},
    "unbanpiriya": {"text": "ใช้งานได้ปกติ", "is_online": True}
}

last_announce_msg_id = None 

def get_animated_emoji(emoji_id):
    emoji = bot.get_emoji(emoji_id)
    if emoji:
        return str(emoji)
    return f"<a:emoji:{emoji_id}>"

def create_status_embed(title_text):
    all_online = system_status["tr"]["is_online"] and system_status["unbanpiriya"]["is_online"]
    embed_color = 0x2ecc71 if all_online else 0xe74c3c 

    embed = discord.Embed(
        title=f"🌐 {title_text}",
        description="อัปเดตสถานะการทำงานของระบบแบบ Real-time\n━━━━━━━━━━━━━━━━━━━━━━",
        color=embed_color
    )
    
    tr_emoji = get_animated_emoji(EMOJI_ON_ID) if system_status["tr"]["is_online"] else get_animated_emoji(EMOJI_OFF_ID)
    unban_emoji = get_animated_emoji(EMOJI_ON_ID) if system_status["unbanpiriya"]["is_online"] else get_animated_emoji(EMOJI_OFF_ID)

    embed.add_field(name="🔹 ระบบ TR", value=f"> {tr_emoji} **{system_status['tr']['text']}**\n", inline=False)
    embed.add_field(name="🔹 ระบบ Unbanpiriya", value=f"> {unban_emoji} **{system_status['unbanpiriya']['text']}**\n", inline=False)
    
    embed.set_footer(text="ระบบทำงานออนไลน์อัตโนมัติตลอด 24 ชั่วโมง")
    return embed

async def send_status_update(channel, title):
    global last_announce_msg_id
    
    if last_announce_msg_id:
        try:
            old_msg = await channel.fetch_message(last_announce_msg_id)
            await old_msg.delete()
        except:
            pass
            
    embed = create_status_embed(title)
    content = f"<@&{PING_ROLE_ID}> 📢 **{title}**"
    
    new_msg = await channel.send(content=content, embed=embed)
    last_announce_msg_id = new_msg.id

# ---------------------------------------------------------
# ฟังก์ชันแปลภาษาไทย (ใช้ deep-translator) + ส่งการ์ด
# ---------------------------------------------------------
async def process_and_forward_update(raw_text):
    try:
        cleaned_text = raw_text.replace("@everyone", "").replace("@here", "").strip()
        if not cleaned_text:
            return

        translated = GoogleTranslator(source='auto', target='th').translate(cleaned_text)

        channel = bot.get_channel(MY_UPDATE_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="📢 อัปเดตใหม่จากระบบ (แปลภาษาไทย)",
                description=translated,
                color=0x3498db,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="📝 ข้อความต้นฉบับ (Original)", value=f"```\n{cleaned_text[:1000]}\n```", inline=False)
            embed.set_footer(text="ระบบแปลภาษาและแจ้งเตือนอัตโนมัติ")
            
            await channel.send(content=f"📢 <@&{PING_ROLE_ID}> **มีอัปเดตใหม่ครับ!**", embed=embed)
            print("✅ ส่งข่าวสารที่แปลแล้วลงช่องสำเร็จ!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการแปล/ส่งข้อความ: {e}")

# ---------------------------------------------------------
# คำสั่งสั่งแปลด้วยตัวเอง
# ---------------------------------------------------------
@bot.command()
async def translate(ctx, *, text: str):
    if ctx.author.id == OWNER_ID:
        await process_and_forward_update(text)
        await ctx.send("✅ แปลภาษาและประกาศลงช่องเรียบร้อยแล้วครับ!")

# ---------------------------------------------------------
# ระบบแผงควบคุม
# ---------------------------------------------------------
class ControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
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

tz_th = datetime.timezone(datetime.timedelta(hours=7))
time_6am = datetime.time(hour=6, minute=0, tzinfo=tz_th)

@tasks.loop(time=time_6am)
async def auto_daily_status():
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel:
        await send_status_update(channel, "สรุปสถานะระบบประจำวัน (06:00 น.)")

@bot.event
async def on_ready():
    print(f"✅ บอทหลัก {bot.user.name} ออนไลน์เรียบร้อยแล้ว!")
    bot.add_view(ControlPanel())
    if not auto_daily_status.is_running():
        auto_daily_status.start()

@bot.command()
async def setup(ctx):
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
# รันบอทหลัก
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ Error: ไม่พบ DISCORD_TOKEN!")
else:
    bot.run(TOKEN)
