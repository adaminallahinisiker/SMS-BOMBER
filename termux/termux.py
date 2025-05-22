import os
import sys
import time
import json
import random
import threading
from api import SendSms

CONFIG_FILE = "config.json"
BAD_FILE = "bad.json"
PROXY_FILE = "proxyler.txt"
PROXY_BLACKLIST_FILE = "proxy_blacklist.txt"

def get_default_settings():
    return {
        "auto_skip_failed": True,
        "use_proxy": False,
        "random_proxy": True,
    }

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**get_default_settings(), **json.load(f)}
        except:
            return get_default_settings()
    else:
        return get_default_settings()

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def save_failed_services(data):
    with open(BAD_FILE, "w") as f:
        json.dump(list(data), f)

def load_failed_services():
    if os.path.exists(BAD_FILE):
        try:
            with open(BAD_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def load_proxies():
    if not os.path.exists(PROXY_FILE):
        return []
    with open(PROXY_FILE) as f:
        return [line.strip() for line in f if line.strip()]

def load_proxy_blacklist():
    if not os.path.exists(PROXY_BLACKLIST_FILE):
        return set()
    with open(PROXY_BLACKLIST_FILE) as f:
        return set(line.strip() for line in f if line.strip())

def blacklist_proxy(proxy):
    with open(PROXY_BLACKLIST_FILE, "a") as f:
        f.write(proxy + "\n")

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    clear_terminal()
    print("""
███████╗██████╗ ███████╗███╗   ██╗ █████╗ ███████╗
██╔════╝██╔══██╗██╔════╝████╗  ██║██╔══██╗╚════██║
█████╗  ██████╔╝█████╗  ██╔██╗ ██║╚██████║    ██╔╝
██╔══╝  ██╔══██╗██╔══╝  ██║╚██╗██║ ╚═══██║   ██╔╝ 
███████╗██║  ██║███████╗██║ ╚████║ █████╔╝   ██║  
╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝ ╚════╝    ╚═╝  
                                                  
    """)

def get_proxy():
    if not settings.get("use_proxy") or not proxies:
        return None
    proxy = random.choice(proxies)
    if proxy in blacklisted:
        return get_proxy()
    return proxy

def run_service(sms, attr):
    proxy = get_proxy()
    try:
        before = sms.adet
        getattr(sms, attr)()
        if sms.adet > before:
            print(f"[✓] {attr.upper():<20} → BAŞARILI")
        else:
            raise Exception("artış yok")
    except:
        print(f"[X] {attr.upper():<20} → BAŞARISIZ")
        failed_services.add(attr)
        save_failed_services(failed_services)
        if proxy:
            blacklist_proxy(proxy)

def send_sms_loop(phone, mail, kere, interval, turbo=False):
    sms = SendSms(phone, mail)
    sent = 0

    def process():
        nonlocal sent
        for attr in servisler_sms:
            if settings["auto_skip_failed"] and attr in failed_services:
                continue
            if kere and sent >= kere:
                return
            run_service(sms, attr)
            sent += 1
            time.sleep(interval)

    if turbo:
        while not kere or sent < kere:
            threads = []
            for attr in servisler_sms:
                if settings["auto_skip_failed"] and attr in failed_services:
                    continue
                t = threading.Thread(target=run_service, args=(sms, attr))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
            sent += len(threads)
    else:
        while not kere or sent < kere:
            process()

def ayarlar_menusu():
    while True:
        print_banner()
        print("⚙️  Ayarlar")
        print("1. Başarısız servisleri atla:     {}".format(settings['auto_skip_failed']))
        print("2. Proxy kullan:                   {}".format(settings['use_proxy']))
        print("3. Proxy rastgele seçilsin mi?:   {}".format(settings['random_proxy']))
        print("4. Ayarları kaydet ve çık")
        secim = input("\nSeçim yap [1-4]: ")
        if secim == "1":
            settings['auto_skip_failed'] = not settings['auto_skip_failed']
        elif secim == "2":
            settings['use_proxy'] = not settings['use_proxy']
        elif secim == "3":
            settings['random_proxy'] = not settings['random_proxy']
        elif secim == "4":
            save_config(settings)
            break

servisler_sms = [func for func in dir(SendSms) if callable(getattr(SendSms, func)) and not func.startswith("__")]
settings = load_config()
failed_services = load_failed_services()
proxies = load_proxies()
blacklisted = load_proxy_blacklist()

def main_menu():
    while True:
        print_banner()
        print("1. SMS Gönder")
        print("2. Ayarlar")
        print("3. Çıkış")
        secim = input("\nSeçiminiz: ")
        if secim == "1":
            sms_gonder_menusu()
        elif secim == "2":
            ayarlar_menusu()
        elif secim == "3":
            print("\nÇıkılıyor...")
            break


def sms_gonder_menusu():
    print_banner()
    print("📲 SMS GÖNDER")
    phone = input("[?] Telefon Numarası (5xx...): ")
    mail = input("[?] Mail (opsiyonel): ")
    try:
        kere = int(input("[?] Kaç adet SMS gönderilsin? (0 = sonsuz): "))
    except:
        kere = 0
    try:
        interval = float(input("[?] Gönderim aralığı (saniye): "))
    except:
        interval = 3.0
    turbo = input("[?] Turbo mod? (e/h): ").lower() == 'e'

    print("\nGönderim başlıyor... CTRL+C ile durdurabilirsiniz.\n")
    try:
        send_sms_loop(phone, mail, kere if kere > 0 else None, interval, turbo)
    except KeyboardInterrupt:
        print("\n⛔ Gönderim durduruldu.")

if __name__ == "__main__":
    main_menu()
