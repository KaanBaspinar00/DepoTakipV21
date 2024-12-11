# pages/2_Çalışan.py

import streamlit as st
import pandas as pd
import os
from pyzbar.pyzbar import decode
from PIL import Image
import yaml
import yaml
import streamlit as st

# Load user roles from roles.yaml
with open("roles.yaml", "r") as file:
    roles = yaml.safe_load(file)

def authenticate_user(username, password):
    """
    Check if the username exists and the password matches.
    """
    if username in roles["users"]:
        return roles["users"][username]["password"] == password
    return False

def get_user_role(username):
    """
    Return the role of the authenticated user.
    """
    if username in roles["users"]:
        return roles["users"][username]["role"]
    return None

# Check if the user is already authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Display login form
    st.title("Giriş Yap")

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş"):
        if authenticate_user(username, password):
            st.success(f"Hoşgeldiniz, {username}!")
            user_role = get_user_role(username)
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user_role
        else:
            st.error("Geçersiz kullanıcı adı veya şifre!")

# Restrict access to authenticated users
if not st.session_state["authenticated"]:
    st.stop()

# File name for the stock data
file_name = "Ürün_Stok.xlsx"

# Load existing data or create a new DataFrame if the file doesn't exist
if os.path.exists(file_name):
    stock_data = pd.read_excel(file_name)
    if "Uyarı" not in stock_data.columns:
        stock_data["Uyarı"] = 0
else:
    st.error("Stok verisi bulunamadı! Lütfen admin tarafından verileri giriniz.")
    stock_data = pd.DataFrame(columns=["Ürün Adı", "Gönderen", "Alan", "Miktar", "Birim", "Uyarı"])
    stock_data["Uyarı"] = 0

# Streamlit page configuration

# Title of the worker panel
st.title("Stok Takip Programı - Çalışan Paneli")

# Camera-based QR Code Scanner
st.header("QR Kod ile İşlem")
st.write("Kamera otomatik olarak açılacaktır. Lütfen QR kodu taratın.")
camera_image = st.camera_input("Kamera")

if camera_image:
    # Convert the captured image to a PIL image
    img = Image.open(camera_image)

    # Decode the QR code from the image
    decoded_objects = decode(img)

    if decoded_objects:
        # Assume the first QR code in the image
        qr_code = decoded_objects[0].data.decode("utf-8")
        st.success(f"QR Kod Tespit Edildi: {qr_code}")

        # Search for the asset with the matching QR code
        matching_asset = stock_data[stock_data['Ürün Adı'] == qr_code]

        if matching_asset.empty:
            st.error("Bu QR koduna ait bir stok bulunamadı.")
        else:
            # Display the matching asset details
            st.subheader("Seçilen Stok Detayları")
            st.dataframe(matching_asset)

            # Input for how much the worker will use
            kullanilacak_miktar = st.number_input("Kullanılacak Miktar", step=0.1, format="%.2f")

            if st.button("Onayla ve Kaydet"):
                # Check if there is enough stock
                if kullanilacak_miktar > matching_asset.iloc[0]["Miktar"]:
                    st.error("Yetersiz stok! Daha az bir miktar giriniz.")
                else:
                    # Deduct the used amount from the stock
                    stock_data.loc[matching_asset.index[0], "Miktar"] -= kullanilacak_miktar

                    # Save to Excel
                    stock_data.to_excel(file_name, index=False)

                    st.success("İşlem başarıyla kaydedildi ve stok güncellendi!")
    else:
        st.error("QR kod tespit edilemedi. Lütfen doğru bir QR kod gösterdiğinizden emin olun.")

# Display the stock data
st.header("Mevcut Stok Verileri")
if not stock_data.empty:
    # Add highlighting for rows where Miktar < Uyarı
    def highlight_row(row):
        if row["Miktar"] < row["Uyarı"]:
            return ["background-color: yellow"] * len(row)
        return [""] * len(row)

    styled_data = stock_data.style.apply(highlight_row, axis=1)
    st.dataframe(styled_data, use_container_width=True)
else:
    st.info("Stok verisi bulunmamaktadır.")


