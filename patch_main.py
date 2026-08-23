import os

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """    if "error" in result:
        return {"status": "complete", "draft": {"impact_summary": "DEBUG ERROR: " + str(result["error"]), "detection_and_notification": "", "root_cause_analysis": "", "mitigation_and_recovery": "", "preventive_measures": ""}}
        
    return result"""

new_code = """    if "error" in result:
        return {"status": "complete", "draft": {"impact_summary": "DEBUG ERROR: " + str(result["error"]), "detection_and_notification": "", "root_cause_analysis": "", "mitigation_and_recovery": "", "preventive_measures": ""}}
        
    result["status"] = "complete"
    if "draft" not in result or not result["draft"]:
        result["draft"] = {"impact_summary": "", "detection_and_notification": "", "root_cause_analysis": "", "mitigation_and_recovery": "", "preventive_measures": ""}
    return result"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find old code")
