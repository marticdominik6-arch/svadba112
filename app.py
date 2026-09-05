import os
import re
import streamlit as st

# Postavke stranice preko cijelog ekrana
st.set_page_config(page_title="Galerija Vjenčanja", layout="wide")

# Ugrađeni CSS stilovi (pozadina, fontovi, centriranje i izgled gumba)
st.markdown(
    """
    <style>
    /* Pozadina cijele aplikacije */
    .stApp {
        background-color: #faf7f5;
    }
    
    /* Stil naslova */
    h1 {
        text-align: center;
        color: #4a3b32;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    p {
        text-align: center;
        color: #7c6f64;
        font-size: 1.1rem;
    }

    /* Okviri i stil kartica slika */
    div[data-testid="stImage"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
        background-color: white;
    }
    div[data-testid="stImage"]:hover {
        transform: translateY(-4px);
    }

    /* Prilagodba gumba za preuzimanje da prate temu */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #f0eae1;
        color: #4a3b32;
        border: 1px solid #dcd3cb;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #4a3b32;
        color: white;
        border-color: #4a3b32;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("❤️ Galerija Vjenčanja ❤️")
st.write(
    "Dobrodošli u našu galeriju! Ovdje možete pregledavati i preuzimati uspomene s našeg vjenčanja."
)
st.divider()

# Putanja do novog foldera na GitHubu
IMAGE_FOLDER = "galerija1"


@st.cache_data
def get_local_images():
  if not os.path.exists(IMAGE_FOLDER):
    return []

  # Podržani formati slika
  valid_extensions = (".jpg", ".jpeg", ".png", ".webp")

  # Dohvati sve datoteke iz foldera
  images = [
      f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(valid_extensions)
  ]

  # Pametno sortiranje po brojevima u imenu (npr. slika (1), slika (2)...)
  images.sort(
      key=lambda x: [
          int(s) if s.isdigit() else s for s in re.split(r"(\d+)", x)
      ]
  )
  return images


# Učitaj listu slika
image_files = get_local_images()

if not image_files:
  st.warning(
      f"⚠️ Trenutno nema slika u folderu '{IMAGE_FOLDER}' na GitHubu. Molimo"
      " dodajte slike u repozitorij."
  )
else:
  # Paginacija (prikazuje 60 slika po stranici radi brzine i stabilnosti)
  IMAGES_PER_PAGE = 60
  total_images = len(image_files)
  total_pages = (total_images - 1) // IMAGES_PER_PAGE + 1

  # Izbor stranice na vrhu
  col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
  with col_p2:
    page = st.selectbox(
        "Odabir stranice galerije:",
        range(1, total_pages + 1),
        format_func=lambda x: f"Stranica {x} od {total_pages}",
    )

  # Izračun indeksa za trenutnu stranicu
  start_idx = (page - 1) * IMAGES_PER_PAGE
  end_idx = min(start_idx + IMAGES_PER_PAGE, total_images)
  current_page_images = image_files[start_idx:end_idx]

  st.markdown(
      f"<p style='text-align: center; font-size: 0.95rem; color: #8c8278;'>Prikazuje"
      f" se {start_idx + 1} - {end_idx} od ukupno {total_images} slika</p>",
      unsafe_allow_html=True,
  )
  st.markdown("<br>", unsafe_allow_html=True)

  # Prikaz slika u 3 stupca
  cols = st.columns(3)
  for index, img_name in enumerate(current_page_images):
    col_idx = index % 3
    img_path = os.path.join(IMAGE_FOLDER, img_name)

    with cols[col_idx]:
      # Prikaz slike iz lokalnog repozitorija
      st.image(img_path, use_container_width=True)

      # Gumb za preuzimanje slike na uređaj
      with open(img_path, "rb") as file:
        st.download_button(
            label="⬇️ Preuzmi sliku",
            data=file,
            file_name=img_name,
            mime="image/webp",  # Ako su slike u WebP formatu
            key=f"dl_{img_name}",
        )
      st.markdown(
          "<br>", unsafe_allow_html=True
      )  # Razmak između redova kartica
