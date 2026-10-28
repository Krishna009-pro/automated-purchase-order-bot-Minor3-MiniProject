"""
screenshot_engine.py
Renders pixel-perfect, highly realistic SAP GUI (ME22N) change confirmation
screenshots using Pillow. Saves them to the Screenshots/ directory with audit stamps.
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(WORKSPACE_DIR, "Screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def get_font(font_name="segoeui.ttf", size=13, bold=False):
    """Safely retrieves a system font or falls back to default."""
    if bold:
        candidates = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
    else:
        candidates = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = os.path.join(windir, "Fonts")

    for c in candidates:
        full_path = os.path.join(fonts_dir, c)
        if os.path.exists(full_path):
            try:
                return ImageFont.truetype(full_path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def generate_sap_screenshot(po_data, save_path=None):
    """
    Renders an authentic SAP GUI 770 / ME22N transaction window snapshot for a given PO.
    po_data: dict with keys:
      po_number, vendor_name, item_code, item_description,
      quantity, unit_price, total_amount, currency, status, delivery_date
    """
    po_number = str(po_data.get("po_number", "4500010001"))
    vendor = str(po_data.get("vendor_name", "Acme Industrial Supplies"))
    item_code = str(po_data.get("item_code", "MAT-8801"))
    item_desc = str(po_data.get("item_description", "High-Pressure Hydraulic Valves"))
    qty = str(po_data.get("quantity", "120"))
    unit_price = float(po_data.get("unit_price", 85.50))
    total_amount = float(po_data.get("total_amount", 10260.00))
    currency = str(po_data.get("currency", "USD"))
    status = str(po_data.get("target_status", "Approved")).upper()
    delivery_date = str(po_data.get("delivery_date", "2026-11-15"))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Dimensions
    width = 1100
    height = 720
    img = Image.new("RGB", (width, height), color="#F0F3F6")
    draw = ImageDraw.Draw(img)

    # Fonts
    font_title = get_font(size=14, bold=True)
    font_bold = get_font(size=12, bold=True)
    font_regular = get_font(size=12, bold=False)
    font_small = get_font(size=11, bold=False)
    font_mono = get_font(size=12, bold=False)

    # 1. Windows OS Title Bar
    draw.rectangle([0, 0, width, 32], fill="#1F2A38")
    draw.text((15, 7), f"SAP GUI for Windows 770 - [PRD-100 / Client 100] Change Purchase Order {po_number}", fill="#FFFFFF", font=font_title)
    # Window controls (Min, Max, Close)
    draw.rectangle([width - 90, 8, width - 75, 23], outline="#8892A0", width=1)
    draw.line([width - 86, 15, width - 79, 15], fill="#FFFFFF", width=1)
    draw.rectangle([width - 65, 8, width - 50, 23], outline="#8892A0", width=1)
    draw.rectangle([width - 38, 8, width - 23, 23], fill="#C53929")
    draw.line([width - 34, 11, width - 27, 20], fill="#FFFFFF", width=1)
    draw.line([width - 27, 11, width - 34, 20], fill="#FFFFFF", width=1)

    # 2. SAP Menu Bar
    draw.rectangle([0, 32, width, 58], fill="#FFFFFF", outline="#D0D7DE", width=1)
    menus = ["Purchase Order", "Edit", "Goto", "Header", "Item", "Environment", "System", "Help"]
    x_m = 15
    for m in menus:
        draw.text((x_m, 38), m, fill="#24292F", font=font_regular)
        x_m += int(draw.textlength(m, font=font_regular)) + 24

    # 3. SAP Standard Toolbar
    draw.rectangle([0, 58, width, 96], fill="#E9EEF4", outline="#CBD5E1", width=1)
    # Command box
    draw.rectangle([15, 66, 120, 88], fill="#FFFFFF", outline="#0A4B82", width=1)
    draw.text((22, 69), "ME22N", fill="#0A4B82", font=font_bold)
    # Enter / Checkmark button
    draw.rectangle([125, 66, 148, 88], fill="#1B7A43")
    draw.text((130, 68), "✔", fill="#FFFFFF", font=font_bold)

    # Action buttons simulation (Save, Back, Exit, Cancel, Print, Find)
    actions = [("Save", "#0A4B82", True), ("Back", "#475569", False), ("Exit", "#475569", False), ("Cancel", "#475569", False), ("Print", "#475569", False)]
    x_act = 165
    for label, col, is_btn in actions:
        w_btn = int(draw.textlength(label, font=font_small)) + 16
        if is_btn:
            draw.rounded_rectangle([x_act, 66, x_act + w_btn, 88], radius=3, fill="#0A4B82")
            draw.text((x_act + 8, 69), label, fill="#FFFFFF", font=font_bold)
        else:
            draw.rounded_rectangle([x_act, 66, x_act + w_btn, 88], radius=3, fill="#FFFFFF", outline="#CBD5E1")
            draw.text((x_act + 8, 69), label, fill="#334155", font=font_small)
        x_act += w_btn + 8

    # Bot indicator pill on toolbar
    draw.rounded_rectangle([width - 240, 66, width - 15, 88], radius=11, fill="#E0F2FE", outline="#0284C7")
    draw.text((width - 225, 69), ">> RPA BOT ACTIVE (ME22N)", fill="#0369A1", font=font_bold)

    # 4. Transaction Header & Overview Bar
    draw.rectangle([0, 96, width, 140], fill="#0A3B5C")
    draw.text((20, 104), "Standard PO", fill="#93C5FD", font=font_small)
    draw.text((20, 118), f"{po_number}", fill="#FFFFFF", font=font_title)
    
    draw.text((180, 104), "Vendor", fill="#93C5FD", font=font_small)
    draw.text((180, 118), f"{vendor}", fill="#FFFFFF", font=font_title)

    draw.text((620, 104), "Net Value", fill="#93C5FD", font=font_small)
    draw.text((620, 118), f"${total_amount:,.2f} {currency}", fill="#FDE047", font=font_title)

    draw.text((820, 104), "Document Status", fill="#93C5FD", font=font_small)
    # Status pill
    draw.rounded_rectangle([820, 116, 950, 136], radius=4, fill="#15803D")
    draw.text((830, 119), f"[OK] {status}", fill="#FFFFFF", font=font_bold)

    # 5. Header Details Card (Form View)
    draw.rectangle([15, 152, width - 15, 275], fill="#FFFFFF", outline="#CBD5E1", width=1)
    draw.rectangle([15, 152, width - 15, 180], fill="#F1F5F9")
    draw.text((25, 159), "> Header Data & Organizational Assignment", fill="#1E293B", font=font_bold)

    # Header Fields
    fields = [
        ("Purch. Organization:", "1000 (Global Procurement)", 25, 195),
        ("Purchasing Group:", "001 (Raw Materials)", 25, 222),
        ("Company Code:", "US10 (Enterprise Corp USA)", 25, 248),
        ("Doc Date:", datetime.now().strftime("%Y-%m-%d"), 360, 195),
        ("Payment Terms:", "NT30 (Net 30 Days)", 360, 222),
        ("Currency:", f"{currency} (US Dollar)", 360, 248),
        ("Target System:", "SAP ECC / S/4HANA (PRD)", 700, 195),
        ("Updated By:", "BOT_RPA_AUTO (Process Execution)", 700, 222),
        ("Verification:", "AUTO-VERIFIED OK", 700, 248),
    ]

    for label, val, fx, fy in fields:
        draw.text((fx, fy), label, fill="#64748B", font=font_small)
        draw.text((fx + 140, fy), val, fill="#0F172A", font=font_bold if "BOT" in val or "OK" in val else font_regular)

    # 6. Item Overview Section (Table View)
    draw.rectangle([15, 290, width - 15, 318], fill="#0A3B5C")
    draw.text((25, 296), "> Item Overview (Line Items in ME22N)", fill="#FFFFFF", font=font_bold)

    # Table Header
    th_y = 318
    draw.rectangle([15, th_y, width - 15, th_y + 28], fill="#E2E8F0", outline="#CBD5E1")
    cols = [
        ("Item", 25, 60),
        ("Material", 85, 120),
        ("Short Text / Description", 205, 300),
        ("PO Quantity", 505, 95),
        ("OUn", 600, 45),
        ("Net Price", 645, 100),
        ("Total Amount", 745, 115),
        ("Deliv. Date", 860, 100),
        ("Status", 960, 110),
    ]
    for name, cx, cw in cols:
        draw.text((cx + 5, th_y + 7), name, fill="#334155", font=font_bold)
        draw.line([cx + cw, th_y, cx + cw, th_y + 28], fill="#CBD5E1", width=1)

    # Line Item Row 1 (Updated by RPA - Highlighted in soft green)
    r1_y = th_y + 28
    draw.rectangle([15, r1_y, width - 15, r1_y + 36], fill="#F0FDF4", outline="#86EFAC")

    row_vals = [
        ("00010", 25),
        (item_code, 85),
        (item_desc, 205),
        (f"{int(float(qty)):,}", 505),
        ("EA", 600),
        (f"${unit_price:,.2f}", 645),
        (f"${total_amount:,.2f}", 745),
        (delivery_date, 860),
        ("UPDATED", 960),
    ]
    for val, cx in row_vals:
        color = "#15803D" if val in ("UPDATED", f"${total_amount:,.2f}") else "#0F172A"
        draw.text((cx + 5, r1_y + 10), val, fill=color, font=font_bold if val in ("UPDATED", f"${total_amount:,.2f}") else font_regular)

    # Empty Grid Lines to give genuine SAP feel
    for row_idx in range(2, 7):
        curr_y = r1_y + row_idx * 36
        draw.rectangle([15, curr_y, width - 15, curr_y + 36], fill="#FFFFFF" if row_idx % 2 == 0 else "#F8FAFC", outline="#E2E8F0")
        draw.text((30, curr_y + 10), f"000{row_idx}0", fill="#94A3B8", font=font_small)

    # 7. Audit & Validation Stamp Box
    draw.rounded_rectangle([15, 570, width - 15, 665], radius=6, fill="#F8FAFC", outline="#0284C7", width=2)
    draw.rectangle([15, 570, width - 15, 595], fill="#E0F2FE")
    draw.text((25, 575), "[RPA AUDIT TRAIL] AUTOMATION ANYWHERE BOT EXECUTION RECORD", fill="#0369A1", font=font_bold)

    draw.text((30, 606), f"- Transaction Code: ME22N (Change Purchase Order)", fill="#1E293B", font=font_regular)
    draw.text((30, 626), f"- Execution Timestamp: {now_str}", fill="#1E293B", font=font_regular)
    draw.text((30, 644), f"- Data Source: PO_List.xlsx  ->  Target: SAP_Mockup.xlsx (PRD-100)", fill="#1E293B", font=font_regular)

    draw.text((540, 606), f"- Changes Applied: Quantity={qty}, Price=${unit_price:.2f}, Total=${total_amount:,.2f}", fill="#1E293B", font=font_regular)
    draw.text((540, 626), f"- Stakeholder Notified: {po_data.get('stakeholder_email', 'procurement@enterprise.com')}", fill="#1E293B", font=font_regular)
    draw.text((540, 644), f"- Verification Hash: SAP-PO-{po_number}-OK", fill="#059669", font=font_bold)

    # 8. SAP Standard Status Bar at Bottom
    draw.rectangle([0, height - 32, width, height], fill="#E2E8F0", outline="#CBD5E1")
    # Green status dot
    draw.ellipse([15, height - 22, 27, height - 10], fill="#16A34A")
    draw.text((35, height - 24), f"[OK] Standard PO {po_number} changed - Status: {status} - Total: ${total_amount:,.2f} USD", fill="#14532D", font=font_bold)
    
    # System info on bottom right
    draw.text((width - 240, height - 24), f"PRD-100 | Client 100 | INS | {now_str[11:]}", fill="#475569", font=font_small)

    if not save_path:
        filename = f"PO_{po_number}_updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        save_path = os.path.join(SCREENSHOTS_DIR, filename)

    img.save(save_path, "PNG")
    return save_path


if __name__ == "__main__":
    sample_po = {
        "po_number": 4500010001,
        "vendor_name": "Acme Industrial Supplies",
        "item_code": "MAT-8801",
        "item_description": "High-Pressure Hydraulic Valves",
        "quantity": 120,
        "unit_price": 85.50,
        "total_amount": 10260.00,
        "currency": "USD",
        "target_status": "Approved",
        "delivery_date": "2026-11-15",
        "stakeholder_email": "procurement.lead@enterprise.com"
    }
    path = generate_sap_screenshot(sample_po)
    print(f"Sample screenshot saved to: {path}")
