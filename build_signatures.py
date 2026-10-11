import urllib.request
import json
import re
from datetime import datetime

# 1. Известные процессы майнеров, стиллеров, RAT и троянов
STATIC_PROCESSES = [
    # Майнеры
    "xmrig", "xmr-stak", "ethminer", "phoenixminer", "nbminer", "t-rex",
    "gminer", "lolminer", "teamredminer", "nanominer", "cpuminer", 
    "silentminer", "silentcryptominer", "wildrig", "srbminer", "bminer",
    # С Cryptojacking / Клипперы
    "clipper", "autoclip", "cryptoclipper",
    # Свежие стиллеры и трояны (Lumma, RedLine, AsyncRAT, Warzone, Stealc)
    "redline", "lumma", "stealc", "vidar", "racoon", "asyncrat",
    "remcos", "agenttesla", "njrat", "xworm", "quasar", "dcrat"
]

# 2. Характерные файлы майнеров и дропперов
STATIC_FILES = [
    "xmrig.exe", "WinRing0x64.sys", "config.json", "pools.txt",
    "libcrypto-1_1-x64.dll", "silent.exe", "miner.exe", "stub.exe"
]

# 3. Фиды пулов майнинга
POOL_FEEDS = [
    "https://raw.githubusercontent.com/hoshsadiq/adblock-nocoin-list/master/hosts",
    "https://raw.githubusercontent.com/Marf/coinblockerlists/master/hosts"
]

# 4. Фид свежих хэшей вредоносных программ (MalwareBazaar от abuse.ch)
# Содержит последние обнаруженные образцы троянов, вымогателей и стиллеров
MALWARE_HASH_FEED = "https://bazaar.abuse.ch/export/txt/sha256/recent/"

def fetch_pool_domains():
    domains = set([
        "stratum+tcp://", "stratum+ssl://", "nanopool.org", "ethermine.org",
        "supportxmr.com", "minexmr.com", "2miners.com", "f2pool.com",
        "hashvault.pro", "moneroocean.stream", "poolin.me", "viabtc.com"
    ])
    
    headers = {"User-Agent": "Mozilla/5.0 (MinerSearchPro-Bot)"}
    
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
            print(f"[-] Не удалось загрузить фид пулов {url}: {e}")
            
    return sorted(list(domains))

def fetch_malware_hashes(limit=1500):
    hashes = set()
    headers = {"User-Agent": "Mozilla/5.0 (MinerSearchPro-Bot)"}
    
    print("[*] Загрузка актуальных хэшей вирусов с MalwareBazaar...")
    try:
        req = urllib.request.Request(MALWARE_HASH_FEED, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            for line in content.splitlines():
                line = line.strip()
                # Пропускаем комментарии фида abuse.ch
                if not line or line.startswith('#'):
                    continue
                # Валидируем SHA-256 хэш (ровно 64 hex-символа)
                if re.match(r'^[a-fA-F0-9]{64}$', line):
                    hashes.add(line.lower())
                    if len(hashes) >= limit:
                        break
        print(f"[+] Успешно получено {len(hashes)} хэшей вирусов.")
    except Exception as e:
        print(f"[-] Не удалось загрузить хэши с MalwareBazaar: {e}")
        
    return sorted(list(hashes))

def main():
    print("[+] Сборка расширенной базы сигнатур (Майнеры + Вирусы)...")
    pools = fetch_pool_domains()
    virus_hashes = fetch_malware_hashes(limit=2000)
    
    today_version = datetime.utcnow().strftime("%Y.%m.%d")
    
    database = {
        "version": today_version,
        "lastUpdatedUtc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "processSignatures": sorted(list(set(STATIC_PROCESSES))),
        "poolSignatures": pools,
        "fileSignatures": sorted(list(set(STATIC_FILES))),
        "virusHashSignatures": virus_hashes  # Новая база SHA-256 хэшей вирусов
    }
    
    with open("signatures.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
        
    print(f"[+] Готово! Пулов: {len(pools)}, Хэшей вирусов: {len(virus_hashes)}. Версия: {today_version}")

if __name__ == "__main__":
    main()
