# BIST Portföy Yönetim Botu

Telegram üzerinden BIST hisse senedi portföyünüzü yönetebileceğiniz, alarm kurabileceğiniz ve takip edebileceğiniz kapsamlı bir sistem.

## 🚀 Yeni Özellikler

📊 **Detaylı Raporlama**
- Hisse bazında detaylı performans analizi
- Günlük kapanış raporları
- Oynaklık analizi
- Portföy ağırlıklandırması

🔔 **Akıllı Bildirimler**
- Ani fiyat hareketleri bildirimleri
- Oynaklık alarmları
- Otomatik günlük/kapanış raporları
- Kişiselleştirilebilir ayarlar

⚙️ **Ayarlar Sistemi**
- Bildirim tercihleri
- Rapor saatleri
- Eşik değerleri
- Kişiselleştirme

## Özellikler

📊 **Portföy Yönetimi**
- Hisse ekleme/çıkarma
- Anlık kar/zarar takibi
- Portföy değeri hesaplama
- İşlem geçmişi

🔔 **Alarm Sistemi**
- Fiyat alarmı kurma (üstü/altı)
- Otomatik bildirimler
- Çoklu alarm desteği
- Oynaklık alarmları

📈 **Hisse Bilgileri**
- Anlık fiyat takibi
- BIST 30 listesi
- Detaylı hisse bilgileri
- Gün içi en yüksek/düşük

📋 **Raporlama**
- Detaylı portföy raporu
- Günlük kapanış raporu
- Performans analizi
- En iyi/en zayıf performans

☁️ **Bulut Senkronizasyonu**
- GitHub ile veri senkronizasyonu
- Otomatik yedekleme
- Çoklu cihaz desteği

## Kurulum

### 1. Repository'yi Klonlama
```bash
git clone https://github.com/b_ozgur/bist-portfolio.git
cd bist-portfolio
```

### 2. Python Bağımlılıkları
```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenleri
`.env.example` dosyasını kopyalayın ve düzenleyin:
```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GITHUB_REPO_USERNAME=lenovo77tablet77tr
GITHUB_REPO_NAME=bist-portfolio
GITHUB_TOKEN=github_personal_access_tokenunuz
ADMIN_USER_ID=496807443
```

### 4. Telegram Bot Token Alma
1. [@BotFather](https://t.me/botfather) ile yeni bot oluşturun
2. `/newbot` komutu ile bot oluşturun
3. Token'ı kopyalayın ve `.env` dosyasına ekleyin

### 5. GitHub Personal Access Token Alma
1. GitHub hesabınızda Settings → Developer settings → Personal access tokens
2. Generate new token (repo权限)
3. Token'ı kopyalayın ve `.env` dosyasına ekleyin

## Kullanım

### Bot Komutları

**Temel Komutlar:**
- `/start` - Başlangıç ve yardım
- `/yardım` - Yardım menüsü
- `/portföy` - Portföyünüzü görüntüle
- `/detaylı_rapor` - Detaylı portföy raporu
- `/kapanış_raporu` - Günlük kapanış raporu

**Portföy İşlemleri:**
- `/ekle <hisse> <adet> <fiyat>` - Hisse ekle
- `/sat <hisse> <adet> [fiyat]` - Hisse sat
- `/alarm <hisse> <fiyat> <tip>` - Alarm kur
- `/alarmlar` - Aktif alarmlarınız

**Bilgi ve Ayarlar:**
- `/bilgi <hisse>` - Hisse bilgileri
- `/hisseler` - BIST 30 listesi
- `/fiyat <hisse>` - Anlık fiyat
- `/ayarlar` - Bildirim ayarlarınız
- `/ayarla <özellik> <değer>` - Ayarları değiştir

### Örnek Kullanım

```
/ekle GARAN 100 45.50
/alarm THYAO 150.00 üstü
/sat ASELS 50 85.75
/detaylı_rapor
/ayarla oynaklık_eşiği 3.0
/ayarla günlük_rapor evet
```

### Ayarlar

Kişiselleştirilebilir ayarlar:
- **Günlük Rapor**: Otomatik günlük portföy raporu
- **Kapanış Raporu**: Piyasa kapanışında rapor
- **Fiyat Alarmları**: Fiyat alarm bildirimleri
- **Oynaklık Alarmları**: Ani fiyat hareketleri
- **Rapor Saati**: Raporların gönderileceği saat
- **Oynaklık Eşiği**: Oynaklık alarm yüzdesi
- **Fiyat Değişim Eşiği**: Fiyat değişim alarm yüzdesi

## GitHub Actions ile Otomatik Çalışma

### 1. Repository Secrets
GitHub repository'nizde Settings → Secrets and variables → Actions bölümüne aşağıdaki secret'ları ekleyin:

- `TELEGRAM_BOT_TOKEN`: `8521102221:AAEJrpjEUgMEEBIPl-bzkd8sUGU_U1Tsyd8`
- `GITHUB_REPO_USERNAME`: `b_ozgur`
- `GITHUB_REPO_NAME`: `bist-portfolio`
- `GITHUB_TOKEN`: GitHub personal access token
- `ADMIN_USER_ID`: `496807443`

### 2. Workflow'lar
- `deploy.yml` - Botu çalıştırır
- `scheduler.yml` - Her 5 dakikada bir alarmları kontrol eder
- `reports.yml` - Günlük ve kapanış raporları gönderir

### 3. Otomatik Çalışma
Repository'ye push yaptığınızda bot otomatik olarak başlar ve:
- Piyasa saatlerinde alarmları kontrol eder
- Günlük raporları gönderir (09:00)
- Kapanış raporlarını gönderir (18:00)
- Verileri GitHub ile senkronize eder

## Proje Yapısı

```
bist-portfolio/
├── src/
│   ├── telegram_bot.py      # Telegram bot ana kodu
│   ├── portfolio_manager.py # Portföy yönetimi
│   └── github_sync.py       # GitHub senkronizasyonu
├── data/
│   ├── portfolio.json       # Portföy verileri
│   ├── alarms.json          # Alarm verileri
│   ├── settings.json        # Kullanıcı ayarları
│   └── market_data.json     # Piyasa verileri
├── config/
│   └── bist_stocks.json     # BIST 30 hisse listesi
├── .github/workflows/       # GitHub Actions
├── main.py                  # Ana uygulama
├── requirements.txt         # Python bağımlılıkları
└── README.md               # Bu dosya
```

## Veri Depolama

Tüm veriler GitHub repository'sinde JSON formatında saklanır:
- `data/portfolio.json` - Kullanıcı portföyleri
- `data/alarms.json` - Kullanıcı alarmları
- `data/settings.json` - Kullanıcı ayarları
- `data/market_data.json` - Piyasa verileri ve geçmiş

Bu sayede:
- Verileriniz güvende
- Herhangi bir cihazdan erişilebilir
- Otomatik yedekleme
- Versiyon kontrolü

## Güvenlik

- Bot token'ları güvenli saklanır
- Veriler şifrelenmiş GitHub'da depolanır
- Admin yetkileri ile kontrol
- GitHub Actions güvenliği

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit yapın (`git commit -am 'Yeni özellik eklendi'`)
4. Push yapın (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## Lisans

MIT License

## Destek

Sorularınız için:
- GitHub Issues
- Telegram: @b_ozgur

---

**Not:** Bu proje sadece eğitim amaçlıdır ve yatırım tavsiyesi içermez.
