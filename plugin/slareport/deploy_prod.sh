#!/bin/bash

# GLPI Slareport PRODUCTION Deployment Script (Bash Version)
# Target: ITSM-PROD (10.42.2.149)

HOST_IP="10.42.2.149"
USER="bora"
REMOTE_PATH="/var/www/html/glpi/plugins/slareport"
ZIP_NAME="slareport_prod.zip"

echo -e "\e[31m--- !!! SLA Report PROD YAYINA ALMA BAŞLATILDI !!! ---\e[0m"
echo -e "\e[31mHedef Sunucu: $HOST_IP\e[0m"

# 1. Dosyaları paketleme
echo -e "\e[33m[1/3] Dosyalar paketleniyor...\e[0m"
if command -v zip >/dev/null 2>&1; then
    zip -r $ZIP_NAME . -x ".git/*" ".vscode/*" ".gemini/*" "*.md" "deploy*" "*.zip" "docs/*"
elif command -v powershell.exe >/dev/null 2>&1; then
    echo -e "\e[34mBilgi: 'zip' bulunamadı, PowerShell ile paketleniyor...\e[0m"
    powershell.exe -Command "Get-ChildItem -Exclude '.git', '.vscode', '.gemini', 'docs', 'deploy*', '*.zip', '*.md' | Compress-Archive -DestinationPath '$ZIP_NAME' -Force"
else
    echo -e "\e[31mHATA: Paketleme aracı bulunamadı!\e[0m"
    exit 1
fi

if [ ! -f "$ZIP_NAME" ]; then
    echo -e "\e[31mHATA: $ZIP_NAME oluşturulamadı!\e[0m"
    exit 1
fi

# 2. SCP ile gönderim
echo -e "\e[33m[2/3] PROD Sunucusuna gönderiliyor (Şifre: Glpi**2025)...\e[0m"
scp $ZIP_NAME ${USER}@${HOST_IP}:/tmp/${ZIP_NAME}

if [ $? -ne 0 ]; then
    echo -e "\e[31mHATA: Dosya gönderilemedi!\e[0m"
    rm $ZIP_NAME
    exit 1
fi

# 3. SSH üzerinden çıkarma (sudo şifresi sorulacaktır)
echo -e "\e[33m[3/3] PROD Sunucusunda dosyalar açılıyor...\e[0m"
# -t flag'i sudo şifresi girişi için gerekli TTY'yi sağlar
ssh -t ${USER}@${HOST_IP} "sudo mkdir -p $REMOTE_PATH; sudo unzip -o /tmp/$ZIP_NAME -d $REMOTE_PATH; sudo chown -R www-data:www-data $REMOTE_PATH; sudo rm /tmp/$ZIP_NAME"

if [ $? -ne 0 ]; then
    echo -e "\e[31mHATA: PROD Sunucu işlemleri başarısız!\e[0m"
else
    echo -e "\e[32m--- TAMAMLANDI: PROD Ortamı başarıyla güncellendi! ---\e[0m"
    # Başarılıysa geçici zip'i sil
    rm $ZIP_NAME
fi

read -p "Bitirmek için Enter'a basın..."
