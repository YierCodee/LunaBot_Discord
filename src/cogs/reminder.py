import os
import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands
from src.database import supabase

class ReminderCog(commands.Cog):
    def __init__(self, bot, luna_group): # Tambahkan parameter luna_group
        self.bot = bot
        self.luna_group = luna_group      # Simpan sebagai atribut
        self.channel_id = int(os.getenv("CHANNEL_ID", 0))
        
        # DAFTARKAN COMMAND SECARA MANUAL KE GRUP LUNA
        cmd_jadwal = app_commands.Command(
            name="test-reminder-jadwal",
            description="[TEST] Tes pengingat jadwal besok secara manual",
            callback=self.test_reminder_jadwal  # Mengikat self (Cog)
        )
        self.luna_group.add_command(cmd_jadwal, override=True)
        
        cmd_tugas = app_commands.Command(
            name="test-reminder-tugas",
            description="[TEST] Tes pengingat tugas deadline besok secara manual",
            callback=self.test_reminder_tugas
        )
        self.luna_group.add_command(cmd_tugas, override=True)
        
        self.daily_reminder.start()

    def cog_unload(self):
        self.daily_reminder.cancel()
        # Hapus command saat Cog di-unload untuk mencegah error saat reload
        self.luna_group.remove_command("test-reminder-jadwal")
        self.luna_group.remove_command("test-reminder-tugas")

    TARGET_TIME = datetime.time(hour=19, minute=0, second=0)

    # ----------------------------------------------------
    # HELPER FUNCTIONS (Logika Utama Pengingat)
    # ----------------------------------------------------
    async def check_and_send_jadwal(self, channel):
        # ... (Kode helper Anda tetap sama persis seperti sebelumnya) ...
        hari_map = {
            0: "Senin", 1: "Selasa", 2: "Rabu",
            3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"
        }
        besok_dt = datetime.datetime.now() + datetime.timedelta(days=1)
        nama_hari_besok = hari_map[besok_dt.weekday()]

        res_jadwal = supabase.table("jadwal").select("*").ilike("hari", nama_hari_besok).execute()
        data_jadwal = res_jadwal.data

        if data_jadwal:
            embed = discord.Embed(
                title=f"⏰ PENGINGAT KELAS BESOK ({nama_hari_besok.upper()})",
                description="Persiapkan diri Anda! Berikut adalah jadwal perkuliahan untuk besok:",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3652/3652191.png")

            for item in data_jadwal:
                value_text = (
                    f"⏰ **Waktu:** `{item['jam']}`\n"
                    f"🏛️ **Ruangan:** `{item['ruangan']}`\n"
                    f"👨‍🏫 **Dosen:** {item.get('dosen', '-')}"
                )
                embed.add_field(name=f"📖 {item['matkul']}", value=value_text, inline=False)

            embed.set_footer(text="Pengingat Otomatis H-1 Perkuliahan")
            await channel.send(content="@everyone 🔔 **Jadwal Kelas Besok!**", embed=embed)
            return True
        return False

    async def check_and_send_tugas(self, channel):
        # ... (Kode helper Anda tetap sama persis seperti sebelumnya) ...
        besok_dt = datetime.datetime.now() + datetime.timedelta(days=1)
        tanggal_besok_str = besok_dt.strftime("%d/%m/%Y")

        res_tugas = supabase.table("tugas").select("*").eq("deadline", tanggal_besok_str).execute()
        data_tugas = res_tugas.data

        if data_tugas:
            embed = discord.Embed(
                title=f"⚠️ PENGINGAT TUGAS DEADLINE BESOK ({tanggal_besok_str})",
                description="Segera selesaikan tugas berikut sebelum terlambat!",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2680/2680908.png")

            for item in data_tugas:
                value_text = (
                    f"> **Deskripsi:** {item['deskripsi']}\n"
                    f"> 👨‍🏫 **Dosen:** {item.get('dosen', '-')}\n"
                    f"> ⏰ **Deadline:** `{item['deadline']}`"
                )
                embed.add_field(
                    name=f"📌 ID: `{item['id']}` | {item['matkul']}",
                    value=value_text,
                    inline=False
                )

            embed.set_footer(text="Gunakan /selesai <id> jika tugas sudah selesai")
            await channel.send(content="@everyone 🚨 **Ada Tugas Yang Harus Dikumpulkan Besok!**", embed=embed)
            return True
        else:
            embed_empty = discord.Embed(
                title=f"🎉 TIDAK ADA DEADLINE TUGAS BESOK ({tanggal_besok_str})",
                description="Tidak ada tugas yang perlu dikumpulkan besok. Tetap jaga kesehatan!",
                color=discord.Color.green()
            )
            await channel.send(embed=embed_empty)
            return False

    @tasks.loop(time=TARGET_TIME)
    async def daily_reminder(self):
        if not self.channel_id:
            return

        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        try:
            await self.check_and_send_jadwal(channel)
            await self.check_and_send_tugas(channel)
        except Exception as e:
            print(f"❌ Error pada daily_reminder: {e}")

    @daily_reminder.before_loop
    async def before_daily_reminder(self):
        await self.bot.wait_until_ready()

    # ----------------------------------------------------
    # CALLBACKS (Tanpa decorator @ di atasnya)
    # ----------------------------------------------------
    async def test_reminder_jadwal(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                await interaction.followup.send("❌ Channel ID tidak ditemukan!", ephemeral=True)
                return

            await self.check_and_send_jadwal(channel)
            await interaction.followup.send("✅ Tes pengingat jadwal selesai dijalankan!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Terjadi kesalahan: {e}", ephemeral=True)

    async def test_reminder_tugas(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                await interaction.followup.send("❌ Channel ID tidak ditemukan!", ephemeral=True)
                return

            await self.check_and_send_tugas(channel)
            await interaction.followup.send("✅ Tes pengingat tugas selesai dijalankan!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Terjadi kesalahan: {e}", ephemeral=True)

async def setup(bot):
    # Kirim instance grup dari main.py ke Cog ini
    await bot.add_cog(ReminderCog(bot, bot.luna_group))