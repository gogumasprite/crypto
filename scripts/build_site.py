import json
import os
import datetime
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

# Configuration
DATA_FILE = os.path.join("data", "yields.json")
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"

def build_site():
    print("[*] Starting site build process...")
    
    # 1. Load Data
    if not os.path.exists(DATA_FILE):
        print(f"[!] Data file not found: {DATA_FILE}. Run fetch_data.py first.")
        return
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        pools = json.load(f)
    
    # 2. Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    base_template = env.get_template("base.html")
    index_template = env.get_template("index.html")
    detail_template = env.get_template("detail.html")
    
    build_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 3. Load Referrals
    REFERRAL_FILE = os.path.join("data", "referrals.json")
    referrals = {"projects": {}, "default": "#"}
    if os.path.exists(REFERRAL_FILE):
        with open(REFERRAL_FILE, "r", encoding="utf-8") as f:
            referrals = json.load(f)

    # 4. Prepare Metadata & Slugs
    for pool in pools:
        # Create a unique, SEO-friendly slug
        slug_base = f"{pool['chain']}-{pool['project']}-{pool['symbol']}-{pool['pool'][:8]}"
        pool['slug'] = slugify(slug_base)
        
        # Inject referral link
        project_id = pool.get("project", "").lower()
        pool['referral_link'] = referrals["projects"].get(project_id, referrals.get("default", "#"))

    # 5. Generate Index Page
    print("[*] Generating index page...")
    index_html = index_template.render(pools=pools, build_time=build_time)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    
    # 6. Generate Detail Pages
    print(f"[*] Generating {len(pools)} detail pages...")
    pools_dir = os.path.join(OUTPUT_DIR, "pools")
    if not os.path.exists(pools_dir):
        os.makedirs(pools_dir)
        
    for pool in pools:
        detail_html = detail_template.render(pool=pool, build_time=build_time)
        file_path = os.path.join(pools_dir, f"{pool['slug']}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(detail_html)
            
    print(f"[*] Build complete. All files saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    build_site()
