**Yalnızca Türk numaralarına SMS göndermek için geliştirilmiş gelişmiş bir araçtır.**  
GUI ve Termux sürümleri mevcuttur.

---

## 🚀 Özellikler

- 🟩 Matrix temalı modern arayüz (CustomTkinter ile)
- 📊 Toplam gönderilen SMS grafiği (matplotlib)
- 🧪 API Servis Test sekmesi (bozuk servisleri tespit etme)
- 🌐 Proxy desteği (`proxyler.txt`)
  - Proxy'ler rastgele seçilir
  - Hatalı proxy'ler otomatik blacklist'e alınır
- ⚙️ Ayarlar Menüsü:
  - Tema (dark/light/system)
  - Renk teması seçimi (green, blue, dark-blue)
  - Giriş şifresi, log ayarları, bad.json kontrolü
- 🧱 Termux Terminal Sürümü:
  - Menülü kullanım
  - Arayüzsüz sade terminal
  - Turbo mod, sonsuz gönderim, log kontrolü

---

## ⚠️ Uyarı

Bu araç **yalnızca eğitim, test ve kişisel kullanım** amacıyla geliştirilmiştir.  
Tüm kullanım sorumluluğu kullanıcıya aittir.  
Lütfen yasalara uygun şekilde kullanınız.

---

## 📦 Gereksinimler

Python 3.10 veya 3.11 önerilir.  
GUI sürümü için `customtkinter`, `matplotlib`, `colorama`, `requests` gerekir.  
Termux sürümü için sadece `requests` ve `colorama` yeterlidir.

### 🔧 Pip ile tek komutla yükleme:

```bash
pip install colorama requests customtkinter matplotlib
