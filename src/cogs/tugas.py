import os
import datetime
import discord
import pytz
from discord.ext import commands, tasks
from discord import app_commands
from src.database import supabase
from src.ui.tugas_ui import TugasView

class TugasCog(commands.Cog):
    def __init__(self, bot, luna_group):
        self.bot = bot
        self.luna_group = luna_group
        # Ambil CHANNEL_ID untuk kirim pesan otomatis
        self.channel_id = int(os.getenv("CHANNEL_ID", 0))
        
        # Daftarkan command daftar-tugas
        cmd_tugas = app_commands.Command(
            name="tugas",
            description="Menampilkan daftar tugas kelas",
            callback=self.daftar_tugas
        )
        self.luna_group.add_command(cmd_tugas, override=True)
        
        # Daftarkan command tambah-tugas
        cmd_tambah = app_commands.Command(
            name="tambah-tugas",
            description="Menambahkan tugas baru",
            callback=self.tambah_tugas
        )
        self.luna_group.add_command(cmd_tambah, override=True)

        # Mulai background task untuk hapus tugas otomatis
        self.auto_delete_expired.start()

    def cog_unload(self):
        self.auto_delete_expired.cancel()
        self.luna_group.remove_command("tugas")
        self.luna_group.remove_command("tambah-tugas")

    # ----------------------------------------------------
    # BACKGROUND TASK (Cek Tugas Kadaluarsa Setiap 1 Jam)
    # ----------------------------------------------------
    @tasks.loop(minutes=20)
    async def auto_delete_expired(self):
        try:
            response = supabase.table("tugas").select("*").execute()
            data = response.data
            
            if not data:
                return
                
            # Gunakan timezone Asia/Jakarta agar sesuai WIB
            today = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).date()
            ids_to_delete = []
            deleted_tasks_info = [] # Untuk menyimpan info tugas yang dihapus (matkul & deadline)
            
            for item in data:
                try:
                    # Ambil hanya bagian tanggalnya (misal: "2023-01-01" dari "2023-01-01 00:00:00+00")
                    deadline_str = str(item['deadline']).split(' ')[0]
                    deadline_date = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
                    
                    # Jika tanggal deadline sudah lewat dari tanggal hari ini
                    if deadline_date < today:
                        ids_to_delete.append(item['id'])
                        # Simpan info untuk ditampilkan di pesan
                        deleted_tasks_info.append(f"📌 **{item['matkul']}** (Deadline: {deadline_str})")
                except ValueError:
                    # Abaikan jika ada data tanggal yang corrupt/formatnya salah
                    continue
            
            if ids_to_delete:
                # Hapus dari database
                for id_to_delete in ids_to_delete:
                    supabase.table("tugas").delete().eq("id", id_to_delete).execute()
                
                print(f"🧹 Otomatis menghapus {len(ids_to_delete)} tugas yang sudah lewat deadline.")
                
                # Kirim pesan ke channel Discord
                if self.channel_id:
                    channel = self.bot.get_channel(self.channel_id)
                    if channel:
                        # Buat embed untuk notifikasi
                        embed = discord.Embed(
                            title="🧹 Pembersihan Tugas Otomatis",
                            description=f"Sistem telah menghapus **{len(ids_to_delete)} tugas** yang sudah melewati batas deadline:",
                            color=discord.Color.dark_gray()
                        )
                        
                        # Gabungkan info tugas yang dihapus (maksimal 1024 karakter untuk value field)
                        tasks_list = "\n".join(deleted_tasks_info)
                        if len(tasks_list) > 1024:
                            tasks_list = tasks_list[:1020] + "..."
                            
                        embed.add_field(name="Tugas yang Dihapus:", value=tasks_list, inline=False)
                        embed.set_footer(text="Sistem otomatis Luna Bot")
                        embed.timestamp = datetime.datetime.now(pytz.timezone('Asia/Jakarta'))
                        
                        await channel.send(embed=embed)
                        
        except Exception as e:
            print(f"❌ Error pada auto_delete_expired: {e}")

    @auto_delete_expired.before_loop
    async def before_auto_delete_expired(self):
        await self.bot.wait_until_ready()

    # ----------------------------------------------------
    # SLASH COMMANDS CALLBACKS
    # ----------------------------------------------------
    async def daftar_tugas(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            response = supabase.table("tugas").select("*").execute()
            data = response.data

            if not data:
                embed = discord.Embed(
                    title="🎉 Bebas Tugas!",
                    description="Tidak ada tugas aktif saat ini. Selamat beristirahat!",
                    color=discord.Color.brand_green()
                )
                await interaction.followup.send(embed=embed)
                return

            embed = discord.Embed(
                title="📚 DAFTAR TUGAS KELAS",
                description=f"Total tugas aktif: **{len(data)}**\nTugas yang sudah lewat deadline akan otomatis terhapus.",
                color=discord.Color.blurple()
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2680/2680908.png")

            for item in data:
                embed.add_field(
                    name=f"📌 `{item['id']}` | {item['matkul']}",
                    value=f"> **Deskripsi:** {item['deskripsi']}\n> ⏰ **Deadline:** `{item['deadline']}`",
                    inline=False
                )

            embed.set_footer(text="Updated automatically via Supabase", icon_url=interaction.user.display_avatar.url)
            view = TugasView()
            await interaction.followup.send(embed=embed, view=view)

        except Exception as e:
            await interaction.followup.send(f"❌ Terjadi kesalahan: {e}")

    @app_commands.describe(
        matkul="Nama Mata Kuliah", 
        deskripsi="Detail Tugas", 
        deadline="Format: YYYY-MM-DD (Contoh: 2025-12-31)",
        dosen="Nama Dosen Pengampu (Opsional)"
    )
    async def tambah_tugas(
        self, 
        interaction: discord.Interaction, 
        matkul: str, 
        deskripsi: str, 
        deadline: str,
        dosen: str = "-"
    ):
        await interaction.response.defer()
        try:
            supabase.table("tugas").insert({
                "matkul": matkul,
                "deskripsi": deskripsi,
                "deadline": deadline,
                "dosen": dosen
            }).execute()
            await interaction.followup.send(f"✅ Tugas **{matkul}** berhasil ditambahkan!")
        except Exception as e:
            await interaction.followup.send(f"❌ Gagal menambahkan tugas: {e}")

async def setup(bot):
    # Kirim instance grup dari main.py ke Cog ini
    await bot.add_cog(TugasCog(bot, bot.luna_group))