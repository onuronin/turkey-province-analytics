# Türkiye İl Bazlı Proje Haritası 🗺️

Excel dosyasından il bazlı proje/başvuru sayılarını okuyarak interaktif Türkiye haritası oluşturan Flask web uygulaması.

## Özellikler

- 📊 Excel (`.xlsx`) dosyası yükleyerek veri aktarımı
- 🎨 12 farklı renk skalası seçeneği
- 🏷️ 5 farklı etiket modu (il adı, sayı, her ikisi vb.)
- 🔢 Tüm illeri etiketleme seçeneği
- 🌈 Arka plan, metin, lejant rengi özelleştirme
- 🎭 Şeffaf arka plan desteği
- 📉 Isı haritası çizelgesi (colorbar) açma/kapama
- ❌ Başvurusu olmayan illeri ayrı renk ile gösterme
- 📥 PNG ve PDF olarak dışa aktarma

## Kurulum

### Gereksinimler

- Python 3.10+
- pip

### Adımlar

```bash
# 1. Repoyu klonla
git clone https://github.com/KULLANICI_ADIN/REPO_ADIN.git
cd REPO_ADIN

# 2. Sanal ortam oluştur (önerilir)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Uygulamayı başlat
python app.py
```

Tarayıcıda `http://localhost:5000` adresine git.

## Kullanım

1. **Excel Yükle** — İl adı ve proje sayısı sütunlarını içeren `.xlsx` dosyasını yükle
2. Sütun eşleştirmesini yap (il adı sütunu, sayı sütunu)
3. Renk skalası, etiket modu ve diğer görsel ayarları seç
4. **Haritayı Oluştur** butonuna tıkla
5. İstersen PNG veya PDF olarak indir

### Excel Formatı

| İl Adı | Proje Sayısı |
|--------|-------------|
| Ankara | 42 |
| İstanbul | 87 |
| İzmir | 31 |
| ... | ... |

## Proje Yapısı

```
├── app.py                      # Flask uygulaması (backend)
├── templates/
│   └── index.html              # Tek sayfa arayüz (frontend)
├── turkey_provinces.geojson    # Türkiye il sınırları (GeoJSON)
├── requirements.txt            # Python bağımlılıkları
└── uploads/                    # Yüklenen Excel dosyaları (git'e dahil değil)
```

## Bağımlılıklar

| Kütüphane | Amaç |
|-----------|------|
| `flask` | Web sunucusu ve API |
| `pandas` | Excel okuma ve veri işleme |
| `geopandas` | Coğrafi veri işleme (il koordinatları) |
| `plotly` | İnteraktif choropleth harita |
| `kaleido` | PNG/PDF dışa aktarma |
| `openpyxl` | `.xlsx` dosyası okuma motoru |
| `werkzeug` | Güvenli dosya yükleme |

## Lisans

MIT
