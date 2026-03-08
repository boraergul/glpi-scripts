
import os

# HTML Boilerplate
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #2c3e50;
            color: #ffffff;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .footer {{
            background-color: #ecf0f1;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            margin: 20px 0;
            background-color: #3498db;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }}
        .info-box {{
            background-color: #e8f6f3;
            border-left: 4px solid #1abc9c;
            padding: 15px;
            margin: 15px 0;
        }}
        .alert-box {{
            background-color: #fcebeb;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 15px 0;
        }}
        .table-data {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .table-data th, .table-data td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
            text-align: left;
        }}
        .table-data th {{
            background-color: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ultron Bilişim A.Ş.</h1>
        </div>
        <div class="content">
            {body}
        </div>
        <div class="footer">
            <p>&copy; 2026 Ultron Bilişim A.Ş. All rights reserved.</p>
            <p>Bu e-posta otomatik olarak oluşturulmuştur. Lütfen yanıtlamayınız.<br>This email was generated automatically. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""

# Template Definitions
TEMPLATES = {
    "proactive_alarm_first": {
        "tr": {
            "subject": "Proaktif Alarm: ##ticket.title##",
            "body": """
            <p>Merhaba ##ticket.authors##,</p>
            <p>Monitoring sistemlerimiz bir alarm tespit etti ###ticket.id##</p>

            <table class="table-data">
                <tr><th>Alarm Tipi:</th><td>##ticket.title##</td></tr>
                <tr><th>Tespit Zamanı:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Etkilenen Sistem:</th><td>##ticket.category##</td></tr>
                <tr><th>Öncelik Seviyesi:</th><td>##ticket.priority##</td></tr>
                <tr><th>SLA Hedefi:</th><td>##ticket.sla_ttr##</td></tr>
                <tr><th>Durumu:</th><td>##ticket.status##</td></tr>
            </table>

            <div class="info-box">
                <strong>ALARM AÇIKLAMASI:</strong>
                <p>##ticket.content##</p>
            </div>

            <div class="info-box">
                <strong>ATILAN ADIMLAR:</strong>
                <p>iNOC ekibimiz alarm üzerinde çalışmaya başlamıştır. İlk değerlendirme ve müdahale devam etmektedir.</p>
            </div>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">Talebi Görüntüle</a>
        </p>
        """
        },
        "en": {
            "subject": "Proactive Alarm: ##ticket.title##",
            "body": """
            <p>Hello ##ticket.authors##,</p>
            <p>Our monitoring systems detected an alarm ###ticket.id##</p>

            <table class="table-data">
                <tr><th>Alarm Type:</th><td>##ticket.title##</td></tr>
                <tr><th>Detection Time:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Affected System:</th><td>##ticket.category##</td></tr>
                <tr><th>Priority Level:</th><td>##ticket.priority##</td></tr>
                <tr><th>SLA Target:</th><td>##ticket.sla_ttr##</td></tr>
                <tr><th>Status:</th><td>##ticket.status##</td></tr>
            </table>

            <div class="info-box">
                <strong>ALARM DESCRIPTION:</strong>
                <p>##ticket.content##</p>
            </div>

            <div class="info-box">
                <strong>ACTIONS TAKEN:</strong>
                <p>Our iNOC team has started working on the alarm. Initial assessment and intervention are in progress.</p>
            </div>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">View Ticket</a>
        </p>
            """
        }
    },
    "proactive_alarm_resolution": {
        "tr": {
            "subject": "Çözüldü - ##ticket.title##",
            "body": """
            <p>Merhaba ##ticket.authors##,</p>
            <p>Çözüm kaydı oluşturuldu ###ticket.id##</p>

            <table class="table-data">
                <tr><th>Konu:</th><td>##ticket.title##</td></tr>
                <tr><th>Oluşturma Tarihi:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Destek Uzmanı:</th><td>##ticket.assigntogroups##</td></tr>
                <tr><th>Durumu:</th><td>##ticket.status##</td></tr>
                <tr><th>Müşteri:</th><td>##ticket.shortentity##</td></tr>
                <tr><th>Cevap Yazan Temsilci:</th><td>##ticket.solution.author##</td></tr>
            </table>

            <br>
            <h3>ÇÖZÜM BİLGİSİ:</h3>
            <p>##ticket.solution.description##</p>
            
            <div class="info-box">
                <ul style="list-style-type: none; padding: 0;">
                     <li><strong>Çözüm Tarihi:</strong> ##ticket.solvedate##</li>
                     <li><strong>Çözüm Süresi:</strong> ##ticket.time##</li>
                </ul>
            </div>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">Talebi Görüntüle</a>
        </p>
            """
        },
        "en": {
            "subject": "Resolved - ##ticket.title##",
            "body": """
            <p>Hello ##ticket.authors##,</p>
            <p>Resolution record created ###ticket.id##</p>

            <table class="table-data">
                <tr><th>Subject:</th><td>##ticket.title##</td></tr>
                <tr><th>Creation Date:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Support Specialist:</th><td>##ticket.assigntogroups##</td></tr>
                <tr><th>Status:</th><td>##ticket.status##</td></tr>
                <tr><th>Customer:</th><td>##ticket.shortentity##</td></tr>
                <tr><th>Responding Agent:</th><td>##ticket.solution.author##</td></tr>
            </table>

            <br>
            <h3>RESOLUTION DETAILS:</h3>
            <p>##ticket.solution.description##</p>
            
            <div class="info-box">
                <ul style="list-style-type: none; padding: 0;">
                     <li><strong>Resolution Date:</strong> ##ticket.solvedate##</li>
                     <li><strong>Resolution Time:</strong> ##ticket.time##</li>
                </ul>
            </div>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">View Ticket</a>
        </p>
            """
        }
    },
    "ticket_opening_confirmation": {
        "tr": {
            "subject": "Destek Talebiniz Alındı - ##ticket.title##",
            "body": """
            <p>Merhaba ##ticket.authors##,</p>
            <p>Yeni destek talebi oluşturuldu ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Konu:</th><td>##ticket.title##</td></tr>
                <tr><th>Oluşturma Tarihi:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Destek Uzmanı:</th><td>##ticket.assigntogroups##</td></tr>
                <tr><th>Durumu:</th><td>##ticket.status##</td></tr>
                <tr><th>Müşteri:</th><td>##ticket.shortentity##</td></tr>
                <tr><th>Öncelik:</th><td>##ticket.priority##</td></tr>
                <tr><th>Kategori:</th><td>##ticket.category##</td></tr>
            </table>

            <div class="info-box">
                <strong>PROBLEM AÇIKLAMASI:</strong>
                <p>##ticket.content##</p>
            </div>

            <div class="info-box">
                <strong>BİLGİLENDİRME:</strong>
                <p>Sözleşmeli müşterilerimiz için sözleşme kapsamındaki SLA sürelerine uygun olarak dönüş sağlanmaktadır, sözleşmeniz yok ise ilgili departmandaki uzmanlarımız sizlerle ilk müsait olduklarında iletişime geçecektir.</p>
            </div>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">Talebi Görüntüle</a>
        </p>
            """
        },
        "en": {
            "subject": "Support Request Received - ##ticket.title##",
            "body": """
            <p>Hello ##ticket.authors##,</p>
            <p>New support request created ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Subject:</th><td>##ticket.title##</td></tr>
                <tr><th>Creation Date:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Support Specialist:</th><td>##ticket.assigntogroups##</td></tr>
                <tr><th>Status:</th><td>##ticket.status##</td></tr>
                <tr><th>Customer:</th><td>##ticket.shortentity##</td></tr>
                <tr><th>Priority:</th><td>##ticket.priority##</td></tr>
                <tr><th>Category:</th><td>##ticket.category##</td></tr>
            </table>

            <div class="info-box">
                <strong>PROBLEM DESCRIPTION:</strong>
                <p>##ticket.content##</p>
            </div>

            <div class="info-box">
                <strong>INFORMATION:</strong>
                <p>For our contracted customers, responses are provided in accordance with the SLA periods within the scope of the contract. If you do not have a contract, our specialists in the relevant department will contact you as soon as they are available.</p>
            </div>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">View Ticket</a>
        </p>
            """
        }
    },
    "status_update": {
        "tr": {
            "subject": "Durum Güncellemesi - ##ticket.title##",
            "body": """
            <p>Merhaba ##ticket.authors##,</p>
            <p>Yeni etkinlik kaydı oluşturuldu ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Konu:</th><td>##ticket.title##</td></tr>
                <tr><th>Oluşturma Tarihi:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Destek Uzmanı:</th><td>##ticket.assigntogroups##</td></tr>
                <tr><th>Durumu:</th><td>##ticket.status##</td></tr>
                <tr><th>Müşteri:</th><td>##ticket.shortentity##</td></tr>
                <tr><th>Cevap Yazan Temsilci:</th><td>##ticket.lastupdater##</td></tr>
            </table>

            <div class="info-box">
                <strong>GÜNCEL DURUM:</strong>
                <p>##IFfollowup####followup.content####ENDIFfollowup##</p>
            </div>

            <div class="info-box" style="margin-top: 15px; border-left-color: #3498db;">
                <strong>SON İŞLEMLER / RECENT ACTIVITY:</strong>
                <ul style="padding-left: 20px; margin-top: 10px;">
                ##FOREACHtimelineitems##
                    <li style="margin-bottom: 10px;">
                        <strong>##timelineitems.date## - ##timelineitems.author##:</strong><br>
                        ##timelineitems.description##
                    </li>
                ##ENDFOREACHtimelineitems##
                </ul>
            </div>


            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">Talebi Görüntüle</a>
        </p>
            """
        },
        "en": {
            "subject": "Status Update - ##ticket.title##",
            "body": """
            <p>Hello ##ticket.authors##,</p>
            <p>New activity record created ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Subject:</th><td>##ticket.title##</td></tr>
                <tr><th>Creation Date:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Support Specialist:</th><td>##ticket.assigntogroups##</td></tr>
                <tr><th>Status:</th><td>##ticket.status##</td></tr>
                <tr><th>Customer:</th><td>##ticket.shortentity##</td></tr>
                <tr><th>Responding Agent:</th><td>##ticket.lastupdater##</td></tr>
            </table>

            <div class="info-box">
                <strong>CURRENT STATUS:</strong>
                <p>##IFfollowup####followup.content####ENDIFfollowup##</p>
            </div>

            <div class="info-box" style="margin-top: 15px; border-left-color: #3498db;">
                <strong>RECENT ACTIVITY:</strong>
                <ul style="padding-left: 20px; margin-top: 10px;">
                ##FOREACHtimelineitems##
                    <li style="margin-bottom: 10px;">
                        <strong>##timelineitems.date## - ##timelineitems.author##:</strong><br>
                        ##timelineitems.description##
                    </li>
                ##ENDFOREACHtimelineitems##
                </ul>
            </div>


            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">View Ticket</a>
        </p>
            """
        }
    },
    "major_incident_announcement": {
        "tr": {
            "subject": "[MAJOR INCIDENT] ##ticket.title##",
            "body": """
            <div class="alert-box" style="text-align: center;">
                <h2>⚠️ MAJOR INCIDENT DUYURUSU</h2>
            </div>
            
            <p>Sayın ##ticket.authors##,</p>
            <p>Kritik bir olay tespit edilmiş ve Major Incident prosedürü başlatılmıştır.</p>
            
            <h3>INCIDENT DETAYLARI:</h3>
            <ul style="list-style-type: none;">
                <li><strong>Incident ID:</strong> ##ticket.id##</li>
                <li><strong>Başlangıç Zamanı:</strong> ##ticket.creationdate##</li>
                <li><strong>Etkilenen Servisler:</strong> ##ticket.category##</li>
            </ul>

            <div class="info-box">
                <strong>GÜNCEL DURUM:</strong>
                <p>##ticket.content##</p>
            </div>

            <h3>ÇALIŞAN EKİP:</h3>
            <ul>
                <li>Major Incident Manager: ##ticket.assigntousers##</li>
            </ul>

            <p><strong>GÜNCELLEME SIKLIĞI:</strong> 15 dakikada bir güncelleme yapılacaktır.</p>

            <a href="##ticket.url##" class="button" style="background-color: #e74c3c;">War Room Linki</a>

            <p>Bu kritik durumda sabır ve anlayışınız için teşekkür ederiz.</p>
            <p><strong>Ultron Bilişim Major Incident Ekibi</strong></p>
            """
        },
        "en": {
            "subject": "[MAJOR INCIDENT] ##ticket.title##",
            "body": """
            <div class="alert-box" style="text-align: center;">
                <h2>⚠️ MAJOR INCIDENT ANNOUNCEMENT</h2>
            </div>
            
            <p>Dear ##ticket.authors##,</p>
            <p>A critical incident has been detected and the Major Incident procedure has been initiated.</p>
            
            <h3>INCIDENT DETAILS:</h3>
            <ul style="list-style-type: none;">
                <li><strong>Incident ID:</strong> ##ticket.id##</li>
                <li><strong>Start Time:</strong> ##ticket.creationdate##</li>
                <li><strong>Affected Services:</strong> ##ticket.category##</li>
            </ul>

            <div class="info-box">
                <strong>CURRENT STATUS:</strong>
                <p>##ticket.content##</p>
            </div>

            <h3>HANDLING TEAM:</h3>
            <ul>
                <li>Major Incident Manager: ##ticket.assigntousers##</li>
            </ul>

            <p><strong>UPDATE FREQUENCY:</strong> Updates will be provided every 15 minutes.</p>

            <a href="##ticket.url##" class="button" style="background-color: #e74c3c;">War Room Link</a>

            <p>We appreciate your patience and understanding in this critical situation.</p>
            <p><strong>Ultron Bilişim Major Incident Team</strong></p>
            """
        }
    },
    "major_incident_update": {
        "tr": {
            "subject": "[MAJOR INCIDENT] Güncelleme - ##ticket.title##",
            "body": """
            <div class="alert-box">
                <strong>MAJOR INCIDENT GÜNCELLEMESİ</strong>
            </div>

            <p>Sayın ##ticket.authors##,</p>
            <p>Devam eden major incident hakkında son güncelleme:</p>
            
            <div class="info-box">
                <strong>GÜNCEL DURUM:</strong>
                <p>##IFfollowup####followup.content####ENDIFfollowup##</p>
            </div>

            <div class="info-box" style="margin-top: 15px; border-left-color: #3498db;">
                <strong>SON İŞLEMLER / RECENT ACTIVITY:</strong>
                <ul style="padding-left: 20px; margin-top: 10px;">
                ##FOREACHtimelineitems##
                    <li style="margin-bottom: 10px;">
                        <strong>##timelineitems.date## - ##timelineitems.author##:</strong><br>
                        ##timelineitems.description##
                    </li>
                ##ENDFOREACHtimelineitems##
                </ul>
            </div>

            <p><strong>TAHMİNİ ÇÖZÜM SÜRESİ:</strong> ##ticket.sla_ttr##</p>

            <p><strong>Ultron Bilişim Major Incident Ekibi</strong></p>
            """
        },
        "en": {
            "subject": "[MAJOR INCIDENT] Update - ##ticket.title##",
            "body": """
            <div class="alert-box">
                <strong>MAJOR INCIDENT UPDATE</strong>
            </div>

            <p>Dear ##ticket.authors##,</p>
            <p>Latest update regarding the ongoing major incident:</p>
            
            <div class="info-box">
                <strong>CURRENT STATUS:</strong>
                <p>##IFfollowup####followup.content####ENDIFfollowup##</p>
            </div>

            <div class="info-box" style="margin-top: 15px; border-left-color: #3498db;">
                <strong>RECENT ACTIVITY:</strong>
                <ul style="padding-left: 20px; margin-top: 10px;">
                ##FOREACHtimelineitems##
                    <li style="margin-bottom: 10px;">
                        <strong>##timelineitems.date## - ##timelineitems.author##:</strong><br>
                        ##timelineitems.description##
                    </li>
                ##ENDFOREACHtimelineitems##
                </ul>
            </div>

            <p><strong>ESTIMATED RESOLUTION TIME:</strong> ##ticket.sla_ttr##</p>

            <p><strong>Ultron Bilişim Major Incident Team</strong></p>
            """
        }
    },
    "major_incident_resolution": {
        "tr": {
            "subject": "[MAJOR INCIDENT - ÇÖZÜLDÜ] ##ticket.title##",
            "body": """
            <div class="info-box" style="background-color: #d4edda; border-color: #28a745;">
                <h2 style="color: #155724; margin: 0; text-align: center;">✅ MAJOR INCIDENT ÇÖZÜLDÜ</h2>
            </div>
            
            <p>Sayın ##ticket.authors##,</p>
            <p>Major incident başarıyla çözülmüş ve servisler normal duruma dönmüştür.</p>
            
            <h3>ÖZET BİLGİLER:</h3>
            <ul style="list-style-type: none;">
                <li>Incident ID: ##ticket.id##</li>
                <li>Başlangıç: ##ticket.creationdate##</li>
                <li>Çözüm: ##ticket.solvedate##</li>
                <li>Toplam Süre: ##ticket.actiontime##</li>
            </ul>

            <h3>ÇÖZÜM ÖZETİ:</h3>
            <p>##ticket.solution.description##</p>

            <div class="info-box">
                <strong>POST-INCIDENT REVIEW:</strong>
                <p>Detaylı Post-Incident Review raporu 48 saat içinde paylaşılacaktır.</p>
            </div>

            <p>Gösterdiğiniz anlayış ve sabır için çok teşekkür ederiz.</p>
            <p>Saygılarımızla,<br><strong>Ultron Bilişim Major Incident Ekibi</strong></p>
            """
        },
        "en": {
            "subject": "[MAJOR INCIDENT - RESOLVED] ##ticket.title##",
            "body": """
            <div class="info-box" style="background-color: #d4edda; border-color: #28a745;">
                <h2 style="color: #155724; margin: 0; text-align: center;">✅ MAJOR INCIDENT RESOLVED</h2>
            </div>
            
            <p>Dear ##ticket.authors##,</p>
            <p>The major incident has been successfully resolved and services have returned to normal status.</p>
            
            <h3>SUMMARY:</h3>
            <ul style="list-style-type: none;">
                <li>Incident ID: ##ticket.id##</li>
                <li>Start Time: ##ticket.creationdate##</li>
                <li>Resolution Time: ##ticket.solvedate##</li>
                <li>Total Duration: ##ticket.actiontime##</li>
            </ul>

            <h3>RESOLUTION SUMMARY:</h3>
            <p>##ticket.solution.description##</p>

            <div class="info-box">
                <strong>POST-INCIDENT REVIEW:</strong>
                <p>A detailed Post-Incident Review report will be shared within 48 hours.</p>
            </div>

            <p>We thank you for your patience and understanding.</p>
            <p>Best Regards,<br><strong>Ultron Bilişim Major Incident Team</strong></p>
            """
        }
    },
    "field_service_appointment": {
        "tr": {
            "subject": "Saha Ziyareti Randevu Talebi - ##ticket.title##",
            "body": """
            <p>Merhaba ##ticket.authors##,</p>
            <p>Ticket'ınız için saha müdahalesi gerektiği tespit edilmiştir ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Konu:</th><td>##ticket.title##</td></tr>
                <tr><th>Oluşturma Tarihi:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Müdahale Tipi:</th><td>##ticket.category##</td></tr>
                <tr><th>Atanan Teknisyen:</th><td>##ticket.assigntousers##</td></tr>
                <tr><th>Durumu:</th><td>##ticket.status##</td></tr>
                <tr><th>Müşteri:</th><td>##ticket.shortentity##</td></tr>
            </table>

            <div class="info-box">
                <strong>BİZE SAĞLAMANIZ GEREKENLER:</strong>
                <ul>
                    <li>Lokasyon tam adresi ve yol tarifi</li>
                    <li>İrtibat kişisi ve telefon</li>
                    <li>Güvenlik/otopark prosedürleri</li>
                    <li>Özel ekipman/araç gereç ihtiyacı</li>
                </ul>
            </div>

            <p>Lütfen size uygun olan randevu seçeneğini bu email'i yanıtlayarak bildiriniz.</p>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">Talebi Görüntüle</a>
        </p>
            """
        },
        "en": {
            "subject": "Field Service Appointment Request - ##ticket.title##",
            "body": """
            <p>Hello ##ticket.authors##,</p>
            <p>It has been determined that an on-site intervention is required for your ticket ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Subject:</th><td>##ticket.title##</td></tr>
                <tr><th>Creation Date:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Intervention Type:</th><td>##ticket.category##</td></tr>
                <tr><th>Assigned Technician:</th><td>##ticket.assigntousers##</td></tr>
                <tr><th>Status:</th><td>##ticket.status##</td></tr>
                <tr><th>Customer:</th><td>##ticket.shortentity##</td></tr>
            </table>

            <div class="info-box">
                <strong>REQUIRED FROM YOU:</strong>
                <ul>
                    <li>Full location address and directions</li>
                    <li>Contact person and phone number</li>
                    <li>Security/parking procedures</li>
                    <li>Special equipment/tool requirements</li>
                </ul>
            </div>

            <p>Please reply to this email to confirm the appointment option that suits you best.</p>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">View Ticket</a>
        </p>
            """
        }
    },
    "field_service_completion": {
        "tr": {
            "subject": "Saha Müdahalesi Tamamlandı - ##ticket.title##",
            "body": """
            <p>Merhaba ##ticket.authors##,</p>
            <p>Saha müdahalemiz başarıyla tamamlanmıştır ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Konu:</th><td>##ticket.title##</td></tr>
                <tr><th>Oluşturma Tarihi:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Teknisyen:</th><td>##ticket.assigntousers##</td></tr>
                <tr><th>Durumu:</th><td>##ticket.status##</td></tr>
                <tr><th>Müşteri:</th><td>##ticket.shortentity##</td></tr>
            </table>

            <div class="info-box">
                <strong>YAPILAN İŞLEMLER:</strong>
                <p>##ticket.solution.description##</p>
            </div>
            
             <div class="info-box">
                <ul style="list-style-type: none; padding: 0;">
                     <li><strong>Tamamlanma Zamanı:</strong> ##ticket.solvedate##</li>
                </ul>
            </div>

            <p>İlgili dökümanlar ve fotoğraflar ticket'a eklenmiştir.</p>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">Talebi Görüntüle</a>
        </p>
            """
        },
        "en": {
            "subject": "Field Intervention Completed - ##ticket.title##",
            "body": """
            <p>Hello ##ticket.authors##,</p>
            <p>Our field intervention has been successfully completed ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Subject:</th><td>##ticket.title##</td></tr>
                <tr><th>Creation Date:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Technician:</th><td>##ticket.assigntousers##</td></tr>
                <tr><th>Status:</th><td>##ticket.status##</td></tr>
                <tr><th>Customer:</th><td>##ticket.shortentity##</td></tr>
            </table>

            <div class="info-box">
                <strong>WORK PERFORMED:</strong>
                <p>##ticket.solution.description##</p>
            </div>
            
            <div class="info-box">
                <ul style="list-style-type: none; padding: 0;">
                     <li><strong>Completion Time:</strong> ##ticket.solvedate##</li>
                </ul>
            </div>

            <p>Related documents and photos have been attached to the ticket.</p>

            <br>
        <p style="text-align: center;">
            <a href="##ticket.url##" class="button">View Ticket</a>
        </p>
            """
        }
    },
    "planned_change_notification": {
        "tr": {
            "subject": "[CHANGE] Planlı Bakım Bildirimi - ##ticket.title##",
            "body": """
            <p>Merhaba ##ticket.authors##,</p>
            <p>Sistemlerinizde planlı bir değişiklik/bakım gerçekleştirilecektir ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Change ID:</th><td>##ticket.id##</td></tr>
                <tr><th>Change Türü:</th><td>##ticket.category##</td></tr>
                <tr><th>Başlangıç:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Tahmini Çözüm:</th><td>##ticket.sla_ttr##</td></tr>
                <tr><th>Etkilenen Sistemler:</th><td>##ticket.item.name##</td></tr>
                <tr><th>Durumu:</th><td>##ticket.status##</td></tr>
            </table>

            <div class="info-box">
                <strong>DEĞİŞİKLİĞİN AMACI:</strong>
                <p>##ticket.content##</p>
            </div>

            <div class="info-box">
                <strong>KULLANICILARA TAVSİYELER:</strong>
                <ul>
                    <li>Lütfen çalışmalarınızı kaydediniz.</li>
                    <li>Kesinti süresince sisteme erişim olmayabilir.</li>
                </ul>
            </div>

            <br>
            <p style="font-size: 12px; color: #666;">Detayları görüntülemek için dashboard'a erişin<br>
            <a href="##ticket.url##">##ticket.url##</a></p>
            """
        },
        "en": {
            "subject": "[CHANGE] Planned Maintenance Notification - ##ticket.title##",
            "body": """
            <p>Hello ##ticket.authors##,</p>
            <p>A planned change/maintenance will be performed on your systems ###ticket.id##</p>
            
            <table class="table-data">
                <tr><th>Change ID:</th><td>##ticket.id##</td></tr>
                <tr><th>Change Type:</th><td>##ticket.category##</td></tr>
                <tr><th>Start:</th><td>##ticket.creationdate##</td></tr>
                <tr><th>Estimated Resolution:</th><td>##ticket.sla_ttr##</td></tr>
                <tr><th>Affected Systems:</th><td>##ticket.item.name##</td></tr>
                <tr><th>Status:</th><td>##ticket.status##</td></tr>
            </table>

            <div class="info-box">
                <strong>PURPOSE OF CHANGE:</strong>
                <p>##ticket.content##</p>
            </div>

            <div class="info-box">
                <strong>RECOMMENDATIONS FOR USERS:</strong>
                <ul>
                    <li>Please save your work.</li>
                    <li>Access to the system may be unavailable during the downtime.</li>
                </ul>
            </div>

            <br>
            <p style="font-size: 12px; color: #666;">Access dashboard to view details<br>
            <a href="##ticket.url##">##ticket.url##</a></p>
            """
        }
    },
    "emergency_change_notification": {
        "tr": {
            "subject": "[EMERGENCY CHANGE] Acil Değişiklik - ##ticket.title##",
            "body": """
            <div class="alert-box">
                <h2 style="margin: 0;">ACİL DEĞİŞİKLİK BİLDİRİMİ</h2>
            </div>
            
            <p>Sayın ##ticket.authors##,</p>
            <p>Kritik bir durumu çözmek için acil bir değişiklik uygulanacaktır.</p>
            
            <h3>ACİL DEĞİŞİKLİK DETAYLARI:</h3>
            <ul style="list-style-type: none;">
                <li><strong>Emergency Change ID:</strong> ##ticket.id##</li>
                <li><strong>Uygulama Zamanı:</strong> ##ticket.creationdate##</li>
                <li><strong>Etkilenen Sistemler:</strong> ##ticket.item.name##</li>
            </ul>

            <div class="alert-box">
                <strong>ACİLİYET SEBEBİ:</strong>
                <p>##ticket.content##</p>
            </div>

            <p>Anlayışınız için teşekkür ederiz.</p>
            <p>Saygılarımızla,<br><strong>Ultron Bilişim Change Management</strong></p>
            """
        },
        "en": {
            "subject": "[EMERGENCY CHANGE] Emergency Change - ##ticket.title##",
            "body": """
            <div class="alert-box">
                <h2 style="margin: 0;">EMERGENCY CHANGE NOTIFICATION</h2>
            </div>
            
            <p>Dear ##ticket.authors##,</p>
            <p>An emergency change will be implemented to resolve a critical situation.</p>
            
            <h3>EMERGENCY CHANGE DETAILS:</h3>
            <ul style="list-style-type: none;">
                <li><strong>Emergency Change ID:</strong> ##ticket.id##</li>
                <li><strong>Implementation Time:</strong> ##ticket.creationdate##</li>
                <li><strong>Affected Systems:</strong> ##ticket.item.name##</li>
            </ul>

            <div class="alert-box">
                <strong>REASON FOR URGENCY:</strong>
                <p>##ticket.content##</p>
            </div>

            <p>We appreciate your understanding.</p>
            <p>Best Regards,<br><strong>Ultron Bilişim Change Management</strong></p>
            """
        }
    },
    "daily_report": {
        "tr": {
            "subject": "Günlük Operasyon Raporu - ##ticket.creationdate##",
            "body": """
            <p>Sayın ##ticket.authors##,</p>
            <p>##ticket.creationdate## tarihli günlük operasyon raporumuzu paylaşmak isteriz.</p>
            <p>Rapor detayları ekte veya aşağıdaki açıklama alanındadır.</p>

            <div class="info-box">
                <strong>RAPOR İÇERİĞİ:</strong>
                <p>##ticket.content##</p>
            </div>

            <p>Saygılarımızla,<br><strong>Ultron Bilişim Operations Team</strong></p>
            """
        },
        "en": {
            "subject": "Daily Operation Report - ##ticket.creationdate##",
            "body": """
            <p>Dear ##ticket.authors##,</p>
            <p>We would like to share the daily operation report for ##ticket.creationdate##.</p>
            <p>Report details are attached or in the description below.</p>

            <div class="info-box">
                <strong>REPORT CONTENT:</strong>
                <p>##ticket.content##</p>
            </div>

            <p>Best Regards,<br><strong>Ultron Bilişim Operations Team</strong></p>
            """
        }
    },
    "monthly_report": {
        "tr": {
            "subject": "Aylık Hizmet Performans Raporu",
            "body": """
            <p>Sayın ##ticket.authors##,</p>
            <p>Hizmet performans raporumuzu sunmaktan memnuniyet duyarız.</p>
            
            <h3>RAPOR ÖZETİ:</h3>
            <p>##ticket.content##</p>

            <p>Detaylı rapor ve grafikler ekte mevcuttur.</p>
            <p>Saygılarımızla,<br><strong>Ultron Bilişim Account Management</strong></p>
            """
        },
        "en": {
            "subject": "Monthly Service Performance Report",
            "body": """
            <p>Dear ##ticket.authors##,</p>
            <p>We are pleased to present our service performance report.</p>
            
            <h3>REPORT SUMMARY:</h3>
            <p>##ticket.content##</p>

            <p>Detailed report and charts are attached.</p>
            <p>Best Regards,<br><strong>Ultron Bilişim Account Management</strong></p>
            """
        }
    },
    "contract_renewal_90": {
        "tr": {
            "subject": "Sözleşme Yenileme - 90 Gün Kaldı",
            "body": """
            <p>Sayın ##ticket.authors##,</p>
            <p>Mevcut hizmet sözleşmenizin bitiş tarihine 90 gün kaldı.</p>
            
            <div class="info-box">
                <strong>SÖZLEŞME BİLGİLERİ:</strong>
                <p>##ticket.content##</p>
            </div>

            <h3>YENİLEME TOPLANTISI:</h3>
            <p>Yenileme koşullarını görüşmek ve ihtiyaçlarınızı değerlendirmek için bir toplantı planlamak isteriz.</p>

            <p>Saygılarımızla,<br><strong>Ultron Bilişim Account Management</strong></p>
            """
        },
        "en": {
            "subject": "Contract Renewal - 90 Days Remaining",
            "body": """
            <p>Dear ##ticket.authors##,</p>
            <p>There are 90 days remaining until the expiration of your current service contract.</p>
            
            <div class="info-box">
                <strong>CONTRACT DETAILS:</strong>
                <p>##ticket.content##</p>
            </div>

            <h3>RENEWAL MEETING:</h3>
            <p>We would like to schedule a meeting to discuss renewal terms and evaluate your needs.</p>

            <p>Best Regards,<br><strong>Ultron Bilişim Account Management</strong></p>
            """
        }
    },
    "contract_end_30": {
        "tr": {
            "subject": "ÖNEMLİ: Sözleşme Bitiş Bildirimi - 30 Gün",
            "body": """
            <div class="alert-box">
                <strong>⚠️ ÖNEMLİ HATIRLATMA</strong>
            </div>

            <p>Sayın ##ticket.authors##,</p>
            <p>Mevcut hizmet sözleşmenizin bitiş tarihine 30 gün kaldı. Kesintisiz hizmet için acil karar beklenmektedir.</p>
            
            <table class="table-data">
                <tr><th>Açıklama</th><td>##ticket.content##</td></tr>
                <tr><th>Bitiş Tarihi</th><td>##ticket.duedate##</td></tr>
            </table>

            <p>Saygılarımızla,<br><strong>Ultron Bilişim Account Management</strong></p>
            """
        },
        "en": {
            "subject": "IMPORTANT: Contract Expiration Notification - 30 Days",
            "body": """
            <div class="alert-box">
                <strong>⚠️ IMPORTANT REMINDER</strong>
            </div>

            <p>Dear ##ticket.authors##,</p>
            <p>There are 30 days remaining until your current service contract expires. Immediate decision is expected for uninterrupted service.</p>
            
            <table class="table-data">
                <tr><th>Description</th><td>##ticket.content##</td></tr>
                <tr><th>End Date</th><td>##ticket.duedate##</td></tr>
            </table>

            <p>Best Regards,<br><strong>Ultron Bilişim Account Management</strong></p>
            """
        }
    },
    "sla_breach_warning": {
        "tr": {
            "subject": "[SLA ALERT] Ticket ##ticket.id## - SLA İhlali Riski",
            "body": """
            <div class="alert-box">
                <h2 style="margin: 0; text-align: center;">⚠️ SLA İHLALİ RİSKİ</h2>
            </div>

            <p>Sayın Yöneticiler,</p>
            <p>Aşağıdaki ticket SLA ihlali riski taşımaktadır.</p>
            
            <h3>TICKET DETAYLARI:</h3>
            <ul style="list-style-type: none;">
                <li>Ticket ID: ##ticket.id##</li>
                <li>Müşteri: ##ticket.authors##</li>
                <li>Öncelik: ##ticket.priority##</li>
                <li>Atanan: ##ticket.assigntousers##</li>
            </ul>

            <div class="alert-box">
                <strong>SLA DURUMU:</strong>
                <ul>
                    <li>Response SLA: ##ticket.internal_time_to_own##</li>
                    <li>Resolution SLA: ##ticket.time_to_resolve##</li>
                </ul>
            </div>

            <h3>GEREKLİ AKSİYON:</h3>
            <p>Lütfen acil müdahale edin veya eskalasyon yapın.</p>

            <p><strong>GLPI Otomasyon</strong></p>
            """
        },
        "en": {
            "subject": "[SLA ALERT] Ticket ##ticket.id## - SLA Breach Risk",
            "body": """
            <div class="alert-box">
                <h2 style="margin: 0; text-align: center;">⚠️ SLA BREACH RISK</h2>
            </div>

            <p>Dear Managers,</p>
            <p>The following ticket carries a risk of SLA breach.</p>
            
            <h3>TICKET DETAILS:</h3>
            <ul style="list-style-type: none;">
                <li>Ticket ID: ##ticket.id##</li>
                <li>Customer: ##ticket.authors##</li>
                <li>Priority: ##ticket.priority##</li>
                <li>Assigned To: ##ticket.assigntousers##</li>
            </ul>

            <div class="alert-box">
                <strong>SLA STATUS:</strong>
                <ul>
                    <li>Response SLA: ##ticket.internal_time_to_own##</li>
                    <li>Resolution SLA: ##ticket.time_to_resolve##</li>
                </ul>
            </div>

            <h3>REQUIRED ACTION:</h3>
            <p>Please intervene immediately or escalate.</p>

            <p><strong>GLPI Automation</strong></p>
            """
        }
    },
    "escalation_customer": {
        "tr": {
            "subject": "Eskalasyon - ##ticket.title##",
            "body": """
            <p>Sayın ##ticket.authors##,</p>
            <p>Ticket'ınız üst yönetime eskaleedilmiştir.</p>
            
            <div class="alert-box">
                <strong>ESKALASYON SEBEBİ VE DETAYLAR:</strong>
                <p>##ticket.content##</p>
            </div>

            <h3>YENİ ATAMA:</h3>
            <ul>
                <li>Sorumlu: ##ticket.assigntousers##</li>
                <li>Grup: ##ticket.assigntogroups##</li>
            </ul>

            <p>##ticket.assigntousers## en kısa sürede sizinle iletişime geçecektir.</p>

            <p>Saygılarımızla,<br><strong>Ultron Bilişim Management</strong></p>
            """
        },
        "en": {
            "subject": "Escalation - ##ticket.title##",
            "body": """
            <p>Dear ##ticket.authors##,</p>
            <p>Your ticket has been escalated to upper management.</p>
            
            <div class="alert-box">
                <strong>REASON FOR ESCALATION AND DETAILS:</strong>
                <p>##ticket.content##</p>
            </div>

            <h3>NEW ASSIGNMENT:</h3>
            <ul>
                <li>Owner: ##ticket.assigntousers##</li>
                <li>Group: ##ticket.assigntogroups##</li>
            </ul>

            <p>##ticket.assigntousers## will contact you as soon as possible.</p>

            <p>Best Regards,<br><strong>Ultron Bilişim Management</strong></p>
            """
        }
    },
    "csat_survey": {
        "tr": {
            "subject": "Memnuniyet Anketi - Ticket ##ticket.id##",
            "body": """
            <p>Sayın ##ticket.authors##,</p>
            <p>Ticket ##ticket.id## çözümlendi. Hizmetimizi değerlendirmenizi rica ederiz.</p>
            
            <div class="info-box" style="text-align: center;">
                <h3>HİZMET KALİTESİNİ DEĞERLENDİRİN:</h3>
                <p>1 = Çok Kötü | 5 = Mükemmel</p>
            </div>

            <table class="table-data" style="width: auto; margin: 0 auto;">
                <tr>
                    <td><strong>1. Yanıt Süresi:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
                <tr>
                    <td><strong>2. Çözüm Kalitesi:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
                <tr>
                    <td><strong>3. İletişim:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
                <tr>
                    <td><strong>4. Teknik Yetkinlik:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
            </table>

            <h3>EK YORUMLARINIZ:</h3>
            <p style="border-bottom: 1px solid #ccc; height: 30px;"></p>
            <p style="border-bottom: 1px solid #ccc; height: 30px;"></p>

            <div style="text-align: center; margin-top: 30px;">
                <a href="##ticket.urlapproval##" class="button">Anketi Tamamlamak İçin Tıklayın</a>
            </div>

            <p style="text-align: center; margin-top: 20px;">Değerli görüşleriniz için teşekkür ederiz.</p>
            <p style="text-align: center;"><strong>Ultron Bilişim</strong></p>
            """
        },
        "en": {
            "subject": "Satisfaction Survey - Ticket ##ticket.id##",
            "body": """
            <p>Dear ##ticket.authors##,</p>
            <p>Ticket ##ticket.id## has been resolved. We request you to evaluate our service.</p>
            
            <div class="info-box" style="text-align: center;">
                <h3>RATE OUR SERVICE QUALITY:</h3>
                <p>1 = Very Poor | 5 = Excellent</p>
            </div>

            <table class="table-data" style="width: auto; margin: 0 auto;">
                <tr>
                    <td><strong>1. Response Time:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
                <tr>
                    <td><strong>2. Resolution Quality:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
                <tr>
                    <td><strong>3. Communication:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
                <tr>
                    <td><strong>4. Technical Competence:</strong></td>
                    <td>&#9744; 1 &nbsp; &#9744; 2 &nbsp; &#9744; 3 &nbsp; &#9744; 4 &nbsp; &#9744; 5</td>
                </tr>
            </table>

            <h3>YOUR COMMENTS:</h3>
            <p style="border-bottom: 1px solid #ccc; height: 30px;"></p>
            <p style="border-bottom: 1px solid #ccc; height: 30px;"></p>

            <div style="text-align: center; margin-top: 30px;">
                <a href="##ticket.urlapproval##" class="button">Click to Complete Survey</a>
            </div>

            <p style="text-align: center; margin-top: 20px;">Thank you for your valuable feedback.</p>
            <p style="text-align: center;"><strong>Ultron Bilişim</strong></p>
            """
        }
    },
    "generic_ticket_resolution": {
        "tr": {
            "subject": "Çözüldü - ##ticket.title##",
            "body": """
            <p>Sayın ##ticket.authors##,</p>
            <p>Talebiniz başarıyla çözümlenmiştir.</p>
            
            <div class="info-box">
                <strong>ÇÖZÜM BİLGİSİ:</strong>
                <p>##ticket.solution.description##</p>
            </div>

            <ul style="list-style-type: none; padding: 0;">
                <li><strong>Çözüm Tarihi:</strong> ##ticket.solvedate##</li>
                <li><strong>Çözüm Süresi:</strong> ##ticket.time##</li>
            </ul>

            <p>Çözümü onaylamak veya reddetmek için lütfen aşağıdaki bağlantıyı kullanınız.</p>
            <a href="##ticket.url##" class="button">Ticket'ı Görüntüle ve Onayla</a>

            <p>Saygılarımızla,<br><strong>Ultron Bilişim Service Desk</strong></p>
            """
        },
        "en": {
            "subject": "Resolved - ##ticket.title##",
            "body": """
            <p>Dear ##ticket.authors##,</p>
            <p>Your request has been successfully resolved.</p>
            
            <div class="info-box">
                <strong>RESOLUTION DETAILS:</strong>
                <p>##ticket.solution.description##</p>
            </div>

            <ul style="list-style-type: none; padding: 0;">
                <li><strong>Resolution Date:</strong> ##ticket.solvedate##</li>
                <li><strong>Resolution Time:</strong> ##ticket.time##</li>
            </ul>

            <p>Please use the link below to approve or reject the resolution.</p>
            <a href="##ticket.url##" class="button">View & Approve Ticket</a>

            <p>Best Regards,<br><strong>Ultron Bilişim Service Desk</strong></p>
            """
        }
    },
    "ticket_validation_request": {
        "tr": {
            "subject": "[ONAY GEREKİYOR] ##ticket.id## - ##ticket.title##",
            "body": """
            <div class="alert-box" style="background-color: #fff3cd; border-color: #ffc107;">
                <h3 style="margin: 0; color: #856404;">⚠️ ONAYINIZ BEKLENİYOR</h3>
            </div>
            
            <p>Sayın ##ticket.authors##,</p>
            <p>Aşağıdaki talep için onayınıza ihtiyaç duyulmaktadır.</p>
            
            <div class="info-box">
                <strong>TALEP DETAYLARI:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Talep Eden:</strong> ##ticket.authors##</li>
                    <li><strong>Başlık:</strong> ##ticket.title##</li>
                    <li><strong>Tarih:</strong> ##ticket.creationdate##</li>
                </ul>
                <p><strong>Açıklama:</strong><br>##ticket.content##</p>
            </div>

            <p>Lütfen onay durumunuzu belirtmek için sisteme giriş yapınız.</p>
            <a href="##ticket.urlvalidation##" class="button">Onay Ekranına Git</a>
            """
        },
        "en": {
            "subject": "[APPROVAL REQUIRED] ##ticket.id## - ##ticket.title##",
            "body": """
            <div class="alert-box" style="background-color: #fff3cd; border-color: #ffc107;">
                <h3 style="margin: 0; color: #856404;">⚠️ APPROVAL REQUIRED</h3>
            </div>
            
            <p>Dear ##ticket.authors##,</p>
            <p>Your approval is required for the following request.</p>
            
            <div class="info-box">
                <strong>REQUEST DETAILS:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Requester:</strong> ##ticket.authors##</li>
                    <li><strong>Title:</strong> ##ticket.title##</li>
                    <li><strong>Date:</strong> ##ticket.creationdate##</li>
                </ul>
                <p><strong>Description:</strong><br>##ticket.content##</p>
            </div>

            <p>Please log in to the system to provide your approval.</p>
            <a href="##ticket.urlvalidation##" class="button">Go to Approval Page</a>
            """
        }
    },
    "ticket_recall": {
        "tr": {
            "subject": "[HATIRLATMA] ##ticket.id## - ##ticket.title##",
            "body": """
            <p>Merhaba,</p>
            <p>Bu otomatik bir hatırlatmadır. Aşağıdaki ticket henüz çözüme ulaşmamıştır veya işlem beklemektedir.</p>
            
            <div class="info-box">
                <strong>TICKET BİLGİSİ:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li>ID: ##ticket.id##</li>
                    <li>Başlık: ##ticket.title##</li>
                    <li>Durum: ##ticket.status##</li>
                    <li>Son Güncelleme: ##ticket.updatedate##</li>
                </ul>
            </div>

            <a href="##ticket.url##" class="button">Ticket'a Git</a>
            """
        },
        "en": {
            "subject": "[REMINDER] ##ticket.id## - ##ticket.title##",
            "body": """
            <p>Hello,</p>
            <p>This is an automated reminder. The following ticket is still pending or requires action.</p>
            
            <div class="info-box">
                <strong>TICKET INFO:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li>ID: ##ticket.id##</li>
                    <li>Title: ##ticket.title##</li>
                    <li>Status: ##ticket.status##</li>
                    <li>Last Update: ##ticket.updatedate##</li>
                </ul>
            </div>

            <a href="##ticket.url##" class="button">Go to Ticket</a>
            """
        }
    },
    "delete_ticket": {
        "tr": {
            "subject": "[SİLİNDİ] Ticket ##ticket.id## - ##ticket.title##",
            "body": """
            <p>Sayın Kullanıcı,</p>
            <p><strong>##ticket.id##</strong> numaralı ticket sistemden silinmiştir.</p>
            <div class="alert-box">
                <strong>SİLİNME NEDENİ:</strong>
                <p>Yönetici veya sistem tarafından silme işlemi gerçekleştirildi.</p>
            </div>
            """
        },
        "en": {
            "subject": "[DELETED] Ticket ##ticket.id## - ##ticket.title##",
            "body": """
            <p>Dear User,</p>
            <p>Ticket <strong>##ticket.id##</strong> has been deleted from the system.</p>
            <div class="alert-box">
                <strong>REASON:</strong>
                <p>Deletion performed by administrator or system.</p>
            </div>
            """
        }
    },
    "new_problem": {
        "tr": {
            "subject": "Yeni Problem: ##problem.title##",
            "body": """
            <div class="alert-box" style="background-color: #f8d7da; border-color: #f5c6cb;">
                <h3 style="margin: 0; color: #721c24;">⚠️ YENİ PROBLEM KAYDI</h3>
            </div>
            
            <p>Sayın İlgili,</p>
            <p>Sistemde yeni bir problem kaydı oluşturulmuştur.</p>
            
            <div class="info-box">
                <strong>PROBLEM DETAYLARI:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>ID:</strong> ##problem.id##</li>
                    <li><strong>Başlık:</strong> ##problem.title##</li>
                    <li><strong>Tarih:</strong> ##problem.creationdate##</li>
                    <li><strong>Öncelik:</strong> ##problem.priority##</li>
                </ul>
                <p><strong>Açıklama:</strong><br>##problem.content##</p>
            </div>

            <a href="##problem.url##" class="button">Problemi Görüntüle</a>
            """
        },
        "en": {
            "subject": "New Problem: ##problem.title##",
            "body": """
            <div class="alert-box" style="background-color: #f8d7da; border-color: #f5c6cb;">
                <h3 style="margin: 0; color: #721c24;">⚠️ NEW PROBLEM RECORD</h3>
            </div>
            
            <p>Dear User,</p>
            <p>A new problem record has been created in the system.</p>
            
            <div class="info-box">
                <strong>PROBLEM DETAILS:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>ID:</strong> ##problem.id##</li>
                    <li><strong>Title:</strong> ##problem.title##</li>
                    <li><strong>Date:</strong> ##problem.creationdate##</li>
                    <li><strong>Priority:</strong> ##problem.priority##</li>
                </ul>
                <p><strong>Description:</strong><br>##problem.content##</p>
            </div>

            <a href="##problem.url##" class="button">View Problem</a>
            """
        }
    },
    "update_problem": {
        "tr": {
            "subject": "Problem Güncelleme: ##problem.title##",
            "body": """
            <p>Sayın İlgili,</p>
            <p>Problem kaydı güncellenmiştir.</p>
            
            <div class="info-box">
                <strong>GÜNCELLEME DETAYI:</strong>
                <p>##problem.content##</p>
            </div>

            <a href="##problem.url##" class="button">Problemi Görüntüle</a>
            """
        },
        "en": {
            "subject": "Problem Update: ##problem.title##",
            "body": """
            <p>Dear User,</p>
            <p>The problem record has been updated.</p>
            
            <div class="info-box">
                <strong>UPDATE DETAIL:</strong>
                <p>##problem.content##</p>
            </div>

            <a href="##problem.url##" class="button">View Problem</a>
            """
        }
    },
    "resolve_problem": {
        "tr": {
            "subject": "Problem Çözüldü: ##problem.title##",
            "body": """
            <div class="info-box" style="background-color: #d4edda; border-color: #28a745;">
                <h3 style="margin: 0; color: #155724;">✅ PROBLEM ÇÖZÜLDÜ</h3>
            </div>
            
            <p>Sayın İlgili,</p>
            <p>Problem kaydı çözüme kavuşturulmuştur.</p>
            
            <div class="info-box">
                <strong>ÇÖZÜM:</strong>
                <p>##problem.solution.description##</p>
                <p><strong>Analiz Türü:</strong> ##problem.solution.type##</p>
            </div>

            <a href="##problem.url##" class="button">Detayları Görüntüle</a>
            """
        },
        "en": {
            "subject": "Problem Resolved: ##problem.title##",
            "body": """
            <div class="info-box" style="background-color: #d4edda; border-color: #28a745;">
                <h3 style="margin: 0; color: #155724;">✅ PROBLEM RESOLVED</h3>
            </div>
            
            <p>Dear User,</p>
            <p>The problem record has been resolved.</p>
            
            <div class="info-box">
                <strong>RESOLUTION:</strong>
                <p>##problem.solution.description##</p>
                <p><strong>Analysis Type:</strong> ##problem.solution.type##</p>
            </div>

            <a href="##problem.url##" class="button">View Details</a>
            """
        }
    },
    "generic_update_change": {
        "tr": {
            "subject": "[CHANGE] ##change.id## - Güncelleme: ##change.name##",
            "body": """
            <p>Sayın İlgili,</p>
            <p>Change kaydında bir güncelleme yapılmıştır.</p>
            
            <div class="info-box">
                <strong>SON DURUM:</strong>
                <p>##change.content##</p>
            </div>

            <a href="##change.url##" class="button">Değişikliği Görüntüle</a>
            """
        },
        "en": {
            "subject": "[CHANGE] ##change.id## - Update: ##change.name##",
            "body": """
            <p>Dear User,</p>
            <p>An update has been made to the change record.</p>
            
            <div class="info-box">
                <strong>LATEST STATUS:</strong>
                <p>##change.content##</p>
            </div>

            <a href="##change.url##" class="button">View Change</a>
            """
        }
    },
    "change_validation_request": {
        "tr": {
            "subject": "[CHANGE ONAY] ##change.id## - ##change.name##",
            "body": """
            <div class="alert-box" style="background-color: #fff3cd; border-color: #ffc107;">
                <h3 style="margin: 0; color: #856404;">⚠️ DEĞİŞİKLİK ONAYI BEKLENİYOR</h3>
            </div>
            
            <p>Sayın İlgili,</p>
            <p>Aşağıdaki değişiklik talebi onayınıza sunulmuştur.</p>
            
            <div class="info-box">
                <strong>CHANGE DETAYLARI:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>ID:</strong> ##change.id##</li>
                    <li><strong>Başlık:</strong> ##change.name##</li>
                    <li><strong>Etki Analizi:</strong> ##change.impactcontent##</li>
                    <li><strong>Geri Dönüş Planı:</strong> ##change.controlistcontent##</li>
                </ul>
            </div>

            <a href="##change.urlvalidation##" class="button">Onay Ekranına Git</a>
            """
        },
        "en": {
            "subject": "[CHANGE APPROVAL] ##change.id## - ##change.name##",
            "body": """
            <div class="alert-box" style="background-color: #fff3cd; border-color: #ffc107;">
                <h3 style="margin: 0; color: #856404;">⚠️ CHANGE APPROVAL REQUIRED</h3>
            </div>
            
            <p>Dear User,</p>
            <p>The following change request has been submitted for your approval.</p>
            
            <div class="info-box">
                <strong>CHANGE DETAILS:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>ID:</strong> ##change.id##</li>
                    <li><strong>Title:</strong> ##change.name##</li>
                    <li><strong>Impact Analysis:</strong> ##change.impactcontent##</li>
                    <li><strong>Rollback Plan:</strong> ##change.controlistcontent##</li>
                </ul>
            </div>

            <a href="##change.urlvalidation##" class="button">Go to Approval Page</a>
            """
        }
    },
    "new_project": {
        "tr": {
            "subject": "[PROJE] Yeni Proje: ##project.name##",
            "body": """
            <p>Merhaba,</p>
            <p>Sisteme yeni bir proje eklenmiştir.</p>
            
            <div class="info-box">
                <strong>PROJE KARTI:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Proje Kodu:</strong> ##project.code##</li>
                    <li><strong>Proje Adı:</strong> ##project.name##</li>
                    <li><strong>Öncelik:</strong> ##project.priority##</li>
                    <li><strong>Yönetici:</strong> ##project.manager##</li>
                </ul>
                <p><strong>Açıklama:</strong><br>##project.content##</p>
            </div>

            <a href="##project.url##" class="button">Projeyi Görüntüle</a>
            """
        },
        "en": {
            "subject": "[PROJECT] New Project: ##project.name##",
            "body": """
            <p>Hello,</p>
            <p>A new project has been added to the system.</p>
            
            <div class="info-box">
                <strong>PROJECT CARD:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Code:</strong> ##project.code##</li>
                    <li><strong>Name:</strong> ##project.name##</li>
                    <li><strong>Priority:</strong> ##project.priority##</li>
                    <li><strong>Manager:</strong> ##project.manager##</li>
                </ul>
                <p><strong>Description:</strong><br>##project.content##</p>
            </div>

            <a href="##project.url##" class="button">View Project</a>
            """
        }
    },
    "project_task": {
        "tr": {
            "subject": "[PROJE GÖREVİ] ##projecttask.name## - ##project.name##",
            "body": """
            <p>Sayın İlgili,</p>
            <p>Size yeni bir proje görevi atanmış veya güncellenmiştir.</p>
            
            <div class="info-box">
                <strong>GÖREV DETAYI:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Görev:</strong> ##projecttask.name##</li>
                    <li><strong>Proje:</strong> ##project.name##</li>
                    <li><strong>Başlangıç:</strong> ##projecttask.begin##</li>
                    <li><strong>Bitiş:</strong> ##projecttask.end##</li>
                </ul>
                <p>##projecttask.content##</p>
            </div>

            <a href="##projecttask.url##" class="button">Görevi Görüntüle</a>
            """
        },
        "en": {
            "subject": "[PROJECT TASK] ##projecttask.name## - ##project.name##",
            "body": """
            <p>Dear User,</p>
            <p>A new project task has been assigned to you or updated.</p>
            
            <div class="info-box">
                <strong>TASK DETAIL:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Task:</strong> ##projecttask.name##</li>
                    <li><strong>Project:</strong> ##project.name##</li>
                    <li><strong>Start:</strong> ##projecttask.begin##</li>
                    <li><strong>End:</strong> ##projecttask.end##</li>
                </ul>
                <p>##projecttask.content##</p>
            </div>

            <a href="##projecttask.url##" class="button">View Task</a>
            """
        }
    },
    "password_forget": {
        "tr": {
            "subject": "[GÜVENLİK] Şifre Sıfırlama Talebi",
            "body": """
            <p>Sayın ##user.realname##,</p>
            <p>Hesabınız için şifre sıfırlama talebi alınmıştır.</p>
            
            <div class="info-box">
                <p>Eğer bu talebi siz yapmadıysanız, lütfen bu e-postayı dikkate almayınız.</p>
                <p>Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayınız:</p>
            </div>

            <a href="##user.urlpasswordforgotten##" class="button">Şifremi Sıfırla</a>
            
            <p>Bu bağlantı güvenliğiniz için belirli bir süre sonra geçerliliğini yitirecektir.</p>
            """
        },
        "en": {
            "subject": "[SECURITY] Password Reset Request",
            "body": """
            <p>Dear ##user.realname##,</p>
            <p>A password reset request has been received for your account.</p>
            
            <div class="info-box">
                <p>If you did not make this request, please ignore this email.</p>
                <p>Click the link below to reset your password:</p>
            </div>

            <a href="##user.urlpasswordforgotten##" class="button">Reset My Password</a>
            
            <p>This link will expire after a certain period for your security.</p>
            """
        }
    },
    "password_expiration": {
        "tr": {
            "subject": "[UYARI] Şifrenizin Kullanım Süresi Doluyor",
            "body": """
            <div class="alert-box">
                <strong>⚠️ ŞİFRE SÜRESİ UYARISI</strong>
            </div>
            
            <p>Sayın ##user.realname##,</p>
            <p>Şifrenizin kullanım süresi yakında dolacaktır.</p>
            
            <div class="info-box">
                <p>Kesintisiz erişim için lütfen şifrenizi en kısa sürede güncelleyiniz.</p>
            </div>

            <a href="##glpi.url##" class="button">Sisteme Giriş Yap ve Değiştir</a>
            """
        },
        "en": {
            "subject": "[WARNING] Your Password is Expiring",
            "body": """
            <div class="alert-box">
                <strong>⚠️ PASSWORD EXPIRATION WARNING</strong>
            </div>
            
            <p>Dear ##user.realname##,</p>
            <p>Your password is about to expire.</p>
            
            <div class="info-box">
                <p>Please update your password as soon as possible for uninterrupted access.</p>
            </div>

            <a href="##glpi.url##" class="button">Login and Change</a>
            """
        }
    },
    "new_reservation": {
        "tr": {
            "subject": "[REZERVASYON] ##reservation.item##",
            "body": """
            <p>Sayın ##user.realname##,</p>
            <p>Rezervasyon işleminiz başarıyla kaydedilmiştir.</p>
            
            <div class="info-box">
                <strong>REZERVASYON DETAYLARI:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Öğe:</strong> ##reservation.item##</li>
                    <li><strong>Başlangıç:</strong> ##reservation.begin##</li>
                    <li><strong>Bitiş:</strong> ##reservation.end##</li>
                </ul>
                <p>##reservation.comment##</p>
            </div>
            """
        },
        "en": {
            "subject": "[RESERVATION] ##reservation.item##",
            "body": """
            <p>Dear ##user.realname##,</p>
            <p>Your reservation has been successfully recorded.</p>
            
            <div class="info-box">
                <strong>RESERVATION DETAILS:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Item:</strong> ##reservation.item##</li>
                    <li><strong>Start:</strong> ##reservation.begin##</li>
                    <li><strong>End:</strong> ##reservation.end##</li>
                </ul>
                <p>##reservation.comment##</p>
            </div>
            """
        }
    },
    "consumable_alert": {
        "tr": {
            "subject": "[STOK UYARISI] ##item.name## - Stok Azalıyor",
            "body": """
            <div class="alert-box">
                <h3 style="margin: 0;">⚠️ STOK KRİTİK SEVİYEDE</h3>
            </div>
            
            <p>Sayın Stok Yöneticisi,</p>
            <p>Aşağıdaki sarf malzemesi veya kartuş için stok seviyesi alarm eşiğinin altına düşmüştür.</p>
            
            <div class="info-box">
                <strong>ÜRÜN BİLGİSİ:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Ürün:</strong> ##item.name##</li>
                    <li><strong>Referans:</strong> ##item.ref##</li>
                    <li><strong>Kalan Stok:</strong> ##item.stock##</li>
                    <li><strong>Alarm Eşiği:</strong> ##item.alarm_threshold##</li>
                </ul>
            </div>

            <p>Lütfen tedarik süreci başlatınız.</p>
            """
        },
        "en": {
            "subject": "[STOCK ALERT] ##item.name## - Low Stock",
            "body": """
            <div class="alert-box">
                <h3 style="margin: 0;">⚠️ CRITICAL STOCK LEVEL</h3>
            </div>
            
            <p>Dear Stock Manager,</p>
            <p>The stock level for the following consumable or cartridge has fallen below the alarm threshold.</p>
            
            <div class="info-box">
                <strong>PRODUCT INFO:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    <li><strong>Product:</strong> ##item.name##</li>
                    <li><strong>Reference:</strong> ##item.ref##</li>
                    <li><strong>Remaining Stock:</strong> ##item.stock##</li>
                    <li><strong>Alarm Threshold:</strong> ##item.alarm_threshold##</li>
                </ul>
            </div>

            <p>Please initiate the procurement process.</p>
            """
        }
    },
    # --- CUSTOM TEMPLATES (System, Admin, Edge Cases) ---
    "custom_mysql_sync": {
        "tr": {
            "subject": "[SİSTEM] MySQL Senkronizasyon Uyarısı",
            "body": """
            <div class="alert-box">
                <h3 style="margin: 0;">⚠️ SQL REPLİKA SENKRONİZASYON SORUNU</h3>
            </div>
            <p><strong>DB Yöneticisi Dikkatine,</strong></p>
            <p>GLPI veritabanı replikasyonu arasında senkronizasyon sorunu tespit edilmiştir.</p>
            <div class="info-box">
                <p>##mysqlvalidator.text##</p>
            </div>
            <p>Lütfen veritabanı loglarını kontrol ediniz.</p>
            """
        },
        "en": {
            "subject": "[SYSTEM] MySQL Synchronization Alert",
            "body": """
            <div class="alert-box">
                <h3 style="margin: 0;">⚠️ SQL REPLICA SYNCHRONIZATION ISSUE</h3>
            </div>
            <p><strong>Attention DB Admin,</strong></p>
            <p>A synchronization issue has been detected in GLPI database replication.</p>
            <div class="info-box">
                <p>##mysqlvalidator.text##</p>
            </div>
            <p>Please check database logs.</p>
            """
        }
    },
    "custom_crontask_watcher": {
        "tr": {
            "subject": "[OTOMASYON] Cron Görevi Hatası: ##crontask.name##",
            "body": """
            <div class="alert-box" style="background-color: #f8d7da; border-color: #f5c6cb;">
                 <strong>⚠️ OTOMATİK GÖREV HATASI</strong>
            </div>
            <p><strong>##crontask.name##</strong> adlı otomatik görevde sorun yaşanmıştır.</p>
            <div class="info-box">
                <strong>Hata Detayı:</strong>
                <p>##crontask.description##</p>
            </div>
            """
        },
        "en": {
            "subject": "[AUTOMATION] Cron Task Error: ##crontask.name##",
            "body": """
            <div class="alert-box" style="background-color: #f8d7da; border-color: #f5c6cb;">
                 <strong>⚠️ AUTOMATED TASK ERROR</strong>
            </div>
            <p>An issue occurred with the automated task <strong>##crontask.name##</strong>.</p>
            <div class="info-box">
                <strong>Error Detail:</strong>
                <p>##crontask.description##</p>
            </div>
            """
        }
    },
    "custom_receiver_errors": {
        "tr": {
            "subject": "[MAIL] E-posta Alım Hatası",
            "body": """
            <div class="alert-box">
                <strong>⚠️ MAİL ALIM HATASI (RECEIVER)</strong>
            </div>
            <p>GLPI mail alıcısı (Receiver) bağlantı hatasıyla karşılaştı.</p>
            <div class="info-box">
                <p>##mailcollector.errors##</p>
            </div>
            """
        },
        "en": {
            "subject": "[MAIL] Email Receiver Error",
            "body": """
            <div class="alert-box">
                <strong>⚠️ EMAIL RECEIVER ERROR</strong>
            </div>
            <p>GLPI mail receiver encountered a connection error.</p>
            <div class="info-box">
                <p>##mailcollector.errors##</p>
            </div>
            """
        }
    },
    "custom_item_not_unique": {
        "tr": {
            "subject": "[VERİ] Mükerrer Kayıt Uyarısı",
            "body": """
            <p>Sistemde benzersiz olması gereken bir alan için mükerrer kayıt tespit edildi.</p>
            <div class="info-box">
                <strong>Nesne:</strong> ##item.type##<br>
                <strong>Mesaj:</strong> ##item.message##
            </div>
            """
        },
        "en": {
            "subject": "[DATA] Duplicate Record Warning",
            "body": """
            <p>A duplicate record has been detected for a field that must be unique.</p>
            <div class="info-box">
                <strong>Item:</strong> ##item.type##<br>
                <strong>Message:</strong> ##item.message##
            </div>
            """
        }
    },
    "custom_saved_search_alert": {
        "tr": {
            "subject": "[RAPOR] Kayıtlı Arama Bildirimi: ##savedsearch.name##",
            "body": """
            <p>Sayın Kullanıcı,</p>
            <p><strong>##savedsearch.name##</strong> adlı kayıtlı aramanız için yeni sonuçlar var.</p>
            <div class="info-box">
                <strong>Sonuç Sayısı:</strong> ##savedsearch.count##
            </div>
            <a href="##savedsearch.url##" class="button">Sonuçları Görüntüle</a>
            """
        },
        "en": {
            "subject": "[REPORT] Saved Search Alert: ##savedsearch.name##",
            "body": """
            <p>Dear User,</p>
            <p>There are new results for your saved search <strong>##savedsearch.name##</strong>.</p>
            <div class="info-box">
                <strong>Count:</strong> ##savedsearch.count##
            </div>
            <a href="##savedsearch.url##" class="button">View Results</a>
            """
        }
    },
    "custom_plugin_updates": {
        "tr": {
            "subject": "[MARKETPLACE] Eklenti Güncelleme Kontrolü",
            "body": """
            <p>Eklenti güncellemeleri kontrol edildi.</p>
            <div class="info-box">
                <p>##plugin.updates##</p>
            </div>
            """
        },
        "en": {
            "subject": "[MARKETPLACE] Plugin Update Check",
            "body": """
            <p>Plugin updates have been checked.</p>
            <div class="info-box">
                <p>##plugin.updates##</p>
            </div>
            """
        }
    },
    "custom_delete_project": {
        "tr": {
            "subject": "[SİLİNDİ] Proje: ##project.name##",
            "body": """
            <div class="alert-box">
                <strong>⚠️ PROJE SİLİNDİ</strong>
            </div>
            <p><strong>##project.name##</strong> (##project.code##) projesi sistemden silinmiştir.</p>
            <p>Silen: ##project.users_id_lastupdater##</p>
            """
        },
        "en": {
            "subject": "[DELETED] Project: ##project.name##",
            "body": """
            <div class="alert-box">
                <strong>⚠️ PROJECT DELETED</strong>
            </div>
            <p>Project <strong>##project.name##</strong> (##project.code##) has been deleted from the system.</p>
            <p>Deleted by: ##project.users_id_lastupdater##</p>
            """
        }
    },
    "custom_delete_problem": {
        "tr": {
            "subject": "[SİLİNDİ] Problem: ##problem.name##",
            "body": """
            <div class="alert-box">
                <strong>⚠️ PROBLEM SİLİNDİ</strong>
            </div>
            <p><strong>##problem.id## - ##problem.name##</strong> kaydı silinmiştir.</p>
            """
        },
        "en": {
            "subject": "[DELETED] Problem: ##problem.name##",
            "body": """
            <div class="alert-box">
                <strong>⚠️ PROBLEM DELETED</strong>
            </div>
            <p>Record <strong>##problem.id## - ##problem.name##</strong> has been deleted.</p>
            """
        }
    },
    "custom_delete_change": {
        "tr": {
            "subject": "[SİLİNDİ] Change: ##change.name##",
            "body": """
            <div class="alert-box">
                <strong>⚠️ DEĞİŞİKLİK SİLİNDİ</strong>
            </div>
            <p><strong>##change.id## - ##change.name##</strong> kaydı silinmiştir.</p>
            """
        },
        "en": {
            "subject": "[DELETED] Change: ##change.name##",
            "body": """
            <div class="alert-box">
                <strong>⚠️ CHANGE DELETED</strong>
            </div>
            <p>Record <strong>##change.id## - ##change.name##</strong> has been deleted.</p>
            """
        }
    },
    "custom_kb_new": {
        "tr": {
            "subject": "[BİLGİ BANKASI] Yeni Makale: ##knowbaseitem.name##",
            "body": """
            <p>Bilgi Bankasına yeni bir makale eklendi.</p>
            <div class="info-box">
                <strong>Başlık:</strong> ##knowbaseitem.name##<br>
                <strong>Kategori:</strong> ##knowbaseitem.category##
            </div>
            <a href="##knowbaseitem.url##" class="button">Okumak İçin Tıklayın</a>
            """
        },
        "en": {
            "subject": "[KNOWLEDGE BASE] New Article: ##knowbaseitem.name##",
            "body": """
            <p>A new article has been added to the Knowledge Base.</p>
            <div class="info-box">
                <strong>Title:</strong> ##knowbaseitem.name##<br>
                <strong>Category:</strong> ##knowbaseitem.category##
            </div>
            <a href="##knowbaseitem.url##" class="button">Click to Read</a>
            """
        }
    },
    "custom_kb_update": {
        "tr": {
            "subject": "[KB GÜNCELLEME] ##knowbaseitem.name##",
            "body": """
            <p>Bir makale güncellendi.</p>
            <h3>##knowbaseitem.name##</h3>
            <a href="##knowbaseitem.url##" class="button">Değişiklikleri Gör</a>
            """
        },
        "en": {
            "subject": "[KB UPDATE] ##knowbaseitem.name##",
            "body": """
            <p>An article has been updated.</p>
            <h3>##knowbaseitem.name##</h3>
            <a href="##knowbaseitem.url##" class="button">View Changes</a>
            """
        }
    },
    "custom_kb_delete": {
        "tr": {
            "subject": "[KB SİLİNDİ] ##knowbaseitem.name##",
            "body": """
            <p><strong>##knowbaseitem.name##</strong> başlıklı makale silinmiştir.</p>
            """
        },
        "en": {
            "subject": "[KB DELETED] ##knowbaseitem.name##",
            "body": """
            <p>The article <strong>##knowbaseitem.name##</strong> has been deleted.</p>
            """
        }
    },
    "custom_unlock_item": {
         "tr": {
            "subject": "[KİLİT] Kilit Açma İsteği: ##item.type##",
            "body": """
            <p>Kilitli bir nesne için kilit açma isteği gönderildi.</p>
            <div class="info-box">
                <strong>Nesne:</strong> ##item.type##<br>
                <strong>İsteyen:</strong> ##user.realname##
            </div>
            """
        },
        "en": {
            "subject": "[LOCK] Unlock Request: ##item.type##",
            "body": """
            <p>An unlock request has been sent for a locked item.</p>
            <div class="info-box">
                <strong>Item:</strong> ##item.type##<br>
                <strong>Requester:</strong> ##user.realname##
            </div>
            """
        }
    },
    "custom_credit_expired": {
         "tr": {
            "subject": "[FİNANS] Kredi Süresi Doldu",
            "body": """
            <div class="alert-box">⚠️ KREDİ SÜRESİ DOLDU</div>
            """
        },
        "en": {
             "subject": "[FINANCE] Credit Expired",
             "body": """
             <div class="alert-box">⚠️ CREDIT EXPIRED</div>
             """
        }
    },
    "custom_low_credits": {
         "tr": {
            "subject": "[FİNANS] Kredi Azaldı",
            "body": """
             <div class="alert-box">⚠️ DÜŞÜK KREDİ BAKİYESİ</div>
            """
        },
        "en": {
             "subject": "[FINANCE] Low Credits",
             "body": """
             <div class="alert-box">⚠️ LOW CREDIT BALANCE</div>
             """
        }
    },
    "custom_infocoms": {
         "tr": {
            "subject": "[FİNANS] Mali Bilgi Alarmı: ##item.name##",
            "body": """
            <p>Cihaz veya varlık üzerinde mali uyarı oluştu.</p>
             <div class="info-box">
                <strong>Varlık:</strong> ##item.name##
            </div>
            """
        },
        "en": {
             "subject": "[FINANCE] Infocom Alert: ##item.name##",
             "body": """
             <p>Financial alert triggered on asset.</p>
             <div class="info-box">
                <strong>Asset:</strong> ##item.name##
            </div>
             """
        }
    },
    "custom_plugin_releasetask_new": {
        "tr": {
            "subject": "[RELEASE] Yeni Görev: ##task.description##",
            "body": """
            <p>Release yönetimi kapsamında yeni bir görev eklendi.</p>
            <div class="info-box">
                <strong>Görev:</strong> ##task.description##<br>
                <strong>Durum:</strong> ##task.state##
            </div>
            """
        },
        "en": {
            "subject": "[RELEASE] New Task: ##task.description##",
            "body": """
            <p>A new task has been added within release management.</p>
            <div class="info-box">
                <strong>Task:</strong> ##task.description##<br>
                <strong>State:</strong> ##task.state##
            </div>
            """
        }
    },
    "custom_plugin_releasetask_update": {
        "tr": {
            "subject": "[RELEASE] Görev Güncellendi: ##task.description##",
            "body": """
            <p>Release görevi güncellendi.</p>
            <div class="info-box">
                <strong>Görev:</strong> ##task.description##<br>
                <strong>Son Durum:</strong> ##task.state##
            </div>
            """
        },
        "en": {
            "subject": "[RELEASE] Task Updated: ##task.description##",
            "body": """
            <p>Release task has been updated.</p>
            <div class="info-box">
                <strong>Task:</strong> ##task.description##<br>
                <strong>State:</strong> ##task.state##
            </div>
            """
        }
    },
    "custom_plugin_releasetask_delete": {
        "tr": {
            "subject": "[RELEASE] Görev Silindi: ##task.description##",
            "body": """
            <div class="alert-box">⚠️ RELEASE GÖREVİ SİLİNDİ</div>
            <p><strong>##task.description##</strong> görevi silinmiştir.</p>
            """
        },
        "en": {
            "subject": "[RELEASE] Task Deleted: ##task.description##",
            "body": """
            <div class="alert-box">⚠️ RELEASE TASK DELETED</div>
            <p>Task <strong>##task.description##</strong> has been deleted.</p>
            """
        }
    },
    "ticket_task_notification": {
        "tr": {
            "subject": "[GÖREV] ##ticket.title##",
            "body": """
            <p><strong>Talep ###ticket.id##</strong> için yeni bir görev eklendi veya güncellendi.</p>
            <div class="info-box">
                <strong>Görev Tanımı:</strong> ##task.description##<br>
                <strong>Durum:</strong> ##task.status##<br>
                <strong>Atanan:</strong> ##task.tech##
            </div>
            <p><a href="##ticket.url##">Talebe Git</a></p>
            """
        },
        "en": {
            "subject": "[TASK] ##ticket.title##",
            "body": """
            <p>A new task has been added or updated for <strong>Ticket ###ticket.id##</strong>.</p>
            <div class="info-box">
                <strong>Task Description:</strong> ##task.description##<br>
                <strong>Status:</strong> ##task.status##<br>
                <strong>Technician:</strong> ##task.tech##
            </div>
            <p><a href="##ticket.url##">Go to Ticket</a></p>
            """
        }
    }
}

def generate_templates():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_dir = os.path.join(base_dir, 'html')
    
    for template_key, languages in TEMPLATES.items():
        for lang, content in languages.items():
            lang_dir = os.path.join(html_dir, lang)
            
            # Use ASCII safe formatting for HTML template to avoid encoding issues with repr
            # But here we are writing bytes or utf-8 text.
            full_html = HTML_TEMPLATE.format(
                subject=content['subject'],
                body=content['body']
            )
            
            file_name = f"{template_key}.html"
            file_path = os.path.join(lang_dir, file_name)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                print(f"Generated HTML: {os.path.join(lang, file_name)}")
            except Exception as e:
                print(f"Error generating HTML {file_name}: {e}")

            # --- Text Version Generation ---
            text_dir = os.path.join(base_dir, 'text', lang)
            os.makedirs(text_dir, exist_ok=True)
            
            text_body = convert_html_to_text(content['body'])
            text_subject = content['subject']
            full_text = f"Subject: {text_subject}\n\n{text_body}"
            
            try:
                with open(os.path.join(text_dir, f"{template_key}.txt"), 'w', encoding='utf-8') as f:
                    f.write(full_text)
                print(f"Generated Text: {os.path.join('text', lang, f'{template_key}.txt')}")
            except Exception as e:
                print(f"Error generating Text {template_key}: {e}")

def convert_html_to_text(html):
    import re
    # 1. Replace list items with bullet points
    html = re.sub(r'<li[^>]*>', '\n• ', html, flags=re.IGNORECASE)
    # 2. Replace block elements with double newlines
    html = re.sub(r'</?(div|p|h[1-6]|table|ul|ol)[^>]*>', '\n\n', html, flags=re.IGNORECASE)
    # 3. Replace line breaks
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    # 4. Replace table cells
    html = re.sub(r'<td[^>]*>', ' \t ', html, flags=re.IGNORECASE)
    html = re.sub(r'</tr>', '\n', html, flags=re.IGNORECASE)
    # 5. Extract link text and url
    html = re.sub(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>(.*?)</a>', r'\2 (\1)', html, flags=re.IGNORECASE)
    # 6. Strip all other tags
    text = re.sub(r'<[^>]+>', '', html)
    # 7. Decode HTML entities (basic ones)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
    
    # 8. Clean up whitespace
    lines = [line.strip() for line in text.split('\n')]
    
    clean_lines: list = []
    empty_line_count: int = 0
    for line in lines:
        if line:
            clean_lines.append(line)
            empty_line_count = 0
        elif empty_line_count < 1:
            clean_lines.append(line)
            empty_line_count = empty_line_count + 1
            
    return '\n'.join(clean_lines).strip()

if __name__ == "__main__":
    generate_templates()
