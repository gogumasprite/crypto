import requests
import json
import math
import os

# Configuration
API_URL = "https://yields.llama.fi/pools"
TVL_THRESHOLD = 1_000_000 # $1M
APY_THRESHOLD = 1_000       # 1,000%
OUTPUT_PATH = os.path.join("data", "yields.json")

def calculate_stability_score(tvl, apy, sigma):
    """
    Score = (Log10(TVL) / (1 + Volatility)) * APY
    Volatility proxy = sigma (provided by DefiLlama)
    """
    if tvl <= 0 or apy <= 0:
        return 0
    
    log_tvl = math.log10(tvl)
    volatility = sigma if sigma is not None else 0.5 # Default to moderate volatility if missing
    
    # We use (1 + volatility) to dampen the log_tvl effect for high volatility assets
    # Stability score is higher when TVL is high, APY is high, and Volatility is low.
    score = (log_tvl / (1 + volatility)) * apy
    return round(score, 2)

def fetch_and_process():
    print(f"[*] Fetching data from {API_URL}...")
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        raw_data = response.json()
    except Exception as e:
        print(f"[!] Error fetching data: {e}")
        return

    if raw_data.get("status") != "success":
        print("[!] API returned non-success status.")
        return

    pools = raw_data.get("data", [])
    print(f"[*] Total pools found: {len(pools)}")

    processed_data = []
    skipped_tvl = 0
    skipped_apy = 0

    for pool in pools:
        tvl = pool.get("tvlUsd", 0)
        apy = pool.get("apy", 0)
        sigma = pool.get("sigma", 0)

        # Spam Filtering
        if tvl < TVL_THRESHOLD:
            skipped_tvl += 1
            continue
        
        if apy > APY_THRESHOLD:
            skipped_apy += 1
            continue

        # Stability Score Calculation
        pool["stability_score"] = calculate_stability_score(tvl, apy, sigma)
        
        processed_data.append(pool)

    # Sort by stability score descending
    processed_data.sort(key=lambda x: x["stability_score"], reverse=True)

    print(f"[*] Filtering complete.")
    print(f"    - Skipped (TVL < $1M): {skipped_tvl}")
    print(f"    - Skipped (APY > 1000%): {skipped_apy}")
    print(f"    - Resulting pools: {len(processed_data)}")

    # Save to JSON
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=4, ensure_ascii=False)
    
    print(f"[*] Saved processed data to {OUTPUT_PATH}")

if __name__ == "__main__":
    fetch_and_process()
