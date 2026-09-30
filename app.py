import os
import re
import requests
import streamlit as st
from collections import Counter
from html import escape

# ============================================================
# KONFIGURASI (ubah bagian ini saja)
# ============================================================
USERNAME = "Dani23TI"                  # username GitHub
NAMA = "Dani"                          # nama yang tampil di halaman
PERAN = "Mahasiswa Teknik Informatika"
TENTANG = (
    "Mahasiswa Teknik Informatika di Politeknik Caltex Riau. "
    "Saya mengerjakan berbagai proyek web, deep learning, dan NLP, "
    "dan seluruh proyek di bawah ini diambil langsung dari GitHub."
)

# Kosongkan INCLUDE untuk menampilkan semua repo milik sendiri.
# Isi dengan nama repo jika hanya ingin menampilkan proyek tertentu.
INCLUDE = []
# Repo yang tidak ingin ditampilkan (misal repo percobaan)
EXCLUDE = ["GitHub-React", "React-Sedap", "2tib-2355301042-praksul-app", "kolaborasitib", "kolaborasi2tib"]

# Gambar sampul proyek. Secara default memakai gambar otomatis dari GitHub.
# Isi jika ingin memakai screenshot sendiri: {"nama-repo": "https://link-gambar"}
GAMBAR_PROYEK = {}

PENDIDIKAN = [
    {
        "judul": "Teknik Informatika",
        "instansi": "Politeknik Caltex Riau",
        "periode": "2023 - sekarang",
        "deskripsi": "Fokus pada pengembangan web, deep learning, dan NLP.",
    },
]

PENGALAMAN = [
    {
        "judul": "Ganti dengan posisi / peran",
        "instansi": "Ganti dengan nama perusahaan / organisasi",
        "periode": "Ganti dengan periode",
        "deskripsi": "Ganti dengan deskripsi singkat pekerjaan.",
    },
]

# Kontak: kosongkan nilainya jika tidak ingin ditampilkan
KONTAK = {
    "GitHub": f"https://github.com/{USERNAME}",
    "LinkedIn": "",
    "Email": "",   # contoh: "mailto:nama@email.com"
}

st.set_page_config(
    page_title=f"Portofolio {NAMA}",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STYLE (tema hitam)
# ============================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: #000000; color: #e5e5e5; }
[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="collapsedControl"],
#MainMenu, footer { display: none !important; }
html, [data-testid="stMain"], section.main { scroll-behavior: smooth; }
.block-container { max-width: 1100px; padding-top: 5.5rem; padding-bottom: 4rem; }

/* Navbar */
.nav { position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 6vw; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px);
  border-bottom: 1px solid #1f1f1f; }
.nav .brand { color: #22c55e; font-weight: 700; font-size: 1.05rem; }
.nav .menu { display: flex; gap: 28px; }
.nav .menu a { color: #a3a3a3; text-decoration: none; font-size: 0.9rem; transition: color .2s; }
.nav .menu a:hover { color: #ffffff; }

/* Section */
.sec { scroll-margin-top: 90px; padding-top: 3.5rem; }
.label { color: #22c55e; font-weight: 600; font-size: 0.85rem; letter-spacing: .08em; text-transform: uppercase; }
.title { color: #ffffff; font-weight: 800; font-size: 2rem; margin: 6px 0 8px 0; }
.sub { color: #737373; font-size: 0.95rem; margin-bottom: 1.5rem; }

/* Hero */
.hero { padding: 2.5rem 0 1rem 0; }
.hero h1 { color: #ffffff; font-size: 3.2rem; font-weight: 800; line-height: 1.1; margin: 8px 0 14px 0; }
.hero h1 span { color: #22c55e; }
.hero p { color: #a3a3a3; max-width: 640px; font-size: 1.05rem; line-height: 1.7; }
.btn { display: inline-block; padding: 10px 20px; border-radius: 10px; font-weight: 600;
  font-size: 0.9rem; text-decoration: none; margin: 14px 10px 0 0; }
.btn.solid { background: #ffffff; color: #000000; }
.btn.line { border: 1px solid #2a2a2a; color: #e5e5e5; }
.btn.line:hover { border-color: #22c55e; color: #22c55e; }

/* Kartu statistik */
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 2rem; }
.stat { background: #0d0d0d; border: 1px solid #1f1f1f; border-radius: 14px; padding: 18px 20px; }
.stat .k { color: #737373; font-size: 0.8rem; }
.stat .v { color: #ffffff; font-size: 1.7rem; font-weight: 700; margin-top: 4px; }
.stat .v.g { color: #22c55e; }

/* Chip */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.chip { background: rgba(34,197,94,0.10); color: #4ade80; border: 1px solid rgba(34,197,94,0.25);
  padding: 4px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 500; }

/* Panel & kartu proyek */
.panel { background: #0d0d0d; border: 1px solid #1f1f1f; border-radius: 14px; padding: 22px 24px; }
.panel p { color: #a3a3a3; line-height: 1.75; margin: 0; }
.card { background: #0d0d0d; border: 1px solid #1f1f1f; border-radius: 14px; overflow: hidden;
  margin-bottom: 8px; transition: border-color .2s; }
.card:hover { border-color: #22c55e; }
.card .thumb { width: 100%; aspect-ratio: 2 / 1; object-fit: cover; display: block;
  background: #111111; border-bottom: 1px solid #1f1f1f; }
.card .body { padding: 16px 18px 18px 18px; }
.card .name { color: #ffffff; font-weight: 700; font-size: 1.1rem; }
.card .desc { color: #a3a3a3; font-size: 0.9rem; line-height: 1.6; margin-top: 6px; min-height: 3.2em; }
.card .links { margin-top: 14px; display: flex; gap: 16px; }
.card .links a { color: #22c55e; font-size: 0.85rem; font-weight: 600; text-decoration: none; }
.card .links a:hover { text-decoration: underline; }
.card .meta { color: #525252; font-size: 0.75rem; margin-top: 10px; }

/* Riwayat */
.item { background: #0d0d0d; border: 1px solid #1f1f1f; border-left: 3px solid #22c55e;
  border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; }
.item .t { color: #ffffff; font-weight: 700; }
.item .i { color: #4ade80; font-size: 0.9rem; margin-top: 2px; }
.item .p { color: #737373; font-size: 0.8rem; margin-top: 2px; }
.item .d { color: #a3a3a3; font-size: 0.9rem; margin-top: 8px; line-height: 1.6; }

/* Widget Streamlit */
[data-testid="stExpander"] { background: #0a0a0a; border: 1px solid #1f1f1f; border-radius: 12px; margin-bottom: 22px; }
[data-testid="stTextInput"] input, [data-baseweb="select"] > div { background: #0d0d0d !important; border-color: #1f1f1f !important; }
hr { border-color: #1f1f1f; }
@media (max-width: 800px) {
  .nav .menu { display: none; }
  .stats { grid-template-columns: 1fr; }
  .hero h1 { font-size: 2.2rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# SECRET / TOKEN
# ============================================================
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")


GITHUB_TOKEN = get_secret("GITHUB_TOKEN")

GH_HEADERS = {"Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    GH_HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


# ============================================================
# AMBIL DATA DARI GITHUB
# ============================================================
@st.cache_data(ttl=3600, show_spinner="Mengambil daftar repository...")
def get_repos():
    repos, page = [], 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers=GH_HEADERS,
            params={"per_page": 100, "page": page, "sort": "pushed"},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1

    hasil = []
    for repo in repos:
        if repo["fork"] or repo["name"] in EXCLUDE:
            continue
        if INCLUDE and repo["name"] not in INCLUDE:
            continue
        hasil.append(repo)
    return hasil


@st.cache_data(ttl=3600)
def get_readme(repo_name):
    r = requests.get(
        f"https://api.github.com/repos/{USERNAME}/{repo_name}/readme",
        headers={**GH_HEADERS, "Accept": "application/vnd.github.raw+json"},
        timeout=20,
    )
    return r.text if r.ok else ""


@st.cache_data(ttl=3600)
def get_languages(repo_name):
    r = requests.get(
        f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages",
        headers=GH_HEADERS,
        timeout=20,
    )
    return list(r.json().keys()) if r.ok else []


def ringkas_readme(readme):
    """Ambil kalimat pertama README yang bukan judul/badge sebagai ringkasan."""
    for baris in readme.splitlines():
        b = baris.strip()
        if not b or b.startswith(("#", "![", "[![", "<", "|", "---", "```", ">", "-", "*", "=")):
            continue
        b = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", b)
        b = b.replace("**", "").replace("`", "")
        if len(b) >= 30:
            return b[:220] + ("..." if len(b) > 220 else "")
    return ""


# ============================================================
# KOMPONEN HTML
# ============================================================
def chips_html(daftar):
    return "".join(f'<span class="chip">{escape(x)}</span>' for x in daftar)


def kartu_proyek(repo, bahasa, ringkasan):
    name = repo["name"]
    gambar = GAMBAR_PROYEK.get(name) or f"https://opengraph.githubassets.com/1/{USERNAME}/{name}"
    desc = repo["description"] or ringkasan or "Belum ada deskripsi."
    links = f'<a href="{repo["html_url"]}" target="_blank">GitHub ↗</a>'
    if repo.get("homepage"):
        links += f'<a href="{escape(repo["homepage"])}" target="_blank">Demo ↗</a>'
    return (
        '<div class="card">'
        f'<img class="thumb" src="{gambar}" onerror="this.style.display=\'none\'">'
        '<div class="body">'
        f'<div class="name">{escape(name)}</div>'
        f'<div class="desc">{escape(desc)}</div>'
        f'<div class="chips">{chips_html(bahasa)}</div>'
        f'<div class="links">{links}</div>'
        f'<div class="meta">Update: {repo["pushed_at"][:10]}</div>'
        '</div></div>'
    )


def daftar_riwayat(items):
    out = ""
    for it in items:
        out += (
            '<div class="item">'
            f'<div class="t">{escape(it["judul"])}</div>'
            f'<div class="i">{escape(it["instansi"])}</div>'
            f'<div class="p">{escape(it["periode"])}</div>'
            f'<div class="d">{escape(it["deskripsi"])}</div>'
            '</div>'
        )
    return out


def judul_section(id_, label, judul, sub=""):
    st.markdown(
        f'<div class="sec" id="{id_}"><div class="label">{label}</div>'
        f'<div class="title">{judul}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# DATA
# ============================================================
try:
    repos = get_repos()
except Exception as e:
    st.error(f"Gagal mengambil data GitHub: {e}")
    st.stop()

bahasa_repo = {r["name"]: get_languages(r["name"]) for r in repos}
hitung_bahasa = Counter(b for daftar in bahasa_repo.values() for b in daftar)
terakhir = max((r["pushed_at"] for r in repos), default="")[:10] or "-"


# ============================================================
# NAVBAR
# ============================================================
st.markdown(
    f"""
<div class="nav">
  <div class="brand">{escape(NAMA.lower())}</div>
  <div class="menu">
    <a href="#beranda" target="_self">Beranda</a>
    <a href="#tentang" target="_self">Tentang Saya</a>
    <a href="#portfolio" target="_self">Portfolio</a>
    <a href="#pendidikan" target="_self">Pendidikan</a>
    <a href="#pengalaman" target="_self">Pengalaman</a>
    <a href="#kontak" target="_self">Kontak</a>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# BERANDA
# ============================================================
st.markdown(
    f'<div class="sec hero" id="beranda"><div class="label">{escape(PERAN)}</div>'
    f'<h1>Halo, saya <span>{escape(NAMA)}</span></h1>'
    f'<p>{escape(TENTANG)}</p>'
    '<a class="btn solid" href="#portfolio" target="_self">Lihat Portfolio</a>'
    f'<a class="btn line" href="https://github.com/{USERNAME}" target="_blank">GitHub</a>'
    '<div class="stats">'
    f'<div class="stat"><div class="k">Total Proyek</div><div class="v g">{len(repos)}</div></div>'
    f'<div class="stat"><div class="k">Teknologi Digunakan</div><div class="v">{len(hitung_bahasa)}</div></div>'
    f'<div class="stat"><div class="k">Update Terakhir</div><div class="v">{terakhir}</div></div>'
    '</div></div>',
    unsafe_allow_html=True,
)


# ============================================================
# TENTANG SAYA
# ============================================================
judul_section("tentang", "Tentang Saya", "Profil & Tech Stack")
kiri, kanan = st.columns(2)
with kiri:
    st.markdown(
        f'<div class="panel"><p>{escape(TENTANG)}</p></div>',
        unsafe_allow_html=True,
    )
with kanan:
    teratas = [b for b, _ in hitung_bahasa.most_common(12)]
    st.markdown(
        '<div class="panel"><div class="label">Teknologi dari repository</div>'
        f'<div class="chips">{chips_html(teratas)}</div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# PORTFOLIO
# ============================================================
judul_section("portfolio", "Portfolio", "Project", "Proyek yang pernah dikembangkan, diambil langsung dari GitHub.")

f1, f2 = st.columns([2, 2])
with f1:
    cari = st.text_input("Cari proyek", placeholder="Ketik nama atau deskripsi...")
with f2:
    pilih_bahasa = st.multiselect("Filter teknologi", sorted(hitung_bahasa))

tampil = [
    r for r in repos
    if (not cari or cari.lower() in r["name"].lower()
        or cari.lower() in (r["description"] or "").lower())
    and (not pilih_bahasa or any(b in bahasa_repo[r["name"]] for b in pilih_bahasa))
]

if not tampil:
    st.info("Tidak ada proyek yang cocok.")

for i in range(0, len(tampil), 2):
    kolom = st.columns(2)
    for kol, repo in zip(kolom, tampil[i:i + 2]):
        with kol:
            readme = get_readme(repo["name"])
            st.markdown(
                kartu_proyek(repo, bahasa_repo[repo["name"]], ringkas_readme(readme)),
                unsafe_allow_html=True,
            )
            with st.expander("Lihat README"):
                if readme:
                    st.markdown(readme)
                else:
                    st.info("Repo ini belum punya README.")


# ============================================================
# PENDIDIKAN
# ============================================================
judul_section("pendidikan", "Pendidikan", "Riwayat Pendidikan", "Pernah dan sedang belajar pada program berikut.")
st.markdown(daftar_riwayat(PENDIDIKAN), unsafe_allow_html=True)


# ============================================================
# PENGALAMAN
# ============================================================
judul_section("pengalaman", "Pengalaman", "Pengalaman Kerja, Freelance & Magang", "Pernah dan sedang bekerja pada tempat berikut.")
st.markdown(daftar_riwayat(PENGALAMAN), unsafe_allow_html=True)


# ============================================================
# KONTAK
# ============================================================
judul_section("kontak", "Kontak", "Mari Terkoneksi", "Terbuka untuk kolaborasi, diskusi proyek, atau peluang baru.")
tombol = "".join(
    f'<a class="btn line" href="{escape(url)}" target="_blank">{escape(nama)}</a>'
    for nama, url in KONTAK.items() if url
)
st.markdown(tombol, unsafe_allow_html=True)
st.markdown(
    f'<div style="color:#525252;font-size:0.8rem;margin-top:3rem;">© {escape(NAMA)} · dibuat dengan Streamlit</div>',
    unsafe_allow_html=True,
)
