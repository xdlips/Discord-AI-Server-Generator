# AI Discord Server Setup

AI destekli terminal uygulaması. Discord sunucularını doğal dil konuşmasıyla tasarlar ve otomatik olarak kurar.

![Ana Menü](assets/preview_menu.png)

## Özellikler

- **AI ile tasarım** — Sunucunu sade bir dille tanımla, AI gerekli soruları sorar ve her şeyi kurar
- **Mevcut sunucu düzenleme** — Ne değiştirmek istediğini söyle, AI farkları tespit edip uygular
- **Config'den yeniden kurulum** — Kayıtlı yapılandırmaları farklı sunuculara kolayca uygula
- **Export / Import** — Config dosyalarını JSON olarak paylaş veya içe aktar
- **Tam izin desteği** — Thread, ses, etkinlik, soundboard dahil tüm Discord izin bayrakları
- **Doğru rol sıralaması** — Roller Discord hiyerarşisinde doğru konuma otomatik yerleştirilir
- **Kullanıcı & bot token** — Hem kişisel hesap token'ı hem bot token'ıyla çalışır
- **Türkçe & İngilizce** — Tam arayüz çevirisi

---

## Gereksinimler

- Python 3.11 veya üzeri
- [OpenRouter](https://openrouter.ai) API anahtarı
- Discord kullanıcı token'ı veya bot token'ı

---

## Kurulum

```bash
git clone https://github.com/xdlips/ai-discord-setup
cd ai-discord-setup
pip install -r requirements.txt
```

`.env.example` dosyasını `.env` olarak kopyala ve doldur:

```env
OPENROUTER_API_KEY=sk-or-...
MODEL=openai/gpt-oss-120b:free
```

Çalıştır:

```bash
python main.py
```

---

## Önerilen Model

```
openai/gpt-oss-120b:free
```

---

## Kullanım

### 1 — Yeni sunucu kurulumu

Menüden **Kurulum** seçeneğini aç, Discord token'ını ve sunucu ID'ni gir, ardından istediğin sunucuyu sade bir metinle tanımla.

![Kurulum Ekranı](assets/preview_setup.png)

AI gerekirse ek sorular sorar, sonrasında tam yapılandırmayı üretir. Onaylamadan önce özet (kaç rol, kaç kanal) gösterilir.

![Kurulum Süreci](assets/preview_build.png)

### 2 — Mevcut sunucuyu düzenleme

**Düzenle** seçeneğiyle daha önce kurulmuş bir sunucuyu seç ya da direkt ID gir. Ne değiştirmek istediğini açıkla — kanal ekle/sil, izinleri güncelle, rol düzenle — AI sadece değişen kısmı hesaplayıp uygular.

### 3 — Kayıtlı config'den yeniden kurulum

**Yeniden Kur** seçeneğiyle daha önce kaydedilen yapılandırmayı aynı sunucuya ya da tamamen farklı bir sunucuya uygula.

### 4 — Kayıtlı config yönetimi

![Config Yönetimi](assets/preview_configs.png)

Kayıtlı yapılandırmaları görüntüle, JSON olarak dışa aktar, hazır bir JSON'ı içe aktar veya sil.

---

## Token nasıl alınır?

**Kullanıcı token'ı (kişisel hesap):**
Discord'u tarayıcıda aç → F12 ile DevTools → Network sekmesi → sayfayı yenile → `discord.com/api` adresine giden herhangi bir istek → `Authorization` header değerini kopyala.

**Bot token'ı:**
[discord.com/developers](https://discord.com/developers/applications) adresinde uygulama oluştur → Bot ekle → token'ı kopyala. Botun sunucuya yeterli yetkiyle davet edilmiş olduğundan emin ol.

> ⚠️ Token'larını asla paylaşma. Kullanıcı token'ı hesabına tam erişim sağlar.

---

## Sunucu ID nasıl alınır?

Discord Ayarları → Gelişmiş → Geliştirici Modu'nu etkinleştir. Sunucu ikonuna sağ tıkla → **Sunucu ID'sini Kopyala**.

---

## Lisans

MIT
