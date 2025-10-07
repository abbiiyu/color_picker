import streamlit as st
from PIL import Image
from io import BytesIO
from streamlit_image_coordinates import streamlit_image_coordinates
import pandas as pd
import base64

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="Color Picker Final", page_icon="🎨")

# ---------------- STATE ----------------
if "selected_x" not in st.session_state:
    st.session_state.selected_x = None
if "selected_y" not in st.session_state:
    st.session_state.selected_y = None
if "img_bytes" not in st.session_state:
    st.session_state.img_bytes = None

# ---------------- UTIL ----------------
def rgb_to_hex(rgb):
    if len(rgb) == 4:
        rgb = rgb[:3]
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

def get_color_from_bytes(img_bytes, x, y):
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    w, h = img.size
    if 0 <= x < w and 0 <= y < h:
        px = img.getpixel((x, y))
        return px, rgb_to_hex(px)
    return None, None

def make_highlight_image(img, x, y, radius=4, color=(255,0,0)):
    img2 = img.copy()
    w, h = img2.size
    for i in range(max(0, x-radius), min(w, x+radius)):
        for j in range(max(0, y-radius), min(h, y+radius)):
            img2.putpixel((i, j), color)
    return img2

# ---------------- UI ----------------
st.title("🎨 Color Picker & Grid Warna Otomatis")
st.write("Upload gambar, klik untuk ambil warna, atau masukkan koordinat manual.")

uploaded = st.file_uploader("Upload gambar (PNG/JPG)", type=["png","jpg","jpeg"])

if uploaded:
    st.session_state.img_bytes = uploaded.getvalue()
    img = Image.open(BytesIO(st.session_state.img_bytes)).convert("RGB")
    ow, oh = img.size

    MAX_W, MAX_H = 1000, 700
    ratio = min(1.0, MAX_W / ow, MAX_H / oh)
    display_w, display_h = int(ow * ratio), int(oh * ratio)

    st.caption(f"Ukuran asli: {ow} × {oh} — Tampilan: {display_w} × {display_h}")

    cols = st.columns([3, 1])
    with cols[0]:
        st.markdown("**Klik pada gambar untuk memilih warna**")
        click_val = streamlit_image_coordinates(img, key="img_coord", width=display_w, height=display_h)
        if click_val and "x" in click_val and "y" in click_val:
            st.session_state.selected_x = int(click_val["x"] / ratio)
            st.session_state.selected_y = int(click_val["y"] / ratio)

    with cols[1]:
        st.markdown("## Hasil & Input")

        # --- Manual input ---
        x_manual = st.number_input("X (0 - {})".format(ow-1), 0, ow-1, st.session_state.selected_x or 0, step=1)
        y_manual = st.number_input("Y (0 - {})".format(oh-1), 0, oh-1, st.session_state.selected_y or 0, step=1)
        if st.button("Ambil warna di koordinat"):
            st.session_state.selected_x = int(x_manual)
            st.session_state.selected_y = int(y_manual)

        # --- Hasil warna langsung tampil ---
        if st.session_state.selected_x is not None and st.session_state.selected_y is not None:
            sx, sy = st.session_state.selected_x, st.session_state.selected_y
            px, hx = get_color_from_bytes(st.session_state.img_bytes, sx, sy)
            if px:
                st.markdown("**Warna terpilih:**")
                st.markdown(f"- Koordinat (original): **X = {sx}, Y = {sy}**")
                st.markdown(f"- RGB: `{px}`")
                st.markdown(f"- HEX: `{hx}`")
                st.markdown(
                    f"<div style='width:80px;height:80px;background:{hx};border-radius:10px;border:2px solid #333'></div>",
                    unsafe_allow_html=True
                )

                if st.button("Tampilkan highlight (gambar besar)"):
                    highlight = make_highlight_image(img, sx, sy, radius=5)
                    st.image(highlight, caption="Titik klik diberi tanda merah", use_column_width=True)
        else:
            st.info("Klik pada gambar atau masukkan koordinat manual untuk memilih warna.")

    st.markdown("---")
    st.markdown("## 🧩 Grid Warna dari Gambar")

    step = st.slider("Sampling tiap berapa pixel:", 5, 100, 25, step=5)
    img_small = img.resize((ow // step, oh // step))
    w2, h2 = img_small.size

    data = []
    for y in range(h2):
        row = []
        for x in range(w2):
            px = img_small.getpixel((x, y))
            hx = rgb_to_hex(px)
            row.append(
                f"<div style='width:40px;height:40px;background:{hx};border:1px solid #444;border-radius:6px'></div><div style='font-size:10px'>{hx}</div>"
            )
        data.append(row)

    df = pd.DataFrame(data)

    # scrollable table
    st.markdown(
        f"""
        <div style="overflow-x: auto; white-space: nowrap; padding:5px;">
            {df.to_html(escape=False, index=False)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CSV export
    csv_data = [
        {"x": x, "y": y, "RGB": str(img_small.getpixel((x, y))), "HEX": rgb_to_hex(img_small.getpixel((x, y)))}
        for y in range(h2)
        for x in range(w2)
    ]
    csv = pd.DataFrame(csv_data).to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()

    st.markdown(
        f"""
        <a href="data:file/csv;base64,{b64}" download="grid_warna.csv">
            <button style="background-color:#1f6feb;color:white;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;">
                💾 Unduh CSV warna
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )

else:
    st.info("Upload gambar terlebih dahulu untuk mulai.")
