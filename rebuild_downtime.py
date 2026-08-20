import re

with open('static/dashboard.html', 'r', encoding='utf-8') as f:
    dashboard = f.read()

with open('static/downtime.html', 'r', encoding='utf-8') as f:
    downtime = f.read()

# Extract the script and styles from downtime.html
style_match = re.search(r'<style>(.*?)</style>', downtime, re.DOTALL)
style_content = style_match.group(0) if style_match else ''

script_match = re.search(r'<script>(.*?)</script>', downtime, re.DOTALL)
script_content = script_match.group(0) if script_match else ''

# Extract the main UI we built for downtime
# We want everything inside the flex-1 overflow-hidden flex flex-col md:flex-row div
ui_match = re.search(r'<div class="flex-1 overflow-hidden flex flex-col md:flex-row">(.*?)</div>\s*</main>', downtime, re.DOTALL)
if not ui_match:
    # Alternative extraction
    ui_match = re.search(r'<main[^>]*>.*?<header[^>]*>.*?</header>(.*?)</main>', downtime, re.DOTALL)

ui_content = ui_match.group(1) if ui_match else '<div>Error extracting UI</div>'

# Now we inject this into dashboard.html's main area
# Replace what's inside dashboard's <main> tag
def replacer(m):
    return m.group(1) + f"""
    <header class="mb-lg flex justify-between items-center">
        <h1 class="text-2xl font-bold text-on-surface">Downtime Register</h1>
    </header>
    <div class="flex-1 flex gap-4 h-full" style="height: calc(100vh - 120px)">
        {ui_content}
    </div>
    """ + m.group(2)

new_downtime = re.sub(r'(<main[^>]*>).*?(</main>)', replacer, dashboard, flags=re.DOTALL)

# Inject the styles into head
new_downtime = new_downtime.replace('</head>', style_content + '\n</head>')

# Inject script before </body>
new_downtime = new_downtime.replace('</body>', script_content + '\n</body>')

# Update title
new_downtime = re.sub(r'<title>.*?</title>', '<title>Downtime Register - Daily BRIEF</title>', new_downtime)

# Make the downtime sidebar link active
# Dashboard link should lose 'bg-primary/10 text-primary border-l-4 border-primary aria-current="page"'
# And it should just be the secondary link style.
active_classes = 'bg-primary/10 text-primary font-medium border-l-4 border-primary'
inactive_classes = 'text-secondary hover:bg-surface-container transition-colors border-l-4 border-transparent'

# Change Dashboard to inactive
new_downtime = new_downtime.replace(
    '<a href="/dashboard" class="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary font-medium border-l-4 border-primary" aria-current="page">',
    '<a href="/dashboard" class="flex items-center gap-3 px-3 py-2 rounded-lg text-secondary hover:bg-surface-container transition-colors border-l-4 border-transparent">'
)

# Change Downtime Register to active
new_downtime = new_downtime.replace(
    '<a href="/downtime" class="flex items-center gap-3 px-3 py-2 rounded-lg text-secondary hover:bg-surface-container transition-colors border-l-4 border-transparent">',
    '<a href="/downtime" class="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary font-medium border-l-4 border-primary" aria-current="page">'
)

with open('static/downtime.html', 'w', encoding='utf-8') as f:
    f.write(new_downtime)

print("downtime.html rebuilt based on dashboard.html shell.")
