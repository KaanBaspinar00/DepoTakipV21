import streamlit as st
import pandas as pd
import os
import yaml
import uuid
import time
import docx
from fpdf import FPDF
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
            ürün_adi = st.selectbox("Ürün Adı", options=["Ürün A", "Ürün B", "Ürün C"])
            gönderen = st.selectbox("Gönderen", options=["Gönderen 1", "Gönderen 2", "Gönderen 3"])
            alan = st.selectbox("Alan", options=["Alan 1", "Alan 2", "Depo"])
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

            # Delete feature
            st.subheader("Silmek İstediğiniz Satırları Seçin")
            delete_indices = st.multiselect(
                "Silinecek Satır İndeksleri", options=filtered_data.index, format_func=lambda x: f"Satır {x + 1}"
            )

            if st.button("Seçili Satırları Sil"):
                if delete_indices:
                    stock_data = stock_data.drop(index=delete_indices).reset_index(drop=True)
                    stock_data.to_excel(file_name, index=False)
                    st.success("Seçili satırlar başarıyla silindi!")
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

            st.divider()
            st.write("Stok Tablosu")
            # Show highlighted dataframe above the editor
            styled_full = stock_data.style.apply(highlight_row, axis=1)
            st.dataframe(styled_full, use_container_width=True)

    # Add "Etiketler" tab
    with st.tabs(["Stok İşlemleri", "Uyarı Belirle", "Etiketler"])[2]:
        st.title("Etiketler")
    
        etikeler_folder = "ETİKETLER"  # Path to the main folder
    
        if not os.path.exists(etikeler_folder):
            st.error(f"{etikeler_folder} klasörü mevcut değil. Lütfen doğru yolu kontrol edin.")
        else:
            subfolders = [f for f in os.listdir(etikeler_folder) if os.path.isdir(os.path.join(etikeler_folder, f))]
    
            selected_subfolder = st.selectbox("Alt Klasör Seçiniz", options=subfolders, format_func=lambda x: x.capitalize())
    
            if selected_subfolder:
                subfolder_path = os.path.join(etikeler_folder, selected_subfolder)
                doc_files = [f for f in os.listdir(subfolder_path) if f.endswith(".doc") or f.endswith(".docx")]
    
                selected_doc = st.selectbox("Doküman Seçiniz", options=doc_files, format_func=lambda x: x.capitalize())
    
                if selected_doc:
                    doc_path = os.path.join(subfolder_path, selected_doc)
    
                    try:
                        doc = docx.Document(doc_path)
                        st.subheader(f"Seçilen Doküman: {selected_doc}")
    
                        # Display document content
                        for paragraph in doc.paragraphs:
                            st.write(paragraph.text)
    
                        # Print option - Create PDF
                        if st.button("Yazdır"):
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
    
                            # Add content to the PDF
                            for paragraph in doc.paragraphs:
                                pdf.multi_cell(0, 10, paragraph.text)
    
                            # Create a downloadable PDF file
                            pdf_buffer = io.BytesIO()
                            pdf.output(pdf_buffer)
                            pdf_buffer.seek(0)
    
                            st.download_button(
                                label="PDF Olarak İndir",
                                data=pdf_buffer,
                                file_name=f"{selected_doc}.pdf",
                                mime="application/pdf"
                            )
    
                    except Exception as e:
                        st.error(f"Doküman okunurken bir hata oluştu: {e}")



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
