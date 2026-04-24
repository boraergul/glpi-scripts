#!/bin/bash

# GLPI Slareport Deployment Script (Bash Version)

HOST_IP="10.42.2.146"
USER="glpi"
REMOTE_PATH="/var/www/glpi/plugins/slareport"
ZIP_NAME="slareport.zip"

echo -e "\e[36m--- SLA Report Yayına Alma Başlatıldı (Bash) ---\e[0m"

# 1. Dosyaları paketleme
echo -e "\e[33m[1/3] Dosyalar paketleniyor...\e[0m"
if command -v zip >/dev/null 2>&1; then
    zip -r $ZIP_NAME . -x ".git/*" ".vscode/*" ".gemini/*" "*.md" "deploy.*" "slareport.zip"
elif command -v powershell.exe >/dev/null 2>&1; then
    echo -e "\e[34mBilgi: 'zip' bulunamadı, PowerShell ile paketleniyor...\e[0m"
    powershell.exe -Command "Get-ChildItem -Exclude '.git', '.vscode', '.gemini', '*.md', 'deploy.*', '$ZIP_NAME' | Compress-Archive -DestinationPath '$ZIP_NAME' -Force"
else
    echo -e "\e[34mBilgi: Paketleme aracı bulunamadı, mevcut slareport.zip kullanılıyor.\e[0m"
fi

if [ ! -f "$ZIP_NAME" ]; then
    echo -e "\e[31mHATA: $ZIP_NAME bulunamadı!\e[0m"
    exit 1
fi

# 2. SCP ile gönderim
echo -e "\e[33m[2/3] Sunucuya gönderiliyor (Şifre: Glpi**2025)...\e[0m"
scp $ZIP_NAME ${USER}@${HOST_IP}:/tmp/${ZIP_NAME}

if [ $? -ne 0 ]; then
    echo -e "\e[31mHATA: Dosya gönderilemedi!\e[0m"
    exit 1
fi

# 3. SSH üzerinden çıkarma (sudo şifresi sorulacaktır)
echo -e "\e[33m[3/3] Sunucuda dosyalar açılıyor...\e[0m"
# -t flag'i sudo şifresi girişi için gerekli TTY'yi sağlar
ssh -t ${USER}@${HOST_IP} "sudo mkdir -p $REMOTE_PATH; sudo unzip -o /tmp/$ZIP_NAME -d $REMOTE_PATH; sudo chown -R www-data:www-data $REMOTE_PATH; sudo rm /tmp/$ZIP_NAME"

if [ $? -ne 0 ]; then
    echo -e "\e[31mHATA: Sunucu işlemleri başarısız!\e[0m"
else
    echo -e "\e[32m--- TAMAMLANDI: Eklenti başarıyla güncellendi! ---\e[0m"
    # Başarılıysa geçici zip'i sil
    rm $ZIP_NAME
fi

read -p "Devam etmek için Enter'a basın..."
