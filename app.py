import streamlit as st
import requests
import re

# --- POSTAVKE STRANICE ---
st.set_page_config(
    page_title="Svadbena Galerija",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS STILIZIRANJE (Prilagođeni dizajn i vertikalna pozicija login boxa) ---
st.markdown("""
    <style>
    /* Sakrivanje Streamlitovog headera i footera za čistiji izgled */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Pozadina aplikacije */
    .stApp {
        background-color: #faf9f6;
    }

    /* Stil za naslove */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #2c3e50;
        text-align: center;
    }

    /* Prilagodba gumba */
    .stButton>button {
        border-radius: 20px;
        background-color: #d4af37;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #aa8c2c;
        color: white;
    }

    /* Centriranje i vertikalni pomak login boxa da ne prekriva pozadinu */
    div.stForm {
        background: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 0 auto;
        margin-top: 630px; /* Vertikalni pomak prema dolje */
    }
    </style>
""", unsafe_allow_html=True)

# --- UPRAVLJANJE SESIJOM (LOGIN) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- FUNKCIJA ZA DOHVAT SLIKA IZ ODREĐENE MAPEC ---
@st.cache_data(ttl=3600)
def fetch_images_from_folder(folder_name):
    image_resources = []
    try:
        repo_owner = st.secrets["github"]["owner"]
        repo_name = st.secrets["github"]["repo"]
        token = st.secrets["github"]["token"]
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/HEAD?recursive=1"
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            tree_data = response.json().get("tree", [])
            
            for item in tree_data:
                path = item.get("path", "")
                if path.startswith(f"{folder_name}/") and path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    file_name = path.split('/')[-1]
                    download_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{path}"
                    
                    image_resources.append({
                        "secure_url": download_url,
                        "public_id": file_name
                    })
            
    except Exception as e:
        st.error(f"Greška prilikom spajanja na GitHub: {e}")

    def extract_number(resource):
        public_id = resource.get("public_id", "")
        match = re.search(r'\((\d+)\)', public_id)
        if match:
            return int(match.group(1))
        numbers = re.findall(r'\d+', public_id)
        if numbers:
            return int(numbers[-1])
        return 0

    return sorted(image_resources, key=extract_number)

# --- FUNKCIJA ZA DOHVAT GLAVNE GALERIJE (Galerija 1 i 2) ---
@st.cache_data(ttl=3600)
def fetch_main_gallery_images():
    image_resources = []
    try:
        repo_owner = st.secrets["github"]["owner"]
        repo_name = st.secrets["github"]["repo"]
        token = st.secrets["github"]["token"]
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/HEAD?recursive=1"
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            tree_data = response.json().get("tree", [])
            
            for item in tree_data:
                path = item.get("path", "")
                if (path.startswith("galerija1/") or path.startswith("galerija2/")) and path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    file_name = path.split('/')[-1]
                    download_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{path}"
                    
                    image_resources.append({
                        "secure_url": download_url,
                        "public_id": file_name
                    })
            
    except Exception as e:
        st.error(f"Greška prilikom spajanja na GitHub: {e}")

    def extract_number(resource):
        public_id = resource.get("public_id", "")
        match = re.search(r'\((\d+)\)', public_id)
        if match:
            return int(match.group(1))
        numbers = re.findall(r'\d+', public_id)
        if numbers:
            return int(numbers[-1])
        return 0

    return sorted(image_resources, key=extract_number)

# --- EKRAN ZA PRIJAVU ---
if not st.session_state.authenticated:
    st.markdown("<h1>Dobrodošli na našu svadbenu galeriju</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("<h3 style='text-align: center;'>Unesite šifru za pristup</h3>", unsafe_allow_html=True)
        password_input = st.text_input("Šifra", type="password", label_visibility="collapsed", placeholder="Unesite šifru...")
        submit_button = st.form_submit_button("Uđi u galeriju")
        
        if submit_button:
            if password_input == st.secrets["auth"]["password"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Netočna šifra. Pokušajte ponovno.")

# --- GLAVNA APLIKACIJA NAKON PRIJAVE ---
else:
    # Izbornik na vrhu za prebacivanje između Glavne galerije i Svadbenog albuma
    st.markdown("<br>", unsafe_allow_html=True)
    
    pogled = st.radio(
        "Odabir prikaza",
        ["📸 Glavna galerija", "💍 Svadbeni album"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("---")

    # 1. PRIKAZ GLAVNE GALERIJE (Galerija 1 i 2)
    if pogled == "📸 Glavna galerija":
        st.markdown("<h1>📸 Svadbena Galerija</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Dobrodošli u naše najljepše uspomene!</p>", unsafe_allow_html=True)
        
        images = fetch_main_gallery_images()
        
        if not images:
        # Prikaz opcije za upload ako je galerija prazna (Admin dio)
            st.info("Trenutno nema slika u glavnoj galeriji.")
            with st.expander("🔑 Admin panel (Upload slika)"):
                uploaded_file = st.file_uploader("Izaberi sliku", type=['png', 'jpg', 'jpeg', 'webp'])
                target_folder = st.selectbox("Odaberi mapu", ["galerija1", "galerija2"])
                if uploaded_file and st.button("Učitaj na GitHub"):
                    st.success("Spreman za upload (koristite GitHub sučelje za masovni unos ili prilagodite API upload po potrebi).")
        else:
            # Prikaz slika u mreži (3 stupca)
            cols_per_row = 3
            for i in range(0, len(images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(images):
                        img_data = images[i + j]
                        with cols[j]:
                            st.image(img_data["secure_url"], use_container_width=True)
                            st.markdown(f"<p style='text-align: center; font-size: 12px; color: #888;'>{img_data['public_id']}</p>", unsafe_allow_html=True)

    # 2. PRIKAZ SVADBENOG ALBUMA (Galerija 3 - Izolirano)
    else:
        st.markdown("<h1>💍 Svadbeni Album</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Posebni izdvojeni trenuci našeg vjenčanja</p>", unsafe_allow_html=True)
        
        album_images = fetch_images_from_folder("galerija3")
        
        if not album_images:
            st.info("U svadbenom albumu trenutno nema slika. (Dodajte ih u mapu `galerija3` na GitHubu)")
        else:
            # Prikaz slika iz galerije 3 u mreži
            cols_per_row = 3
            for i in range(0, len(album_images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(album_images):
                        img_data = album_images[i + j]
                        with cols[j]:
                            st.image(img_data["secure_url"], use_container_width=True)
                            st.markdown(f"<p style='text-align: center; font-size: 12px; color: #888;'>{img_data['public_id']}</p>", unsafe_allow_html=True)
