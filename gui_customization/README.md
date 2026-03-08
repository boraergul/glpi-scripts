# GLPI GUI Customization

Bu CSS dosyası, GLPI arayüzünü özelleştirmek için kullanılır. Ultron logolarını ve arka plan görselini GLPI'a entegre eder.

## 📋 Özellikler

### 1. **Giriş Ekranı Logosu**
- GLPI giriş sayfasındaki varsayılan logo yerine Ultron logosu gösterilir
- Boyut: 300x90px
- Pozisyon: Ortalanmış

### 2. **Ana Sayfa Arka Plan Görseli**
- Giriş ekranı hariç tüm sayfalarda arka planda Ultron favicon gösterilir
- Boyut: 150x150px
- Pozisyon: Ekran ortasında sabit (scroll ile hareket etmez)

### 3. **Ana Menü Logosu (Açık Menü)**
- Sol üst köşedeki logo (menü açıkken)
- Boyut: 200x55px
- Ultron logosu kullanılır

### 4. **Mini Menü İkonu (Kapalı Menü)**
- Menü kapalıyken gösterilen küçük ikon
- Boyut: 50x50px
- Ultron favicon kullanılır

---

## 🚀 Kurulum

### Yöntem 1: GLPI UI Customization (Önerilen)

1. GLPI yönetici paneline giriş yapın
2. **Setup → General → Display** menüsüne gidin
3. **CSS** sekmesine tıklayın
4. `gui_customization.css` dosyasının içeriğini kopyalayıp yapıştırın
5. Değişiklikleri kaydedin
6. Tarayıcınızı yenileyin (Ctrl+F5)

### Yöntem 2: CSS Dosyası Yükleme

1. `gui_customization.css` dosyasını GLPI sunucusuna yükleyin:
   ```
   /var/www/html/glpi/css/gui_customization.css
   ```

2. GLPI yapılandırma dosyasında (`config/config_db.php`) CSS dosyasını referans verin

3. Tarayıcı önbelleğini temizleyin

---

## 🖼️ Kullanılan Görseller

| Görsel | URL | Kullanım Yeri |
|--------|-----|---------------|
| Ultron Logosu | `https://itsm.ultron.com.tr/front/document.send.php?docid=6` | Giriş ekranı, ana menü logosu |
| Ultron Favicon | `https://nportal.ultron.com.tr/tenant-favicons/1758833178_68d5aa1acf196.png` | Arka plan, mini menü ikonu |

> **Not:** Görsellerin erişilebilir olduğundan emin olun. Harici URL'ler kullanıldığı için internet bağlantısı gereklidir.

---

## 🔧 Özelleştirme

### Logo Boyutlarını Değiştirme

**Giriş Ekranı Logosu:**
```css
body.login-page #login-logo {
    width: 300px !important;  /* Genişlik */
    height: 90px !important;  /* Yükseklik */
}
```

**Ana Menü Logosu:**
```css
span.glpi-logo {
    width: 200px !important;  /* Genişlik */
    height: 55px !important;  /* Yükseklik */
}
```

### Arka Plan Görsel Boyutu:
```css
body:not(.login-page) {
    background-size: 150px 150px;  /* Genişlik x Yükseklik */
}
```

### Logo URL'lerini Değiştirme

CSS dosyasında `background-image: url("...")` satırlarını bulup kendi logo URL'lerinizi yazın.

---

## ⚠️ Önemli Notlar

1. **GLPI Güncellemeleri:** GLPI güncellendiğinde CSS sınıf isimleri değişebilir. Bu durumda CSS dosyasını güncellemeniz gerekebilir.

2. **Tarayıcı Önbelleği:** Değişiklikleri görmek için tarayıcı önbelleğini temizleyin (Ctrl+Shift+Delete) veya hard refresh yapın (Ctrl+F5).

3. **Harici URL Bağımlılığı:** Logolar harici sunuculardan çekildiği için internet bağlantısı gereklidir. Lokal kurulumlar için görselleri GLPI sunucusuna yükleyip lokal URL kullanın.

4. **!important Kullanımı:** CSS'te `!important` kullanılarak GLPI'ın varsayılan stilleri ezilmiştir. Bu, tema değişikliklerinde sorun yaratabilir.

---

## 🐛 Sorun Giderme

### Logolar Görünmüyor
- Tarayıcı konsolunu açın (F12) ve ağ (Network) sekmesinde görsel URL'lerinin yüklenip yüklenmediğini kontrol edin
- Görsellerin erişilebilir olduğundan emin olun (URL'leri tarayıcıda açmayı deneyin)

### CSS Değişiklikleri Uygulanmıyor
- Tarayıcı önbelleğini temizleyin (Ctrl+Shift+Delete)
- Hard refresh yapın (Ctrl+F5)
- GLPI'da CSS'in doğru şekilde kaydedildiğini kontrol edin

### Menü Logosu Bozuk Görünüyor
- Logo boyutlarını ayarlayın
- `background-size: contain` özelliği logo oranlarını korur

---

## 📝 Versiyon Geçmişi

| Versiyon | Tarih | Değişiklikler |
|----------|-------|---------------|
| 1.0 | 2025-12-28 | İlk sürüm - Logo değiştirme ve arka plan ekleme |

---

## 📞 Destek

Sorunlar veya öneriler için IT ekibiyle iletişime geçin.

---

**Hazırlayan:** IT Ekibi  
**Son Güncelleme:** 28 Aralık 2025
