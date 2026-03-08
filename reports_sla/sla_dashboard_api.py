#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLPI SLA Compliance Dashboard API
==================================
Flask-based REST API for SLA compliance dashboard.
"""

from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import requests
import urllib3
import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import io
import csv

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Cache için basit bir mekanizma
cache = {
    'entities': {'data': None, 'timestamp': None},
    'slas': {'data': None, 'timestamp': None},
    'compliance': {'data': None, 'timestamp': None, 'params': None}
}
CACHE_TTL = 300  # 5 dakika

# Config dosyası yolları
CONFIG_PATHS = [
    'config.json',
    '../config/config.json',
    '../../config/config.json'
]

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
        return response.json()['session_token']
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

def is_cache_valid(cache_key):
    """Cache geçerli mi kontrol et"""
    if cache[cache_key]['data'] is None or cache[cache_key]['timestamp'] is None:
        return False
    
    elapsed = (datetime.now() - cache[cache_key]['timestamp']).total_seconds()
    return elapsed < CACHE_TTL

def fetch_all_entities(config, session_token):
    """Tüm entity'leri çek"""
    if is_cache_valid('entities'):
        return cache['entities']['data']
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    entities = {}
    range_start = 0
    range_size = 1000
    
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
                # Entity ismini temizle
                clean_name = entity['completename']
                if clean_name.startswith('Root entity > '):
                    clean_name = clean_name.replace('Root entity > ', '', 1)
                elif clean_name.startswith('Root Entity > '):
                    clean_name = clean_name.replace('Root Entity > ', '', 1)
                entities[entity['id']] = clean_name
            
            range_start += range_size
        else:
            break
    
    cache['entities']['data'] = entities
    cache['entities']['timestamp'] = datetime.now()
    
    return entities

def fetch_all_slas(config, session_token):
    """Tüm SLA tanımlarını çek"""
    if is_cache_valid('slas'):
        return cache['slas']['data']
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    slas = {}
    range_start = 0
    range_size = 1000
    
    while True:
        response = requests.get(
            f"{config['GLPI_URL']}/SLA",
            headers=headers,
            params={'range': f'{range_start}-{range_start + range_size - 1}'},
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            batch = response.json()
            if not batch:
                break
            
            for sla in batch:
                slas[sla['id']] = {
                    'name': sla['name'],
                    'type': sla['type'],
                    'number_time': sla.get('number_time', 0),
                    'definition_time': sla.get('definition_time', 'hour')
                }
            
            range_start += range_size
        else:
            break
    
    cache['slas']['data'] = slas
    cache['slas']['timestamp'] = datetime.now()
    
    return slas

def fetch_tickets(config, session_token, start_date, end_date):
    """Tüm ticketları çek"""
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': config['GLPI_APP_TOKEN']
    }
    
    tickets = []
    range_start = 0
    range_size = 1000
    
    while True:
        response = requests.get(
            f"{config['GLPI_URL']}/Ticket",
            headers=headers,
            params={
                'range': f'{range_start}-{range_start + range_size - 1}',
                'expand_dropdowns': 'false',
                'with_devices': 'false',
                'with_disks': 'false',
                'with_softwares': 'false',
                'with_connections': 'false',
                'with_networkports': 'false',
                'with_infocoms': 'false',
                'with_contracts': 'false',
                'with_documents': 'false',
                'with_tickets': 'false',
                'with_problems': 'false',
                'with_changes': 'false',
                'with_notes': 'false',
                'with_logs': 'false'
            },
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                batch = response.json()
                if not batch:
                    break
                
                for ticket in batch:
                    ticket_date = ticket.get('date', '')[:10]
                    
                    if ticket_date < start_date or ticket_date > end_date:
                        continue
                    
                    tickets.append(ticket)
                
                range_start += range_size
                
                if len(batch) < range_size:
                    break
                    
            except Exception as e:
                break
        elif response.status_code == 206:
            try:
                batch = response.json()
                if not batch:
                    break
                
                for ticket in batch:
                    ticket_date = ticket.get('date', '')[:10]
                    if ticket_date >= start_date and ticket_date <= end_date:
                        tickets.append(ticket)
                
                range_start += range_size
            except:
                break
        else:
            break
    
    return tickets

def convert_to_seconds(number_time, definition_time):
    """SLA süresini saniyeye çevir"""
    if definition_time == 'minute':
        return number_time * 60
    elif definition_time == 'hour':
        return number_time * 3600
    elif definition_time == 'day':
        return number_time * 86400
    else:
        return number_time * 3600

def clean_entity_name(entity_name):
    """Entity isminden 'Root Entity > ' kısmını kaldır"""
    if entity_name.startswith('Root entity > '):
        return entity_name.replace('Root entity > ', '', 1)
    elif entity_name.startswith('Root Entity > '):
        return entity_name.replace('Root Entity > ', '', 1)
    elif entity_name.startswith('Ultron Bilişim > '):
        return entity_name.replace('Ultron Bilişim > ', '', 1)
    return entity_name

def analyze_sla_compliance(tickets, entities, slas):
    """SLA uyumunu analiz et"""
    stats = defaultdict(lambda: {
        'total': 0,      # Toplam Ticket
        'sla_total': 0,  # SLA'lı Ticket
        'sla_ok': 0,
        'sla_violated': 0,
        'sla_active': 0,
        'tickets': []
    })
    
    for ticket in tickets:
        entity_id = ticket.get('entities_id', 0)
        entity_name = clean_entity_name(entities.get(entity_id, f"Unknown ({entity_id})"))
        
        stats[entity_name]['total'] += 1
        
        sla_ttr_id = ticket.get('slas_id_ttr', 0)
        sla_tto_id = ticket.get('slas_id_tto', 0)

        # SLA var mı kontrol et
        has_sla = False
        if (sla_ttr_id and sla_ttr_id in slas) or (sla_tto_id and sla_tto_id in slas):
            has_sla = True
            stats[entity_name]['sla_total'] += 1
        
        if not has_sla:
            continue
        
        try:
            solve_delay_stat = int(ticket.get('solve_delay_stat') or 0)
        except (ValueError, TypeError):
            solve_delay_stat = 0
        
        try:
            time_to_own = int(ticket.get('time_to_own') or 0)
        except (ValueError, TypeError):
            time_to_own = 0
        
        has_violation = False
        violation_details = []
        
        # TTR kontrolü
        if sla_ttr_id and sla_ttr_id in slas:
            sla_ttr = slas[sla_ttr_id]
            sla_limit_seconds = convert_to_seconds(
                sla_ttr['number_time'], 
                sla_ttr['definition_time']
            )
            
            # 1. Çözülmüş ticketlarda gecikme kontrolü
            if solve_delay_stat > 0 and solve_delay_stat > sla_limit_seconds:
                has_violation = True
                delay = solve_delay_stat - sla_limit_seconds
                violation_details.append({
                    'type': 'TTR',
                    'sla_name': sla_ttr['name'],
                    'limit': sla_limit_seconds,
                    'actual': solve_delay_stat,
                    'delay': delay,
                    'status': 'solved'
                })
            
            # 2. Henüz çözülmemiş (Aktif) ticketlarda gecikme kontrolü
            elif ticket.get('status', 0) < 5 and solve_delay_stat == 0:
                time_to_resolve_str = ticket.get('time_to_resolve')
                if time_to_resolve_str:
                    try:
                        ttr_date = datetime.strptime(time_to_resolve_str, '%Y-%m-%d %H:%M:%S')
                        current_time = datetime.now()
                        
                        if current_time > ttr_date:
                            has_violation = True
                            delay_seconds = (current_time - ttr_date).total_seconds()
                            violation_details.append({
                                'type': 'TTR',
                                'sla_name': sla_ttr['name'],
                                'limit': sla_limit_seconds,
                                'actual': int(delay_seconds),
                                'delay': int(delay_seconds),
                                'status': 'active'
                            })
                    except ValueError:
                        pass
        
        # TTO kontrolü
        if sla_tto_id and sla_tto_id in slas:
            sla_tto = slas[sla_tto_id]
            sla_limit_seconds = convert_to_seconds(
                sla_tto['number_time'], 
                sla_tto['definition_time']
            )
            
            if time_to_own > 0 and time_to_own > sla_limit_seconds:
                has_violation = True
                delay = time_to_own - sla_limit_seconds
                violation_details.append({
                    'type': 'TTO',
                    'sla_name': sla_tto['name'],
                    'limit': sla_limit_seconds,
                    'actual': time_to_own,
                    'delay': delay,
                    'status': 'assigned'
                })
        
        if has_violation:
            stats[entity_name]['sla_violated'] += 1
            sla_status = 'violated'
        elif solve_delay_stat > 0 or time_to_own > 0:
            stats[entity_name]['sla_ok'] += 1
            sla_status = 'compliant'
        else:
            # Aktif ticketlar için henüz ihlal yoksa buraya düşecek
            stats[entity_name]['sla_active'] += 1
            sla_status = 'active'
        
        ticket_info = {
            'id': ticket.get('id'),
            'name': ticket.get('name'),
            'date': ticket.get('date'),
            'solve_date': ticket.get('solvedate'),
            'sla_ttr_id': sla_ttr_id,
            'sla_tto_id': sla_tto_id,
            'solve_delay': solve_delay_stat,
            'time_to_own': time_to_own,
            'has_violation': has_violation,
            'violations': violation_details,
            'sla_status': sla_status
        }
        
        stats[entity_name]['tickets'].append(ticket_info)
    
    return dict(stats)

@app.route('/')
def index():
    """Ana sayfa"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/dashboard.css')
def serve_css():
    """CSS dosyasını serve et"""
    return send_from_directory('.', 'dashboard.css')

@app.route('/dashboard.js')
def serve_js():
    """JS dosyasını serve et"""
    return send_from_directory('.', 'dashboard.js')

@app.route('/api/config')
def get_config():
    """GLPI base URL'ini döndür"""
    try:
        config = load_config()
        # API URL'den base URL'i çıkar (apirest.php kısmını kaldır)
        glpi_url = config['GLPI_URL'].replace('/apirest.php', '')
        # Sondaki slash'i kaldır (çift slash önlemek için)
        glpi_url = glpi_url.rstrip('/')
        return jsonify({
            'success': True,
            'glpi_base_url': glpi_url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/entities')
def get_entities():
    """Entity listesini döndür"""
    try:
        config = load_config()
        session_token = init_session(config)
        
        try:
            entities = fetch_all_entities(config, session_token)
            
            # Liste formatına çevir
            entity_list = [
                {'id': eid, 'name': name} 
                for eid, name in sorted(entities.items(), key=lambda x: x[1])
            ]
            
            return jsonify({
                'success': True,
                'entities': entity_list
            })
        finally:
            kill_session(config, session_token)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compliance-data')
def get_compliance_data():
    """SLA uyum verilerini döndür"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        entity_filter = request.args.get('entity_id')
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': 'start_date ve end_date parametreleri gerekli'
            }), 400
        
        config = load_config()
        session_token = init_session(config)
        
        try:
            entities = fetch_all_entities(config, session_token)
            slas = fetch_all_slas(config, session_token)
            tickets = fetch_tickets(config, session_token, start_date, end_date)
            
            if not tickets:
                return jsonify({
                    'success': True,
                    'summary': {
                        'total_tickets': 0,
                        'sla_ok': 0,
                        'sla_violated': 0,
                        'sla_active': 0,
                        'compliance_rate': 0
                    },
                    'entities': [],
                    'tickets': []
                })
            
            stats = analyze_sla_compliance(tickets, entities, slas)
            
            # Entity filtresi uygula
            if entity_filter:
                entity_name = entities.get(int(entity_filter))
                if entity_name and entity_name in stats:
                    stats = {entity_name: stats[entity_name]}
                else:
                    stats = {}
            
            # Özet istatistikler
            total_tickets = sum(s['total'] for s in stats.values())
            total_sla_tickets = sum(s['sla_total'] for s in stats.values())
            total_ok = sum(s['sla_ok'] for s in stats.values())
            total_violated = sum(s['sla_violated'] for s in stats.values())
            total_active = sum(s['sla_active'] for s in stats.values())
            compliance_rate = (total_ok / total_sla_tickets * 100) if total_sla_tickets > 0 else 0
            
            # Entity bazlı veriler
            entity_data = []
            for entity_name, data in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
                violation_rate = (data['sla_violated'] / data['sla_total'] * 100) if data['sla_total'] > 0 else 0
                entity_data.append({
                    'entity': clean_entity_name(entity_name),
                    'total': data['total'],
                    'sla_total': data['sla_total'],
                    'sla_ok': data['sla_ok'],
                    'sla_violated': data['sla_violated'],
                    'sla_active': data.get('sla_active', 0),
                    'violation_rate': round(violation_rate, 2),
                    'compliance_rate': round(100 - violation_rate, 2)
                })
            
            # Ticket detaylarını topla (Global Liste)
            all_tickets = []
            for entity_name, data in stats.items():
                for ticket in data['tickets']:
                    # SLA'sı olmayanları listeye dahil etme (isteğe bağlı, şimdilik sadece SLA'lıları alalım ki tablo dolmasın)
                    # Veya kullanıcı isteğine göre "Active (Within SLA)" ve "Compliant" dendiği için SLA'sı olanlar kastediliyor.
                    
                    if not (ticket['sla_ttr_id'] or ticket['sla_tto_id']):
                        continue

                    # Durum belirle (artık hesaplanmış geliyor)
                    status = ticket.get('sla_status', 'compliant')
                    
                    # SLA İsimlerini topla
                    sla_names_list = []
                    if ticket['sla_ttr_id'] and ticket['sla_ttr_id'] in slas:
                        sla_names_list.append(slas[ticket['sla_ttr_id']]['name'])
                    if ticket['sla_tto_id'] and ticket['sla_tto_id'] in slas:
                        sla_names_list.append(slas[ticket['sla_tto_id']]['name'])
                    
                    sla_names_str = ', '.join(sla_names_list)

                    all_tickets.append({
                        'entity': clean_entity_name(entity_name),
                        'ticket_id': ticket['id'],
                        'ticket_name': ticket['name'],
                        'date': ticket['date'],
                        'status': status,
                        'row_class': 'violation' if status == 'violated' else ('success' if status == 'compliant' else 'info'),
                        'sla_names': sla_names_str,
                        'violation_details': ticket['violations'] # Varsa detay
                    })
            
            # Tarihe göre tersten sırala (en yeni en üstte)
            all_tickets.sort(key=lambda x: x['date'], reverse=True)

            return jsonify({
                'success': True,
                'summary': {
                    'total_tickets': total_tickets,
                    'total_sla_tickets': total_sla_tickets,
                    'sla_ok': total_ok,
                    'sla_violated': total_violated,
                    'sla_active': total_active,
                    'compliance_rate': round(compliance_rate, 2)
                },
                'entities': entity_data,
                'tickets': all_tickets[:500]  # İlk 500 kayıt (UI performansı için limit)
            })
            
        finally:
            kill_session(config, session_token)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export/csv')
def export_csv():
    """CSV export"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Tarih parametreleri gerekli'}), 400
        
        config = load_config()
        session_token = init_session(config)
        
        try:
            entities = fetch_all_entities(config, session_token)
            slas = fetch_all_slas(config, session_token)
            tickets = fetch_tickets(config, session_token, start_date, end_date)
            stats = analyze_sla_compliance(tickets, entities, slas)
            
            # CSV oluştur
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Entity', 'Toplam Ticket', 'SLA\'lı Ticket', 'SLA Uygun', 'SLA İhlal', 'SLA Devam (Aktif)', 'İhlal Oranı %'])
            
            for entity_name, data in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
                violation_rate = (data['sla_violated'] / data['sla_total'] * 100) if data['sla_total'] > 0 else 0
                writer.writerow([
                    clean_entity_name(entity_name),
                    data['total'],
                    data['sla_total'],
                    data['sla_ok'],
                    data['sla_violated'],
                    data.get('sla_active', 0),
                    f"{violation_rate:.2f}"
                ])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'sla_report_{start_date}_{end_date}.csv'
            )
            
        finally:
            kill_session(config, session_token)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("SLA Compliance Dashboard API")
    print("=" * 60)
    print("Dashboard: http://localhost:5000")
    print("API Endpoints:")
    print("  - GET /api/entities")
    print("  - GET /api/compliance-data?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD")
    print("  - GET /api/export/csv?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
