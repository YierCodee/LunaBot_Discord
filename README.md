# Luna Bot

Bot Discord untuk pengelolaan tugas, jadwal kuliah, dan pengingat otomatis menggunakan Python dan Supabase.

## Fitur

- **Tugas** — Lihat, tambah, dan hapus otomatis tugas yang sudah expired
- **Jadwal** — Lihat jadwal kuliah dengan filter hari menggunakan dropdown
- **Reminder** — Pengingat otomatis setiap hari jam 19:00 WIB untuk jadwal besok dan deadline tugas

## Tech Stack

- Python 3.14
- discord.py v2.7.1
- Supabase (database backend)
- python-dotenv (env management)

## Struktur Projek

```
.
├── main.py                 # Entrypoint bot
├── .env                    # Environment variables (secret)
├── .gitignore
├── src/
│   ├── config.py           # Load env vars
│   ├── database.py         # Inisialisasi Supabase client
│   ├── luna_group.py       # Definisi slash command group
│   ├── cogs/
│   │   ├── tugas.py        # Cog untuk manajemen tugas
│   │   ├── jadwal.py       # Cog untuk jadwal kuliah
│   │   └── reminder.py     # Cog untuk pengingat otomatis
│   └── ui/
│       ├── jadwal_ui.py    # Dropdown filter jadwal per hari
│       └── tugas_ui.py     # Tombol refresh daftar tugas
```

## Setup

1. **Clone repo**
   ```bash
   git clone <repo-url>
   cd discord
   ```

2. **Buat virtual environment**
   ```bash
   python3.14 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install discord.py supabase python-dotenv
   ```

4. **Buat file `.env`** di root project:
   ```
   BOT_TOKEN=token_bot_discord
   GUILD_ID=id_server
   SUPABASE_URL=url_supabase
   SUPABASE_KEY=anon_key_supabase
   CHANNEL_ID=id_channel
   ```

5. **Jalankan bot**
   ```bash
   python main.py
   ```

## Slash Commands

Semua command diakses via `/luna` di Discord:

| Command | Deskripsi |
|---------|-----------|
| `/luna tugas` | Lihat daftar tugas aktif |
| `/luna tambah-tugas` | Tambah tugas baru |
| `/luna jadwal` | Lihat jadwal kuliah |
| `/luna tambah-jadwal` | Tambah jadwal baru |

## Catatan

- Bot menggunakan guild-specific command sync (bukan global), jadi command hanya muncul di server yang sesuai dengan `GUILD_ID`
- Reminder otomatis jalan setiap hari jam 19:00 WIB
- Tugas expired akan dihapus otomatis dari database
- `.env` sudah ada di `.gitignore` — jangan commit file ini
