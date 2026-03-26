import re
import csv
import os

def get_core_tag(raw_content):
    # Strip common logic prefixes/suffixes to get the base GLPI tag
    core = raw_content.strip()
    
    # Order matters: strip longer prefixes first
    prefixes = ['FOREACH FIRST <number> ', 'FOREACH LAST <number> ', 'FOREACH ', 'ENDFOREACH', 'IF', 'ENDIF', 'ELSE']
    for p in prefixes:
        if core.startswith(p):
            core = core[len(p):].strip()
            # Special case for ELSE which might be standalone
            if not core and p == 'ELSE':
                return 'ELSE'
            break
    return core

def load_valid_tags(file_path):
    valid_tags = set()
    try:
        if file_path.endswith('.csv'):
            with open(file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    tag_entry = row.get('Tag', '')
                    if not tag_entry: continue
                    
                    parts = re.findall(r'##(.*?)##', tag_entry)
                    for p in parts:
                        core = get_core_tag(p)
                        if core:
                            valid_tags.add(core.lower()) # Case insensitive
        elif file_path.endswith('.md'):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '|' in line and '##' in line:
                        parts = re.findall(r'##(.*?)##', line)
                        for p in parts:
                            core = get_core_tag(p)
                            if core:
                                valid_tags.add(core.lower())
    except Exception as e:
        print(f"Error loading tags from {file_path}: {e}")
    return valid_tags

def extract_tags_from_file(file_path):
    tags_found = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.finditer(r'##(.*?)##', content)
            for m in matches:
                tags_found.append({
                    'tag': m.group(1),
                    'line': content.count('\n', 0, m.start()) + 1
                })
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return tags_found

def validate():
    md_path = 'glpi_notification_tags.md'
    csv_path = 'templatetags.csv'
    generator_path = 'generate_email_templates.py'
    
    valid_tags = set()
    if os.path.exists(md_path):
        valid_tags.update(load_valid_tags(md_path))
    if os.path.exists(csv_path):
        valid_tags.update(load_valid_tags(csv_path))
        
    if not valid_tags:
        print(f"No tag definition files found. Please ensure {md_path} or {csv_path} exist.")
        return
    
    # Common GLPI internal tags that might be missing from documentation files
    known_undocumented_tags = {
        'else', 'glpi.url', 'glpi.name', 'lang.gmt', 'lang.ticket.url',
        'change.name', 'crontask.description', 'crontask.name',
        'followup', 'followup.content',
        'item.alarm_threshold', 'item.message', 'item.ref', 'item.stock', 'item.type',
        'knowbaseitem.category', 'knowbaseitem.name', 'knowbaseitem.url',
        'mailcollector.errors', 'mysqlvalidator.text', 'plugin.updates',
        'problem.creationdate', 'problem.name', 'problem.priority', 'problem.solution.description', 'problem.solution.type',
        'project.code', 'project.content', 'project.manager', 'project.name', 'project.priority', 'project.url', 'project.users_id_lastupdater',
        'projecttask.begin', 'projecttask.content', 'projecttask.end', 'projecttask.name', 'projecttask.url',
        'reservation.begin', 'reservation.comment', 'reservation.end', 'reservation.item',
        'savedsearch.count', 'savedsearch.name', 'savedsearch.url',
        'task.state', 'task.tech',
        'ticket.actiontime', 'ticket.internal_time_to_own', 'ticket.time_to_resolve', 'ticket.updatedate', 'ticket.urlapproval',
        'user.realname', 'user.urlpasswordforgotten'
    } 
    
    extracted = extract_tags_from_file(generator_path)
    invalid_tags = []
    
    for item in extracted:
        raw_tag = item['tag']
        # Handle the ###ticket.id## case which is actually ## + #ticket.id + ##
        # or simple text followed by ##tag##. But regex captures everything between ##...##
        # If it's ###ticket.id##, and regex is ##(.*?)##, it might capture #ticket.id.
        core_tag = get_core_tag(raw_tag).lower()
        if core_tag.startswith('#'): core_tag = core_tag[1:]
        
        if not core_tag or core_tag in known_undocumented_tags:
            continue
            
        if core_tag not in valid_tags:
            invalid_tags.append({
                'raw': raw_tag,
                'core': core_tag,
                'line': item['line']
            })

    if not invalid_tags:
        print("✅ All tags in generate_email_templates.py are valid!")
    else:
        print(f"❌ Found {len(invalid_tags)} potentially invalid tags:")
        # Group by tag name to see unique issues
        unique_invalid = {}
        for it in invalid_tags:
            if it['core'] not in unique_invalid:
                unique_invalid[it['core']] = []
            unique_invalid[it['core']].append(it['line'])
        
        for tag, lines in sorted(unique_invalid.items()):
            lines_str = ", ".join(map(str, sorted(list(set(lines)))[:5]))
            if len(set(lines)) > 5: lines_str += "..."
            print(f"- '{tag}' (used on lines: {lines_str})")

if __name__ == "__main__":
    validate()
