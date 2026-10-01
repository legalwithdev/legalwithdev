#!/usr/bin/env python3
# Point the "Watch legal videos" button to the new /videos feed page
# (instead of opening the overlay).
OLD = "    if(b) b.addEventListener('click', open);"
NEW = "    if(b) b.addEventListener('click', function(){ location.href='/videos'; });"

for p in ['index.html', 'app.html']:
    s = open(p, encoding='utf-8').read()
    if NEW in s:
        print('SKIP already pointed:', p); continue
    if OLD not in s:
        print('WARN anchor not found:', p); continue
    s = s.replace(OLD, NEW, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('PATCHED', p)
print('DONE')
