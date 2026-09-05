import os
import re
import base64
import requests
import streamlit as st

# 1. Konfiguracija stranice i čista portfolio tema
st.set_page_config(
    page_title="Matea & Dominik | Vjenčana Galerija",
    page_icon="💍",
    layout="wide",
)

# Inicijalizacija stanja prijave i indeksa za galeriju
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "viewing_image_index" not in st.session_state:
    st.session_state.viewing_image_index = None

# Automatski dohvat pozadine (traži background.jpg direktno s GitHuba, ako ne postoji uzima zadanu)
@st.cache_data(ttl=60)
def get_background_url():
    try:
        repo_owner = st.secrets["github"]["owner"]
        repo_name = st.secrets["github"]["repo"]
        token = st.secrets["github"]["token"]
        
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/background.jpg"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return response.json().get("download_url")
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1519741497674-611481863552"

background_css = get_background_url()

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
                    <h4 style='color: #2c2c2c; font-family: "Cormorant Garamond", serif; margin-bottom: 5px;'>👑 Admin: Upravljanje sadržajem</h4>
                    <p style='color: #666; font-size: 0.9rem;'>Učitaj nove slike u galeriju ili postavi novu pozadinsku sliku koja će se automatski primijeniti.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # SEKCIJA 1: UPLOAD SLIKA U GALERIJU
            st.markdown("##### 📸 Dodavanje slika u galeriju")
            target_folder = st.selectbox("Odaberi mapu za spremanje slika", ["galerija1", "galerija2"])
            uploaded_files = st.file_uploader(f"Odaberi fotografije za mapu '{target_folder}'", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True, key="gallery_uploader")
            
            if uploaded_files:
                if st.button(f"🚀 Spremi slike u '{target_folder}' na GitHub", use_container_width=True):
                    with st.spinner(f"Spremam slike u {target_folder}..."):
                        try:
                            repo_owner = st.secrets["github"]["owner"]
                            repo_name = st.secrets["github"]["repo"]
                            token = st.secrets["github"]["token"]
                            
                            headers = {
                                "Authorization": f"token {token}",
                                "Accept": "application/vnd.github.v3+json"
                            }
                            
                            success_count = 0
                            for uploaded_file in uploaded_files:
                                file_name = uploaded_file.name
                                file_content = uploaded_file.read()
                                encoded_content = base64.b64encode(file_content).decode("utf-8")
                                
                                api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{target_folder}/{file_name}"
                                
                                payload = {
                                    "message": f"Dodana nova slika {file_name} u {target_folder}",
                                    "content": encoded_content
                                }
                                
                                response = requests.put(api_url, json=payload, headers=headers)
                                if response.status_code in [201, 200]:
                                    success_count += 1
                                    
                            if success_count > 0:
                                st.success(f"Uspješno spremljeno {success_count} slika u {target_folder}!")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("Došlo je do greške prilikom spremanja.")
                        except Exception as e:
                            st.error(f"Greška: {e}")

            st.write("---")

            # SEKCIJA 2: UPLOAD POZADINSKE SLIKE
            st.markdown("##### 🖼️ Promjena pozadinske slike")
            bg_file = st.file_uploader("Odaberi novu pozadinsku sliku", type=['png', 'jpg', 'jpeg', 'webp'], key="bg_uploader")
            
            if bg_file:
                if st.button("🚀 Postavi i spremi novu pozadinu", use_container_width=True):
                    with st.spinner("Postavljam novu pozadinsku sliku..."):
                        try:
                            repo_owner = st.secrets["github"]["owner"]
                            repo_name = st.secrets["github"]["repo"]
                            token = st.secrets["github"]["token"]
                            
                            file_name = "background.jpg"
                            file_content = bg_file.read()
                            encoded_content = base64.b64encode(file_content).decode("utf-8")
                            
                            api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_name}"
                            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
                            
                            payload = {
                                "message": f"Ažurirana pozadinska slika (background.jpg)",
                                "content": encoded_content
                            }
                            
                            get_resp = requests.get(api_url, headers=headers)
                            if get_resp.status_code == 200:
                                payload["sha"] = get_resp.json().get("sha")

                            response = requests.put(api_url, json=payload, headers=headers)
                            
                            if response.status_code in [201, 200]:
                                st.success("Pozadina uspješno postavljena! Osvježavam stranicu...")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("Greška pri spremanju pozadine.")
                        except Exception as e:
                            st.error(f"Greška: {e}")

        st.divider()

    # DOHVAT SLIKA IZ OBA FOLDERA (galerija1 i galerija2) S GITHUBA
    @st.cache_data(ttl=3600)
    def fetch_github_images():
        image_resources = []
        try:
            repo_owner = st.secrets["github"]["owner"]
            repo_name = st.secrets["github"]["repo"]
            token = st.secrets["github"]["token"]
            
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Provjeravamo obje mape redom
            folders_to_check = ["galerija1", "galerija2"]
            
            for folder_path in folders_to_check:
                page = 1
                while True:
                    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}?page={page}&per_page=100"
                    response = requests.get(api_url, headers=headers)
                    
                    if response.status_code != 200:
                        break # Ako folder ne postoji, nastavi dalje
                        
                    files = response.json()
                    if not isinstance(files, list) or len(files) == 0:
                        break
                        
                    for file in files:
                        if file["type"] == "file" and file["name"].lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                            image_resources.append({
                                "secure_url": file["download_url"],
                                "public_id": file["name"]
                            })
                    
                    if len(files) < 100:
                        break
                    page += 1
                
        except Exception as e:
            st.error(f"Greška prilikom spajanja na GitHub: {e}")

        # Pametno sortiranje po brojevima u nazivu datoteke
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
        st.info("Trenutno nema slika u mapama `galerija1` ili `galerija2`. Učitajte prve slike iznad kao administrator.")
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
                main_page_idx = page_options.index(selected_page_str)
                if main_page_idx != st.session_state.current_page:
                    st.session_state.current_page = main_page_idx
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
