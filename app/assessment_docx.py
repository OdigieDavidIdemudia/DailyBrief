import os
from docx import Document
from docx.shared import Pt, RGBColor
from app.schemas_assessment import ToolAssessment

def render_assessment_report(subsidiary_name: str, assessment: ToolAssessment, out_path: str):
    template_path = os.path.join('static', 'reports', 'GTBank_Tool_Assessment_Template.docx')
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")
        
    doc = Document(template_path)
    
    # Sort findings: CRITICAL > HIGH > MEDIUM > LOW, then by finding_number
    severity_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
    sorted_findings = sorted(
        assessment.findings, 
        key=lambda f: (severity_order.get(f.severity, 99), f.finding_number or 999)
    )
    
    # Helper for safe text replacement
    def _replace_paragraph_text(paragraph, new_text):
        if paragraph.runs:
            for i, r in enumerate(paragraph.runs):
                if i == 0:
                    r.text = new_text
                else:
                    r.text = ""
        else:
            paragraph.text = new_text

    # Find placeholders and target insertion point
    findings_heading = None
    for p in doc.paragraphs:
        # Fill title and performed by
        if "GTBANK [SUBSIDIARY]:" in p.text:
            new_text = p.text.replace("[SUBSIDIARY]", assessment.subsidiary_name if hasattr(assessment, 'subsidiary_name') else subsidiary_name)
            new_text = new_text.replace("[TOOL NAME]", assessment.tool_display_name)
            new_text = new_text.replace("[DD/MM/YYYY]", assessment.assessment_date)
            _replace_paragraph_text(p, new_text)
        elif "Performed by:" in p.text:
            new_text = p.text.replace("[Assessor Name]", assessment.performed_by)
            _replace_paragraph_text(p, new_text)
        elif "[Tool Name]" in p.text:
            new_text = p.text.replace("[Tool Name]", assessment.tool_display_name)
            _replace_paragraph_text(p, new_text)
            
        if "Findings and Recommendations" in p.text.strip():
            findings_heading = p
            
    # Delete filler text after findings heading
    if findings_heading:
        curr = findings_heading._element.getnext()
        while curr is not None:
            nxt = curr.getnext()
            curr.getparent().remove(curr)
            curr = nxt
            
    # Insert findings
    if findings_heading:
        def insert_p_func(text="", style=None):
            p = doc.add_paragraph("")
            if style:
                p.style = style
            else:
                p.style = "Normal"
            if text:
                r = p.add_run(text)
                r.font.name = "Abadi"
                r.font.size = Pt(12)
            return p

        for i, finding in enumerate(sorted_findings):
            # Number and title
            p_title = insert_p_func("", style="Heading 2" if "Heading 2" in [s.name for s in doc.styles] else "Normal")
            run = p_title.add_run(f"{i+1}. {finding.title} - {finding.severity}")
            run.font.name = "Abadi"
            run.font.size = Pt(12)
            run.bold = True
            
            if finding.severity == "CRITICAL":
                run.font.color.rgb = RGBColor(139, 0, 0) # Dark Red
            elif finding.severity == "HIGH":
                run.font.color.rgb = RGBColor(255, 0, 0) # Red
            elif finding.severity == "MEDIUM":
                run.font.color.rgb = RGBColor(255, 165, 0) # Orange/Yellow
                
            # Impact
            p_impact = insert_p_func("", style="List Bullet" if "List Bullet" in [s.name for s in doc.styles] else "Normal")
            r1 = p_impact.add_run("Impact: ")
            r1.bold = True
            r1.font.name = "Abadi"
            r1.font.size = Pt(12)
            
            r2 = p_impact.add_run(finding.impact)
            r2.font.name = "Abadi"
            r2.font.size = Pt(12)
            
            # Recommendation
            p_rec = insert_p_func("", style="List Bullet" if "List Bullet" in [s.name for s in doc.styles] else "Normal")
            r3 = p_rec.add_run("Recommendation: ")
            r3.bold = True
            r3.font.name = "Abadi"
            r3.font.size = Pt(12)
            
            r4 = p_rec.add_run(finding.recommendation)
            r4.font.name = "Abadi"
            r4.font.size = Pt(12)
            
            insert_p_func("") # spacing
            
        # Optional Advisories
        for i, adv in enumerate(assessment.advisories):
            p_adv = insert_p_func("", style="Heading 2" if "Heading 2" in [s.name for s in doc.styles] else "Normal")
            run = p_adv.add_run(f"Advisory: {adv.topic}")
            run.font.name = "Abadi"
            run.font.size = Pt(12)
            run.bold = True
            run.font.color.rgb = RGBColor(0, 102, 204) # Blue
            
            p_ctx = insert_p_func(adv.context)
            
            p_rec = insert_p_func("", style="List Bullet" if "List Bullet" in [s.name for s in doc.styles] else "Normal")
            r3 = p_rec.add_run("Recommendation: ")
            r3.bold = True
            r3.font.name = "Abadi"
            r3.font.size = Pt(12)
            
            r4 = p_rec.add_run(adv.recommendation)
            r4.font.name = "Abadi"
            r4.font.size = Pt(12)
            
            insert_p_func("")
            
    doc.save(out_path)
