import discord
from src.database import supabase

class TugasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.primary, emoji="🔄")
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            response = supabase.table("tugas").select("*").execute()
            data = response.data

            if not data:
                embed = discord.Embed(
                    title="🎉 Bebas Tugas!",
                    description="Tidak ada tugas aktif saat ini.",
                    color=discord.Color.brand_green()
                )
            else:
                embed = discord.Embed(
                    title="📚 DAFTAR TUGAS KELAS (Refreshed)",
                    description=f"Total tugas aktif: **{len(data)}**\nGunakan `/selesai` untuk menghapus tugas.",
                    color=discord.Color.blurple()
                )
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2680/2680908.png")

                for item in data:
                    embed.add_field(
                        name=f"📌 `{item['id']}` | {item['matkul']}",
                        value=f"> **Deskripsi:** {item['deskripsi']}\n> ⏰ **Deadline:** `{item['deadline']}`",
                        inline=False
                    )

            await interaction.edit_original_response(embed=embed, view=self)
        except Exception as e:
            await interaction.followup.send(f"❌ Gagal memperbarui data: {e}", ephemeral=True)