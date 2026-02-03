import json
import os
import datetime
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

# Configuration
DATA_FILE = os.path.join("data", "yields.json")
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"
SITE_URL = "https://crypto-yield-arbitrage.vercel.app" # To be updated with real domain

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

    # 4.1 Pre-calculate Similar Pools (by APY)
    # Sort by APY to find close neighbors
    pools_by_apy = sorted(pools, key=lambda x: x.get('apy', 0))
    pool_neighbors = {}
    for i, pool in enumerate(pools_by_apy):
        # Pick 5 neighbors (2 before, 3 after handling boundaries)
        start = max(0, i - 2)
        end = min(len(pools_by_apy), i + 4)
        neighbors = [p for p in pools_by_apy[start:end] if p['slug'] != pool['slug']]
        pool_neighbors[pool['slug']] = neighbors[:5]

    # 5. Generate Index Page
    print("[*] Generating index page...")
    # Pass 'recent_pools' (just another slice for the bottom section to prompt crawling)
    index_html = index_template.render(pools=pools, recent_pools=pools[100:150], build_time=build_time)
    
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
        similar = pool_neighbors.get(pool['slug'], [])
        detail_html = detail_template.render(pool=pool, similar_pools=similar, site_url=SITE_URL, build_time=build_time)
        file_path = os.path.join(pools_dir, f"{pool['slug']}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(detail_html)
            
    print(f"[*] Build complete. All files saved to {OUTPUT_DIR}/")

    # 7. Generate Sitemap.xml
    print("[*] Generating sitemap.xml...")
    sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Add home
    sitemap_content.append(f"  <url><loc>{SITE_URL}/</loc><lastmod>{datetime.datetime.now().strftime('%Y-%m-%d')}</lastmod><priority>1.0</priority></url>")
    
    # Add pools
    for pool in pools:
        sitemap_content.append(f"  <url><loc>{SITE_URL}/pools/{pool['slug']}.html</loc><lastmod>{datetime.datetime.now().strftime('%Y-%m-%d')}</lastmod><priority>0.8</priority></url>")
    
    sitemap_content.append('</urlset>')
    
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_content))

    # 8. Generate robots.txt
    print("[*] Generating robots.txt...")
    robots_content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_content)

if __name__ == "__main__":
    build_site()
