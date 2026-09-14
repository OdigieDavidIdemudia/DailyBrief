import os
from docx import Document
from docx.shared import Pt, RGBColor

from docx.oxml.ns import qn

def disable_update_fields(doc):
    try:
        settings = doc.settings.element
        update_fields = settings.find(qn('w:updateFields'))
        if update_fields is not None:
            settings.remove(update_fields)
    except Exception:
        pass

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def _delete_paragraphs_between_elements(p_start, p_end):
    """Deletes all XML elements between two paragraph elements."""
    if p_start is None or p_end is None:
        return
    curr = p_start._element.getnext()
    while curr is not None and curr is not p_end._element:
        nxt = curr.getnext()
        curr.getparent().remove(curr)
        curr = nxt

def _delete_element_and_following(p_start):
    """Deletes p_start and all elements up to end of document."""
    if p_start is None:
        return
    curr = p_start._element.getnext()
    while curr is not None:
        nxt = curr.getnext()
        curr.getparent().remove(curr)
        curr = nxt

def enforce_heading_style(paragraph):
    """Enforces LEFT alignment and BLACK color on section headings."""
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in paragraph.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)

def _replace_paragraph_text(paragraph, new_text):
    if paragraph.runs:
        for i, r in enumerate(paragraph.runs):
            if i == 0:
                r.text = new_text
            else:
                r.text = ""
    else:
        paragraph.text = new_text

def render_tia_report(data: dict, output_path: str):
    template_path = os.path.join(os.getcwd(), "static", "reports", "GTCO Threat Intelligence Advisory - Master Template.docx")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")
        
    doc = Document(template_path)
    disable_update_fields(doc)
    
    # 1. Fill Cover Page & Metadata placeholders
    for p in doc.paragraphs:
        if "TIA(DDMMYY/NNN)" in p.text:
            new_text = p.text.replace("TIA(DDMMYY/NNN)", data.get("report_id", ""))
            _replace_paragraph_text(p, new_text)
        elif p.text.startswith("Report Title:"):
            _replace_paragraph_text(p, f"Report Title: {data.get('title', '')}")
        elif p.text.startswith("Date:"):
            _replace_paragraph_text(p, f"Date: {data.get('date', '')}")
        elif p.text.startswith("Prepared By:"):
            _replace_paragraph_text(p, f"Prepared By: {data.get('prepared_by', '')}")
        elif p.text.startswith("Reviewed By:"):
            _replace_paragraph_text(p, f"Reviewed By: {data.get('reviewed_by', '')}")
        elif p.text.startswith("Organization/Unit:"):
            _replace_paragraph_text(p, f"Organization/Unit: {data.get('org_unit', '')}")
            
    # 2. Map all headings to their paragraph objects
    h_elements = {}
    for p in doc.paragraphs:
        text = p.text.strip().lower()
        if text.startswith('executive summary'): h_elements['executive_summary'] = p
        elif text.startswith('threat landscape'): h_elements['threat_landscape'] = p
        elif text.startswith('indicators of compromise'): h_elements['iocs'] = p
        elif text.startswith('detection rules'): h_elements['detection_rules'] = p
        elif text.startswith('impact assessment'): h_elements['impact_assessment'] = p
        elif text.startswith('affected assets'): h_elements['affected_assets'] = p
        elif text.startswith('recommendation and mitigations'): h_elements['recommendations'] = p
        elif text == 'references': h_elements['references'] = p
        elif text == 'appendices': h_elements['appendices'] = p
        elif text == 'table of content': h_elements['toc'] = p

    # Fix heading styles
    for k, p in h_elements.items():
        if k != 'toc':
            enforce_heading_style(p)
            
    # Ordered headings
    headings_order = [
        'executive_summary', 'threat_landscape', 'iocs', 'detection_rules',
        'impact_assessment', 'affected_assets', 'recommendations', 'references', 'appendices'
    ]

    # --- DELETE LEGACY CONTENT AND INSERT NEW CONTENT ---
    # We do this backwards to avoid messing up any forward references, though XML deletion is stable.
    for i in range(len(headings_order) - 1, -1, -1):
        curr_k = headings_order[i]
        curr_p = h_elements.get(curr_k)
        if not curr_p:
            continue
            
        next_k = headings_order[i+1] if i + 1 < len(headings_order) else None
        next_p = h_elements.get(next_k) if next_k else None
        
        if next_p:
            _delete_paragraphs_between_elements(curr_p, next_p)
        else:
            _delete_element_and_following(curr_p)
            
        # --- INSERT CONTENT ---
        # Note: insert_paragraph_before on next_p puts it between curr_p and next_p.
        # If there is no next_p, we just append to the document.
        
        def insert_p_func(text="", style=None):
            target_style = style if style else "Normal"
            if next_p:
                p = next_p.insert_paragraph_before("")
            else:
                p = doc.add_paragraph("")
                
            p.style = target_style
            if text:
                r = p.add_run(text)
                r.font.name = "Abadi"
                r.font.size = Pt(12)
            return p

        if curr_k == 'executive_summary':
            insert_p_func(data.get('executive_summary', ''))
            
        elif curr_k == 'threat_landscape':
            insert_p_func(data.get('threat_landscape', ''))
            
        elif curr_k == 'iocs':
            iocs = data.get('iocs', [])
            if not iocs:
                insert_p_func("No indicators of compromise supplied and automatic enrichment was disabled for this report.")
            else:
                # Group by type
                grouped = {}
                for ioc in iocs:
                    grouped.setdefault(ioc.get('type'), []).append(ioc)
                    
                for idx, (ioc_type, items) in enumerate(grouped.items()):
                    # Category heading
                    cat_p = insert_p_func(f"{idx+1}. {ioc_type.replace('_', ' ').title()}:", style="List Paragraph")
                    # Force restart numbering isn't easy with python-docx, but we apply List Paragraph.
                    for item in items:
                        val = item.get('value')
                        ctx = item.get('context')
                        prov = ""
                        conf = f" (Confidence: {item.get('confidence')})" if item.get('confidence') else ""
                        text = f"{val}"
                        if ctx: text += f" - {ctx}"
                        text += f" {prov}{conf}"
                        insert_p_func(text, style="List Paragraph")
                        
        elif curr_k == 'detection_rules':
            rules = data.get('detection_rules', [])
            for r in rules:
                insert_p_func(f"Target: {r.get('target', '')}")
                logic_p = insert_p_func(f"Logic: {r.get('logic', '')}")
                if r.get('notes'):
                    insert_p_func(f"Notes: {r.get('notes')}")
                insert_p_func("")
                
        elif curr_k == 'impact_assessment':
            insert_p_func(data.get('impact_assessment', ''))
            
        elif curr_k == 'affected_assets':
            assets = data.get('affected_assets', [])
            for asset in assets:
                insert_p_func(asset, style="List Paragraph")
                
        elif curr_k == 'recommendations':
            recs = data.get('recommendations', [])
            for idx, r in enumerate(recs):
                insert_p_func(f"{idx+1}. {r.get('action', '')}", style="List Paragraph")
                for sub in (r.get('sub_items') or []):
                    insert_p_func(sub, style="List Paragraph") # Ideally sub-bullet, but keeping it simple
                    
        elif curr_k == 'references':
            refs = data.get('references', [])
            for idx, r in enumerate(refs):
                date_str = f" ({r.get('date')})" if r.get('date') else ""
                insert_p_func(f"{idx+1}. {r.get('source', '')}, \"{r.get('title', '')}\"{date_str} - {r.get('url', '')}", style="List Paragraph")
                
        elif curr_k == 'appendices':
            apps = data.get('appendices', [])
            if not apps or apps == ["None"]:
                insert_p_func("1. None", style="List Paragraph")
            else:
                for idx, a in enumerate(apps):
                    insert_p_func(f"{idx+1}. {a}", style="List Paragraph")

    doc.save(output_path)
