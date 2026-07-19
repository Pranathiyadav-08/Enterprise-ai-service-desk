import traceback
import os

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")

    def make_pdf(filename, title, lines):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 12)
        pdf.ln(4)
        for line in lines:
            pdf.multi_cell(0, 8, line)
            pdf.ln(1)
        pdf.output(filename)
        print(f"Created: {filename}")

    make_pdf(os.path.join(DOCS, "hr_policy.pdf"), "HR Policy", [
        "Leave Policy",
        "Employees are entitled to the following leaves per year:",
        "12 Casual Leaves, 12 Sick Leaves, 20 Earned Leaves.",
        "Leave balance resets every January 1st.",
        "Leaves must be applied at least 2 days in advance except for sick leave.",
        "Unused earned leaves can be carried forward up to a maximum of 30 days.",
        "Attendance Policy",
        "Employees must maintain a minimum of 90 percent attendance per quarter.",
        "Late arrivals beyond 3 times in a month will be marked as half-day.",
        "Appraisal Policy",
        "Performance appraisals are conducted annually in March.",
        "Increments are based on performance ratings from 1 to 5.",
    ])

    make_pdf(os.path.join(DOCS, "it_support.pdf"), "IT Support Guide", [
        "VPN Issues",
        "If your VPN is not connecting:",
        "1. Restart the VPN client.",
        "2. Check your internet connection.",
        "3. Clear VPN cache and reconnect.",
        "4. If unresolved, contact IT Helpdesk at it-support@company.com.",
        "Password Reset",
        "Visit the self-service portal at portal.company.com.",
        "Click Forgot Password and follow the steps.",
        "For account lockouts, contact IT Helpdesk immediately.",
        "Laptop Issues",
        "For hardware issues, raise a ticket at helpdesk.company.com.",
        "Replacement laptops are provided within 2 business days.",
        "Software Installation",
        "All software installations must be approved by the IT department.",
        "Submit a software request form at least 3 days in advance.",
    ])

    make_pdf(os.path.join(DOCS, "company_policy.pdf"), "Company Policy", [
        "Work From Home Policy",
        "Employees are allowed to work remotely up to 2 days per week.",
        "Work from home requires prior approval from the reporting manager.",
        "Employees must be reachable during core hours 10 AM to 4 PM.",
        "WFH is not permitted during the first 3 months of joining.",
        "Code of Conduct",
        "All employees must maintain professional behavior at all times.",
        "Harassment of any kind will result in immediate disciplinary action.",
        "Confidential company information must not be shared externally.",
        "Travel and Reimbursement Policy",
        "Business travel must be pre-approved by department head.",
        "Economy class is the standard for domestic travel.",
        "Reimbursement claims must be submitted within 7 days of travel.",
        "Receipts are mandatory for all claims above 500 rupees.",
    ])

    print("All 3 PDFs created successfully.")

except Exception:
    traceback.print_exc()
