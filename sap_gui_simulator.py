"""
sap_gui_simulator.py
A Tkinter-based realistic desktop simulation of the SAP GUI 770 / ME22N transaction window.
Allows the RPA bot to visually interact, type into fields, trigger save actions,
and capture live window screenshots.
"""

import os
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageGrab

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(WORKSPACE_DIR, "Screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


class SAPSimulatorWindow:
    def __init__(self, root=None):
        self.is_standalone = root is None
        self.root = root if root else tk.Tk()
        self.root.title("SAP GUI for Windows 770 - [PRD-100] Change Purchase Order (ME22N)")
        self.root.geometry("1020x680")
        self.root.configure(bg="#F0F3F6")
        self.root.resizable(True, True)

        # State Variables
        self.var_tcode = tk.StringVar(value="ME22N")
        self.var_po_num = tk.StringVar(value="4500010001")
        self.var_vendor = tk.StringVar(value="Acme Industrial Supplies")
        self.var_doc_type = tk.StringVar(value="NB - Standard PO")
        self.var_net_val = tk.StringVar(value="$10,260.00 USD")
        self.var_status = tk.StringVar(value="Draft")
        self.var_item_code = tk.StringVar(value="MAT-8801")
        self.var_desc = tk.StringVar(value="High-Pressure Hydraulic Valves")
        self.var_qty = tk.StringVar(value="120")
        self.var_price = tk.StringVar(value="85.50")
        self.var_amount = tk.StringVar(value="10260.00")
        self.var_delivery = tk.StringVar(value="2026-11-15")
        self.var_system = tk.StringVar(value="PRD-100")
        self.var_status_msg = tk.StringVar(value="SAP Ready. Enter PO number or run RPA Bot.")

        self._build_ui()

    def _build_ui(self):
        # 1. SAP Menu Bar Simulation
        menu_frame = tk.Frame(self.root, bg="#FFFFFF", height=26, relief="flat", bd=1)
        menu_frame.pack(fill="x")
        menus = ["Purchase Order", "Edit", "Goto", "Header", "Item", "Environment", "System", "Help"]
        for m in menus:
            lbl = tk.Label(menu_frame, text=m, bg="#FFFFFF", fg="#24292F", font=("Segoe UI", 9), padx=8, pady=3)
            lbl.pack(side="left")

        # 2. SAP Standard Toolbar
        toolbar = tk.Frame(self.root, bg="#E9EEF4", height=38, relief="groove", bd=1)
        toolbar.pack(fill="x", padx=0, pady=0)

        # Command input
        tk.Label(toolbar, text="Cmd:", bg="#E9EEF4", fg="#475569", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(10, 2))
        cmd_ent = tk.Entry(toolbar, textvariable=self.var_tcode, width=12, font=("Segoe UI", 9, "bold"), fg="#0A4B82", relief="solid", bd=1)
        cmd_ent.pack(side="left", padx=2, pady=6)

        btn_enter = tk.Button(toolbar, text="OK", bg="#16A34A", fg="#FFFFFF", font=("Segoe UI", 8, "bold"), padx=6, relief="flat", command=self.on_enter)
        btn_enter.pack(side="left", padx=4)

        # Standard action buttons
        self.btn_save = tk.Button(toolbar, text="Save (Ctrl+S)", bg="#0A3B5C", fg="#FFFFFF", font=("Segoe UI", 8, "bold"), padx=8, relief="flat", command=self.save_current_po)
        self.btn_save.pack(side="left", padx=6)

        tk.Button(toolbar, text="Back (F3)", bg="#E2E8F0", fg="#334155", font=("Segoe UI", 8), padx=6, relief="flat").pack(side="left", padx=2)
        tk.Button(toolbar, text="Exit (Shift+F3)", bg="#E2E8F0", fg="#334155", font=("Segoe UI", 8), padx=6, relief="flat").pack(side="left", padx=2)
        tk.Button(toolbar, text="Cancel (F12)", bg="#E2E8F0", fg="#334155", font=("Segoe UI", 8), padx=6, relief="flat").pack(side="left", padx=2)

        # RPA Status Pill on Toolbar
        self.lbl_bot_pill = tk.Label(toolbar, text=">> RPA READY <<", bg="#E0F2FE", fg="#0284C7", font=("Segoe UI", 9, "bold"), padx=10, relief="solid", bd=1)
        self.lbl_bot_pill.pack(side="right", padx=12, pady=4)

        # 3. Transaction Header Bar (SAP Blue Banner)
        banner = tk.Frame(self.root, bg="#0A3B5C", height=50)
        banner.pack(fill="x")

        # PO & Vendor info
        tk.Label(banner, text="Purchase Order:", bg="#0A3B5C", fg="#93C5FD", font=("Segoe UI", 9)).place(x=15, y=6)
        self.lbl_po_display = tk.Label(banner, textvariable=self.var_po_num, bg="#0A3B5C", fg="#FFFFFF", font=("Segoe UI", 12, "bold"))
        self.lbl_po_display.place(x=15, y=24)

        tk.Label(banner, text="Vendor:", bg="#0A3B5C", fg="#93C5FD", font=("Segoe UI", 9)).place(x=150, y=6)
        self.lbl_vendor_display = tk.Label(banner, textvariable=self.var_vendor, bg="#0A3B5C", fg="#FFFFFF", font=("Segoe UI", 12, "bold"))
        self.lbl_vendor_display.place(x=150, y=24)

        tk.Label(banner, text="Net Value:", bg="#0A3B5C", fg="#93C5FD", font=("Segoe UI", 9)).place(x=520, y=6)
        self.lbl_net_display = tk.Label(banner, textvariable=self.var_net_val, bg="#0A3B5C", fg="#FDE047", font=("Segoe UI", 12, "bold"))
        self.lbl_net_display.place(x=520, y=24)

        tk.Label(banner, text="Status:", bg="#0A3B5C", fg="#93C5FD", font=("Segoe UI", 9)).place(x=720, y=6)
        self.lbl_status_display = tk.Label(banner, textvariable=self.var_status, bg="#15803D", fg="#FFFFFF", font=("Segoe UI", 10, "bold"), padx=8, pady=1)
        self.lbl_status_display.place(x=720, y=24)

        # 4. Header Details Group
        hdr_frame = tk.LabelFrame(self.root, text=" Header Details & Organization (ME22N) ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#1E293B", relief="solid", bd=1)
        hdr_frame.pack(fill="x", padx=12, pady=10)

        # Grid form fields
        tk.Label(hdr_frame, text="PO Number:", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        self.ent_po = tk.Entry(hdr_frame, textvariable=self.var_po_num, width=16, font=("Segoe UI", 9, "bold"), relief="solid", bd=1)
        self.ent_po.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        tk.Label(hdr_frame, text="Vendor Name:", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=10, pady=4)
        self.ent_vendor = tk.Entry(hdr_frame, textvariable=self.var_vendor, width=32, font=("Segoe UI", 9), relief="solid", bd=1)
        self.ent_vendor.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        tk.Label(hdr_frame, text="Doc Date:", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9)).grid(row=0, column=4, sticky="w", padx=10, pady=4)
        tk.Label(hdr_frame, text=datetime.now().strftime("%Y-%m-%d"), bg="#FFFFFF", fg="#0F172A", font=("Segoe UI", 9, "bold")).grid(row=0, column=5, sticky="w", padx=5, pady=4)

        tk.Label(hdr_frame, text="Purch. Org:", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        tk.Label(hdr_frame, text="1000 - Global Procurement", bg="#FFFFFF", fg="#0F172A", font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w", padx=5, pady=4)

        tk.Label(hdr_frame, text="Company Code:", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", padx=10, pady=4)
        tk.Label(hdr_frame, text="US10 - Enterprise USA", bg="#FFFFFF", fg="#0F172A", font=("Segoe UI", 9)).grid(row=1, column=3, sticky="w", padx=5, pady=4)

        tk.Label(hdr_frame, text="Target Status:", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9)).grid(row=1, column=4, sticky="w", padx=10, pady=4)
        self.ent_status = tk.Entry(hdr_frame, textvariable=self.var_status, width=14, font=("Segoe UI", 9, "bold"), fg="#15803D", relief="solid", bd=1)
        self.ent_status.grid(row=1, column=5, sticky="w", padx=5, pady=4)

        # 5. Line Items Group
        item_frame = tk.LabelFrame(self.root, text=" Item Overview & Line Items (ME22N) ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#1E293B", relief="solid", bd=1)
        item_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Table header
        cols_frame = tk.Frame(item_frame, bg="#0A3B5C", height=26)
        cols_frame.pack(fill="x")
        columns = [("Item", 45), ("Material Code", 110), ("Short Description", 280), ("Quantity", 80), ("Unit", 45), ("Net Price", 90), ("Total Amount", 110), ("Delivery Date", 100)]
        for col_name, width in columns:
            tk.Label(cols_frame, text=col_name, bg="#0A3B5C", fg="#FFFFFF", font=("Segoe UI", 8, "bold"), width=width // 8, anchor="w", padx=4).pack(side="left")

        # Row 1 Editable entry widgets
        self.r1_frame = tk.Frame(item_frame, bg="#F0FDF4", height=32, relief="solid", bd=1)
        self.r1_frame.pack(fill="x", padx=2, pady=4)

        tk.Label(self.r1_frame, text="00010", bg="#F0FDF4", fg="#0F172A", font=("Segoe UI", 8, "bold"), width=6).pack(side="left")
        self.ent_item = tk.Entry(self.r1_frame, textvariable=self.var_item_code, width=14, font=("Segoe UI", 9), relief="solid", bd=1)
        self.ent_item.pack(side="left", padx=2)

        self.ent_desc = tk.Entry(self.r1_frame, textvariable=self.var_desc, width=35, font=("Segoe UI", 9), relief="solid", bd=1)
        self.ent_desc.pack(side="left", padx=2)

        self.ent_qty = tk.Entry(self.r1_frame, textvariable=self.var_qty, width=10, font=("Segoe UI", 9, "bold"), relief="solid", bd=1)
        self.ent_qty.pack(side="left", padx=2)

        tk.Label(self.r1_frame, text="EA", bg="#F0FDF4", fg="#0F172A", font=("Segoe UI", 9), width=5).pack(side="left")

        self.ent_price = tk.Entry(self.r1_frame, textvariable=self.var_price, width=12, font=("Segoe UI", 9), relief="solid", bd=1)
        self.ent_price.pack(side="left", padx=2)

        self.ent_tot = tk.Entry(self.r1_frame, textvariable=self.var_amount, width=14, font=("Segoe UI", 9, "bold"), fg="#15803D", relief="solid", bd=1)
        self.ent_tot.pack(side="left", padx=2)

        self.ent_deliv = tk.Entry(self.r1_frame, textvariable=self.var_delivery, width=14, font=("Segoe UI", 9), relief="solid", bd=1)
        self.ent_deliv.pack(side="left", padx=2)

        # Empty Mock Lines
        for idx in range(2, 6):
            mock_line = tk.Frame(item_frame, bg="#FFFFFF" if idx % 2 == 0 else "#F8FAFC", height=24)
            mock_line.pack(fill="x", padx=2, pady=1)
            tk.Label(mock_line, text=f"000{idx}0", bg=mock_line["bg"], fg="#94A3B8", font=("Segoe UI", 8), width=6).pack(side="left")

        # 6. Bottom Status Bar (SAP Status Area)
        self.status_bar = tk.Frame(self.root, bg="#E2E8F0", height=28, relief="sunken", bd=1)
        self.status_bar.pack(fill="x", side="bottom")

        self.lbl_status_icon = tk.Label(self.status_bar, text="[OK]", bg="#E2E8F0", fg="#16A34A", font=("Segoe UI", 9, "bold"))
        self.lbl_status_icon.pack(side="left", padx=(8, 2))

        self.lbl_status_text = tk.Label(self.status_bar, textvariable=self.var_status_msg, bg="#E2E8F0", fg="#0F172A", font=("Segoe UI", 9))
        self.lbl_status_text.pack(side="left", padx=4)

        tk.Label(self.status_bar, text="PRD-100 | Client 100 | INS", bg="#E2E8F0", fg="#64748B", font=("Segoe UI", 8)).pack(side="right", padx=10)

    def on_enter(self):
        self.var_status_msg.set(f"Loaded transaction {self.var_tcode.get()}.")

    def load_po_data(self, po_dict):
        """Populates the simulator with a specific PO dictionary."""
        self.var_po_num.set(str(po_dict.get("po_number", "")))
        self.var_vendor.set(str(po_dict.get("vendor_name", "")))
        self.var_item_code.set(str(po_dict.get("item_code", "")))
        self.var_desc.set(str(po_dict.get("item_description", "")))
        self.var_qty.set(str(po_dict.get("quantity", "")))
        self.var_price.set(f"{float(po_dict.get('unit_price', 0)):.2f}")
        self.var_amount.set(f"{float(po_dict.get('total_amount', 0)):.2f}")
        self.var_delivery.set(str(po_dict.get("delivery_date", "")))
        target_status = str(po_dict.get("target_status", "Approved"))
        self.var_status.set(target_status)
        self.var_net_val.set(f"${float(po_dict.get('total_amount', 0)):,.2f} USD")
        self.lbl_bot_pill.config(text=f">> PROCESSING PO #{self.var_po_num.get()} <<", bg="#FEF08A", fg="#854D0E")
        self.var_status_msg.set(f"Updating PO {self.var_po_num.get()} (Vendor: {self.var_vendor.get()})...")
        self.root.update()

    def save_current_po(self):
        """Simulates clicking Save button in SAP."""
        po_num = self.var_po_num.get()
        self.var_status.set("Approved")
        self.lbl_status_display.config(bg="#15803D")
        self.lbl_bot_pill.config(text=">> SAVED BY RPA BOT <<", bg="#DCFCE7", fg="#166534")
        self.var_status_msg.set(f"[OK] Standard PO {po_num} changed successfully (Status: Approved).")
        self.root.update()

    def capture_screenshot(self, save_path=None):
        """Captures window image or renders high-fidelity image if minimized."""
        from screenshot_engine import generate_sap_screenshot
        po_data = {
            "po_number": self.var_po_num.get(),
            "vendor_name": self.var_vendor.get(),
            "item_code": self.var_item_code.get(),
            "item_description": self.var_desc.get(),
            "quantity": self.var_qty.get(),
            "unit_price": float(self.var_price.get() or 0),
            "total_amount": float(self.var_amount.get() or 0),
            "currency": "USD",
            "target_status": self.var_status.get(),
            "delivery_date": self.var_delivery.get()
        }
        return generate_sap_screenshot(po_data, save_path=save_path)


if __name__ == "__main__":
    app = SAPSimulatorWindow()
    app.root.mainloop()
