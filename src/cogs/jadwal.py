import discord
from discord.ext import commands
from discord import app_commands
from src.database import supabase
from src.ui.jadwal_ui import JadwalView

class JadwalCog(commands.Cog):
    def __init__(self, bot, luna_group):
        self.bot = bot
        self.luna_group = luna_group
        
        # Daftarkan command jadwal
        cmd_jadwal = app_commands.Command(
            name="jadwal",
            description="Menampilkan Jadwal Kuliah",
            callback=self.jadwal
        )
        self.luna_group.add_command(cmd_jadwal, override=True)
        
        # Daftarkan command tambah-jadwal
        cmd_tambah = app_commands.Command(
            name="tambah-jadwal",
            description="Menambahkan jadwal mata kuliah baru",
            callback=self.tambah_jadwal
        )
        self.luna_group.add_command(cmd_tambah, override=True)

    def cog_unload(self):
        self.luna_group.remove_command("jadwal")
        self.luna_group.remove_command("tambah-jadwal")

    async def jadwal(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            response = supabase.table("jadwal").select("*").execute()
            data = response.data

            if not data:
                embed = discord.Embed(
                    title="🗓️ Jadwal Belum Diatur",
                    description="Belum ada data jadwal di database.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return

            embed = discord.Embed(
                title="🗓️ JADWAL PERKULIAHAN",
                description="Pilih hari pada dropdown di bawah untuk memfilter matakuliah!",
                color=discord.Color.teal()
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3652/3652191.png")

            for item in data:
                value_text = (
                    f"⏰ **Waktu:** `{item['jam']}`\n"
                    f"🏛️ **Ruangan:** `{item['ruangan']}`\n"
                    f"👨‍🏫 **Dosen:** {item.get('dosen', '-')}"
                )
                embed.add_field(
                    name=f"📌 [{item['hari']}] {item['matkul']}",
                    value=value_text,
                    inline=False
                )

            view = JadwalView()
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            await interaction.followup.send(f"❌ Terjadi kesalahan: {e}")

    # Letakkan @app_commands.describe PERSIS di atas fungsi callback-nya
    @app_commands.describe(
        hari="Contoh: Senin / Selasa",
        matkul="Nama Mata Kuliah",
        jam="Contoh: 08:00 - 10:30 WIB",
        ruangan="Contoh: Lab Komputer 2",
        dosen="Nama Dosen (Opsional)"
    )
    async def tambah_jadwal(self, interaction: discord.Interaction, hari: str, matkul: str, jam: str, ruangan: str, dosen: str = "-"):
        await interaction.response.defer()
        try:
            supabase.table("jadwal").insert({
                "hari": hari.capitalize(),
                "matkul": matkul,
                "jam": jam,
                "ruangan": ruangan,
                "dosen": dosen
            }).execute()

            await interaction.followup.send(f"✅ Jadwal **{matkul}** ({hari.capitalize()}) berhasil ditambahkan!")
        except Exception as e:
            await interaction.followup.send(f"❌ Gagal menambahkan jadwal: {e}")

async def setup(bot):
    # Kirim instance grup dari main.py ke Cog ini
    await bot.add_cog(JadwalCog(bot, bot.luna_group))