"""
app.py
Interactive Web Dashboard for Automated Purchase Order Management Bot (RPA).
Provides real-time RPA execution monitoring, live Excel data inspection,
screenshots gallery, email notification previews, and demo dataset controls.
"""

import os
import glob
import pandas as pd
import streamlit as st
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Automated Purchase Order RPA Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
PO_LIST_PATH = os.path.join(WORKSPACE_DIR, "PO_List.xlsx")
SAP_MOCK_PATH = os.path.join(WORKSPACE_DIR, "SAP_Mockup.xlsx")
SCREENSHOTS_DIR = os.path.join(WORKSPACE_DIR, "Screenshots")
EMAILS_DIR = os.path.join(WORKSPACE_DIR, "Emails")
LOG_PATH = os.path.join(WORKSPACE_DIR, "bot_execution.log")

# Custom CSS for executive look
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0A3B5C;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 25px;
    }
    .metric-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 16px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-badge-ok {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .status-badge-pending {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    po_df = pd.DataFrame()
    sap_df = pd.DataFrame()
    audit_df = pd.DataFrame()
    
    if os.path.exists(PO_LIST_PATH):
        try:
            po_df = pd.read_excel(PO_LIST_PATH, sheet_name="Purchase_Orders")
        except Exception:
            pass

    if os.path.exists(SAP_MOCK_PATH):
        try:
            sap_df = pd.read_excel(SAP_MOCK_PATH, sheet_name="ME22N_Purchase_Orders")
            audit_df = pd.read_excel(SAP_MOCK_PATH, sheet_name="SAP_Audit_Trail")
        except Exception:
            pass

    return po_df, sap_df, audit_df


# Header Section
st.markdown('<div class="main-title">🛠️ Automated Purchase Order Management Bot (RPA)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Enterprise SAP ECC / S/4HANA Process Automation (Transaction ME22N) | Automation Anywhere & Python</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&auto=format&fit=crop&q=60", width="stretch")
st.sidebar.header("🤖 RPA Control Panel")

run_mode = st.sidebar.radio(
    "Execution Mode",
    ["Headless Background", "Desktop Visual GUI Simulation", "SAP Windows Scripting (COM)"],
    index=0,
    help="Select how the RPA bot executes the SAP transaction."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")

col_sb1, col_sb2 = st.sidebar.columns(2)
with col_sb1:
    if st.button("🔄 Reset Data", help="Re-initializes PO_List and SAP_Mockup to initial pending state"):
        import generate_mock_data
        generate_mock_data.create_po_list(PO_LIST_PATH)
        generate_mock_data.create_sap_mockup(SAP_MOCK_PATH)
        st.sidebar.success("Datasets reset to default pending status!")
        st.rerun()

with col_sb2:
    if st.button("🧹 Clear Logs", help="Clears the execution log file"):
        if os.path.exists(LOG_PATH):
            open(LOG_PATH, "w").close()
            st.sidebar.success("Logs cleared.")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
**Tech Stack:**
- **RPA Tool**: Automation Anywhere (A360) / Python
- **ERP Target**: SAP GUI 770 (ME22N)
- **Data Stores**: Excel (openpyxl / pandas)
- **Reporting**: Automated MIME Email + PNG Evidence
""")

# Load initial data
po_df, sap_df, audit_df = load_data()

# Calculate Metrics
total_pos = len(po_df) if not po_df.empty else 0
processed_count = len(po_df[po_df["Process_Status"] == "Processed"]) if not po_df.empty and "Process_Status" in po_df.columns else 0
pending_count = total_pos - processed_count
total_value = po_df["Total_Amount"].sum() if not po_df.empty and "Total_Amount" in po_df.columns else 0.0

# KPI Metric Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Total Purchase Orders", value=total_pos)
with m2:
    st.metric(label="Processed Orders", value=f"{processed_count} / {total_pos}", delta=f"{processed_count} done" if processed_count > 0 else "0")
with m3:
    st.metric(label="Pending Queue", value=pending_count, delta=f"-{processed_count}" if processed_count > 0 else None)
with m4:
    st.metric(label="Total Order Value", value=f"${total_value:,.2f} USD")

st.markdown("---")

# Main Content Tabs
tabs = st.tabs([
    "🚀 Bot Execution Center",
    "📊 Excel Data Stores (PO List & SAP)",
    "📸 SAP Screenshots Evidence",
    "✉️ Stakeholder Notifications",
    "📜 Live Execution Logs",
    "📋 Automation Anywhere (A360) Guide"
])

# TAB 1: Bot Execution Center
with tabs[0]:
    st.subheader("⚡ Automated Bot Runner")
    st.write("Click below to trigger the RPA bot. The bot reads `PO_List.xlsx`, connects to/simulates SAP ME22N, applies price/quantity/status changes, saves audit logs, captures visual proof, and generates stakeholder email alerts.")

    if pending_count == 0:
        st.info("💡 **All 6 Purchase Orders are already Processed!** If you want to demonstrate or re-run the bot, click the button below to reset the queue.")
        if st.button("🔄 Reset Queue (Ready 6 Pending Orders)", type="secondary"):
            import generate_mock_data
            generate_mock_data.create_po_list(PO_LIST_PATH)
            generate_mock_data.create_sap_mockup(SAP_MOCK_PATH)
            st.success("Queue reset! 6 purchase orders are now Pending.")
            st.rerun()

    btn_col1, btn_col2 = st.columns([1, 3])
    with btn_col1:
        start_btn = st.button("▶ Start RPA Bot", type="primary", width="stretch")

    if start_btn:
        import sys
        import subprocess

        if run_mode == "Desktop Visual GUI Simulation":
            st.info("🖥️ Launching Desktop SAP GUI Simulator window... Watch your taskbar/screen!")
            subprocess.Popen([sys.executable, "sap_po_updater_bot.py", "--visual", "--delay", "0.8"])
            st.success("Visual Bot is now running on your desktop screen! Once finished, refresh this page to see the latest outputs.")
        else:
            from sap_po_updater_bot import SAPPOUpdaterBot
            bot = SAPPOUpdaterBot(visual_gui=False, delay=0.2)
            
            progress_bar = st.progress(0)
            status_text = st.empty()

            def on_progress(current, total, msg):
                pct = int((current / total) * 100)
                progress_bar.progress(pct)
                status_text.info(f"**Step {current}/{total}**: {msg}")

            with st.spinner("RPA Bot is running ME22N transaction updates..."):
                summary = bot.run(progress_callback=on_progress, auto_reset_if_empty=True)

            progress_bar.progress(100)
            status_text.success(f"🎉 **RPA Execution Complete!** Successfully processed {summary['processed']} orders totaling **${summary.get('total_value', 0):,.2f} USD**.")
            st.session_state["last_run_summary"] = summary
            st.balloons()

    # Display Last Run Results if available
    if "last_run_summary" in st.session_state:
        res = st.session_state["last_run_summary"]
        st.markdown("---")
        st.markdown(f"### ✅ Execution Results: {res['processed']} Orders Updated")
        
        if res.get("items"):
            res_df = pd.DataFrame(res["items"])
            display_res = res_df[["po_number", "vendor", "amount", "status"]]
            display_res.columns = ["PO Number", "Vendor Name", "Order Value (USD)", "Execution Status"]
            display_res["Order Value (USD)"] = display_res["Order Value (USD)"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_res, width="stretch")

    st.markdown("### 📋 Current Processing Queue")
    # Reload latest data
    po_df, sap_df, audit_df = load_data()
    if not po_df.empty:
        display_cols = ["PO_Number", "Vendor_Name", "Item_Code", "Item_Description", "Quantity", "Total_Amount", "Current_Status", "Process_Status", "Processed_At"]
        avail_cols = [c for c in display_cols if c in po_df.columns]
        st.dataframe(po_df[avail_cols], width="stretch")
    else:
        st.warning("No data found in PO_List.xlsx. Click 'Reset Data' in the sidebar to generate initial records.")

# TAB 2: Excel Data Stores
with tabs[1]:
    st.subheader("📁 Live Excel File Explorer")
    excel_choice = st.radio("Select Workbook & Sheet", ["PO_List.xlsx (Queue)", "SAP_Mockup.xlsx (ME22N Orders)", "SAP_Mockup.xlsx (Audit Trail)"], horizontal=True)

    if excel_choice == "PO_List.xlsx (Queue)":
        st.write("Source spreadsheet containing orders queued for RPA processing.")
        if not po_df.empty:
            st.dataframe(po_df, width="stretch")
        else:
            st.info("No data available.")

    elif excel_choice == "SAP_Mockup.xlsx (ME22N Orders)":
        st.write("Target SAP ERP database simulating table `EKKO`/`EKPO` and ME22N transaction records.")
        if not sap_df.empty:
            st.dataframe(sap_df, width="stretch")
        else:
            st.info("No data available.")

    else:
        st.write("Enterprise SAP Audit Trail recording every change executed by `BOT_RPA_AUTO`.")
        if not audit_df.empty:
            st.dataframe(audit_df, width="stretch")
        else:
            st.info("No audit logs yet. Run the bot to generate audit entries.")

# TAB 3: Screenshots Evidence
with tabs[2]:
    st.subheader("📸 SAP Transaction Screenshots")
    st.write("Visual evidence automatically captured by the RPA bot after updating each purchase order in ME22N.")

    images = sorted(glob.glob(os.path.join(SCREENSHOTS_DIR, "*.png")), reverse=True)
    if images:
        selected_img = st.selectbox("Select Captured Screenshot", images, format_func=lambda x: os.path.basename(x))
        if selected_img:
            st.image(selected_img, caption=f"Proof of Update: {os.path.basename(selected_img)}", width="stretch")
            with open(selected_img, "rb") as f:
                st.download_button("⬇️ Download Screenshot", data=f.read(), file_name=os.path.basename(selected_img), mime="image/png")
    else:
        st.info("No screenshots captured yet. Run the bot to capture SAP update snapshots.")

# TAB 4: Stakeholder Notifications
with tabs[3]:
    st.subheader("✉️ Automated Stakeholder / Faculty Notifications")
    st.write("Rich HTML & MIME emails generated with embedded visual verification screenshots.")

    html_emails = sorted(glob.glob(os.path.join(EMAILS_DIR, "*.html")), reverse=True)
    if html_emails:
        selected_email = st.selectbox("Select Email Notice", html_emails, format_func=lambda x: os.path.basename(x))
        if selected_email:
            with open(selected_email, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=650, scrolling=True)
            
            eml_partner = selected_email.replace(".html", ".eml")
            if os.path.exists(eml_partner):
                with open(eml_partner, "rb") as ef:
                    st.download_button("⬇️ Download .EML (Outlook / Mail)", data=ef.read(), file_name=os.path.basename(eml_partner), mime="message/rfc822")
    else:
        st.info("No emails generated yet. Run the bot to dispatch stakeholder notices.")

# TAB 5: Live Execution Logs
with tabs[4]:
    st.subheader("📜 Bot Execution Logs (`bot_execution.log`)")
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
            log_lines = f.readlines()
        st.text_area("Live Log Output", value="".join(log_lines[-100:]), height=400)
    else:
        st.info("Log file not created yet.")

# TAB 6: Automation Anywhere (A360) Guide
with tabs[5]:
    st.subheader("📋 Automation Anywhere (A360) Bot Guide")
    st.markdown("""
### 🏗️ How this translates to Automation Anywhere Enterprise / Community Edition:

| Step # | AA Package / Action | Configuration / Parameters | Equivalent in Python Code |
| :--- | :--- | :--- | :--- |
| **1** | `Application: Open Program/File` | Program Path: `C:\\Program Files\\SAP\\FrontEnd\\SAPgui\\saplogon.exe` (or `SAP_Mockup.xlsx`) | `SAPPOUpdaterBot._init_visual_gui()` |
| **2** | `SAP: Connect / Login` | Connection Name: `PRD [100]`, User: `BOT_RPA_AUTO` | `check_real_sap_gui()` / Windows COM |
| **3** | `Excel Advanced: Open` | File: `PO_List.xlsx`, Sheet: `Purchase_Orders` | `read_pending_pos()` (`openpyxl`) |
| **4** | `Loop: Each row in worksheet` | Record Variable: `$rPOData$` | `for idx, po in enumerate(pending_pos):` |
| **5** | `SAP: Set Text (Command)` | T-Code: `ME22N` (Change Purchase Order) | `load_po_data()` |
| **6** | `SAP: Set Text (Item/Header)` | Field IDs: Order Qty, Net Price, Delivery Date | `update_sap_mockup()` |
| **7** | `SAP: Click (Save)` | Toolbar Button: `btn[11]` (Save) | `save_current_po()` |
| **8** | `Screen: Capture Window` | Window: `SAP GUI*`, Output: `Screenshots/PO_$rPOData[0]$.png` | `generate_sap_screenshot()` (`Pillow`) |
| **9** | `Email: Send` | To: `$rPOData[12]$`, Attachment: `$sScreenshotPath$`, Body: HTML | `save_and_dispatch_email()` (`smtplib/MIME`) |
| **10** | `Excel Advanced: Set Cell` | Column: `Process_Status`, Value: `Processed` | `mark_po_as_processed()` |
| **11** | `Excel Advanced: Close` | Save changes: `True` | `wb.save()` |
| **12** | `SAP: Disconnect` | Close session gracefully | `root.destroy()` |
""")
