import streamlit as st
from PIL import Image
from io import BytesIO
from streamlit_image_coordinates import streamlit_image_coordinates 

# --- KONFIGURASI HALAMAN
# Layout wide memberikan ruang maksimum
st.set_page_config(layout="wide", page_title="Hybrid Color Picker - Sticky Control")
st.title("Color Picker: Interaktif & Manual Koordinator")

# --- INISIALISASI SESSION STATE
if 'images_data' not in st.session_state:
    st.session_state.images_data = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'selected_x' not in st.session_state:
    st.session_state.selected_x = None
if 'selected_y' not in st.session_state:
    st.session_state.selected_y = None

# --- KONVERSI RGB KE HEX
def _from_rgb(rgb):
    """Konversi tuple RGB ke string Hex."""
    if len(rgb) == 4:
        rgb = rgb[:3]
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

# --- LOGIKA PENGAMBILAN & PEMROSESAN WARNA
def get_color_at_coord(img_bytes, x, y):
    """Buka gambar, ambil warna di koordinat (x, y)."""
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        owidth, oheight = img.size
        
        # Koordinat harus integer
        x_int = int(x)
        y_int = int(y)
        
        if 0 <= x_int < owidth and 0 <= y_int < oheight:
            pixs = img.getpixel((x_int, y_int))
            hex_color = _from_rgb(pixs)
            return pixs, hex_color
        else:
            return None, None
    except Exception:
        return None, None

# --- FUNGSI UTAMA TAMPILAN
def show_current_image():
    if not st.session_state.images_data:
        # Tampilkan instruksi di sidebar jika belum ada gambar
        with st.sidebar:
            st.info("Silakan unggah gambar di bawah.")
        return

    # Ambil data gambar yang sedang aktif
    idx = st.session_state.current_index
    filename, img_bytes = st.session_state.images_data[idx]
    img_pil = Image.open(BytesIO(img_bytes)).convert("RGB")
    owidth, oheight = img_pil.size
    
    # --- KONTROL DIPINDAH KE SIDEBAR (STICKY) ---
    with st.sidebar:
        st.markdown(f"**Gambar Saat Ini:** `{filename}`")
        
        # 1. NAVIGASI GAMBAR
        st.markdown("#### Navigasi Gambar")
        nav_col1, nav_col2 = st.columns(2)
        
        if nav_col1.button("⬅️ Prev", disabled=idx == 0):
            st.session_state.current_index = (idx - 1) % len(st.session_state.images_data)
            st.session_state.selected_x = None
            st.session_state.selected_y = None
            st.rerun() 
            
        if nav_col2.button("Next ➡️", disabled=idx == len(st.session_state.images_data) - 1):
            st.session_state.current_index = (idx + 1) % len(st.session_state.images_data)
            st.session_state.selected_x = None
            st.session_state.selected_y = None
            st.rerun() 

        # 2. PEMROSESAN KOORDINAT & TAMPILKAN HASIL WARNA
        st.divider()
        
        # Dapatkan koordinat dari klik interaktif yang tersimpan
        value_from_main = st.session_state.get('last_clicked_coord')
        
        # LOGIKA UPDATE STATE DENGAN KOORDINAT BARU DARI KLIK INTERAKTIF
        if value_from_main and ('x' in value_from_main and 'y' in value_from_main):
            # Koordinat dari komponen sudah disesuaikan ke resolusi gambar asli
            clicked_x = int(value_from_main['x'])
            clicked_y = int(value_from_main['y'])
            
            # Cek jika koordinat benar-benar berubah (lebih stabil)
            if clicked_x != st.session_state.selected_x or clicked_y != st.session_state.selected_y:
                st.session_state.selected_x = clicked_x
                st.session_state.selected_y = clicked_y
                # Kita tidak memanggil st.rerun() di sini; biarkan logika di bawah yang memanggil

        # Tampilkan hasil warna
        if st.session_state.selected_x is not None and st.session_state.selected_y is not None:
            final_x = st.session_state.selected_x
            final_y = st.session_state.selected_y
            
            rgb, hex_color = get_color_at_coord(img_bytes, final_x, final_y)

            if rgb:
                st.subheader("Hasil Warna Terpilih")
                
                st.markdown(f"**Koordinat:** `X: {final_x}, Y: {final_y}`")
                st.text_input("RGB", str(rgb), disabled=True)
                st.text_input("HEX", str(hex_color), disabled=True)

                # Tampilkan kotak warna
                st.markdown(
                    f"""
                    <div style='background-color: {hex_color}; width: 100px; height: 100px; border: 3px solid #ccc; border-radius: 5px; margin-top: 10px;'></div>
                    """,
                    unsafe_allow_html=True
                )
            
        else:
            st.info("Pilih titik di gambar utama.")


        # 3. INPUT KOORDINAT MANUAL (DIPINDAH KE BAWAH HASIL WARNA)
        st.divider()
        st.subheader("3. Input Koordinat Manual")
        
        default_x = st.session_state.selected_x if st.session_state.selected_x is not None else 0
        default_y = st.session_state.selected_y if st.session_state.selected_y is not None else 0
        
        with st.form("manual_coord_form"):
            x_col_form, y_col_form = st.columns(2)
            
            x_input = x_col_form.number_input("X Koord. (0 - {})".format(owidth - 1), 
                                          min_value=0, max_value=owidth - 1, step=1, 
                                          value=default_x, key="x_entry")
            y_input = y_col_form.number_input("Y Koord. (0 - {})".format(oheight - 1), 
                                          min_value=0, max_value=oheight - 1, step=1, 
                                          value=default_y, key="y_entry")
            
            if st.form_submit_button("Ambil Warna (Go)"):
                st.session_state.selected_x = x_input
                st.session_state.selected_y = y_input
                st.rerun() 
    
    # --- KOLOM UTAMA (GAMBAR INTERAKTIF) ---

    st.markdown(f"### 1. Pilih Warna Secara Interaktif (Klik)")
    st.markdown(f"Ukuran Asli: **{owidth}x{oheight}**. Gambar diatur ke **Max Width 700px** untuk stabilitas koordinat.")
    
    # [PERBAIKAN CSS] Injeksi CSS untuk membatasi lebar gambar di badan utama
    st.markdown("""
        <style>
            /* Menargetkan div yang membungkus st.image di komponen interaktif */
            .element-container img {
                max-width: 700px !important; 
                width: auto !important;
                height: auto;
            }
        </style>
        """, unsafe_allow_html=True)
        
    # PENSKALAAN DENGAN LEBAR OTOMATIS KOLOM (tanpa parameter width)
    # Ini harusnya lebih akurat karena Streamlit/Komponen yang menangani scaling.
    value = streamlit_image_coordinates(
        img_pil, 
        key=f"image_coord_{idx}",
        # width=700 DIHAPUS, diganti dengan CSS injection di atas
    )
    
    # Simpan hasil klik ke state temporer untuk diproses di sidebar
    st.session_state.last_clicked_coord = value
    
    # Jika ada klik baru yang terdeteksi, panggil rerun agar sidebar menampilkan hasil
    if value is not None and ('x' in value and 'y' in value):
        current_x = int(value.get('x'))
        current_y = int(value.get('y'))
        
        # Panggil rerun hanya jika koordinat yang baru terdeteksi berbeda dengan yang sedang ditampilkan
        if current_x != st.session_state.selected_x or current_y != st.session_state.selected_y:
            st.rerun()


# --- BAGIAN UPLOADER (DIPINDAH KE PALING BAWAH SIDEBAR)
with st.sidebar:
    st.divider()
    uploaded_files = st.file_uploader(
        "Open Images (Upload file/Multiple files)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        current_names = [data[0] for data in st.session_state.images_data]
        uploaded_names = [file.name for file in uploaded_files]
        
        if uploaded_names != current_names or not st.session_state.images_data:
            
            new_images_data = []
            for uploaded_file in uploaded_files:
                new_images_data.append((uploaded_file.name, uploaded_file.getvalue()))
                
            st.session_state.images_data = new_images_data
            st.session_state.current_index = 0
            st.session_state.selected_x = None
            st.session_state.selected_y = None
            st.rerun() 

# --- TAMPILKAN APLIKASI
show_current_image()
