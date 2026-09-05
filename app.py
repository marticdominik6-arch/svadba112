import os
import re
import requests
import streamlit as st
import cloudinary
import cloudinary.uploader
import cloudinary.api

# 1. Konfiguracija stranice i čista portfolio tema
st.set_page_config(
    page_title="Matea & Dominik | Vjenčana Galerija",
    page_icon="💍",
    layout="wide",
)

# Inicijalizacija Cloudinary-ja (samo za pozadinsku sliku, ako zatreba)
try:
    cloudinary.config(
        cloud_name = st.secrets["cloudinary"]["cloud_name"],
        api_key = st.secrets["cloudinary"]["api_key"],
        api_secret = st.secrets["cloudinary"]["api_secret"],
        secure = True
    )
except Exception:
    pass

# Inicijalizacija stanja prijave i indeksa za galeriju
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "viewing_image_index" not in st.session_state:
    st.session_state.viewing_image_index = None

# Pozadinska slika (fallback na Unsplash ako nema na Cloudinaryju)
@st.cache_data(ttl=3600)
def get_background():
    try:
        resources = cloudinary.api.resources(type="upload", prefix="background/", max_results=1)
        if resources.get("resources"):
            return resources["resources"][0]["secure_url"]
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1519741497674-611481863552"

background_css = get_background()

# 2. Vrhunski CSS za elegantan izgled i pozicioniranje
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Montserrat:wght@300;400;500&display=swap');

    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.1), rgba(250, 250, 250, 0.15)), url("{background_css}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Montserrat', sans-serif;
    }}
    
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .portfolio-header {{
        text-align: center;
        padding: 30px 20px 5px 20px;
        margin-bottom: 10px;
    }}
    .portfolio-title {{
        font-family: 'Cormorant Garamond', serif;
        font-size: 3.8rem;
        font-weight: 400;
        letter-spacing: 1px;
        color: #ffffff;
        text-shadow: 0 2px 10px rgba(0,0,0,0.4);
        margin-bottom: 5px;
    }}
    .portfolio-author {{
        font-size: 1.6rem;
        letter-spacing: 5px;
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        font-weight: 400;
        text-transform: uppercase;
    }}

    .download-link {{
        display: block;
        text-align: center;
        color: #666666;
        padding: 6px;
        text-decoration: none;
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 400;
        transition: color 0.2s ease;
    }}
    .download-link:hover {{
        color: #111111;
        text-decoration: underline;
    }}

    .block-container {{
        padding-top: 2rem !important;
    }}

    .login-wrapper {{
        padding-top: 150px;
    }}
    
    .admin-panel {{
        background: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #dcdcdc;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Vrhunsko zaglavlje
st.markdown(
    """
    <div class="portfolio-header">
        <div class="portfolio-title">Svadbeni album</div>
        <div class="portfolio-author">Matea & Dominik</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. Ekran za prijavu
if not st.session_state.logged_in:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            entered_password = st.text_input("Šifra pristupa", type="password", placeholder="Unesite šifru...", label_visibility="collapsed")
            submit_login = st.form_submit_button("Pogledaj fotografije", use_container_width=True)
            
            if submit_login:
                try:
                    gost_pass = st.secrets["passwords"]["gost_sifra"]
                    admin_pass = st.secrets["passwords"]["admin_pass"]
                except Exception:
                    gost_pass = "md2026"
                    admin_pass = "Ruksak96"
                    
                if entered_password == gost_pass:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.rerun()
                elif entered_password == admin_pass or entered_password == "Ruksak96":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Netočna šifra. Pokušajte ponovno.")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. Glavni dio aplikacije (nakon prijave)
else:
    top_c1, top_c2 = st.columns([8, 2])
    with top_c1:
        role_text = "👑 Prijavljeni ste kao Administrator" if st.session_state.is_admin else "✨ Prijavljeni ste kao Uzvanik"
        st.markdown(f"<p style='color: #fff; font-weight: 500; padding-top: 8px; text-shadow: 0 1px 3px rgba(0,0,0,0.5);'>{role_text}</p>", unsafe_allow_html=True)
    with top_c2:
        if st.button("Odjava", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.viewing_image_index = None
            st.cache_data.clear()
            st.rerun()

    # AKO JE ADMIN - ADMINISTRACIJSKE KONTROLE
    if st.session_state.is_admin:
        with st.container():
            st.markdown(
                """
                <div class="admin-panel">
                    <h4 style='color: #2c2c2c; font-family: "Cormorant Garamond", serif; margin-bottom: 15px;'>👑 Upravljanje galerijom (Admin kontrole)</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            admin_col1, admin_col2 = st.columns(2)
            
            with admin_col1:
                st.markdown("**Promijeni pozadinsku sliku**")
                bg_file = st.file_uploader("Pozadina", type=["jpg", "jpeg", "png"], key="bg_upload", label_visibility="collapsed")
                if bg_file:
                    if st.button("Primijeni pozadinu", use_container_width=True):
                        with st.spinner("Učitavanje..."):
                            try:
                                old_bgs = cloudinary.api.resources(type="upload", prefix="background/")
                                for b in old_bgs.get("resources", []):
                                    cloudinary.uploader.destroy(b["public_id"])
                            except Exception:
                                pass
                            cloudinary.uploader.upload(bg_file, folder="background", use_filename=True, unique_filename=False)
                            st.cache_data.clear()
                            st.success("Pozadina promijenjena!")
                            st.rerun()

            with admin_col2:
                st.info("💡 Slike za galeriju se povlače izravno s tvog GitHub repozitorija. Nove slike dodaj izravno u GitHub mapu definiranu u postavkama (Secrets).")

        st.divider()

    # DOHVAT SLIKA S GITHUBA
    @st.cache_data(ttl=3600)
    def fetch_github_images():
        image_resources = []
        try:
            repo_owner = st.secrets["github"]["owner"]
            repo_name = st.secrets["github"]["repo"]
            folder_path = st.secrets["github"]["folder"]
            
            api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
            headers = {}
            if "token" in st.secrets["github"]:
                headers["Authorization"] = f"token {st.secrets['github']['token']}"
                
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                files = response.json()
                for file in files:
                    if file["type"] == "file" and file["name"].lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        image_resources.append({
                            "secure_url": file["download_url"],
                            "public_id": file["name"]
                        })
            else:
                st.warning(f"GitHub API je vratio statusni kod: {response.status_code}. Provjeri postavke owner, repo i folder u Secretsima.")
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

    image_resources = fetch_github_images()

    if not image_resources:
        st.info("Trenutno nema slika u GitHub repozitoriju ili putanja nije točna. Provjeri postavke mape u Streamlit Secretsima.")
    else:
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("✨ Pregled svih slika (Slideshow)", use_container_width=True):
                st.session_state.viewing_image_index = 0
                st.rerun()
        
        st.write("") 

        # PREGLED JEDNE SLIKE (SLIDESHOW)
        if st.session_state.viewing_image_index is not None:
            idx = st.session_state.viewing_image_index
            total_imgs = len(image_resources)
            current_res = image_resources[idx]
            full_url = current_res["secure_url"]

            col_b1, col_b2 = st.columns([1, 4])
            with col_b1:
                if st.button("← Natrag na mrežu slika", use_container_width=True):
                    st.session_state.viewing_image_index = None
                    st.rerun()

            st.markdown(f"<h4 style='text-align: center; color: #fff; text-shadow: 0 1px 3px rgba(0,0,0,0.5); margin-top: 5px;'>Fotografija {idx + 1} od {total_imgs}</h4>", unsafe_allow_html=True)
            
            col_left, col_img, col_right = st.columns([1, 8, 1])
            
            with col_left:
                st.write("")
                st.write("")
                st.write("")
                if st.button("◀", key="prev_slide", use_container_width=True, help="Prethodna slika"):
                    st.session_state.viewing_image_index = (idx - 1) % total_imgs
                    st.rerun()
                    
            with col_img:
                st.image(full_url, use_container_width=True)
                
            with col_right:
                st.write("")
                st.write("")
                st.write("")
                if st.button("▶", key="next_slide", use_container_width=True, help="Sljedeća slika"):
                    st.session_state.viewing_image_index = (idx + 1) % total_imgs
                    st.rerun()

            st.markdown(f"<a href='{full_url}' target='_blank' class='download-link' style='font-size: 0.9rem; padding: 8px; max-width: 300px; margin: 15px auto; background: #fff; border: 1px solid #ccc; border-radius: 5px;'>Preuzmi izvornu sliku</a>", unsafe_allow_html=True)

        else:
            # MREŽA SLIKA S PAGINACIJOM
            IMAGES_PER_PAGE = 60 
            total_images = len(image_resources)
            total_pages = (total_images - 1) // IMAGES_PER_PAGE + 1

            if "current_page" not in st.session_state:
                st.session_state.current_page = 0

            if st.session_state.current_page >= total_pages:
                st.session_state.current_page = 0

            p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
            with p_col2:
                page_options = [f"Stranica {i+1} od {total_pages} (Slike {i*IMAGES_PER_PAGE+1}-{min((i+1)*IMAGES_PER_PAGE, total_images)})" for i in range(total_pages)]
                selected_page_str = st.selectbox("Navigacija po stranicama", page_options, index=st.session_state.current_page, label_visibility="collapsed")
                new_page_idx = page_options.index(selected_page_str)
                if new_page_idx != st.session_state.current_page:
                    st.session_state.current_page = new_page_idx
                    st.rerun()

            st.write("")

            start_idx = st.session_state.current_page * IMAGES_PER_PAGE
            end_idx = min(start_idx + IMAGES_PER_PAGE, total_images)
            page_resources = image_resources[start_idx:end_idx]

            cols = st.columns(3)
            for index, res in enumerate(page_resources):
                col_idx = index % 3
                img_url = res["secure_url"]
                
                with cols[col_idx]:
                    st.image(img_url, use_container_width=True)
                    st.markdown(f"<a href='{img_url}' target='_blank' class='download-link' style='background: rgba(255,255,255,0.8); border-radius: 4px; margin-bottom: 5px;'>Preuzmi sliku</a>", unsafe_allow_html=True)
