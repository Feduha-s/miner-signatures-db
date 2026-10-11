import urllib.request
import json
import re
from datetime import datetime

STATIC_PROCESSES = [
    # Майнеры
    "xmrig", "xmr-stak", "ethminer", "phoenixminer", "nbminer", "t-rex",
    "gminer", "lolminer", "teamredminer", "nanominer", "cpuminer", 
    "silentminer", "silentcryptominer", "wildrig", "srbminer", "bminer",
    # Клипперы
    "clipper", "autoclip", "cryptoclipper",
    # Стиллеры и трояны (Lumma, RedLine, AsyncRAT, Warzone, Stealc и др.)
    "redline", "lumma", "stealc", "vidar", "racoon", "asyncrat",
    "remcos", "agenttesla", "njrat", "xworm", "quasar", "dcrat"
]

STATIC_FILES = [
    "xmrig.exe", "WinRing0x64.sys", "config.json", "pools.txt",
    "libcrypto-1_1-x64.dll", "silent.exe", "miner.exe", "stub.exe"
]

POOL_FEEDS = [
    "https://raw.githubusercontent.com/hoshsadiq/adblock-nocoin-list/master/hosts",
    "https://raw.githubusercontent.com/Marf/coinblockerlists/master/hosts"
]

MALWARE_HASH_FEED = "https://bazaar.abuse.ch/export/txt/sha256/recent/"

def fetch_pool_domains():
    domains = set([
        "stratum+tcp://", "stratum+ssl://", "nanopool.org", "ethermine.org",
        "supportxmr.com", "minexmr.com", "2miners.com", "f2pool.com",
        "hashvault.pro", "moneroocean.stream", "poolin.me", "viabtc.com"
    ])
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MinerSearchPro-Bot/1.0"}
    
    for url in POOL_FEEDS:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] in ("0.0.0.0", "127.0.0.1"):
                        domain = parts[1].strip().lower()
                        if re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', domain):
                            domains.add(domain)
        except Exception as e:
            print(f"[-] Ошибка загрузки фида {url}: {e}")
            
    return sorted(list(domains))

def fetch_malware_hashes(limit=2000):
    hashes = set()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MinerSearchPro-Bot/1.0"}
    
    print("[*] Загрузка актуальных хэшей вирусов с MalwareBazaar...")
    try:
        req = urllib.request.Request(MALWARE_HASH_FEED, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Валидация 64 символов hex (SHA-256)
                if re.match(r'^[a-fA-F0-9]{64}$', line):
                    hashes.add(line.lower())
                    if len(hashes) >= limit:
                        break
        print(f"[+] Успешно получено {len(hashes)} хэшей.")
    except Exception as e:
        print(f"[-] Ошибка загрузки хэшей MalwareBazaar: {e}")
        
    return sorted(list(hashes))

def main():
    print("[+] Сборка актуальной базы сигнатур (Майнеры + Вирусы)...")
    pools = fetch_pool_domains()
    virus_hashes = fetch_malware_hashes(limit=2500)
    
    today_version = datetime.utcnow().strftime("%Y.%m.%d")
    
    database = {
        "version": today_version,
        "lastUpdatedUtc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "processSignatures": sorted(list(set(STATIC_PROCESSES))),
        "poolSignatures": pools,
        "fileSignatures": sorted(list(set(STATIC_FILES))),
        "virusHashSignatures": virus_hashes
    }
    
    with open("signatures.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
        
    print(f"[+] Готово! Пулов: {len(pools)}, Хэшей вирусов: {len(virus_hashes)}. Версия: {today_version}")

if __name__ == "__main__":
    main()
