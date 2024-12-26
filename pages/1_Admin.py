import streamlit as st
import pandas as pd
import os
import yaml
import uuid
import time
import docx
import io

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
def list_etiketler_files():
    etiketler_folder = "ETİKETLER"
    file_paths = []
    for root, _, files in os.walk(etiketler_folder):
        for file in files:
            if file.endswith(".docx"):
                file_paths.append(os.path.join(root, file))
    return file_paths

def download_file(file_path):
    with open(file_path, "rb") as f:
        return f.read()

def print_file(file_path):
    # Placeholder for actual print logic
    st.success(f"{file_path} gönderildi.")

def log_activity(action, username, details):
    """Log an activity into the activity log file."""
    log_file = "activity_log.csv"
    timestamp = time.strftime("%d/%m/%Y - %H:%M")
    new_entry = pd.DataFrame([{ "Action": action, "User": username, "Details": details, "Timestamp": timestamp }])

    if os.path.exists(log_file):
        existing_logs = pd.read_csv(log_file)
        updated_logs = pd.concat([existing_logs, new_entry], ignore_index=True)
    else:
        updated_logs = new_entry

    updated_logs.to_csv(log_file, index=False)

def show_activity_log():
    """Display the activity log in the admin panel."""
    log_file = "activity_log.csv"
    if os.path.exists(log_file):
        log_data = pd.read_csv(log_file)
        st.dataframe(log_data, use_container_width=True)
    else:
        st.info("Aktivite Bulunamadı !")

        #log_activity("Ürün Ekleme", username,
                     #f"Ürün: {ürün_adi} ; Miktar: {miktar} {birim} ; Alan: {alan} ; Kimden: {gönderen}")


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
            st.rerun()
        st.stop()

    # Add logout button in sidebar
    if st.sidebar.button("Çıkış Yap"):
        logout_user()
        st.rerun()

    file_name = "Ürün_Stok.xlsx"
    if os.path.exists(file_name):
        stock_data = pd.read_excel(file_name)
        if "Uyarı" not in stock_data.columns:
            stock_data["Uyarı"] = 0
    else:
        stock_data = pd.DataFrame(columns=["Ürün Adı", "Gönderen", "Alan", "Miktar", "Birim", "Uyarı"])
        stock_data["Uyarı"] = 0

    # Add "Uyarı Göster" button at the top


    def highlight_row(row):
        if show_warning:
            if row["Miktar"] == 0:
                return ["background-color: red"] * len(row)
            elif row["Miktar"] < row["Uyarı"]:
                return ["background-color: yellow"] * len(row)
        # If not showing warning or conditions not met, no highlight
        return [""] * len(row)

    tab1, tab2, tab3, tab4 = st.tabs(["Stok İşlemleri", "Uyarı Belirle", "Etiketler", "Aktiviteler"])
    show_warning = st.button("Uyarı Göster")

    with tab1:
        with st.sidebar:
            st.header("Ürün Girişi")
            ürün_adi = st.selectbox("Ürün Adı", options= ['50 GR 165 CM ELYAF - DOGA', '60 GR 65 CM ELYAF - DOGA', '60 GR 140 CM ELYAF  - DOGA', '60 GR 150 CM ELYAF - DOGA', '60 GR 160 CM ELYAF - DOGA', '60 GR 210 CM ELYAF  - DOGA', '60 GR 240 CM ELYAF  - DOGA', '80 GR 70 CM ELYAF  - DOGA', '80 GR 75 CM ELYAF  - DOGA', '80 GR 85 CM ELYAF  - DOGA', '100 GR 75 CM ELYAF - DOGA', '100 GR 70 CM ELYAF  - DOGA', '100 GR 210 CM ELYAF  - DOGA', '120 GR 85 CM ELYAF  - DOGA', '120 GR 160 CM ELYAF  - DOGA', '210 GULLU JAGAR  - JAGAR NAIM', '210 YILANLI JAGAR - JAGAR NAIM', '210 DIAGONAL JAGAR - JAGAR NAIM', '210 NOKTALI JAGAR - JAGAR NAIM', '210 BAKLAVA JAGAR - JAGAR NAIM', '210 UC CIZGILI JAGAR - JAGAR NAIM', '210 EKRU 3 CIZGILI BEKART  - BEKART (TEKIRDAG)', '210 GRI 3 CIZGILI BEKART  - BEKART (TEKIRDAG)', '210 EKRU DUZ BEKART  - BEKART (TEKIRDAG)', '80 GR 240 CM MIKRO  - KARESI', '80 GR 80 CM MIKRO  - KARESI', '80 GR 90 CM MIKRO - KARESI', '80 GR 75 CM MIKRO - KARESI', '100 GR 300 CM MIKRO - KARESI', '100 GR 90 CM MIKRO  - KARESI', '100 GR 80 CM MIKRO  - KARESI', '100 GR 75 CM MIKRO  - KARESI', '220 CM ASTAR - KARESI', '46 CM BASKISIZ KOLI - KOLI HALIL', '30 CM BASKISIZ KOLI  - KOLI HALIL', '35 CM BASKISIZ KOLI - KOLI HALIL', '42 CM BASKILI KOLI  - KOLI HALIL', '50 CM BASKILI KOLI  - KOLI HALIL', 'GOMLEK KOLISI - KOLI HALIL', 'CARSAF KOLISI - KOLI HALIL', 'DANTEL SARIM KOLISI - KOLI HALIL', '220 CM ASTAR  - LALE', '250 CM BEYAZ IP  - LALE', '160 CM ASTAR  - LALE', '240 CM BEYAZ IP  - LALE', '80 CM BEYAZ IP  - LALE', '160 CM BEYAZ IP - LALE', '90 CM BEYAZ IP  - LALE', '5,5 CM ASTAR  - LALE', '75 CM ASTAR - LALE', '160 CM POLY PUANTIYE  - LALE', '80 CM POLY PUANTIYE  - LALE', '160 CM 120 GR BEYAZ IP - LALE', 'ARMURLU BAKLAVA - LALE', '4,5 CM POLY PUANTIYE  - LALE', '60 GR 70 CM TELA  - ARZU TOPRAK (TELA -BURSA)', '60 GR 80 CM TELA - ARZU TOPRAK (TELA -BURSA)', '60 GR 160 CM TELA - ARZU TOPRAK (TELA -BURSA)', '80 GR 160 CM TELA  - ARZU TOPRAK (TELA -BURSA)', '80 GR 80 CM TELA - ARZU TOPRAK (TELA -BURSA)', '40 GR 160 CM TELA - ARZU TOPRAK (TELA -BURSA)', '40 GR 120 CM TELA - ARZU TOPRAK (TELA -BURSA)', '40 GR 90 CM TELA - ARZU TOPRAK (TELA -BURSA)', '40 GR 67 CM TELA - ARZU TOPRAK (TELA -BURSA)', '40 GR 80 CM TELA  - ARZU TOPRAK (TELA -BURSA)', '60 GR 65 CM TELA  - ARZU TOPRAK (TELA -BURSA)', '15 GR 75 CM TELA  - ARZU TOPRAK (TELA -BURSA)', '15 GR 80 CM TELA  - ARZU TOPRAK (TELA -BURSA)', '15 GR 210 CM TELA  - ARZU TOPRAK (TELA -BURSA)', '75 CM ASTAR - URBA', '80 CM ASTAR  - URBA', '90 CM ASTAR  - URBA', '165 CM ASTAR - URBA', '210 CM ASTAR - URBA', '60 CM ASTAR - URBA', '65 CM ASTAR  - URBA', '330 CM ASTAR - URBA', '280 CM ASTAR - URBA', '300 CM ASTAR - URBA', '280 CM SEKER KASAR  - URBA', '90 CM SEKER KASAR - URBA', '80 CM SEKER KASAR  - URBA', '5,5 CM SEKER KASAR  - URBA', '60 GR 70 CM TELA  - MALZEM', '60 GR 80 CM TELA - MALZEM', '60 GR 160 CM TELA - MALZEM', '80 GR 160 CM TELA  - MALZEM', '80 GR 80 CM TELA - MALZEM', '40 GR 160 CM TELA - MALZEM', '40 GR 120 CM TELA - MALZEM', '40 GR 90 CM TELA - MALZEM', '40 GR 67 CM TELA - MALZEM', '40 GR 80 CM TELA  - MALZEM', '60 GR 65 CM TELA  - MALZEM', '15 GR 75 CM TELA  - MALZEM', '15 GR 80 CM TELA  - MALZEM', '15 GR 210 CM TELA  - MALZEM', '220 CM ASTAR  - URBA', '250 CM BEYAZ IP  - URBA', '160 CM ASTAR  - URBA', '240 CM BEYAZ IP  - URBA', '80 CM BEYAZ IP  - URBA', '160 CM BEYAZ IP - URBA', '90 CM BEYAZ IP  - URBA', '5,5 CM ASTAR  - URBA', '75 CM ASTAR - URBA', '160 CM POLY PUANTIYE  - URBA', '80 CM POLY PUANTIYE  - URBA', '160 CM 120 GR BEYAZ IP - URBA', '4,5 CM POLY PUANTIYE  - URBA', '80 GR 240 CM MIKRO  - URBA', '80 GR 80 CM MIKRO  - URBA', '80 GR 90 CM MIKRO - URBA', '80 GR 75 CM MIKRO - URBA', '100 GR 300 CM MIKRO - URBA', '100 GR 90 CM MIKRO  - URBA', '100 GR 80 CM MIKRO  - URBA', '100 GR 75 CM MIKRO  - URBA', '220 CM ASTAR - URBA'])
            gönderen = st.selectbox("Gönderen", options=["DOGA", "JAGAR NAIM", "BEKART", "KARESI", "KOLI HALIL", "LALE", "URBA", "ARZU TOPRAK", "MALZEM", "URBA", "PIR NAKIS"])
            alan = st.selectbox("Alan", options=["PIR NAKIS" , "DEPO"])
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
                log_activity("Ürün Ekleme", username, f"Ürün: {ürün_adi} ; Miktar: {miktar} {birim} ; Alan: {alan} ; Kimden: {gönderen}")


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

            # Delete feature
            st.subheader("Silmek İstediğiniz Satırları Seçin")
            delete_indices = st.multiselect(
                "Silinecek Satır İndeksleri", options=filtered_data.index, format_func=lambda x: f"Satır {x + 1}"
            )

            if st.button("Seçili Satırları Sil"):
                if delete_indices:
                    deleted_rows = stock_data.iloc[delete_indices]
                    stock_data = stock_data.drop(index=delete_indices).reset_index(drop=True)
                    stock_data.to_excel(file_name, index=False)
                    st.success("Seçili satırlar başarıyla silindi!")
                    log_activity("Satır Sil", username, f"Silinen Satırlar: {deleted_rows.to_dict(orient='records')}")
                    st.rerun()
                else:
                    st.warning("Lütfen silmek istediğiniz satırları seçin.")
        else:
            st.info("Seçilen filtrelere uygun veri bulunmamaktadır.")

    with tab2:

        if stock_data.empty:
            st.info("Stok verisi bulunmamaktadır.")
        else:
            st.write("## Uyarı Değiştirme")
            st.write(
                "Aşağıdaki tabloda 'Uyarı' sütununu istediğiniz gibi güncelleyebilirsiniz. Değişiklikleri yaptıktan sonra 'Güncelle' butonuna tıklayın.")

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
                log_activity("Uyarı Güncellemesi", username, "Depo verisi için uyarıları güncelledi")


            st.divider()
            st.write("Stok Tablosu")
            # Show highlighted dataframe above the editor
            styled_full = stock_data.style.apply(highlight_row, axis=1)
            st.dataframe(styled_full, use_container_width=True)
    with tab3:
        st.header("Etiketler")

        # List Word documents in the "ETİKETLER" folder
        etiketler_folder = "ETİKETLER"
        if not os.path.exists(etiketler_folder):
            st.warning("ETİKETLER klasörü bulunamadı!")
        else:
            files = list_etiketler_files()  # Use the function defined earlier
            if not files:
                st.info("Klasörde herhangi bir Word dosyası bulunamadı.")
            else:
                # Display files in a selectbox
                selected_file = st.selectbox("Görüntülemek istediğiniz dosyayı seçin:", files)

                if selected_file:
                    # Add an option to view the selected document
                    st.subheader("Seçilen Belge")
                    with open(selected_file, "rb") as f:
                        doc = docx.Document(io.BytesIO(f.read()))
                        for para in doc.paragraphs:
                            st.write(para.text)

                    # Add a download button for the selected file
                    st.download_button(
                        label="Dosyayı İndir",
                        data=download_file(selected_file),
                        file_name=os.path.basename(selected_file),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )

                    # Add a button to simulate printing the document
                    if st.button("Yazdır"):
                        print_file(selected_file)


    with tab4:
        st.header("Aktiviteler")
        st.write("All actions performed on the platform are logged here.")
        show_activity_log()
            


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



