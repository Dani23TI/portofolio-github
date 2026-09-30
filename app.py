import os
import requests
import streamlit as st

# ============================================================
# KONFIGURASI
# ============================================================
USERNAME = "Dani23TI"          # username GitHub

# Kosongkan INCLUDE untuk menampilkan semua repo milik sendiri.
# Isi dengan nama repo jika hanya ingin menampilkan proyek tertentu.
INCLUDE = []
# Repo yang tidak ingin ditampilkan (misal repo percobaan)
EXCLUDE = ["GitHub-React", "React-Sedap", "2tib-2355301042-praksul-app"]

st.set_page_config(page_title=f"Portofolio {USERNAME}", page_icon="💻", layout="wide")


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


# ============================================================
# TAMPILAN
# ============================================================
st.title(f"💻 Portofolio {USERNAME}")
st.caption("Daftar proyek diambil langsung dari GitHub.")

try:
    repos = get_repos()
except Exception as e:
    st.error(f"Gagal mengambil data GitHub: {e}")
    st.stop()

# Sidebar: pencarian dan filter bahasa
st.sidebar.header("Filter")
cari = st.sidebar.text_input("Cari proyek")
semua_bahasa = sorted({r["language"] for r in repos if r["language"]})
pilih_bahasa = st.sidebar.multiselect("Bahasa utama", semua_bahasa)

tampil = [
    r for r in repos
    if (not cari or cari.lower() in r["name"].lower()
        or cari.lower() in (r["description"] or "").lower())
    and (not pilih_bahasa or r["language"] in pilih_bahasa)
]

st.write(f"Menampilkan **{len(tampil)}** dari {len(repos)} proyek.")

for repo in tampil:
    with st.expander(f"📁 {repo['name']}"):
        tab_ringkasan, tab_readme = st.tabs(["Ringkasan", "README"])

        with tab_ringkasan:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(repo["description"] or "Belum ada deskripsi.")
                st.markdown(f"[Buka di GitHub]({repo['html_url']})")
                if repo.get("homepage"):
                    st.markdown(f"[Demo / Website]({repo['homepage']})")
            with col2:
                bahasa = get_languages(repo["name"])
                st.caption(f"Teknologi: {', '.join(bahasa) if bahasa else '-'}")
                st.caption(f"Update: {repo['pushed_at'][:10]}")

        with tab_readme:
            readme = get_readme(repo["name"])
            if readme:
                st.markdown(readme)
            else:
                st.info("Repo ini belum punya README.")
