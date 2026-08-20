import os

with open('app/ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

matrix = """
    Global Subsidiary Responsibility Matrix:
    - Ghana: XDR=Victoria, SIEM=N/R, NAC=Victoria, DLP=Victoria, WAF=Victoria, DAM=Victoria, SHELT=Victoria
    - SierraLeone: Akhere (All)
    - U.K: XDR=Idemudia, SIEM=N/R, NAC=Idemudia, DLP=N/R, WAF=N/R, DAM=Idemudia, SHELT=Idemudia
    - Cote D'Ivoire: Temitayo (All)
    - Gambia: Edidiong (All)
    - Tanzania: Moyin (All)
    - Uganda: Godwin (All)
    - Rwanda: XDR=Victoria, SIEM=N/R, NAC=Janet, DLP=Idemudia, WAF=Idemudia, DAM=Godwin, SHELT=Akhere
    - Liberia: David (Idemudia) (All)
    - Kenya: Janet (All)
    - GTPension: XDR=Idemudia, SIEM=Idemudia, NAC=N/R, DLP=N/R, WAF=N/R, DAM=N/R, SHELT=N/R
    - Senegal: XDR=Moyin, SIEM=N/R, NAC=N/R, DLP=N/R, WAF=N/R, DAM=N/R, SHELT=N/R
"""

old_prompt = """    prompt = f\"\"\"
    You are a highly analytical SOC Operations Manager reporting on a subsidiary's security posture.
    Review the provided raw database logs for the subsidiary '{subsidiary_name}' and synthesize a professional Subsidiary Security Status Report.
    
    Populate the summary, sections (Cortex XDR, SIEM, NAC, DLP, Web Proxy, SHELT, WAF), and the key risks requiring CISO attention.
    If information is missing for a specific metric in the logs, use 'N/A' or a brief statement indicating no data is available.
    Output strictly as JSON matching the required schema.

    Raw Logs for Subsidiary {subsidiary_name}:
    {logs_text}
    \"\"\""""

new_prompt = f"""    prompt = f\"\"\"
    You are a highly analytical SOC Operations Manager reporting on a subsidiary's security posture.
    You are generating this report on behalf of David Idemudia Odigie (Idemudia).
    
    Review the provided raw database logs for the subsidiary '{{subsidiary_name}}' and synthesize a professional Subsidiary Security Status Report.
    
    {matrix}

    CRITICAL INSTRUCTION:
    Based on the matrix above, identify if 'Idemudia' (or David) is responsible for a specific tool in '{{subsidiary_name}}'.
    If Idemudia IS responsible: Extract the status from the raw logs and provide detailed metrics. If no data is in logs, use 'N/A'.
    If Idemudia is NOT responsible (e.g. it is assigned to Victoria, N/R, etc.): Do NOT extract logs for this tool. Instead, for all fields in that section, explicitly state 'Not Managed by Idemudia (Managed by [Owner Name])' or 'N/R' if it says N/R.
    
    Populate the summary, sections (Cortex XDR, SIEM, NAC, DLP, Web Proxy, SHELT, WAF), and the key risks requiring CISO attention.
    Output strictly as JSON matching the required schema.

    Raw Logs for Subsidiary {{subsidiary_name}}:
    {{logs_text}}
    \"\"\""""

if old_prompt in content:
    new_content = content.replace(old_prompt, new_prompt)
    with open('app/ai.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully updated ai.py")
else:
    print("Could not find the old prompt in ai.py")
