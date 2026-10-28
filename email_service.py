"""
email_service.py
Generates executive-ready HTML & MIME email notifications for PO updates,
with embedded screenshot evidence, audit metadata, and optional SMTP sending.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
EMAILS_DIR = os.path.join(WORKSPACE_DIR, "Emails")
os.makedirs(EMAILS_DIR, exist_ok=True)


def generate_html_template(po_data, screenshot_rel_or_cid="cid:po_screenshot"):
    """Creates a modern, responsive HTML email template for stakeholders/faculty."""
    po_num = po_data.get("po_number", "4500010001")
    vendor = po_data.get("vendor_name", "Acme Industrial Supplies")
    item_desc = po_data.get("item_description", "Item Description")
    item_code = po_data.get("item_code", "MAT-0000")
    qty = f"{int(float(po_data.get('quantity', 0))):,}"
    price = f"${float(po_data.get('unit_price', 0)):,.2f}"
    total = f"${float(po_data.get('total_amount', 0)):,.2f}"
    status = po_data.get("target_status", "Approved")
    delivery = po_data.get("delivery_date", "2026-11-15")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SAP Purchase Order Update Notice - {po_num}</title>
  <style>
    body {{
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #F3F4F6;
      color: #1F2937;
    }}
    .email-container {{
      max-width: 680px;
      margin: 30px auto;
      background: #FFFFFF;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      border: 1px solid #E5E7EB;
    }}
    .header {{
      background: linear-gradient(135deg, #0A3B5C 0%, #1F4E79 100%);
      padding: 24px 32px;
      color: #FFFFFF;
    }}
    .header h1 {{
      margin: 0 0 6px 0;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header p {{
      margin: 0;
      font-size: 13px;
      color: #BFDBFE;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      background-color: #10B981;
      color: white;
      font-weight: 700;
      font-size: 11px;
      border-radius: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 8px;
    }}
    .content {{
      padding: 28px 32px;
    }}
    .intro {{
      font-size: 14px;
      line-height: 1.6;
      color: #374151;
      margin-bottom: 20px;
    }}
    .details-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      background: #F9FAFB;
      border-radius: 6px;
      overflow: hidden;
      border: 1px solid #E5E7EB;
    }}
    .details-table th, .details-table td {{
      padding: 12px 16px;
      text-align: left;
      font-size: 13px;
    }}
    .details-table th {{
      background-color: #F3F4F6;
      color: #4B5563;
      font-weight: 600;
      border-bottom: 1px solid #E5E7EB;
      width: 35%;
    }}
    .details-table td {{
      color: #111827;
      border-bottom: 1px solid #E5E7EB;
    }}
    .details-table tr:last-child td, .details-table tr:last-child th {{
      border-bottom: none;
    }}
    .highlight {{
      font-weight: 700;
      color: #0A3B5C;
    }}
    .screenshot-section {{
      margin-top: 24px;
      padding: 16px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
    }}
    .screenshot-section h3 {{
      margin: 0 0 12px 0;
      font-size: 13px;
      color: #0F172A;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .screenshot-img {{
      width: 100%;
      border-radius: 4px;
      border: 1px solid #CBD5E1;
      display: block;
    }}
    .footer {{
      background-color: #F9FAFB;
      padding: 20px 32px;
      border-top: 1px solid #E5E7EB;
      font-size: 12px;
      color: #6B7280;
      line-height: 1.5;
    }}
    .footer-highlight {{
      color: #1F2937;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>Automated Purchase Order Update Notice</h1>
      <p>SAP ECC / S/4HANA Process Automation (Transaction: ME22N)</p>
      <div class="badge">RPA STATUS: {status}</div>
    </div>
    
    <div class="content">
      <div class="intro">
        Dear Stakeholder / Faculty Evaluator,<br><br>
        The <strong>Automated Purchase Order Bot</strong> has successfully processed and updated Purchase Order 
        <strong class="highlight">#{po_num}</strong> in the SAP ERP system. Below is the updated order summary and verification evidence.
      </div>

      <table class="details-table">
        <tr>
          <th>Purchase Order (PO)</th>
          <td class="highlight">{po_num}</td>
        </tr>
        <tr>
          <th>Vendor Name</th>
          <td>{vendor}</td>
        </tr>
        <tr>
          <th>Material & Description</th>
          <td><strong>{item_code}</strong> - {item_desc}</td>
        </tr>
        <tr>
          <th>Order Quantity</th>
          <td>{qty} EA</td>
        </tr>
        <tr>
          <th>Net Unit Price</th>
          <td>{price}</td>
        </tr>
        <tr>
          <th>Total Order Value</th>
          <td class="highlight" style="color: #059669; font-size: 15px;">{total} USD</td>
        </tr>
        <tr>
          <th>Updated Status</th>
          <td><span style="color:#15803D; font-weight:700;">{status}</span></td>
        </tr>
        <tr>
          <th>Expected Delivery</th>
          <td>{delivery}</td>
        </tr>
        <tr>
          <th>Execution Engine</th>
          <td>Automation Anywhere RPA / Python ME22N Controller</td>
        </tr>
        <tr>
          <th>Execution Timestamp</th>
          <td>{timestamp}</td>
        </tr>
      </table>

      <div class="screenshot-section">
        <h3>[Visual Verification Screenshot Attached]</h3>
        <img src="{screenshot_rel_or_cid}" alt="SAP GUI ME22N Screenshot" class="screenshot-img" />
      </div>
    </div>

    <div class="footer">
      <div class="footer-highlight">Automated System Generated Notification</div>
      This message was automatically generated and dispatched by the <strong>Automated Purchase Order Management RPA Bot</strong>.<br>
      Target Environment: SAP PRD-100 | Source: PO_List.xlsx | Audit Reference: SAP-PO-{po_num}-OK
    </div>
  </div>
</body>
</html>"""
    return html


def save_and_dispatch_email(po_data, screenshot_path, recipient_override=None, smtp_config=None):
    """
    Builds the MIME message with embedded screenshot, writes .html and .eml files to disk,
    and sends via SMTP if config is provided.
    """
    po_num = po_data.get("po_number", "4500010001")
    recipient = recipient_override or po_data.get("stakeholder_email", "procurement.lead@enterprise.com")
    subject = f"[PO UPDATE CONFIRMATION] PO #{po_num} Status: {po_data.get('target_status', 'Approved')}"

    # Setup MIME
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = "rpa-bot@enterprise-sap.internal"
    msg["To"] = recipient
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    alt_part = MIMEMultipart("alternative")
    msg.attach(alt_part)

    # Plaintext fallback
    text_content = f"""
AUTOMATED PURCHASE ORDER UPDATE NOTICE
========================================
PO Number: {po_num}
Vendor: {po_data.get('vendor_name')}
Status: {po_data.get('target_status', 'Approved')}
Total Amount: ${po_data.get('total_amount'):,.2f} USD
Delivery Date: {po_data.get('delivery_date')}

Execution Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
A screenshot of the updated SAP transaction is attached to this email.
"""
    alt_part.attach(MIMEText(text_content, "plain"))

    # HTML body with cid
    html_body = generate_html_template(po_data, screenshot_rel_or_cid="cid:po_screenshot")
    alt_part.attach(MIMEText(html_body, "html"))

    # Attach screenshot with CID
    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, "rb") as f:
            img_data = f.read()
        img_part = MIMEImage(img_data)
        img_part.add_header("Content-ID", "<po_screenshot>")
        img_part.add_header("Content-Disposition", "inline", filename=os.path.basename(screenshot_path))
        msg.attach(img_part)

    # Save to Emails directory
    timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
    eml_filename = f"Email_PO_{po_num}_{timestamp_slug}.eml"
    html_filename = f"Email_PO_{po_num}_{timestamp_slug}.html"
    
    eml_path = os.path.join(EMAILS_DIR, eml_filename)
    html_path = os.path.join(EMAILS_DIR, html_filename)

    with open(eml_path, "w", encoding="utf-8") as f:
        f.write(msg.as_string())

    # Standalone HTML preview file linking to relative screenshot file
    rel_screenshot = os.path.relpath(screenshot_path, EMAILS_DIR).replace("\\", "/") if screenshot_path else ""
    standalone_html = generate_html_template(po_data, screenshot_rel_or_cid=rel_screenshot)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(standalone_html)

    sent_via_smtp = False
    smtp_error = None
    if smtp_config and smtp_config.get("enabled"):
        try:
            server = smtplib.SMTP(smtp_config.get("host", "localhost"), int(smtp_config.get("port", 25)))
            if smtp_config.get("use_tls"):
                server.starttls()
            if smtp_config.get("user") and smtp_config.get("password"):
                server.login(smtp_config["user"], smtp_config["password"])
            server.send_message(msg)
            server.quit()
            sent_via_smtp = True
        except Exception as e:
            smtp_error = str(e)

    return {
        "po_number": po_num,
        "recipient": recipient,
        "eml_path": eml_path,
        "html_path": html_path,
        "sent_via_smtp": sent_via_smtp,
        "smtp_error": smtp_error
    }


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
    # Test with dummy screenshot if exists
    sc_file = os.path.join(WORKSPACE_DIR, "Screenshots")
    sample_img = None
    if os.path.exists(sc_file):
        pngs = [f for f in os.listdir(sc_file) if f.endswith(".png")]
        if pngs:
            sample_img = os.path.join(sc_file, pngs[0])

    res = save_and_dispatch_email(sample_po, sample_img)
    print("Email generated successfully:")
    print(f"HTML: {res['html_path']}")
    print(f"EML: {res['eml_path']}")
