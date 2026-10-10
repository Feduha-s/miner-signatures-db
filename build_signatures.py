import urllib.request
import json
import re
from datetime import datetime

# Базовые известные процессы и файлы майнеров
STATIC_PROCESSES = [
    "xmrig", "xmr-stak", "ethminer", "phoenixminer", "nbminer", "t-rex",
    "gminer", "lolminer", "teamredminer", "nanominer", "cpuminer", 
    "silentminer", "silentcryptominer", "wildrig", "srbminer", "bminer"
]

STATIC_FILES = [
    "xmrig.exe", "WinRing0x64.sys", "config.json", "pools.txt"
]

# Проверенные фиды открытых баз крипто-пулов и вредоносных хостов
FEEDS = [
    "https://raw.githubusercontent.com/hoshsadiq/adblock-nocoin-list/master/hosts",
    "https://raw.githubusercontent.com/Marf/coinblockerlists/master/hosts",
]

def fetch_pool_domains():
    domains = set([
        "stratum+tcp://", "stratum+ssl://", "nanopool.org", "ethermine.org",
        "supportxmr.com", "minexmr.com", "2miners.com", "f2pool.com",
        "hashvault.pro", "moneroocean.stream", "poolin.me", "viabtc.com"
    ])
    
    headers = {"User-Agent": "Mozilla/5.0 (MinerSearchPro-Bot)"}
    
    for url in FEEDS:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    # Извлечение доменов из hosts-формата (0.0.0.0 domain.com или 127.0.0.1 domain.com)
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] in ("0.0.0.0", "127.0.0.1"):
                        domain = parts[1].strip().lower()
                        if re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', domain):
                            domains.add(domain)
        except Exception as e:
            print(f"[-] Не удалось загрузить фид {url}: {e}")
            
    return sorted(list(domains))

def main():
    print("[+] Сборка актуальной базы сигнатур...")
    pools = fetch_pool_domains()
    
    today_version = datetime.utcnow().strftime("%Y.%m.%d")
    
    database = {
        "version": today_version,
        "lastUpdatedUtc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "processSignatures": sorted(list(set(STATIC_PROCESSES))),
        "poolSignatures": pools,
        "fileSignatures": sorted(list(set(STATIC_FILES)))
    }
    
    with open("signatures.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
        
    print(f"[+] Готово! Всего пулов в базе: {len(pools)}. Версия: {today_version}")

if __name__ == "__main__":
    main()
