import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Türkiye il isimleri normalize etme sözlüğü (Excel'deki farklı yazımları eşleştirmek için)
IL_NORMALIZE = {
    "ADANA": "Adana", "ADIYAMAN": "Adıyaman", "AFYONKARAHİSAR": "Afyonkarahisar",
    "AFYON": "Afyonkarahisar", "AĞRI": "Ağrı", "AGRI": "Ağrı",
    "AKSARAY": "Aksaray", "AMASYA": "Amasya", "ANKARA": "Ankara",
    "ANTALYA": "Antalya", "ARDAHAN": "Ardahan", "ARTVİN": "Artvin",
    "ARTVIN": "Artvin", "AYDIN": "Aydın", "AYDIN": "Aydın",
    "BALIKESİR": "Balıkesir", "BALIKESİR": "Balıkesir", "BALIKESIR": "Balıkesir",
    "BARTIN": "Bartın", "BATMAN": "Batman", "BAYBURT": "Bayburt",
    "BİLECİK": "Bilecik", "BILECIK": "Bilecik", "BİNGÖL": "Bingöl",
    "BINGOL": "Bingöl", "BİTLİS": "Bitlis", "BITLIS": "Bitlis",
    "BOLU": "Bolu", "BURDUR": "Burdur", "BURSA": "Bursa",
    "ÇANAKKALE": "Çanakkale", "CANAKKALE": "Çanakkale", "ÇANKIRI": "Çankırı",
    "CANKIRI": "Çankırı", "ÇORUM": "Çorum", "CORUM": "Çorum",
    "DENİZLİ": "Denizli", "DENIZLI": "Denizli", "DİYARBAKIR": "Diyarbakır",
    "DIYARBAKIR": "Diyarbakır", "DÜZCE": "Düzce", "DUZCE": "Düzce",
    "EDİRNE": "Edirne", "EDIRNE": "Edirne", "ELAZIĞ": "Elazığ",
    "ELAZIG": "Elazığ", "ERZİNCAN": "Erzincan", "ERZINCAN": "Erzincan",
    "ERZURUM": "Erzurum", "ESKİŞEHİR": "Eskişehir", "ESKISEHIR": "Eskişehir",
    "GAZİANTEP": "Gaziantep", "GAZIANTEP": "Gaziantep", "GİRESUN": "Giresun",
    "GIRESUN": "Giresun", "GÜMÜŞHANE": "Gümüşhane", "GUMUSHANE": "Gümüşhane",
    "HAKKARİ": "Hakkari", "HAKKARI": "Hakkari", "HATAY": "Hatay",
    "IĞDIR": "Iğdır", "IGDIR": "Iğdır", "ISPARTA": "Isparta",
    "İSTANBUL": "İstanbul", "ISTANBUL": "İstanbul", "İZMİR": "İzmir",
    "IZMIR": "İzmir", "KAHRAMANMARAŞ": "Kahramanmaraş", "KAHRAMANMARAS": "Kahramanmaraş",
    "KARABÜK": "Karabük", "KARABUK": "Karabük", "KARAMAN": "Karaman",
    "KARS": "Kars", "KASTAMONU": "Kastamonu", "KAYSERİ": "Kayseri",
    "KAYSERI": "Kayseri", "KİLİS": "Kilis", "KILIS": "Kilis",
    "KIRIKKALE": "Kırıkkale", "KIRIKKALe": "Kırıkkale", "KIRKLARELİ": "Kırklareli",
    "KIRKLARELI": "Kırklareli", "KIRŞEHİR": "Kırşehir", "KIRSEHIR": "Kırşehir",
    "KOCAELİ": "Kocaeli", "KOCAELI": "Kocaeli", "KONYA": "Konya",
    "KÜTAHYA": "Kütahya", "KUTAHYA": "Kütahya", "MALATYA": "Malatya",
    "MANİSA": "Manisa", "MANISA": "Manisa", "MARDİN": "Mardin",
    "MARDIN": "Mardin", "MERSİN": "Mersin", "MERSIN": "Mersin",
    "İÇEL": "Mersin", "ICEL": "Mersin", "MUĞLA": "Muğla",
    "MUGLA": "Muğla", "MUŞ": "Muş", "MUS": "Muş",
    "NEVŞEHİR": "Nevşehir", "NEVSEHIR": "Nevşehir", "NİĞDE": "Niğde",
    "NIGDE": "Niğde", "ORDU": "Ordu", "OSMANİYE": "Osmaniye",
    "OSMANIYE": "Osmaniye", "RİZE": "Rize", "RIZE": "Rize",
    "SAKARYA": "Sakarya", "SAMSUN": "Samsun", "SİİRT": "Siirt",
    "SIIRT": "Siirt", "SİNOP": "Sinop", "SINOP": "Sinop",
    "SİVAS": "Sivas", "SIVAS": "Sivas", "ŞANLIURFA": "Şanlıurfa",
    "SANLIURFA": "Şanlıurfa", "URFA": "Şanlıurfa", "ŞIRNAK": "Şırnak",
    "SIRNAK": "Şırnak", "TEKİRDAĞ": "Tekirdağ", "TEKIRDAG": "Tekirdağ",
    "TOKAT": "Tokat", "TRABZON": "Trabzon", "TUNCELİ": "Tunceli",
    "TUNCELI": "Tunceli", "UŞAK": "Uşak", "USAK": "Uşak",
    "VAN": "Van", "YALOVA": "Yalova", "YOZGAT": "Yozgat",
    "ZONGULDAK": "Zonguldak",
}


def normalize_il(isim):
    """İl ismini normalize eder."""
    if pd.isna(isim):
        return None
    isim_upper = str(isim).strip().upper()
    # Türkçe karakterleri büyük harfe çevir
    isim_upper = isim_upper.replace("İ", "İ").replace("I", "I")
    return IL_NORMALIZE.get(isim_upper, str(isim).strip())


def dosya_sec():
    """Dosya seçme dialogu açar."""
    root = tk.Tk()
    root.withdraw()
    dosya_yolu = filedialog.askopenfilename(
        title="Excel Dosyası Seçin",
        filetypes=[("Excel Dosyaları", "*.xlsx *.xls"), ("Tüm Dosyalar", "*.*")]
    )
    root.destroy()
    return dosya_yolu


def sutun_sec_dialog(sutunlar):
    """Sütun seçimi için dialog penceresi."""
    result = {"il": None, "sayi": None}

    dialog = tk.Tk()
    dialog.title("Sütun Seçimi")
    dialog.geometry("400x200")
    dialog.resizable(False, False)

    tk.Label(dialog, text="İl sütununu seçin:", font=("Arial", 11)).grid(row=0, column=0, padx=20, pady=10, sticky="w")
    il_var = tk.StringVar(value=sutunlar[0])
    il_combo = ttk.Combobox(dialog, textvariable=il_var, values=sutunlar, state="readonly", width=25)
    il_combo.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Proje Sayısı sütununu seçin:", font=("Arial", 11)).grid(row=1, column=0, padx=20, pady=10, sticky="w")
    sayi_var = tk.StringVar(value=sutunlar[-1] if len(sutunlar) > 1 else sutunlar[0])
    sayi_combo = ttk.Combobox(dialog, textvariable=sayi_var, values=sutunlar, state="readonly", width=25)
    sayi_combo.grid(row=1, column=1, padx=10, pady=10)

    def tamam():
        result["il"] = il_var.get()
        result["sayi"] = sayi_var.get()
        dialog.destroy()

    tk.Button(dialog, text="Tamam", command=tamam, bg="#0078D4", fg="white",
              font=("Arial", 11), width=10).grid(row=2, column=0, columnspan=2, pady=20)

    dialog.mainloop()
    return result["il"], result["sayi"]


def harita_gorsellestir(excel_dosyasi=None):
    """Ana görselleştirme fonksiyonu."""

    # --- 1. Excel dosyasını seç ---
    if not excel_dosyasi:
        print("Excel dosyası seçiliyor...")
        excel_dosyasi = dosya_sec()
        if not excel_dosyasi:
            print("Dosya seçilmedi. Program sonlandırılıyor.")
            return

    print(f"Dosya yükleniyor: {excel_dosyasi}")

    # --- 2. Excel'i oku ---
    try:
        df = pd.read_excel(excel_dosyasi)
    except Exception as e:
        messagebox.showerror("Hata", f"Excel dosyası okunamadı:\n{e}")
        return

    print(f"Sütunlar: {list(df.columns)}")
    print(df.head())

    # --- 3. Sütunları otomatik tespit veya kullanıcıdan al ---
    sutunlar = list(df.columns)
    il_sutunu = None
    sayi_sutunu = None

    # Otomatik tespit dene
    for col in sutunlar:
        col_lower = str(col).lower()
        if any(k in col_lower for k in ["il", "şehir", "sehir", "city", "province"]):
            il_sutunu = col
        if any(k in col_lower for k in ["proje", "sayı", "sayi", "count", "adet", "toplam"]):
            sayi_sutunu = col

    if not il_sutunu or not sayi_sutunu:
        print("Sütunlar otomatik tespit edilemedi, lütfen seçin.")
        il_sutunu, sayi_sutunu = sutun_sec_dialog(sutunlar)

    if not il_sutunu or not sayi_sutunu:
        print("Sütun seçimi yapılmadı.")
        return

    print(f"İl sütunu: {il_sutunu} | Sayı sütunu: {sayi_sutunu}")

    # --- 4. Veriyi hazırla ---
    df = df[[il_sutunu, sayi_sutunu]].dropna()
    df.columns = ["Il", "Sayi"]
    df["Il"] = df["Il"].apply(normalize_il)
    df["Sayi"] = pd.to_numeric(df["Sayi"], errors="coerce").fillna(0).astype(int)
    df = df.groupby("Il", as_index=False)["Sayi"].sum()

    print("\nNormalize edilmiş veri:")
    print(df)

    # --- 5. Türkiye GeoJSON verisini indir/yükle ---
    geojson_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), "turkey_provinces.geojson")

    if not os.path.exists(geojson_yolu):
        print("GeoJSON dosyası indiriliyor...")
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json"
            urllib.request.urlretrieve(url, geojson_yolu)
            print("GeoJSON indirildi.")
        except Exception as e:
            print(f"GeoJSON indirilemedi: {e}")
            messagebox.showerror(
                "GeoJSON Hatası",
                "Türkiye harita verisi indirilemedi.\n"
                "Lütfen internet bağlantınızı kontrol edin veya\n"
                "'turkey_provinces.geojson' dosyasını script klasörüne koyun.\n\n"
                f"Hata: {e}"
            )
            return

    # --- 6. GeoDataFrame oluştur ---
    try:
        gdf = gpd.read_file(geojson_yolu)
    except Exception as e:
        messagebox.showerror("Hata", f"Harita verisi okunamadı:\n{e}")
        return

    # GeoJSON'daki il isim sütununu bul
    print(f"\nGeoJSON sütunları: {list(gdf.columns)}")
    isim_sutunu = None
    for col in gdf.columns:
        sample = str(gdf[col].iloc[0])
        if any(c in sample for c in ["İstanbul", "Ankara", "İzmir", "Istanbul", "Ankara"]):
            isim_sutunu = col
            break
    if not isim_sutunu:
        # Olası isim sütunlarını dene
        for col in ["name", "NAME", "il", "IL", "province", "PROVINCE", "NAME_1"]:
            if col in gdf.columns:
                isim_sutunu = col
                break

    if not isim_sutunu:
        isim_sutunu = gdf.columns[0]
        print(f"İl isim sütunu bulunamadı, {isim_sutunu} kullanılıyor.")

    print(f"Kullanılan isim sütunu: {isim_sutunu}")

    # GeoJSON'daki il isimlerini normalize et
    gdf["Il_norm"] = gdf[isim_sutunu].apply(normalize_il)

    # --- 7. Birleştir ---
    gdf = gdf.merge(df, left_on="Il_norm", right_on="Il", how="left")
    gdf["Sayi"] = gdf["Sayi"].fillna(0).astype(int)

    # --- 8. Görselleştir ---
    fig, ax = plt.subplots(1, 1, figsize=(20, 12))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    # Renk skalası
    max_sayi = gdf["Sayi"].max()
    if max_sayi == 0:
        max_sayi = 1

    colors = ["#2d3561", "#1e88e5", "#00acc1", "#26c6da", "#ffd740", "#ff6d00"]
    cmap = LinearSegmentedColormap.from_list("turkiye", colors, N=256)

    # Haritayı çiz
    # Boş iller (Sayi=0)
    gdf[gdf["Sayi"] == 0].plot(
        ax=ax,
        color="#2d3561",
        edgecolor="#4a4a8a",
        linewidth=0.5
    )

    # Proje olan iller
    gdf_aktif = gdf[gdf["Sayi"] > 0]
    if not gdf_aktif.empty:
        gdf_aktif.plot(
            ax=ax,
            column="Sayi",
            cmap=cmap,
            vmin=0,
            vmax=max_sayi,
            edgecolor="#ffffff",
            linewidth=0.8,
            legend=False
        )

    # İl etiketleri (proje sayısı > 0 olan iller için)
    for idx, row in gdf[gdf["Sayi"] > 0].iterrows():
        centroid = row.geometry.centroid
        il_adi = row["Il_norm"] if pd.notna(row["Il_norm"]) else ""
        sayi = int(row["Sayi"])

        ax.annotate(
            f"{il_adi}\n{sayi}",
            xy=(centroid.x, centroid.y),
            ha="center",
            va="center",
            fontsize=7,
            fontweight="bold",
            color="white",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="black",
                alpha=0.6,
                edgecolor="none"
            )
        )

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_sayi))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5, aspect=20, pad=0.02)
    cbar.set_label("Proje Sayısı", color="white", fontsize=13, labelpad=10)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")
    cbar.outline.set_edgecolor("white")

    # Başlık ve düzenlemeler
    toplam = df["Sayi"].sum()
    aktif_il = len(df[df["Sayi"] > 0])
    ax.set_title(
        f"Türkiye İl Bazlı Proje Dağılımı\nToplam: {toplam} Proje  |  {aktif_il} İl",
        fontsize=18,
        fontweight="bold",
        color="white",
        pad=20
    )

    ax.axis("off")
    plt.tight_layout()

    # Kaydetme seçeneği
    kayit_yolu = os.path.join(os.path.dirname(os.path.abspath(excel_dosyasi)), "turkiye_proje_haritasi.png")
    plt.savefig(kayit_yolu, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\nHarita kaydedildi: {kayit_yolu}")

    plt.show()
    print("İşlem tamamlandı.")


if __name__ == "__main__":
    harita_gorsellestir()
