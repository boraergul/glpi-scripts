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

def load_valid_tags(csv_path):
    valid_tags = set()
    try:
        # Use utf-8-sig to handle potential BOM
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                tag_entry = row.get('Tag', '')
                if not tag_entry: continue
                
                parts = re.findall(r'##(.*?)##', tag_entry)
                for p in parts:
                    core = get_core_tag(p)
                    if core:
                        valid_tags.add(core.lower()) # Case insensitive
    except Exception as e:
        print(f"Error loading CSV: {e}")
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
        print(f"Error reading file: {e}")
    return tags_found

def validate():
    csv_path = 'templatetags.csv'
    generator_path = 'generate_email_templates.py'
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
    
    valid_tags = load_valid_tags(csv_path)
    # Common GLPI internal tags that might be missing from documentation CSV
    logic_keywords = {'else', 'glpi.url', 'glpi.name'} 
    
    extracted = extract_tags_from_file(generator_path)
    invalid_tags = []
    
    for item in extracted:
        raw_tag = item['tag']
        # Handle the ###ticket.id## case which is actually ## + #ticket.id + ##
        # or simple text followed by ##tag##. But regex captures everything between ##...##
        # If it's ###ticket.id##, and regex is ##(.*?)##, it might capture #ticket.id.
        core_tag = get_core_tag(raw_tag).lower()
        if core_tag.startswith('#'): core_tag = core_tag[1:]
        
        if not core_tag or core_tag in logic_keywords:
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
