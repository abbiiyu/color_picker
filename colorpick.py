import streamlit as st
from PIL import Image
from io import BytesIO
from streamlit_image_coordinates import streamlit_image_coordinates

# ---------- CONFIG ----------
st.set_page_config(layout="wide", page_title="Color Picker Final", page_icon="🎨")

# ---------- STATE ----------
if "selected_x" not in st.session_state:
    st.session_state.selected_x = None
if "selected_y" not in st.session_state:
    st.session_state.selected_y = None
if "last_click" not in st.session_state:
    st.session_state.last_click = None
if "img_bytes" not in st.session_state:
    st.session_state.img_bytes = None

# ---------- UTIL ----------
def rgb_to_hex(rgb):
    if len(rgb) == 4:
        rgb = rgb[:3]
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

def get_color_from_bytes(img_bytes, x, y):
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    w, h = img.size
    x = int(x); y = int(y)
    if 0 <= x < w and 0 <= y < h:
        px = img.getpixel((x, y))
        return px, rgb_to_hex(px)
    return None, None

def make_highlight_image(img, x, y, radius=4, color=(255,0,0)):
    img2 = img.copy()
    w,h = img2.size
    x0 = max(0, x-radius); x1 = min(w-1, x+radius)
    y0 = max(0, y-radius); y1 = min(h-1, y+radius)
    for i in range(x0, x1+1):
        for j in range(y0, y1+1):
            img2.putpixel((i,j), color)
    return img2

# ---------- UI ----------
st.title("🎨 Color Picker — Fix (No crop) + Manual Coordinate Input")
st.write("Upload gambar, klik untuk ambil warna, atau masukkan koordinat X/Y manual (koordinat original).")

uploaded = st.file_uploader("Upload gambar (PNG/JPG)", type=["png","jpg","jpeg"])

if uploaded:
    st.session_state.img_bytes = uploaded.getvalue()
    img = Image.open(BytesIO(st.session_state.img_bytes)).convert("RGB")
    ow, oh = img.size

    # tentukan batas tampilan supaya TIDAK ter-crop
    MAX_W = 1000   # maksimal lebar tampilan (px)
    MAX_H = 700    # maksimal tinggi tampilan (px)
    ratio = min(1.0, MAX_W / ow, MAX_H / oh)  # scale agar muat dalam kotak W x H
    display_w = int(ow * ratio)
    display_h = int(oh * ratio)

    st.caption(f"Ukuran asli: {ow} × {oh}  —  Tampilan: {display_w} × {display_h}")

    cols = st.columns([3, 1])  # kiri: gambar, kanan: kontrol ringkas
    with cols[0]:
        st.markdown("**Klik / Tap pada gambar untuk memilih warna**")
        # panggil komponen: sesuaikan width & height (agar tidak crop)
        click_val = streamlit_image_coordinates(img, key="img_coord", width=display_w, height=display_h)
        # simpan last click
        if click_val and "x" in click_val and "y" in click_val:
            # click_val memberi koordinat relatif pada tampilan; convert ke original
            clicked_x = int(click_val["x"] / ratio)
            clicked_y = int(click_val["y"] / ratio)
            st.session_state.selected_x = clicked_x
            st.session_state.selected_y = clicked_y
            st.session_state.last_click = (clicked_x, clicked_y)

    with cols[1]:
        st.markdown("## Hasil & Input")
        if st.session_state.selected_x is not None and st.session_state.selected_y is not None:
            sx = st.session_state.selected_x
            sy = st.session_state.selected_y
            px, hx = get_color_from_bytes(st.session_state.img_bytes, sx, sy)
            if px:
                st.markdown("**Warna terpilih**")
                st.markdown(f"- Koordinat (original): **X = {sx} , Y = {sy}**")
                st.markdown(f"- RGB: `{px}`")
                st.markdown(f"- HEX: `{hx}`")
                st.markdown(
                    f"<div style='width:80px;height:80px;background:{hx};border-radius:10px;border:2px solid #333'></div>",
                    unsafe_allow_html=True
                )
                # tombol untuk show highlight image besar
                if st.button("Tampilkan highlight (gambar besar)"):
                    highlight = make_highlight_image(img, sx, sy, radius=5, color=(255,0,0))
                    st.image(highlight, caption="Titik klik diberi tanda merah", use_column_width=True)

        else:
            st.info("Belum ada koordinat terpilih. Klik pada gambar atau masukkan manual di bawah.")

        st.markdown("---")
        st.markdown("### Masukkan koordinat manual (original)")
        # nomor input berdasarkan ukuran asli gambar
        x_manual = st.number_input("X (0 - {})".format(ow-1), min_value=0, max_value=ow-1, value=st.session_state.selected_x or 0, step=1)
        y_manual = st.number_input("Y (0 - {})".format(oh-1), min_value=0, max_value=oh-1, value=st.session_state.selected_y or 0, step=1)
        if st.button("Go (ambil warna di koordinat)"):
            st.session_state.selected_x = int(x_manual)
            st.session_state.selected_y = int(y_manual)
            st.experimental_rerun()

    # Tampilkan informasi tambahan dibawah (opsional)
    st.markdown("---")
    st.markdown("**Catatan:** koordinat yang tampil adalah koordinat gambar *original* (bukan posisi pada tampilan yang telah diskalakan).")

else:
    st.info("Upload gambar terlebih dahulu untuk mulai.")
