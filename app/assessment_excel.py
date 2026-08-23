import os
import openpyxl
from openpyxl.utils import get_column_letter
from app.schemas_assessment import ToolAssessment

def _get_target_sheet_name(tool_id: str) -> str:
    mapping = {
        "NAC": "NAC",
        "ActiveDirectory": "Active Directory",
        "PAM": "PAM",
        "SIEM": "SIEM",
        "XDR": "XDR",
        "DAM": "DAM",
        "FIM": "FIM",
        "DLP": "DLP",
        "WebProxy": "Web Proxy",
        "VirtualDevicesNetworks": "Virtual Devices & Networks"
    }
    return mapping.get(tool_id, tool_id)

def get_dashboard_metrics(workbook_path: str) -> dict:
    """Reads Dashboard!B5:H15 from the live workbook."""
    if not os.path.exists(workbook_path):
        # Fallback empty metrics if file doesn't exist yet
        return {"tools": {}, "total": {}}
        
    wb = openpyxl.load_workbook(workbook_path, data_only=True)
    if 'Dashboard' not in wb.sheetnames:
        return {}
        
    ws = wb['Dashboard']
    metrics = {"tools": {}}
    
    # Rows 5 to 14 are tools
    for row_idx in range(5, 15):
        tool_name = ws.cell(row=row_idx, column=2).value # Col B
        if tool_name:
            metrics["tools"][tool_name] = {
                "critical": ws.cell(row=row_idx, column=3).value or 0,
                "high": ws.cell(row=row_idx, column=4).value or 0,
                "medium": ws.cell(row=row_idx, column=5).value or 0,
                "low": ws.cell(row=row_idx, column=6).value or 0,
                "total": ws.cell(row=row_idx, column=7).value or 0,
                "open": ws.cell(row=row_idx, column=8).value or 0,
                "closed": ws.cell(row=row_idx, column=9).value or 0
            }
            
    # Row 15 is TOTAL
    metrics["total"] = {
        "critical": ws.cell(row=15, column=3).value or 0,
        "high": ws.cell(row=15, column=4).value or 0,
        "medium": ws.cell(row=15, column=5).value or 0,
        "low": ws.cell(row=15, column=6).value or 0,
        "total": ws.cell(row=15, column=7).value or 0,
        "open": ws.cell(row=15, column=8).value or 0,
        "closed": ws.cell(row=15, column=9).value or 0
    }
    
    return metrics

def append_tool_findings_to_excel(assessment: ToolAssessment, in_path: str, out_path: str):
    """Appends findings to the correct tab in the Master Workbook."""
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Workbook not found at {in_path}")
        
    wb = openpyxl.load_workbook(in_path)
    sheet_name = _get_target_sheet_name(assessment.tool_id)
    
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Sheet '{sheet_name}' not found in workbook.")
        
    ws = wb[sheet_name]
    
    # Sort findings by severity and number
    severity_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
    sorted_findings = sorted(
        assessment.findings, 
        key=lambda f: (severity_order.get(f.severity, 99), f.finding_number or 999)
    )
    
    if not sorted_findings:
        wb.save(out_path)
        return
        
    # Find the first empty row starting from row 13
    start_row = 13
    curr_row = start_row
    while curr_row <= 37:
        # Check column C (Observation)
        val = ws.cell(row=curr_row, column=3).value
        if not val or str(val).strip() == "":
            break
        curr_row += 1
        
    if curr_row > 37:
        # TODO: Handle capacity warning (insert rows and copy validation/formulas)
        # For MVP, we just overwrite row 37 and beyond, but it breaks the dashboard range.
        pass
        
    # Append findings
    for finding in sorted_findings:
        obs_text = f"{finding.title}: {finding.raw_note}"
        
        # B: Segment
        ws.cell(row=curr_row, column=2).value = finding.segment_sector
        # C: Observation
        ws.cell(row=curr_row, column=3).value = obs_text
        # D: Impact
        ws.cell(row=curr_row, column=4).value = finding.impact
        # E: Severity (Title case to match dropdown: Critical, High, etc.)
        ws.cell(row=curr_row, column=5).value = finding.severity.title()
        # F: Recommendation
        ws.cell(row=curr_row, column=6).value = finding.recommendation
        # H: Status
        ws.cell(row=curr_row, column=8).value = "Open"
        
        curr_row += 1
        
    wb.save(out_path)
