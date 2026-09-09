import discord
from discord.ext import commands
from src.config import BOT_TOKEN, GUILD_ID
from discord import app_commands # Tambahkan ini

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        # 1. Buat Grup LUNA di sini (sebagai instance bot)
        self.luna_group = app_commands.Group(name="luna", description="Perintah seputar Luna Bot")

    async def setup_hook(self):
        await self.load_extension("src.cogs.tugas")
        await self.load_extension("src.cogs.jadwal")
        await self.load_extension("src.cogs.reminder")

        # 2. Daftarkan Grup LUNA ke Command Tree bot
        self.tree.add_command(self.luna_group)

        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)
        

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

         # KODE TESTING SEMENTARA (Hapus setelah lihat hasilnya)
        test_channel_id = 1152590510448451667  # <--- GANTI DENGAN ID CHANNEL ANDA
        test_channel = self.get_channel(test_channel_id) 
        
        if test_channel:            
            # Langsung buat dan kirim embednya ke channel ini
            welcome_text = (
                "Halo teman-teman! 👋✨\n\n"
                "Kenalin nih, **Luna Bot**! 🤖💜 Bot Discord yang siap bantuin kita semua biar nggak kelewatan info seputar tugas dan jadwal kuliah.\n\n"
                "Berikut beberapa fitur kece yang bisa kalian coba:\n\n"
                "📚 **Manajemen Tugas** (`/luna tugas`)\nCek daftar tugas aktif yang belum dikerjakan. Serunya, tugas yang udah lewat deadline bakal kehapus otomatis!\n\n"
                "📝 **Tambah Tugas** (`/luna tambah-tugas`)\nKetemu tugas baru dari dosen? Langsung catat biar nggak lupa!\n\n"
                "🗓️ **Jadwal Kuliah** (`/luna jadwal`)\nIntip jadwal matkul harian. Udah dilengkapi dropdown filter hari juga biar makin praktis!\n\n"
                "⏰ **Pengingat Otomatis**\nNggak perlu takut flashback H-1 pas mau tidur, Luna bakal kirim reminder otomatis setiap jam 19:00 WIB buat infoin jadwal besok dan deadline tugas terdekat!\n\n"
                "Ayo dicoba slash command-nya di server kita (`/luna`)! Kalau ada kendala atau saran fitur, langsung ping aja ya~ Happy studying! 🚀🎓"
            )
            
            embed = discord.Embed(
                description=welcome_text,
                color=discord.Color.purple()
            )
            embed.set_footer(text="Ketik /luna untuk melihat semua perintah yang tersedia!")
            
            try:
                await test_channel.send(embed=embed)
                print("✅ Pesan test berhasil dikirim!")
            except Exception as e:
                print(f"❌ Gagal kirim pesan: {e}")
        else:
            print("❌ Channel tidak ditemukan! Pastikan ID sudah benar.")

client = MyBot()

if __name__ == "__main__":
    client.run(BOT_TOKEN)