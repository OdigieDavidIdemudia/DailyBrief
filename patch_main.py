with open('app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('app = FastAPI')
idx = text.find('\n', idx) + 1

middleware_code = """
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response
"""

new_text = text[:idx] + middleware_code + text[idx:]

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(new_text)
