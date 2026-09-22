import re
import os

with open(r'd:\projects\SCOF_V1\SCOF\scripts\schema_ddl.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

tables = set(re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)', sql, re.IGNORECASE))

with open(r'C:\Users\Gowshick\.gemini\antigravity-ide\brain\a2c1edf9-ac72-4bf0-8dc2-a71df4430a2a\SCOF_Enterprise_Domain_and_Node_Registry.md', 'r', encoding='utf-8') as f:
    text = f.read()

domain_blocks = re.split(r'###\s+Domain\s+(\d+):\s+([^\n]+)', text)

nodes = []
for i in range(1, len(domain_blocks), 3):
    dom_num = domain_blocks[i]
    dom_name = domain_blocks[i+1].strip()
    dom_text = domain_blocks[i+2]
    dom_key = f"Domain {dom_num}: {dom_name}"
    
    for line in dom_text.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|')]
        cols = parts[1:-1]
        if len(cols) >= 8:
            clean_0 = cols[0].strip('`').strip()
            if clean_0.startswith('NOD_'):
                nodes.append({
                    'domain_num': dom_num,
                    'domain': dom_key,
                    'node_id': clean_0,
                    'node_name': cols[1].strip('`').strip(),
                    'class': cols[2].strip('`').strip(),
                    'pk': cols[3].strip('`').strip(),
                    'bk': cols[4].strip('`').strip(),
                    'parent': cols[5].strip('`').strip(),
                    'lifecycle': cols[6].strip('`').strip(),
                    'attrs_rels': cols[7].strip('`').strip()
                })

def to_snake(name):
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    return s

direct_tables = []
non_direct = []

for n in nodes:
    name = n['node_name']
    snake = to_snake(name)
    if snake in tables or name.lower() in tables:
        tbl = snake if snake in tables else name.lower()
        direct_tables.append((n, tbl))
    else:
        non_direct.append(n)

print(f"Total domain nodes: {len(nodes)}")
print(f"Direct table matches: {len(direct_tables)}")
print(f"Non-direct nodes: {len(non_direct)}")

print("\n--- NON-DIRECT NODES BY DOMAIN ---")
by_dom = {}
for n in non_direct:
    d = n['domain']
    by_dom.setdefault(d, []).append(n)

for d, nds in sorted(by_dom.items()):
    print(f"\n{d} ({len(nds)} non-direct):")
    for item in nds:
        print(f"  - {item['node_id']} | {item['node_name']} | {item['class']} | Parent: {item['parent']}")
