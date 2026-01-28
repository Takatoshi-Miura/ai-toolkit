#!/usr/bin/env python3
"""
Auto Clicker Tool for macOS
指定間隔で自動クリックを行うシンプルなツール

使用方法:
    python3 auto_clicker.py

初回実行時にmacOSの「アクセシビリティ」権限が必要です。
システム設定 > プライバシーとセキュリティ > アクセシビリティ
でターミナルを許可してください。
"""

import tkinter as tk
import threading
import time

try:
    from pynput.mouse import Button, Controller
except ImportError:
    print("pynputがインストールされていません。")
    print("以下のコマンドでインストールしてください:")
    print("  python3 -m pip install --user pynput")
    exit(1)


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.mouse = Controller()
        self.is_clicking = False
        self.click_thread = None
        self.click_count = 0

        self.setup_ui()

    def setup_ui(self):
        # タイトル
        tk.Label(
            self.root,
            text="🖱️ Auto Clicker",
            font=("Helvetica", 20, "bold"),
            bg="#f0f0f0"
        ).pack(pady=(20, 20))

        # 間隔設定
        interval_frame = tk.Frame(self.root, bg="#f0f0f0")
        interval_frame.pack(pady=(0, 10))

        tk.Label(
            interval_frame,
            text="クリック間隔:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)

        self.interval_var = tk.StringVar(value="1.0")
        tk.Entry(
            interval_frame,
            textvariable=self.interval_var,
            width=6,
            font=("Helvetica", 12)
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            interval_frame,
            text="秒",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)

        # クリック回数
        self.count_var = tk.StringVar(value="クリック回数: 0")
        tk.Label(
            self.root,
            textvariable=self.count_var,
            font=("Helvetica", 11),
            bg="#f0f0f0"
        ).pack(pady=(5, 5))

        # 状態表示
        self.status_var = tk.StringVar(value="⏸️ 停止中")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Helvetica", 14),
            bg="#f0f0f0"
        ).pack(pady=(5, 15))

        # ON/OFFボタン
        self.toggle_button = tk.Button(
            self.root,
            text="▶️ 開始",
            command=self.toggle_clicking,
            font=("Helvetica", 14, "bold"),
            width=12,
            height=2,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white"
        )
        self.toggle_button.pack(pady=(0, 15))

        # 注意書き
        tk.Label(
            self.root,
            text="💡 ウィンドウを閉じると自動停止",
            font=("Helvetica", 9),
            fg="gray",
            bg="#f0f0f0"
        ).pack(side=tk.BOTTOM, pady=(0, 10))

    def toggle_clicking(self):
        print(f"[DEBUG] toggle called, is_clicking={self.is_clicking}", flush=True)
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError()
        except ValueError:
            self.status_var.set("❌ 無効な間隔")
            return

        self.is_clicking = True
        self.click_count = 0
        self.status_var.set("🔴 クリック中...")
        self.toggle_button.config(
            text="⏹️ 停止",
            bg="#f44336",
            activebackground="#da190b"
        )

        self.click_thread = threading.Thread(
            target=self.click_loop,
            args=(interval,),
            daemon=True
        )
        self.click_thread.start()

    def stop_clicking(self):
        self.is_clicking = False
        self.status_var.set("⏸️ 停止中")
        self.toggle_button.config(
            text="▶️ 開始",
            bg="#4CAF50",
            activebackground="#45a049"
        )

    def click_loop(self, interval):
        print(f"[DEBUG] click_loop started", flush=True)
        while self.is_clicking:
            try:
                self.mouse.click(Button.left)
                self.click_count += 1
                print(f"[DEBUG] click #{self.click_count}", flush=True)
                self.root.after(0, self.update_count)
                time.sleep(interval)
            except Exception as e:
                print(f"[DEBUG] error: {e}", flush=True)
                self.root.after(0, self.stop_clicking)
                break
        print(f"[DEBUG] click_loop ended", flush=True)

    def update_count(self):
        self.count_var.set(f"クリック回数: {self.click_count}")


def main():
    root = tk.Tk()
    app = AutoClickerApp(root)

    def on_closing():
        app.is_clicking = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
