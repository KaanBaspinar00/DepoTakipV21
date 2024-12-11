# pages/1_Admin.py

import streamlit as st
import pandas as pd
import os
import json

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

if st.session_state["role"] != "admin":
    st.error("Bu sayfaya erişim izniniz yok!")
    st.stop()




# File name for the stock data
file_name = "Ürün_Stok.xlsx"

# Load existing data or create a new DataFrame if the file doesn't exist
if os.path.exists(file_name):
    stock_data = pd.read_excel(file_name)
    if "Uyarı" not in stock_data.columns:
        stock_data["Uyarı"] = 0
else:
    stock_data = pd.DataFrame(columns=["Ürün Adı", "Gönderen", "Alan", "Miktar", "Birim", "Uyarı"])
    stock_data["Uyarı"] = 0

st.title("Stok Takip Programı - Admin Paneli")

# Create tabs for different admin functionalities
tab1, tab2 = st.tabs(["Stok İşlemleri", "Uyarı Belirle"])

# ---------------------- Tab 1: Stok İşlemleri ---------------------- #
with tab1:
    with st.sidebar:
        st.header("Ürün Girişi")

        # Inputs for stock entry
        ürün_adi = st.selectbox("Ürün Adı", options=["Ürün A", "Ürün B", "Ürün C"])
        gönderen = st.selectbox("Gönderen", options=["Gönderen 1", "Gönderen 2", "Gönderen 3"])
        alan = st.selectbox("Alan", options=["Alan 1", "Alan 2", "Depo"])
        miktar = st.number_input("Miktar", step=0.1, format="%.2f")
        birim = st.radio("Birim", options=["kg", "metre", "adet"])
        uyari_miktari = st.number_input("Uyarı Miktarı", step=0.1, format="%.2f")

        # Save button
        if st.button("Kaydet"):
            # Check if the same Ürün Adı, Gönderen, Alan, and Birim already exist
            existing_row = stock_data[(stock_data["Ürün Adı"] == ürün_adi) &
                                       (stock_data["Gönderen"] == gönderen) &
                                       (stock_data["Alan"] == alan) &
                                       (stock_data["Birim"] == birim)]

            if not existing_row.empty:
                # Update the Miktar in the existing row
                stock_data.loc[existing_row.index, "Miktar"] += miktar
                stock_data.loc[existing_row.index, "Uyarı"] = uyari_miktari
            else:
                # Append new data to the DataFrame
                new_data = {"Ürün Adı": ürün_adi, "Gönderen": gönderen, "Alan": alan, "Miktar": miktar, "Birim": birim, "Uyarı": uyari_miktari}
                stock_data = pd.concat([stock_data, pd.DataFrame([new_data])], ignore_index=True)

            # Save to Excel
            stock_data.to_excel(file_name, index=False)

            st.success("Veri başarıyla kaydedildi!")

    # Filter section
    st.sidebar.header("Filtreleme")
    filtered_data = stock_data.copy()

    if not stock_data.empty:
        # Filter by Ürün Adı
        ürün_filter = st.sidebar.multiselect("Ürün Adı Filtrele", options=stock_data["Ürün Adı"].unique())
        if ürün_filter:
            filtered_data = filtered_data[filtered_data["Ürün Adı"].isin(ürün_filter)]

        # Filter by Gönderen
        gönderen_filter = st.sidebar.multiselect("Gönderen Filtrele", options=stock_data["Gönderen"].unique())
        if gönderen_filter:
            filtered_data = filtered_data[filtered_data["Gönderen"].isin(gönderen_filter)]

        # Filter by Alan
        alan_filter = st.sidebar.multiselect("Alan Filtrele", options=stock_data["Alan"].unique())
        if alan_filter:
            filtered_data = filtered_data[filtered_data["Alan"].isin(alan_filter)]

        # Filter by Birim
        birim_filter = st.sidebar.multiselect("Birim Filtrele", options=stock_data["Birim"].unique())
        if birim_filter:
            filtered_data = filtered_data[filtered_data["Birim"].isin(birim_filter)]

    # Display the stock data on the main page
    st.header("Mevcut Stok Verileri")

    if not filtered_data.empty:
        # Add highlighting for rows where Miktar < Uyarı
        def highlight_row(row):
            if row["Miktar"] < row["Uyarı"]:
                return ["background-color: yellow"] * len(row)
            return [""] * len(row)

        styled_data = filtered_data.style.apply(highlight_row, axis=1)
        st.dataframe(styled_data, use_container_width=True)
    else:
        st.info("Seçilen filtrelere uygun veri bulunmamaktadır.")

# ---------------------- Tab 2: Uyarı Belirle ---------------------- #
with tab2:
    st.header("Uyarı Değerlerini Düzenle")

    if stock_data.empty:
        st.info("Stok verisi bulunmamaktadır.")
    else:
        st.write("Aşağıdaki tabloda 'Uyarı' sütununu istediğiniz gibi güncelleyebilirsiniz. Değişiklikleri yaptıktan sonra 'Güncelle' butonuna tıklayın.")

        # Use data_editor to allow editing. Specify column configs to make only "Uyarı" column editable
        edited_data = st.data_editor(
            stock_data,
            column_config={
                "Uyarı": st.column_config.NumberColumn("Uyarı", step=0.1, format="%.2f"),
            },
            disabled=["Ürün Adı", "Gönderen", "Alan", "Miktar", "Birim"],  # Make other columns read-only if desired
            use_container_width=True
        )

        if st.button("Güncelle"):
            # Update the stock_data with edited_data
            # Here we assume user only changed Uyarı column since others are disabled.
            stock_data["Uyarı"] = edited_data["Uyarı"]
            stock_data.to_excel(file_name, index=False)
            st.success("Uyarı değerleri başarıyla güncellendi!")
