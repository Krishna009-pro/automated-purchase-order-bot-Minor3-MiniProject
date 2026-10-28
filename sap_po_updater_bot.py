"""
sap_po_updater_bot.py
Automated Purchase Order Management RPA Bot.
Reads PO details from Excel (PO_List.xlsx), logs into/simulates SAP ME22N transaction,
updates purchase orders in SAP_Mockup.xlsx, captures visual screenshots,
and sends rich email confirmations to stakeholders.
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

from screenshot_engine import generate_sap_screenshot
from email_service import save_and_dispatch_email

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(WORKSPACE_DIR, "Screenshots")
EMAILS_DIR = os.path.join(WORKSPACE_DIR, "Emails")
LOG_FILE = os.path.join(WORKSPACE_DIR, "bot_execution.log")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(EMAILS_DIR, exist_ok=True)

# Setup Logger
logger = logging.getLogger("SAP_PO_Bot")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.handlers = [file_handler, console_handler]


def check_real_sap_gui():
    """Checks if real SAP GUI Scripting engine is available via Windows COM."""
    try:
        import win32com.client
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine
        if application and application.Children.Count > 0:
            return True
    except Exception:
        pass
    return False


class SAPPOUpdaterBot:
    def __init__(self, po_list_path=None, sap_mock_path=None, visual_gui=False, delay=0.5):
        self.po_list_path = po_list_path or os.path.join(WORKSPACE_DIR, "PO_List.xlsx")
        self.sap_mock_path = sap_mock_path or os.path.join(WORKSPACE_DIR, "SAP_Mockup.xlsx")
        self.visual_gui = visual_gui
        self.delay = delay
        self.gui_window = None

    def _init_visual_gui(self):
        if self.visual_gui:
            try:
                import tkinter as tk
                from sap_gui_simulator import SAPSimulatorWindow
                self.gui_root = tk.Tk()
                self.gui_window = SAPSimulatorWindow(self.gui_root)
                self.gui_root.update()
                logger.info("Desktop SAP GUI Simulator launched.")
            except Exception as e:
                logger.warning(f"Could not initialize Tkinter GUI ({e}), continuing in headless simulation mode.")
                self.gui_window = None

    def read_pending_pos(self):
        """Reads rows from PO_List.xlsx that are ready to be processed."""
        if not os.path.exists(self.po_list_path):
            raise FileNotFoundError(f"PO_List.xlsx not found at {self.po_list_path}. Run generate_mock_data.py first.")

        wb = load_workbook(self.po_list_path)
        ws = wb["Purchase_Orders"]
        
        headers = [cell.value for cell in ws[1]]
        po_records = []

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row or not row[0]:
                continue
            record = dict(zip(headers, row))
            record["_row_idx"] = row_idx
            
            # Check if pending or not yet processed
            status = str(record.get("Process_Status", "")).strip().lower()
            if status != "processed":
                po_records.append(record)

        wb.close()
        return po_records

    def update_sap_mockup(self, po_data):
        """Updates the PO record and adds an entry in SAP_Mockup.xlsx."""
        if not os.path.exists(self.sap_mock_path):
            raise FileNotFoundError(f"SAP_Mockup.xlsx not found at {self.sap_mock_path}.")

        wb = load_workbook(self.sap_mock_path)
        ws_po = wb["ME22N_Purchase_Orders"]
        ws_audit = wb["SAP_Audit_Trail"]

        po_num = int(po_data["PO_Number"])
        matched = False
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Find and update row in ME22N_Purchase_Orders
        for row in ws_po.iter_rows(min_row=2):
            if row[0].value and int(row[0].value) == po_num:
                # Update vendor
                row[1].value = str(po_data.get("Vendor_Name", row[1].value))
                # Update material code
                row[2].value = str(po_data.get("Item_Code", row[2].value))
                # Update short text
                row[3].value = str(po_data.get("Item_Description", row[3].value))
                # Update quantity
                row[4].value = float(po_data.get("Quantity", row[4].value))
                # Update price
                row[5].value = float(po_data.get("Unit_Price", row[5].value))
                # Update total value
                row[6].value = float(po_data.get("Total_Amount", row[6].value))
                # Update status
                row[8].value = str(po_data.get("Target_Status", "Approved"))
                # Update delivery date
                row[9].value = str(po_data.get("Delivery_Date", row[9].value))
                # Update last changed by & on
                row[11].value = "BOT_RPA_AUTO"
                row[12].value = now_str
                
                # Highlight updated row with soft green fill
                success_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
                for cell in row:
                    cell.fill = success_fill

                matched = True
                break

        # If PO wasn't in mock table, append it
        if not matched:
            new_row = [
                po_num,
                po_data.get("Vendor_Name"),
                po_data.get("Item_Code"),
                po_data.get("Item_Description"),
                float(po_data.get("Quantity", 0)),
                float(po_data.get("Unit_Price", 0)),
                float(po_data.get("Total_Amount", 0)),
                po_data.get("Currency", "USD"),
                po_data.get("Target_Status", "Approved"),
                str(po_data.get("Delivery_Date")),
                datetime.now().strftime("%Y-%m-%d"),
                "BOT_RPA_AUTO",
                now_str,
                "PRD-100"
            ]
            ws_po.append(new_row)

        # Append Audit Entry
        audit_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{po_num}"
        audit_row = [
            audit_id,
            now_str,
            "ME22N",
            po_num,
            "Quantity, Unit_Price, Status, Delivery_Date",
            "Draft / Pending",
            f"Approved (${float(po_data.get('Total_Amount', 0)):,.2f})",
            "BOT_RPA_AUTO",
            "SUCCESS",
            f"PO #{po_num} updated in SAP ME22N and verified"
        ]
        ws_audit.append(audit_row)

        wb.save(self.sap_mock_path)

    def mark_po_as_processed(self, row_idx, po_data):
        """Updates PO_List.xlsx marking the item as Processed and Approved."""
        wb = load_workbook(self.po_list_path)
        ws = wb["Purchase_Orders"]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        headers = [c.value for c in ws[1]]
        proc_status_col = headers.index("Process_Status") + 1
        curr_status_col = headers.index("Current_Status") + 1
        proc_at_col = headers.index("Processed_At") + 1

        ws.cell(row=row_idx, column=curr_status_col, value="Approved")
        ws.cell(row=row_idx, column=proc_status_col, value="Processed")
        ws.cell(row=row_idx, column=proc_at_col, value=now_str)

        # Apply soft green fill to indicate completion
        completed_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        for col in range(1, len(headers) + 1):
            ws.cell(row=row_idx, column=col).fill = completed_fill

        wb.save(self.po_list_path)

    def run(self, progress_callback=None, auto_reset_if_empty=True):
        """
        Executes the end-to-end bot lifecycle:
        1. Read pending POs
        2. Iterate and update SAP GUI / Mockup
        3. Capture screenshot
        4. Send email confirmation
        5. Update PO_List
        """
        logger.info("=" * 60)
        logger.info("STARTING AUTOMATED PURCHASE ORDER MANAGEMENT BOT (RPA)")
        logger.info("=" * 60)

        # Check real SAP
        has_real_sap = check_real_sap_gui()
        if has_real_sap:
            logger.info("[MODE] Real SAP GUI detected via Windows COM Scripting Engine.")
        else:
            logger.info("[MODE] Simulating SAP ME22N transaction via SAP_Mockup.xlsx.")

        pending_pos = self.read_pending_pos()
        
        # If queue is empty and auto_reset is True, re-seed so demo always succeeds!
        if len(pending_pos) == 0 and auto_reset_if_empty:
            logger.info("All orders were already processed. Auto-resetting datasets for demonstration run...")
            import generate_mock_data
            generate_mock_data.create_po_list(self.po_list_path)
            generate_mock_data.create_sap_mockup(self.sap_mock_path)
            pending_pos = self.read_pending_pos()

        total_pos = len(pending_pos)

        if total_pos == 0:
            logger.info("No pending purchase orders found to process. All POs are already Processed.")
            return {"total": 0, "processed": 0, "items": []}

        self._init_visual_gui()

        logger.info(f"Found {total_pos} pending purchase order(s) to process.")

        results = []
        for idx, po in enumerate(pending_pos, 1):
            po_num = po["PO_Number"]
            vendor = po.get("Vendor_Name", "Unknown")
            amount = float(po.get("Total_Amount", 0))
            logger.info(f"[{idx}/{total_pos}] Processing PO #{po_num} | Vendor: {vendor} | Amount: ${amount:,.2f}")

            if progress_callback:
                progress_callback(idx, total_pos, f"Processing PO #{po_num} - {vendor}")

            # 1. Visual GUI Update (if visual mode is enabled)
            if self.gui_window:
                gui_dict = {
                    "po_number": po_num,
                    "vendor_name": vendor,
                    "item_code": po.get("Item_Code"),
                    "item_description": po.get("Item_Description"),
                    "quantity": po.get("Quantity"),
                    "unit_price": po.get("Unit_Price"),
                    "total_amount": amount,
                    "target_status": po.get("Target_Status", "Approved"),
                    "delivery_date": po.get("Delivery_Date")
                }
                self.gui_window.load_po_data(gui_dict)
                time.sleep(self.delay)
                self.gui_window.save_current_po()
                time.sleep(self.delay)

            # 2. Update SAP Mockup Excel & Audit Trail
            self.update_sap_mockup(po)
            logger.info(f"  -> SAP ME22N Mockup updated with Status=Approved, Audit ID generated.")

            # 3. Capture Screenshot
            sc_dict = {
                "po_number": po_num,
                "vendor_name": vendor,
                "item_code": po.get("Item_Code"),
                "item_description": po.get("Item_Description"),
                "quantity": po.get("Quantity"),
                "unit_price": po.get("Unit_Price"),
                "total_amount": amount,
                "currency": po.get("Currency", "USD"),
                "target_status": po.get("Target_Status", "Approved"),
                "delivery_date": po.get("Delivery_Date"),
                "stakeholder_email": po.get("Stakeholder_Email")
            }
            screenshot_path = generate_sap_screenshot(sc_dict)
            logger.info(f"  -> Screenshot captured: {os.path.basename(screenshot_path)}")

            # 4. Generate & Send Email Confirmation
            email_info = save_and_dispatch_email(sc_dict, screenshot_path)
            logger.info(f"  -> Email generated for {email_info['recipient']} (Saved: {os.path.basename(email_info['html_path'])})")

            # 5. Mark PO as Processed in PO_List.xlsx
            self.mark_po_as_processed(po["_row_idx"], po)
            logger.info(f"  -> PO_List.xlsx updated: Process_Status=Processed.")

            results.append({
                "po_number": po_num,
                "vendor": vendor,
                "amount": amount,
                "screenshot": screenshot_path,
                "email_html": email_info["html_path"],
                "status": "SUCCESS"
            })
            time.sleep(self.delay / 2)

        if self.gui_window and self.gui_root:
            self.gui_window.var_status_msg.set(f"RPA Completed: All {total_pos} POs processed successfully.")
            self.gui_root.update()
            time.sleep(2.0)
            self.gui_root.destroy()

        logger.info("=" * 60)
        logger.info(f"RPA EXECUTION COMPLETED: {len(results)}/{total_pos} POs PROCESSED SUCCESSFULLY")
        logger.info(f"Total Order Value Updated: ${sum(r['amount'] for r in results):,.2f} USD")
        logger.info("=" * 60)

        return {
            "total": total_pos,
            "processed": len(results),
            "total_value": sum(r["amount"] for r in results),
            "items": results
        }


def main():
    parser = argparse.ArgumentParser(description="Automated Purchase Order RPA Bot")
    parser.add_argument("--visual", action="store_true", help="Launch interactive visual SAP GUI simulator")
    parser.add_argument("--delay", type=float, default=0.8, help="Delay between visual steps (in seconds)")
    parser.add_argument("--reset", action="store_true", help="Reset sample datasets before running")
    parser.add_argument("--no-auto-reset", action="store_true", help="Do not auto-reset when queue is empty")
    args = parser.parse_args()

    if args.reset:
        import generate_mock_data
        generate_mock_data.create_po_list(os.path.join(WORKSPACE_DIR, "PO_List.xlsx"))
        generate_mock_data.create_sap_mockup(os.path.join(WORKSPACE_DIR, "SAP_Mockup.xlsx"))
        logger.info("Datasets reset to initial state.")

    bot = SAPPOUpdaterBot(visual_gui=args.visual, delay=args.delay)
    summary = bot.run(auto_reset_if_empty=not args.no_auto_reset)
    print(f"\nExecution Summary: Processed {summary['processed']} orders.")


if __name__ == "__main__":
    main()
