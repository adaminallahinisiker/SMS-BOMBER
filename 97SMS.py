import subprocess
import sys

def install(package):
    try:
        __import__(package)
    except ImportError:
        print(f"[!] {package} eksik, yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Gerekli tüm kütüphaneleri burada tanımla
dependencies = {
    "customtkinter": "customtkinter",
    "matplotlib": "matplotlib",
    "tkinter": "tkinter",
    "threading": "threading",
    "subprocess": "subprocess",
    "colorama" : "colorama",
    "requests" : "requests"
}

for name, pkg in dependencies.items():
    install(pkg)

import customtkinter as ctk
import threading
from api import SendSms
import time
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
import json, os, random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

CONFIG_FILE = "config.json"
BAD_FILE = "bad.json"
PROXY_FILE = "proxyler.txt"
PROXY_BLACKLIST_FILE = "proxy_blacklist.txt"
DEFAULT_PASSWORD = "EREN97"

servisler_sms = [func for func in dir(SendSms) if callable(getattr(SendSms, func)) and not func.startswith("__")]

def get_default_settings():
    return {
        "theme": "dark",
        "font_size": "medium",
        "fullscreen_start": False,
        "show_logo": True,
        "log_enabled": True,
        "log_dir": "logs",
        "log_clear_on_exit": False,
        "auto_skip_failed": True,
        "password": DEFAULT_PASSWORD,
        "theme_color": "green",
        "use_proxy": False,
        "random_proxy": True
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

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

class SMSGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = load_config()
        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme(self.settings["theme_color"])

        self.title("Eren97 - SMS GUİ")
        self.geometry("1000x700")
        self.fullscreen = self.settings["fullscreen_start"]
        self.attributes("-fullscreen", self.fullscreen)
        self.bind("<F11>", self.toggle_fullscreen)

        self.failed_services = self.load_failed_services()
        self.total_sms_sent = 0
        self.stop_event = threading.Event()
        self.proxies = self.load_proxies()
        self.blacklisted_proxies = self.load_proxy_blacklist()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tab_sms = self.tabview.add("SMS Gönder")
        self.tab_test = self.tabview.add("Servis Test")
        self.tab_stats = self.tabview.add("İstatistik")
        self.tab_settings = self.tabview.add("Ayarlar")

        self.build_sms_tab()
        self.build_test_tab()
        self.build_stats_tab()
        self.build_settings_tab()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def log(self, msg, tag="info"):
        self.console.insert("end", msg + "\n")
        self.console.see("end")

    def build_sms_tab(self):
        frame = self.tab_sms
        if self.settings["show_logo"]:
            ctk.CTkLabel(frame, text="🟩 E R E N", font=("Courier", 24, "bold"), text_color="lime").pack(pady=10)

        self.phone_entry = ctk.CTkEntry(frame, placeholder_text="Telefon Numarası", width=300)
        self.mail_entry = ctk.CTkEntry(frame, placeholder_text="Mail (opsiyonel)", width=300)
        self.kere_entry = ctk.CTkEntry(frame, placeholder_text="Kaç SMS", width=300)
        self.interval_entry = ctk.CTkEntry(frame, placeholder_text="Gönderim Aralığı", width=300)
        for widget in [self.phone_entry, self.mail_entry, self.kere_entry, self.interval_entry]:
            widget.pack(pady=4)

        btns = ctk.CTkFrame(frame)
        btns.pack(pady=8)
        ctk.CTkButton(btns, text="Normal Gönder", command=self.start_normal).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Turbo Gönder", command=self.start_turbo).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Durdur", command=self.stop_sending, fg_color="red").pack(side="left", padx=10)

        self.console = tk.Text(frame, bg="black", fg="lime", font=("Courier", 12))
        self.console.pack(fill="both", expand=True, padx=5, pady=10)

    def build_test_tab(self):
        frame = self.tab_test
        ctk.CTkLabel(frame, text="Servis Test Paneli", font=("Arial", 18, "bold")).pack(pady=10)
        self.test_phone_entry = ctk.CTkEntry(frame, placeholder_text="Test Telefon Numarası", width=250)
        self.test_phone_entry.pack(pady=5)

        for attr in servisler_sms:
            ctk.CTkButton(frame, text=attr, command=lambda a=attr: self.test_service(a)).pack(pady=2)

    def build_stats_tab(self):
        frame = self.tab_stats
        ctk.CTkLabel(frame, text="Gönderim İstatistikleri", font=("Arial", 18)).pack(pady=10)
        self.stat_label = ctk.CTkLabel(frame, text=f"Toplam Gönderilen SMS: {self.total_sms_sent}")
        self.stat_label.pack(pady=5)

        self.figure = Figure(figsize=(5, 2.5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.canvas.get_tk_widget().pack()

    def build_settings_tab(self):
        frame = self.tab_settings

        def update_theme(value):
            ctk.set_appearance_mode(value)
            self.settings["theme"] = value
            save_config(self.settings)

        def update_color(value):
            ctk.set_default_color_theme(value)
            self.settings["theme_color"] = value
            save_config(self.settings)

        ctk.CTkLabel(frame, text="Tema", font=("Arial", 14)).pack(pady=5)
        ctk.CTkOptionMenu(frame, values=["dark", "light", "system"], command=update_theme).pack()

        ctk.CTkLabel(frame, text="Renk Teması", font=("Arial", 14)).pack(pady=5)
        ctk.CTkOptionMenu(frame, values=["green", "blue", "dark-blue"], command=update_color).pack()

        def toggle_proxy():
            self.settings["use_proxy"] = not self.settings["use_proxy"]
            save_config(self.settings)

        def toggle_random_proxy():
            self.settings["random_proxy"] = not self.settings["random_proxy"]
            save_config(self.settings)

        ctk.CTkButton(frame, text="Proxy Kullan: Aç/Kapat", command=toggle_proxy).pack(pady=5)
        ctk.CTkButton(frame, text="Rastgele Proxy Kullan", command=toggle_random_proxy).pack(pady=5)

    def test_service(self, attr):
        tel = self.test_phone_entry.get()
        try:
            sms = SendSms(tel, None)
            getattr(sms, attr)()
            self.log(f"[✓] {attr} başarılı", "success")
        except:
            self.failed_services.add(attr)
            self.save_failed_services()
            self.log(f"[X] {attr} başarısız", "fail")

    def get_proxy(self):
        if not self.settings.get("use_proxy") or not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        if proxy in self.blacklisted_proxies:
            return self.get_proxy()
        return proxy

    def load_proxies(self):
        if not os.path.exists(PROXY_FILE): return []
        with open(PROXY_FILE) as f:
            return [line.strip() for line in f if line.strip()]

    def load_proxy_blacklist(self):
        if not os.path.exists(PROXY_BLACKLIST_FILE): return set()
        with open(PROXY_BLACKLIST_FILE) as f:
            return set(line.strip() for line in f if line.strip())

    def blacklist_proxy(self, proxy):
        self.blacklisted_proxies.add(proxy)
        with open(PROXY_BLACKLIST_FILE, "a") as f:
            f.write(proxy + "\n")

    def stop_sending(self):
        self.stop_event.set()
        self.log("Gönderim durduruldu.", "info")

    def start_normal(self):
        self.stop_event.clear()
        threading.Thread(target=self.normal_sms, daemon=True).start()

    def start_turbo(self):
        self.stop_event.clear()
        threading.Thread(target=self.turbo_sms, daemon=True).start()

    def normal_sms(self):
        tel = self.phone_entry.get().strip()
        mail = self.mail_entry.get().strip()
        kere = self.kere_entry.get().strip()
        interval = self.interval_entry.get().strip()
        sms = SendSms(tel, mail)

        try:
            kere = int(kere) if kere else None
            interval = int(interval)
        except:
            self.log("⚠️ Sayıları doğru girin!", "fail")
            return

        sent = 0
        while not self.stop_event.is_set():
            for attr in servisler_sms:
                if self.stop_event.is_set() or (kere and sent >= kere):
                    return
                proxy = self.get_proxy()
                try:
                    getattr(sms, attr)()
                    self.total_sms_sent += 1
                    sent += 1
                    self.stat_label.configure(text=f"Toplam Gönderilen SMS: {self.total_sms_sent}")
                    self.ax.clear()
                    self.ax.bar(["Gönderilen"], [self.total_sms_sent])
                    self.canvas.draw()
                    self.log(f"[+] {attr} OK", "success")
                    time.sleep(interval)
                except:
                    self.failed_services.add(attr)
                    self.save_failed_services()
                    if proxy: self.blacklist_proxy(proxy)
                    self.log(f"[-] {attr} FAIL", "fail")

    def turbo_sms(self):
        tel = self.phone_entry.get().strip()
        mail = self.mail_entry.get().strip()
        sms = SendSms(tel, mail)

        def turbo():
            while not self.stop_event.is_set():
                threads = []
                for attr in servisler_sms:
                    if self.settings["auto_skip_failed"] and attr in self.failed_services:
                        continue
                    t = threading.Thread(target=self.run_service, args=(sms, attr), daemon=True)
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
        threading.Thread(target=turbo, daemon=True).start()

    def run_service(self, sms, attr):
        proxy = self.get_proxy()
        try:
            before = sms.adet
            getattr(sms, attr)()
            if sms.adet > before:
                self.total_sms_sent += 1
                self.stat_label.configure(text=f"Toplam Gönderilen SMS: {self.total_sms_sent}")
                self.ax.clear()
                self.ax.bar(["Gönderilen"], [self.total_sms_sent])
                self.canvas.draw()
                self.log(f"[✓] {attr} Başarılı", "success")
            else:
                raise Exception("Gönderim başarısız")
        except:
            self.failed_services.add(attr)
            self.save_failed_services()
            if proxy: self.blacklist_proxy(proxy)
            self.log(f"[X] {attr} HATA", "fail")

    def load_failed_services(self):
        if os.path.exists(BAD_FILE):
            with open(BAD_FILE, "r") as f:
                return set(json.load(f))
        return set()

    def save_failed_services(self):
        with open(BAD_FILE, "w") as f:
            json.dump(list(self.failed_services), f)

if __name__ == "__main__":
    app = SMSGUI()
    app.mainloop()