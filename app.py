import os
import json
import urllib.request
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
GEOJSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "turkey_provinces.geojson")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Türkiye il normalize sözlüğü ──────────────────────────────────────────────
IL_NORMALIZE = {
    "ADANA": "Adana", "ADIYAMAN": "Adıyaman", "AFYONKARAHİSAR": "Afyonkarahisar",
    "AFYON": "Afyonkarahisar", "AĞRI": "Ağrı", "AGRI": "Ağrı",
    "AKSARAY": "Aksaray", "AMASYA": "Amasya", "ANKARA": "Ankara",
    "ANTALYA": "Antalya", "ARDAHAN": "Ardahan", "ARTVİN": "Artvin",
    "ARTVIN": "Artvin", "AYDIN": "Aydın",
    "BALIKESİR": "Balıkesir", "BALIKESIR": "Balıkesir",
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
    "KIRIKKALE": "Kırıkkale", "KIRKLARELİ": "Kırklareli",
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
    if pd.isna(isim):
        return None
    s = str(isim).strip().upper()
    return IL_NORMALIZE.get(s, str(isim).strip())


def ensure_geojson():
    """GeoJSON yoksa indir."""
    if not os.path.exists(GEOJSON_PATH):
        url = "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json"
        urllib.request.urlretrieve(url, GEOJSON_PATH)
    return GEOJSON_PATH


COLOR_SCALES = {
    "blue_orange": [
        [0.0,   "#1e2a4a"],
        [0.001, "#2d3f6e"],
        [0.2,   "#1565c0"],
        [0.5,   "#00acc1"],
        [0.8,   "#ffd740"],
        [1.0,   "#ff6d00"],
    ],
    "blue_light": [
        [0.0,   "#e3f2fd"],
        [0.3,   "#90caf9"],
        [0.6,   "#1976d2"],
        [1.0,   "#0d47a1"],
    ],
    "blue_dark": [
        [0.0,   "#050d1a"],
        [0.001, "#0a1929"],
        [0.25,  "#0d47a1"],
        [0.55,  "#1565c0"],
        [0.8,   "#42a5f5"],
        [1.0,   "#e3f2fd"],
    ],
    "blue_navy": [
        [0.0,   "#001233"],
        [0.3,   "#023e8a"],
        [0.6,   "#0096c7"],
        [1.0,   "#ade8f4"],
    ],
    "blue_steel": [
        [0.0,   "#0d1b2a"],
        [0.3,   "#1b4965"],
        [0.6,   "#5fa8d3"],
        [1.0,   "#cae9ff"],
    ],
    "green": [
        [0.0,   "#0d1f10"],
        [0.001, "#1b3a20"],
        [0.25,  "#2e7d32"],
        [0.6,   "#66bb6a"],
        [1.0,   "#ccff90"],
    ],
    "red": [
        [0.0,   "#1a0a0a"],
        [0.001, "#3e1010"],
        [0.25,  "#b71c1c"],
        [0.6,   "#ef5350"],
        [1.0,   "#ffcdd2"],
    ],
    "purple": [
        [0.0,   "#12001f"],
        [0.001, "#2a0040"],
        [0.25,  "#6a1b9a"],
        [0.6,   "#ce93d8"],
        [1.0,   "#f3e5f5"],
    ],
    "thermal": [
        [0.0,   "#04002c"],
        [0.25,  "#4b0082"],
        [0.5,   "#c2185b"],
        [0.75,  "#ff6f00"],
        [1.0,   "#fff176"],
    ],
    "teal": [
        [0.0,   "#001a1f"],
        [0.001, "#00363d"],
        [0.3,   "#00695c"],
        [0.65,  "#26c6da"],
        [1.0,   "#e0f7fa"],
    ],
    "gold": [
        [0.0,   "#1a1000"],
        [0.001, "#3d2200"],
        [0.3,   "#bf6c00"],
        [0.65,  "#ffb300"],
        [1.0,   "#fff8e1"],
    ],
    "ice_fire": "RdYlBu_r",
}


def _interpolate_color(scale, t):
    """0-1 aralığındaki t değeri için skala rengi döndür."""
    import colorsys
    if isinstance(scale, str):
        return "#ffffff"
    for i in range(len(scale) - 1):
        t0, c0 = scale[i]
        t1, c1 = scale[i + 1]
        if t0 <= t <= t1:
            r = (t - t0) / (t1 - t0) if t1 > t0 else 0
            def hex2rgb(h):
                h = h.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            r0 = hex2rgb(c0); r1 = hex2rgb(c1)
            mixed = tuple(int(r0[j] + (r1[j] - r0[j]) * r) for j in range(3))
            return "#{:02x}{:02x}{:02x}".format(*mixed)
    return scale[-1][1]


def hex_with_alpha(hex_color: str, alpha: float) -> str:
    """Hex rengi rgba() string'ine dönüştür (alpha 0-1)."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def build_map(df_data, il_col, sayi_col, color_scale="blue_orange",
              label_mode="none", show_legend=False, show_all_labels=False,
              bg_color="#0f1629", text_color="#ffffff",
              show_colorbar=True,
              legend_text_color=None, legend_bg_color=None):
    """Plotly choropleth haritası JSON olarak döndür."""
    ensure_geojson()

    # Veriyi hazırla
    df = df_data[[il_col, sayi_col]].dropna().copy()
    df.columns = ["Il", "Sayi"]
    df["Il"] = df["Il"].apply(normalize_il)
    df["Sayi"] = pd.to_numeric(df["Sayi"], errors="coerce").fillna(0).astype(int)
    df = df.groupby("Il", as_index=False)["Sayi"].sum()

    # GeoJSON yükle
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        geojson = json.load(f)

    # GeoJSON'daki il isim özelliğini bul
    sample_props = geojson["features"][0]["properties"]
    name_key = None
    for candidate in ["name", "NAME", "il", "IL", "province", "PROVINCE", "NAME_1"]:
        if candidate in sample_props:
            name_key = candidate
            break
    if not name_key:
        name_key = list(sample_props.keys())[0]

    # GeoJSON feature'larına normalize isim ekle
    for feat in geojson["features"]:
        feat["properties"]["_il_norm"] = normalize_il(feat["properties"].get(name_key, ""))

    # Centroid: representative_point() il sınırları içinde garanti nokta verir
    gdf = gpd.read_file(GEOJSON_PATH)
    gdf["_il_norm"] = gdf[name_key].apply(normalize_il)
    gdf["_rep"] = gdf.geometry.representative_point()
    centroid_map = {row["_il_norm"]: (row["_rep"].x, row["_rep"].y) for _, row in gdf.iterrows()}

    # Tüm iller için temel df
    all_iller = [f["properties"]["_il_norm"] for f in geojson["features"]]
    base_df = pd.DataFrame({"Il": all_iller})
    merged = base_df.merge(df, on="Il", how="left")
    merged["Sayi"] = merged["Sayi"].fillna(0).astype(int)

    max_sayi = max(merged["Sayi"].max(), 1)
    scale = COLOR_SCALES.get(color_scale, COLOR_SCALES["blue_orange"])

    # 0 olan ve > 0 olan illeri ayır
    # Başvuru yok rengi: skalanın EN AÇIK tonu — görseldeki gibi açık renkle ayrı seri
    ZERO_COLOR = _interpolate_color(scale, 0.12)   # t=0.12 → skalanın açık ucu, veri renklerinden farklı
    merged_zero    = merged[merged["Sayi"] == 0].copy()
    merged_nonzero = merged[merged["Sayi"] >  0].copy()

    # Ana choropleth: sadece > 0 iller, skala 1..max_sayi
    fig = px.choropleth(
        merged_nonzero,
        geojson=geojson,
        locations="Il",
        featureidkey="properties._il_norm",
        color="Sayi",
        color_continuous_scale=scale,
        range_color=(1, max_sayi),
        hover_name="Il",
        hover_data={"Sayi": True, "Il": False},
        labels={"Sayi": "Proje Sayısı"},
    )
    fig.update_traces(marker_line_color="rgba(255,255,255,0.7)", marker_line_width=1.2)

    # 0 olan iller için ayrı trace — sabit ZERO_COLOR
    if not merged_zero.empty:
        zero_trace = go.Choropleth(
            geojson=geojson,
            locations=merged_zero["Il"],
            z=[0] * len(merged_zero),
            featureidkey="properties._il_norm",
            colorscale=[[0, ZERO_COLOR], [1, ZERO_COLOR]],
            showscale=False,
            hovertemplate="<b>%{location}</b><br>Proje Sayısı: 0<extra></extra>",
            marker_line_color="rgba(255,255,255,0.7)",
            marker_line_width=1.2,
        )
        fig.add_trace(zero_trace)
        # 0 trace'ini en alta taşı (arkaya)
        fig.data = (fig.data[-1],) + fig.data[:-1]

    # Şeffaf renk özel durumu: Plotly geo bgcolor rgba kabul etmiyor, "white" ile mask yapıyoruz
    _geo_bg = "rgba(0,0,0,0)" if bg_color == "transparent" else bg_color
    _paper_bg = "rgba(0,0,0,0)" if bg_color == "transparent" else bg_color

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor=_geo_bg,
    )

    # ── Veri etiketleri: scattergeo trace ile lon/lat üzerine yaz ──────────────
    aktif = df[df["Sayi"] > 0]

    # --- Veri olan iller ---
    if label_mode != "none" and not aktif.empty:
        from collections import defaultdict
        max_font = 15
        min_font = 8
        groups = defaultdict(lambda: {"lons": [], "lats": [], "texts": []})

        for _, row in aktif.iterrows():
            il = row["Il"]
            sayi = int(row["Sayi"])
            coords = centroid_map.get(il)
            if coords is None:
                continue
            lon, lat = coords

            if label_mode == "name_count":
                text = f"{il}<br><b>{sayi}</b>"
                font_size = 9
            elif label_mode == "count_only":
                text = f"<b>{sayi}</b>"
                font_size = 11
            elif label_mode == "name_only":
                text = f"{il}"
                font_size = 9
            elif label_mode == "scaled":
                ratio = sayi / max_sayi
                font_size = int(min_font + (max_font - min_font) * ratio)
                text = f"{il}<br><b>{sayi}</b>"
            else:
                continue

            groups[font_size]["lons"].append(lon)
            groups[font_size]["lats"].append(lat)
            groups[font_size]["texts"].append(text)

        for sz, g in groups.items():
            fig.add_trace(go.Scattergeo(
                lon=g["lons"],
                lat=g["lats"],
                mode="text",
                text=g["texts"],
                textfont=dict(size=sz, color=text_color, family="Segoe UI"),
                hoverinfo="skip",
                showlegend=False,
            ))

    # --- Veri OLMAYAN iller için il adı (show_all_labels) ---
    if show_all_labels:
        from collections import defaultdict
        # Veri olan illeri set olarak tut
        aktif_set = set(aktif["Il"].tolist()) if not aktif.empty else set()
        pasif_lons, pasif_lats, pasif_texts = [], [], []
        for il_name, coords in centroid_map.items():
            if il_name in aktif_set:
                continue  # zaten veri etiketiyle gösteriliyor
            if il_name is None:
                continue
            lon, lat = coords
            pasif_lons.append(lon)
            pasif_lats.append(lat)
            pasif_texts.append(il_name)

        if pasif_lons:
            fig.add_trace(go.Scattergeo(
                lon=pasif_lons,
                lat=pasif_lats,
                mode="text",
                text=pasif_texts,
                textfont=dict(size=7, color=hex_with_alpha(text_color, 0.75), family="Segoe UI"),
                hoverinfo="skip",
                showlegend=False,
            ))

    # ── Lejant: renk aralıkları + sayı eşleşmesi ──────────────────────────────
    # A4 yatay: 297×210 mm → ~1123×794 px @96dpi
    # Lejant sağ alt köşede küçük ve kompakt
    legend_shapes = []
    legend_annotations = []
    if show_legend:
        # Lejant renk değişkenleri
        _leg_text  = legend_text_color if legend_text_color else text_color
        _leg_bg    = legend_bg_color   if legend_bg_color   else "rgba(8,15,45,0.90)"

        n_steps = 5
        # Satır düzeni (yukarıdan aşağıya):
        #   0: "Başvuru Yok"  ← en üst
        #   1: ince ayraç
        #   2..n_steps+1: veri aralıkları (en yüksek üstte, en düşük altta)
        total_rows = n_steps + 1   # +1: "Başvuru Yok" satırı

        box_x0  = 0.82
        box_x1  = 0.995
        row_h   = 0.030
        box_y0  = 0.01
        box_y1  = box_y0 + row_h * (total_rows + 0.8)

        # ── Dış kutu ──────────────────────────────────────────────────────────
        legend_shapes.append(dict(
            type="rect", xref="paper", yref="paper",
            x0=box_x0, y0=box_y0, x1=box_x1, y1=box_y1,
            fillcolor=_leg_bg,
            line=dict(color="rgba(100,140,220,0.6)", width=1),
            layer="above",
        ))

        # ── "Başvuru Yok" satırı — en üstte ──────────────────────────────────
        zero_row_y = box_y0 + row_h * (total_rows - 0.5)

        legend_shapes.append(dict(
            type="rect", xref="paper", yref="paper",
            x0=box_x0, y0=box_y0 + row_h * (n_steps),
            x1=box_x1, y1=box_y1,
            fillcolor=hex_with_alpha(ZERO_COLOR, 0.18),   # hafif ton farkı — ayrı seri vurgusu
            line=dict(color="rgba(0,0,0,0)", width=0),
            layer="above",
        ))

        legend_shapes.append(dict(
            type="rect", xref="paper", yref="paper",
            x0=box_x0 + 0.006, y0=zero_row_y - 0.010,
            x1=box_x0 + 0.030, y1=zero_row_y + 0.010,
            fillcolor=ZERO_COLOR,
            line=dict(color="rgba(255,255,255,0.5)", width=0.8),
            layer="above",
        ))

        legend_annotations.append(dict(
            xref="paper", yref="paper",
            x=box_x0 + 0.036, y=zero_row_y,
            text="<b>Başvuru Yok</b>",
            showarrow=False,
            font=dict(size=8.5, color=_leg_text),
            xanchor="left", yanchor="middle",
        ))

        # ── Ayraç çizgisi ─────────────────────────────────────────────────────
        legend_shapes.append(dict(
            type="line", xref="paper", yref="paper",
            x0=box_x0 + 0.004, y0=box_y0 + row_h * n_steps,
            x1=box_x1 - 0.004, y1=box_y0 + row_h * n_steps,
            line=dict(color=hex_with_alpha(_leg_text, 0.30), width=0.8),
            layer="above",
        ))

        # ── Veri aralığı satırları (en yüksek üstte, en düşük altta) ─────────
        # Aralıkları 1..max_sayi arasında n_steps'e böl
        thresholds = [max(1, int(round(k * max_sayi / n_steps))) for k in range(n_steps + 1)]
        # thresholds[0]=0 yerine 1 yap
        thresholds[0] = 1

        for i in range(n_steps):
            # i=0 → en yüksek aralık (üstte), i=n_steps-1 → en düşük aralık (altta)
            idx_high = n_steps - i        # en yüksek indeks
            idx_low  = n_steps - i - 1
            val_high = thresholds[idx_high]
            val_low  = thresholds[idx_low]

            t_mid  = (idx_low + idx_high) / (2 * n_steps)
            color  = _interpolate_color(scale, max(t_mid, 0.25))

            row_y_center = box_y0 + row_h * (i + 0.5)

            legend_shapes.append(dict(
                type="rect", xref="paper", yref="paper",
                x0=box_x0 + 0.006, y0=row_y_center - 0.010,
                x1=box_x0 + 0.030, y1=row_y_center + 0.010,
                fillcolor=color,
                line=dict(color="rgba(255,255,255,0.20)", width=0.5),
                layer="above",
            ))

            if i == 0:
                range_text = f"{val_low}'den fazla"
            elif val_low == val_high:
                range_text = f"{val_low}"
            else:
                range_text = f"{val_low}-{val_high} arası"

            legend_annotations.append(dict(
                xref="paper", yref="paper",
                x=box_x0 + 0.036, y=row_y_center,
                text=f"<b>{range_text}</b>",
                showarrow=False,
                font=dict(size=8, color=_leg_text),
                xanchor="left", yanchor="middle",
            ))

    # Türkiye haritası 36°-42° enlem, 26°-45° boylam → ~19° enlem x ~19° boylam
    # Cos düzeltmesi ile gerçek oran ~2.35:1 (en:boy)
    # A4 landscape (1123x794) → kenar boşlukları çıkınca harita alanı ~1103x714
    # Daha geniş format için 1400x680 kullanacağız
    MAP_W, MAP_H = 1400, 680

    fig.update_layout(
        paper_bgcolor=_paper_bg,
        plot_bgcolor=_paper_bg,
        geo_bgcolor=_geo_bg,
        width=MAP_W,
        height=MAP_H,
        font=dict(color=text_color, family="Segoe UI, Arial"),
        margin=dict(l=10, r=10, t=65, b=10),
        title=dict(
            text=f"Türkiye İl Bazlı Proje Dağılımı<br>"
                 f"<sup>Toplam: {merged['Sayi'].sum()} proje  |  "
                 f"{len(df[df['Sayi'] > 0])} il</sup>",
            x=0.5,
            font=dict(size=18, color=text_color),
        ),
        coloraxis_showscale=show_colorbar,
        coloraxis_colorbar=dict(
            title=dict(
                text="Proje<br>Sayısı",
                font=dict(color=text_color),
            ),
            tickfont=dict(color=text_color),
            outlinecolor=text_color,
            len=0.55,
            thickness=14,
            x=0.01,
            xanchor="left",
        ),
        hoverlabel=dict(
            bgcolor="#1e2a4a",
            font_size=14,
            font_family="Segoe UI",
            font_color="white",
        ),
        annotations=legend_annotations,
        shapes=legend_shapes,
    )

    return fig.to_json()


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Dosya bulunamadı."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Dosya seçilmedi."}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".xlsx", ".xls"):
        return jsonify({"error": "Sadece .xlsx ve .xls dosyaları desteklenir."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        return jsonify({"error": f"Excel okunamadı: {e}"}), 400

    columns = list(df.columns)

    # Otomatik sütun tespiti
    il_col = next(
        (c for c in columns if any(k in str(c).lower() for k in ["il", "şehir", "sehir", "city", "province"])),
        None,
    )
    sayi_col = next(
        (c for c in columns if any(k in str(c).lower() for k in ["proje", "sayı", "sayi", "count", "adet", "toplam"])),
        None,
    )

    return jsonify({
        "filename": filename,
        "columns": columns,
        "detected_il": il_col,
        "detected_sayi": sayi_col,
        "preview": df.head(5).to_dict(orient="records"),
    })


@app.route("/map", methods=["POST"])
def map_data():
    data = request.get_json()
    filename = data.get("filename")
    il_col = data.get("il_col")
    sayi_col = data.get("sayi_col")
    color_scale = data.get("color_scale", "blue_orange")
    label_mode = data.get("label_mode", "none")
    show_legend = data.get("show_legend", False)
    show_all_labels = data.get("show_all_labels", False)
    bg_color = data.get("bg_color", "#0f1629")
    text_color = data.get("text_color", "#ffffff")
    show_colorbar = data.get("show_colorbar", True)
    legend_text_color = data.get("legend_text_color") or None
    legend_bg_color   = data.get("legend_bg_color")   or None

    if not all([filename, il_col, sayi_col]):
        return jsonify({"error": "Eksik parametre."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"error": "Dosya bulunamadı, tekrar yükleyin."}), 404

    try:
        df = pd.read_excel(filepath)
        fig_json = build_map(df, il_col, sayi_col, color_scale, label_mode,
                             show_legend, show_all_labels, bg_color, text_color,
                             show_colorbar, legend_text_color, legend_bg_color)
        return jsonify({"figure": fig_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export", methods=["POST"])
def export_map():
    import io
    import kaleido  # noqa – ensure kaleido is importable
    data = request.get_json()
    filename = data.get("filename")
    il_col = data.get("il_col")
    sayi_col = data.get("sayi_col")
    color_scale = data.get("color_scale", "blue_orange")
    label_mode = data.get("label_mode", "none")
    show_legend = data.get("show_legend", False)
    show_all_labels = data.get("show_all_labels", False)
    bg_color = data.get("bg_color", "#0f1629")
    text_color = data.get("text_color", "#ffffff")
    show_colorbar = data.get("show_colorbar", True)
    legend_text_color = data.get("legend_text_color") or None
    legend_bg_color   = data.get("legend_bg_color")   or None
    fmt = data.get("format", "png")  # "png" veya "pdf"

    if not all([filename, il_col, sayi_col]):
        return jsonify({"error": "Eksik parametre."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"error": "Dosya bulunamadı, tekrar yükleyin."}), 404

    try:
        df = pd.read_excel(filepath)
        fig_json = build_map(df, il_col, sayi_col, color_scale, label_mode,
                             show_legend, show_all_labels, bg_color, text_color,
                             show_colorbar, legend_text_color, legend_bg_color)
        import plotly.io as pio
        fig_obj = pio.from_json(fig_json)

        buf = io.BytesIO()
        if fmt == "pdf":
            fig_obj.write_image(buf, format="pdf", width=1400, height=680, scale=2)
            mime = "application/pdf"
            ext = "pdf"
        else:
            fig_obj.write_image(buf, format="png", width=1400, height=680, scale=2)
            mime = "image/png"
            ext = "png"

        buf.seek(0)
        from flask import send_file
        return send_file(
            buf,
            mimetype=mime,
            as_attachment=True,
            download_name=f"turkiye_proje_haritasi.{ext}",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 55)
    print("  Türkiye Proje Haritası uygulaması başlatılıyor...")
    print("  Tarayıcıda açın: http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)
