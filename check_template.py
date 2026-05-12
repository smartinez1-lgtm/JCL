#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_inventory.settings')

import django
django.setup()

from django.template.loader import render_to_string

context = {
    'branch_count': 1,
    'total_stock': 1790,
    'transaction_count': 2,
    'total_sales': 479,
    'branch_sales': [],
    'total_items': 2,
    'low_stock_count': 0,
    'pending_users': [],
    'recent_transactions': [],
    'low_stock_items': [],
}

html = render_to_string('core/dashboard.html', context)
print("="*80)
print("LOOKING FOR 'WELCOME BACK' OR 'CONTROL STOCK':")
print("="*80)
if 'Welcome back' in html:
    idx = html.find('Welcome back')
    print(f"FOUND 'Welcome back' at position {idx}")
    print(html[idx-100:idx+200])
elif 'Control stock' in html:
    idx = html.find('Control stock')
    print(f"FOUND 'Control stock' at position {idx}")
    print(html[idx-100:idx+200])
else:
    print("NEITHER FOUND!")
    # Search for h1 heading
    idx = html.find('<h1')
    if idx != -1:
        print(f"Found h1 at position {idx}:")
        print(html[idx:idx+300])
