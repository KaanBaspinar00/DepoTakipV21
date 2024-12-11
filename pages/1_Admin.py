import streamlit as st
import pandas as pd
import os
import yaml

# Load user roles from roles.yaml
with open("roles.yaml", "r") as file:
    roles = yaml.safe_load(file)

def authenticate_user(username, password):
    users = roles["roles"]["users"]
    if username in users and users[username]["password"] == password:
        return True
    return False

def get_user_role(username):
    return roles["roles"]["users"][username]["role"]

def login_user(username):
    # Instead of a token, store username and a logged_in flag
    st.query_params = {"username": username, "logged_in": "true"}

def logout_user():
    st.query_params = {}  # Clears query params, forcing re-login on refresh

# Check query params
params = st.query_params
logged_in = params.get("logged_in")
username = params.get("username")

if logged_in == "true" and username:
    # User is considered authenticated
    user_role = get_user_role(username)
    if user_role != "admin":
        st.error("Bu sayfaya erişim izniniz yok!")
        if st.button("Çıkış Yap"):
            logout_user()
            st.rerun()
        st.stop()

    # Logout button for admin
    if st.sidebar.button("Çıkış Yap"):
        logout_user()
        st.rerun()

    # At this point, user is authenticated as admin
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

    with tab1:
        with st.sidebar:
            st.header("Ürün Girişi")
            ürün_adi = st.selectbox("Ürün Adı", options=["Ürün A", "Ürün B", "Ürün C"])
            gönderen = st.selectbox("Gönderen", options=["Gönderen 1", "Gönderen 2", "Gönderen 3"])
            alan = st.selectbox("Alan", options=["Alan 1", "Alan 2", "Depo"])
            miktar = st.number_input("Miktar", step=0.1, format="%.2f")
            birim = st.radio("Birim", options=["kg", "metre", "adet"])
            uyari_miktari = st.number_input("Uyarı Miktarı", step=0.1, format="%.2f")

            if st.button("Kaydet"):
                existing_row = stock_data[
                    (stock_data["Ürün Adı"] == ürün_adi) &
                    (stock_data["Gönderen"] == gönderen) &
                    (stock_data["Alan"] == alan) &
                    (stock_data["Birim"] == birim)
                ]

                if not existing_row.empty:
                    stock_data.loc[existing_row.index, "Miktar"] += miktar
                    stock_data.loc[existing_row.index, "Uyarı"] = uyari_miktari
                else:
                    new_data = {
                        "Ürün Adı": ürün_adi,
                        "Gönderen": gönderen,
                        "Alan": alan,
                        "Miktar": miktar,
                        "Birim": birim,
                        "Uyarı": uyari_miktari
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
            def highlight_row(row):
                if row["Miktar"] < row["Uyarı"]:
                    return ["background-color: yellow"] * len(row)
                return [""] * len(row)

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
            login_user(input_user)
            st.success("Giriş başarılı, sayfa yenileniyor...")
            st.rerun()
        else:
            st.error("Geçersiz kullanıcı adı veya şifre!")
