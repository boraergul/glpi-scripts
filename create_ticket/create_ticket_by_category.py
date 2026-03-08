#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLPI Test Ticket Creator by Category
=====================================
Seçilen entity için her ITIL kategorisine ait test ticketları oluşturur.

Kullanım:
    python create_ticket_by_category.py --entity-id 17
    python create_ticket_by_category.py --entity-id 17 --dry-run
"""

import requests
import urllib3
import json
import sys
import os
import argparse
import random
from datetime import datetime

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Config dosyası yolları
CONFIG_PATHS = [
    'config.json',
    '../config/config.json',
    '../../config/config.json'
]

# Kategori bazlı senaryo şablonları
SCENARIO_TEMPLATES = {
    'hardware': [
        {
            'title': 'Laptop Ekran Arızası',
            'content': '''Merhaba,

Kullandığım dizüstü bilgisayarın ekranında dikey çizgiler belirmeye başladı. 
Özellikle sabah ilk açılışta bu durum daha belirgin oluyor.
Ekran parlaklığını ayarladığımda çizgiler artıyor.
Cihazın garanti süresi henüz dolmadı, kontrol edilmesini rica ederim.

Teşekkürler.'''
        },
        {
            'title': 'Klavye Tuş Arızası',
            'content': '''Merhaba,

Masaüstü bilgisayarımın klavyesinde bazı tuşlar çalışmıyor.
Özellikle "E", "R" ve "Space" tuşları bazen yanıt vermiyor.
Bu durum iş verimliliğimi ciddi şekilde etkiliyor.
Yeni bir klavye temini için destek bekliyorum.

Saygılarımla.'''
        },
        {
            'title': 'Monitör Görüntü Problemi',
            'content': '''Merhaba,

Ofisimde kullandığım monitörde görüntü sık sık kesiliyor.
Kablo bağlantılarını kontrol ettim ancak sorun devam ediyor.
Monitör yaklaşık 5 yıllık, değiştirilmesi gerekebilir.
Konuyla ilgilenmenizi rica ederim.

İyi çalışmalar.'''
        }
    ],
    'software': [
        {
            'title': 'Microsoft Office Lisans Hatası',
            'content': '''Merhaba,

Bilgisayarımda Microsoft Office uygulamaları lisans hatası veriyor.
"Ürününüz lisanslanamadı" mesajı alıyorum.
Excel ve Word kullanmam gerekiyor ancak açılmıyor.
Lisans yenileme veya aktivasyon desteği bekliyorum.

Teşekkürler.'''
        },
        {
            'title': 'Yazılım Kurulum Talebi',
            'content': '''Merhaba,

Projemde kullanmam gereken Adobe Acrobat Pro yazılımının kurulmasını talep ediyorum.
PDF düzenleme ve imzalama işlemleri için bu yazılıma ihtiyacım var.
Lisans mevcutsa kurulumun yapılmasını rica ederim.

Saygılarımla.'''
        },
        {
            'title': 'Antivirüs Güncelleme Sorunu',
            'content': '''Merhaba,

Bilgisayarımda kurulu antivirüs yazılımı güncellenemiyor.
"Güncelleme sunucusuna bağlanılamadı" hatası alıyorum.
Güvenlik açısından bu durumun düzeltilmesi kritik.
Yardımcı olmanızı rica ederim.

İyi günler.'''
        }
    ],
    'network': [
        {
            'title': 'İnternet Bağlantı Sorunu',
            'content': '''Merhaba,

Ofisimde internet bağlantısı sık sık kopuyor.
Özellikle öğleden sonra saatlerinde bu problem yaşanıyor.
Video konferans toplantılarında kesintiler oluyor.
Ağ altyapısının kontrol edilmesini talep ediyorum.

Teşekkürler.'''
        },
        {
            'title': 'VPN Bağlantı Hatası',
            'content': '''Merhaba,

Evden çalışırken VPN bağlantısı kuramıyorum.
"Kimlik doğrulama başarısız" hatası alıyorum.
Şifremi sıfırladım ancak sorun devam ediyor.
VPN erişimimin kontrol edilmesini rica ederim.

Saygılarımla.'''
        },
        {
            'title': 'Ağ Yazıcı Erişim Sorunu',
            'content': '''Merhaba,

Departman yazıcısına ağ üzerinden erişemiyorum.
Yazıcı listesinde görünüyor ancak yazdırma komutu çalışmıyor.
Diğer çalışma arkadaşlarımın bu sorunu yaşamadığını öğrendim.
Ağ ayarlarımın kontrol edilmesini istiyorum.

İyi çalışmalar.'''
        }
    ],
    'access': [
        {
            'title': 'Şifre Sıfırlama Talebi',
            'content': '''Merhaba,

Sistem şifremi unuttum ve giriş yapamıyorum.
Şifremi sıfırlamanız gerekiyor.
Acil olarak sisteme erişmem gerekiyor.
Yardımcı olmanızı rica ederim.

Teşekkürler.'''
        },
        {
            'title': 'Dosya Sunucusu Erişim İzni',
            'content': '''Merhaba,

Finans departmanının paylaşımlı klasörüne erişim iznine ihtiyacım var.
Yeni projede bu klasördeki raporları kullanmam gerekiyor.
Yöneticim onay verdi, erişim hakkı tanımlanmasını talep ediyorum.

Saygılarımla.'''
        },
        {
            'title': 'Uygulama Erişim Talebi',
            'content': '''Merhaba,

CRM sistemine erişim yetkisi almam gerekiyor.
Müşteri takibi yapmak için bu sistemi kullanacağım.
Departman müdürümün onayı mevcut.
Kullanıcı hesabı oluşturulmasını rica ederim.

İyi günler.'''
        }
    ],
    'support': [
        {
            'title': 'Genel Teknik Destek Talebi',
            'content': '''Merhaba,

Yeni başladığım için sistemler hakkında bilgi almak istiyorum.
E-posta ayarları ve ağ sürücülerine erişim konusunda yardıma ihtiyacım var.
Kısa bir eğitim veya dokümantasyon paylaşılabilir mi?

Teşekkürler.'''
        },
        {
            'title': 'Yazılım Kullanım Eğitimi',
            'content': '''Merhaba,

Yeni kullanmaya başladığım proje yönetim yazılımı hakkında eğitim almak istiyorum.
Temel özellikleri ve kullanım senaryolarını öğrenmem gerekiyor.
Online veya yüz yüze eğitim imkanı var mı?

Saygılarımla.'''
        },
        {
            'title': 'Sistem Performans Şikayeti',
            'content': '''Merhaba,

Bilgisayarım son günlerde çok yavaş çalışıyor.
Programlar açılırken uzun süre beklemek zorunda kalıyorum.
Disk temizliği yaptım ancak iyileşme olmadı.
Sistem performansının kontrol edilmesini istiyorum.

İyi çalışmalar.'''
        }
    ]
}

def load_config():
    """Config dosyasını yükle"""
    for config_path in CONFIG_PATHS:
        full_path = os.path.join(os.path.dirname(__file__), config_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    raise FileNotFoundError("config.json bulunamadı!")

def init_session(config):
    """GLPI API session başlat"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"user_token {config['GLPI_USER_TOKEN']}",
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    response = requests.get(
        f"{config['GLPI_URL']}/initSession",
        headers=headers,
        verify=False,
        timeout=30
    )
    
    if response.status_code == 200:
        session_token = response.json()['session_token']
        print(f"✓ GLPI session başlatıldı")
        return session_token
    else:
        raise Exception(f"Session başlatılamadı: {response.text}")

def kill_session(config, session_token):
    """GLPI API session kapat"""
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    requests.get(
        f"{config['GLPI_URL']}/killSession",
        headers=headers,
        verify=False,
        timeout=30
    )
    print("✓ Session kapatıldı")

def fetch_entities(config, session_token):
    """Tüm entity'leri çek"""
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    entities = {}
    range_start = 0
    range_size = 1000
    
    print("\nEntity'ler çekiliyor...")
    
    while True:
        response = requests.get(
            f"{config['GLPI_URL']}/Entity",
            headers=headers,
            params={'range': f'{range_start}-{range_start + range_size - 1}'},
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            batch = response.json()
            if not batch:
                break
            
            for entity in batch:
                entities[entity['id']] = entity['completename']
            
            range_start += range_size
        elif response.status_code == 206:
            batch = response.json()
            for entity in batch:
                entities[entity['id']] = entity['completename']
            range_start += range_size
        else:
            break
    
    print(f"✓ {len(entities)} entity bulundu")
    return entities

def fetch_itil_categories(config, session_token):
    """Tüm ITIL kategorilerini çek"""
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    categories = []
    range_start = 0
    range_size = 1000
    
    print("\nITIL kategorileri çekiliyor...")
    
    while True:
        response = requests.get(
            f"{config['GLPI_URL']}/ITILCategory",
            headers=headers,
            params={'range': f'{range_start}-{range_start + range_size - 1}'},
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            batch = response.json()
            if not batch:
                break
            
            for category in batch:
                # Sadece aktif kategorileri al
                if category.get('is_active', 1) == 1:
                    categories.append({
                        'id': category['id'],
                        'name': category['completename'],
                        'comment': category.get('comment', '')
                    })
            
            range_start += range_size
        elif response.status_code == 206:
            batch = response.json()
            for category in batch:
                if category.get('is_active', 1) == 1:
                    categories.append({
                        'id': category['id'],
                        'name': category['completename'],
                        'comment': category.get('comment', '')
                    })
            range_start += range_size
        else:
            break
    
    print(f"✓ {len(categories)} aktif kategori bulundu")
    return categories

def categorize_itil_category(category_name):
    """Kategori adına göre senaryo tipini belirle"""
    name_lower = category_name.lower()
    
    if any(keyword in name_lower for keyword in ['hardware', 'donanım', 'laptop', 'pc', 'monitor', 'printer', 'yazıcı']):
        return 'hardware'
    elif any(keyword in name_lower for keyword in ['software', 'yazılım', 'application', 'uygulama', 'license', 'lisans']):
        return 'software'
    elif any(keyword in name_lower for keyword in ['network', 'ağ', 'internet', 'vpn', 'wifi']):
        return 'network'
    elif any(keyword in name_lower for keyword in ['access', 'erişim', 'permission', 'izin', 'password', 'şifre']):
        return 'access'
    else:
        return 'support'

def generate_scenario(category):
    """Kategori için senaryo üret"""
    category_type = categorize_itil_category(category['name'])
    templates = SCENARIO_TEMPLATES.get(category_type, SCENARIO_TEMPLATES['support'])
    
    # Rastgele bir şablon seç
    scenario = random.choice(templates)
    
    return {
        'title': f"{category['name']} - {scenario['title']}",
        'content': scenario['content']
    }

def create_ticket(config, session_token, entity_id, category, scenario, dry_run=False):
    """Ticket oluştur"""
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    ticket_data = {
        'input': {
            'name': scenario['title'],
            'content': scenario['content'],
            'entities_id': entity_id,
            'itilcategories_id': category['id'],
            'type': 1,  # Request
            'status': 1,  # New
            'urgency': 3,  # Medium
            'impact': 3,  # Medium
            'priority': 3  # Medium
        }
    }
    
    if dry_run:
        print(f"  [DRY-RUN] Ticket oluşturulacak: {scenario['title']}")
        return True
    
    response = requests.post(
        f"{config['GLPI_URL']}/Ticket",
        headers=headers,
        json=ticket_data,
        verify=False,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        ticket_id = response.json().get('id')
        print(f"  ✓ Ticket #{ticket_id} oluşturuldu: {scenario['title']}")
        return True
    else:
        print(f"  ✗ Hata: {response.status_code} - {response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description='GLPI Test Ticket Creator by Category')
    parser.add_argument('--entity-id', type=int, help='Entity ID')
    parser.add_argument('--dry-run', action='store_true', help='Değişiklik yapmadan test et')
    
    args = parser.parse_args()
    
    try:
        # Config yükle
        config = load_config()
        
        # Session başlat
        session_token = init_session(config)
        
        # Entity'leri çek
        entities = fetch_entities(config, session_token)
        
        # Entity seçimi
        if args.entity_id:
            entity_id = args.entity_id
            if entity_id not in entities:
                print(f"✗ Entity ID {entity_id} bulunamadı!")
                kill_session(config, session_token)
                return
        else:
            print("\n=== Entity Seçimi ===")
            sorted_entities = sorted(entities.items(), key=lambda x: x[1])
            for idx, (eid, ename) in enumerate(sorted_entities[:20], 1):
                print(f"{idx}. [{eid}] {ename}")
            
            choice = input("\nEntity numarasını girin (1-20): ")
            try:
                entity_id = sorted_entities[int(choice) - 1][0]
            except (ValueError, IndexError):
                print("✗ Geçersiz seçim!")
                kill_session(config, session_token)
                return
        
        entity_name = entities[entity_id]
        print(f"\n✓ Seçilen Entity: {entity_name} (ID: {entity_id})")
        
        # ITIL kategorilerini çek
        categories = fetch_itil_categories(config, session_token)
        
        if not categories:
            print("✗ Hiç kategori bulunamadı!")
            kill_session(config, session_token)
            return
        
        # Her kategori için ticket oluştur
        print(f"\n{'='*80}")
        print(f"{'DRY-RUN MODE - ' if args.dry_run else ''}Ticket Oluşturma Başlıyor")
        print(f"{'='*80}\n")
        
        success_count = 0
        fail_count = 0
        
        for category in categories:
            print(f"\n📋 Kategori: {category['name']}")
            scenario = generate_scenario(category)
            
            if create_ticket(config, session_token, entity_id, category, scenario, args.dry_run):
                success_count += 1
            else:
                fail_count += 1
        
        # Özet
        print(f"\n{'='*80}")
        print(f"ÖZET")
        print(f"{'='*80}")
        print(f"Toplam Kategori: {len(categories)}")
        print(f"Başarılı: {success_count}")
        print(f"Başarısız: {fail_count}")
        print(f"{'='*80}\n")
        
        # Session kapat
        kill_session(config, session_token)
        
    except Exception as e:
        print(f"\n✗ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
