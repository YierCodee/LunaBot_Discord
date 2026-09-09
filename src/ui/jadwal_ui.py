import discord
from src.database import supabase

class HariSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Semua Hari", emoji="📅", description="Tampilkan seluruh jadwal perkuliahan"),
            discord.SelectOption(label="Senin", emoji="🔴"),
            discord.SelectOption(label="Selasa", emoji="🟠"),
            discord.SelectOption(label="Rabu", emoji="🟡"),
            discord.SelectOption(label="Kamis", emoji="🟢"),
            discord.SelectOption(label="Jumat", emoji="🔵"),
            discord.SelectOption(label="Sabtu", emoji="🟣"),
        ]
        super().__init__(placeholder="🔍 Pilih Hari Perkuliahan...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        pilihan = self.values[0]

        try:
            query = supabase.table("jadwal").select("*")
            if pilihan != "Semua Hari":
                query = query.ilike("hari", pilihan)
            
            data = query.execute().data

            if not data:
                embed_empty = discord.Embed(
                    title=f"💤 Tidak Ada Kuliah ({pilihan})",
                    description="Tidak ada jadwal perkuliahan untuk hari ini. Selamat beristirahat!",
                    color=discord.Color.gold()
                )
                await interaction.edit_original_response(embed=embed_empty, view=self.view)
                return

            embed = discord.Embed(
                title=f"🗓️ JADWAL KULIAH — {pilihan.upper()}",
                description="Berikut adalah daftar matakuliah dan ruangannya:",
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
                    name=f"📖 {item['matkul']} ({item['hari']})",
                    value=value_text,
                    inline=False
                )

            embed.set_footer(text="Gunakan dropdown di bawah untuk memfilter hari")
            await interaction.edit_original_response(embed=embed, view=self.view)

        except Exception as e:
            await interaction.followup.send(f"❌ Terjadi kesalahan: {e}", ephemeral=True)

class JadwalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HariSelect())