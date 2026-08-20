import re

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Use regex to find the catch-all
pattern = re.compile(r'# Catch-all: mount static fallback for root files\n@app\.get\("/\{filename\}"\)\nasync def get_root_static_file.*?raise HTTPException\(status_code=404, detail="File not found"\)', re.DOTALL)

match = pattern.search(content)
if match:
    catch_all_text = match.group(0)
    # Remove it from its current position
    content = content.replace(catch_all_text, '')
    # Append to bottom
    content = content + '\n\n' + catch_all_text
    
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Could not find catch-all")
