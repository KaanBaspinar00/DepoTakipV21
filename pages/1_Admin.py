import streamlit as st
import pandas as pd
import os
import yaml
import uuid
import time

# Load user roles from roles.yaml
with open("roles.yaml", "r") as file:
    roles = yaml.safe_load(file)

TOKEN_EXPIRY = 3600  # seconds (1 hour)

if "token_store" not in st.session_state:
    st.session_state["token_store"] = {}

def authenticate_user(username, password):
    users = roles["roles"]["users"]
    if username in users and users[username]["password"] == password:
        return True
    return False

def get_user_role(username):
    return roles["roles"]["users"][username]["role"]

def login_user(username):
    token = str(uuid.uuid4())
    st.session_state["token_store"][token] = {
        "username": username,
        "expires": time.time() + TOKEN_EXPIRY
    }
    # Set token via st.query_params
    st.query_params = {"token": token}
    return token

def validate_token(token):
    token_info = st.session_state["token_store"].get(token)
    if token_info and time.time() < token_info["expires"]:
        return token_info["username"]
    else:
        if token in st.session_state["token_store"]:
            del st.session_state["token_store"][token]
        return None

def logout_user():
    params = st.query_params
    token = params.get("token")
    if token and token in st.session_state["token_store"]:
        del st.session_state["token_store"][token]
    # Clear query parameters
    st.query_params = {}

# Retrieve current token from query params
params = st.query_params
token = params.get("token")

username = None
if token:
    username = validate_token(token)

if username:
    # User is authenticated
    user_role = get_user_role(username)
    if user_role != "admin":
        st.error("Bu sayfaya erişim izniniz yok!")
        if st.button("Çıkış Yap"):
            logout_user()
            st.experimental_rerun()
        st.stop()

    # Add logout button in sidebar
    if st.sidebar.button("Çıkış Yap"):
        logout_user()
        st.experimental_rerun()

    file_name = "Ürün_Stok.xlsx"
    if os.path.exists(file_name):
        stock_data = pd.read_excel(file_name)
        if "Uyarı" not in stock_data.columns:
            stock_data["Uyarı"] = 0
    else:
        stock_data = pd.DataFrame(columns=["Ürün Adı", "Gönderen", "Alan", "Miktar", "Birim", "Uyarı"])
        stock_data["Uyarı"] = 0

    st.title("Stok Takip Programı - Admin Paneli")
    tab1, tab2 = st.tabs(["Stok İşlemleri", "Uyarı Belirle"])

    # Add "Uyarı Göster" button at the top
    show_warning = st.button("Uyarı Göster")

    def highlight_row(row):
        if show_warning:
            if row["Miktar"] == 0:
                return ["background-color: red"] * len(row)
            elif row["Miktar"] < row["Uyarı"]:
                return ["background-color: yellow"] * len(row)
        # If not showing warning or conditions not met, no highlight
        return [""] * len(row)

    with tab1:
        with st.sidebar:
            st.header("Ürün Girişi")
            ürün_adi = st.selectbox("Ürün Adı", options=[
    "50 GR 165 CM ELYAF",
    "60 GR 65 CM ELYAF",
    "60 GR 140 CM ELYAF",
    "60 GR 150 CM ELYAF",
    "60 GR 160 CM ELYAF",
    "60 GR 210 CM ELYAF",
    "60 GR 240 CM ELYAF",
    "80 GR 70 CM ELYAF",
    "80 GR 75 CM ELYAF",
    "80 GR 85 CM ELYAF",
    "100 GR 75 CM ELYAF",
    "100 GR 70 CM ELYAF",
    "100 GR 210 CM ELYAF",
    "120 GR 85 CM ELYAF",
    "120 GR 160 CM ELYAF",
    "210 GÜLLÜ JAGAR",
    "210 YILANLI JAGAR",
    "210 DİAGONAL JAGAR",
    "210 NOKTALI JAGAR",
    "210 BAKLAVA JAGAR",
    "210 ÜÇ ÇİZGİLİ JAGAR",
    "210 EKRU 3 ÇİZGİLİ BEKART",
    "210 GRİ 3 ÇİZGİLİ BEKART",
    "210 EKRU DÜZ BEKART",
    "80 GR 240 CM MİKRO",
    "80 GR 80 CM MİKRO",
    "80 GR 90 CM MİKRO",
    "80 GR 75 CM MİKRO",
    "100 GR 300 CM MİKRO",
    "100 GR 90 CM MİKRO",
    "100 GR 80 CM MİKRO",
    "100 GR 75 CM MİKRO",
    "220 CM ASTAR",
    "46 CM BASKISIZ KOLİ",
    "30 CM BASKISIZ KOLİ",
    "35 CM BASKISIZ KOLİ",
    "42 CM BASKILI KOLİ",
    "50 CM BASKILI KOLİ",
    "GÖMLEK KOLİSİ",
    "ÇARŞAF KOLİSİ",
    "DANTEL SARIM KOLİSİ",
    "220 CM ASTAR",
    "250 CM BEYAZ İP",
    "160 CM ASTAR",
    "240 CM BEYAZ İP",
    "80 CM BEYAZ İP",
    "160 CM BEYAZ İP",
    "90 CM BEYAZ İP",
    "5,5 CM ASTAR",
    "75 CM ASTAR",
    "160 CM POLY PUANTİYE",
    "80 CM POLY PUANTİYE",
    "160 CM 120 GR BEYAZ İP",
    "4,5 CM POLY PUANTİYE",
    "60 GR 70 CM TELA",
    "60 GR 80 CM TELA",
    "60 GR 160 CM TELA",
    "80 GR 160 CM TELA",
    "80 GR 80 CM TELA",
    "40 GR 160 CM TELA",
    "40 GR 120 CM TELA",
    "40 GR 90 CM TELA",
    "40 GR 67 CM TELA",
    "40 GR 80 CM TELA",
    "60 GR 65 CM TELA",
    "15 GR 75 CM TELA",
    "15 GR 80 CM TELA",
    "15 GR 210 CM TELA",
    "75 CM ASTAR",
    "80 CM ASTAR",
    "90 CM ASTAR",
    "165 CM ASTAR",
    "210 CM ASTAR",
    "60 CM ASTAR",
    "65 CM ASTAR",
    "330 CM ASTAR",
    "280 CM ASTAR",
    "300 CM ASTAR",
    "280 CM ŞEKER KASAR",
    "90 CM ŞEKER KASAR",
    "80 CM ŞEKER KASAR",
    "5,5 CM ŞEKER KASAR"
])
            gönderen = st.selectbox("Gönderen", options=["Doğa", "Jagar Naim", "Bekart", "Karesi", "Koli Halil", "Lale", "Urba", "Arzu Toprak", "Malzem", "Urba", "Pir Nakış"])
            alan = st.selectbox("Alan", options=["Depo", "Pir Nakış"])
            miktar = st.number_input("Miktar", step=0.1, format="%.2f")
            birim = st.radio("Birim", options=["kg", "metre", "adet"])
            # Removed Uyarı Miktarı input

            if st.button("Kaydet"):
                existing_row = stock_data[
                    (stock_data["Ürün Adı"] == ürün_adi) &
                    (stock_data["Gönderen"] == gönderen) &
                    (stock_data["Alan"] == alan) &
                    (stock_data["Birim"] == birim)
                ]

                if not existing_row.empty:
                    stock_data.loc[existing_row.index, "Miktar"] += miktar
                else:
                    new_data = {
                        "Ürün Adı": ürün_adi,
                        "Gönderen": gönderen,
                        "Alan": alan,
                        "Miktar": miktar,
                        "Birim": birim,
                        "Uyarı": 0
                    }
                    stock_data = pd.concat([stock_data, pd.DataFrame([new_data])], ignore_index=True)

                stock_data.to_excel(file_name, index=False)
                st.success("Veri başarıyla kaydedildi!")

        st.sidebar.header("Filtreleme")
        filtered_data = stock_data.copy()

        if not stock_data.empty:
            ürün_filter = st.sidebar.multiselect("Ürün Adı Filtrele", options=stock_data["Ürün Adı"].unique())
            if ürün_filter:
                filtered_data = filtered_data[filtered_data["Ürün Adı"].isin(ürün_filter)]

            gönderen_filter = st.sidebar.multiselect("Gönderen Filtrele", options=stock_data["Gönderen"].unique())
            if gönderen_filter:
                filtered_data = filtered_data[filtered_data["Gönderen"].isin(gönderen_filter)]

            alan_filter = st.sidebar.multiselect("Alan Filtrele", options=stock_data["Alan"].unique())
            if alan_filter:
                filtered_data = filtered_data[filtered_data["Alan"].isin(alan_filter)]

            birim_filter = st.sidebar.multiselect("Birim Filtrele", options=stock_data["Birim"].unique())
            if birim_filter:
                filtered_data = filtered_data[filtered_data["Birim"].isin(birim_filter)]

        st.header("Mevcut Stok Verileri")

        if not filtered_data.empty:
            styled_data = filtered_data.style.apply(highlight_row, axis=1)
            st.dataframe(styled_data, use_container_width=True)
        else:
            st.info("Seçilen filtrelere uygun veri bulunmamaktadır.")

    with tab2:
        st.header("Uyarı Değerlerini Düzenle")

        if stock_data.empty:
            st.info("Stok verisi bulunmamaktadır.")
        else:
            st.write("Aşağıdaki tabloda 'Uyarı' sütununu istediğiniz gibi güncelleyebilirsiniz. Değişiklikleri yaptıktan sonra 'Güncelle' butonuna tıklayın.")

            # Show highlighted dataframe above the editor
            styled_full = stock_data.style.apply(highlight_row, axis=1)
            st.dataframe(styled_full, use_container_width=True)

            edited_data = st.data_editor(
                stock_data,
                column_config={
                    "Uyarı": st.column_config.NumberColumn("Uyarı", step=0.1, format="%.2f"),
                },
                disabled=["Ürün Adı", "Gönderen", "Alan", "Miktar", "Birim"],
                use_container_width=True
            )

            if st.button("Güncelle"):
                stock_data["Uyarı"] = edited_data["Uyarı"]
                stock_data.to_excel(file_name, index=False)
                st.success("Uyarı değerleri başarıyla güncellendi!")
else:
    # Not authenticated
    st.title("Giriş Yap")
    form = st.form("login_form")
    input_user = form.text_input("Kullanıcı Adı")
    input_pass = form.text_input("Şifre", type="password")
    submit = form.form_submit_button("Giriş")

    if submit:
        if authenticate_user(input_user, input_pass):
            token = login_user(input_user)
            st.success("Giriş başarılı, sayfa yenileniyor...")
            st.rerun()
        else:
            st.error("Geçersiz kullanıcı adı veya şifre!")
