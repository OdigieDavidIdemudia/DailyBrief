with open('static/downtime.html', 'r', encoding='utf-8') as f:
    content = f.read()

ids = ['f-downtime_id', 'f-start_date', 'f-start_time', 'f-end_date', 'f-end_time', 'f-duration', 'f-system_affected', 'f-severity', 'f-impact_summary', 'f-detection', 'f-root_cause', 'f-mitigation', 'f-preventive', 'f-internal', 'f-external']

for i in ids:
    if f'id="{i}"' not in content:
        print(f'MISSING ID: {i}')
print('Done checking IDs.')
