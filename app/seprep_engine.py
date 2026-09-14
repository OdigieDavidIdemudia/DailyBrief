import re
import requests
import json
import os
import time

def load_seprep_config():
    try:
        if os.path.exists('seprep_config.json'):
            with open('seprep_config.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return {"vt_key": "", "abuse_key": ""}

def classify_indicator(indicator):
    patterns = {
        "ipv4": r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
        "sha256": r"^[a-fA-F0-9]{64}$",
        "sha1": r"^[a-fA-F0-9]{40}$",
        "md5": r"^[a-fA-F0-9]{32}$",
        "domain": r"^(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)"
    }
    for t, pat in patterns.items():
        if re.match(pat, indicator, re.IGNORECASE):
            return t
    return "unknown"

def query_vt(indicator, ioc_type, vt_key):
    if not vt_key: return {"score": None, "verdict": "Unknown", "error": "No VT Key"}
    base_url = "https://www.virustotal.com/api/v3"
    if ioc_type == "ipv4":
        url = f"{base_url}/ip_addresses/{indicator}"
    elif ioc_type == "domain":
        url = f"{base_url}/domains/{indicator}"
    elif ioc_type in ["sha256", "sha1", "md5"]:
        url = f"{base_url}/files/{indicator}"
    else:
        return None
        
    headers = {"x-apikey": vt_key}
    try:
        # Rate limiting logic (4/min = sleep 15s if we get 429)
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 429:
            return {"score": None, "verdict": "Unknown", "error": "HTTP 429: Error: Rate Limit"}
        if res.status_code == 404:
            return {"score": None, "verdict": "Unknown", "error": "HTTP 404: Not Found"}
        
        data = res.json()
        malicious = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious", 0)
        
        verdict = "Safe"
        if malicious > 2: verdict = "Malicious"
        elif 1 <= malicious <= 2: verdict = "Suspicious"
        
        return {"score": malicious, "verdict": verdict, "error": None}
    except Exception as e:
        return {"score": None, "verdict": "Unknown", "error": str(e)}

def query_abuseipdb(indicator, abuse_key):
    if not abuse_key: return {"score": None, "verdict": "Unknown", "error": "No AbuseIPDB Key", "location": "", "isp": ""}
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": abuse_key, "Accept": "application/json"}
    params = {"ipAddress": indicator, "maxAgeInDays": "90", "verbose": "true"}
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 429:
            return {"score": None, "verdict": "Unknown", "error": "HTTP 429: Error: Rate Limit", "location": "", "isp": ""}
        if res.status_code == 422:
            return {"score": None, "verdict": "Unknown", "error": "HTTP 422: Error: Unprocessable IP", "location": "", "isp": ""}
            
        data = res.json().get("data", {})
        score = data.get("abuseConfidenceScore", 0)
        
        verdict = "Safe"
        if score > 25: verdict = "Malicious"
        elif 0 < score <= 25: verdict = "Suspicious"
        
        return {
            "score": score, 
            "verdict": verdict, 
            "error": None,
            "location": data.get("countryCode", ""),
            "isp": data.get("isp", "")
        }
    except Exception as e:
        return {"score": None, "verdict": "Unknown", "error": str(e), "location": "", "isp": ""}

def enrich_iocs(iocs):
    config = load_seprep_config()
    vt_key = config.get("vt_key")
    abuse_key = config.get("abuse_key")
    
    enriched = []
    
    for item in iocs:
        indicator = item.get("value", "")
        ioc_type = classify_indicator(indicator)
        if ioc_type == "unknown":
            item["reputation_verdict"] = "Unknown"
            item["enrichment_sources"] = "None"
            item["reputation_scores"] = ""
            item["location"] = ""
            item["isp"] = ""
            item["api_errors"] = "Skipped (Unknown format)"
            enriched.append(item)
            continue
            
        # Add rate limiting pause so we don't spam and get completely blocked immediately
        # Since VT limit is 4/min, we sleep a bit to space out.
        # But for 50 IOCs, we'd sleep forever. We'll just rely on the 429 handling.
        
        vt_res = query_vt(indicator, ioc_type, vt_key)
        abuse_res = None
        if ioc_type == "ipv4":
            abuse_res = query_abuseipdb(indicator, abuse_key)
            
        # Aggregation Logic
        verdicts = []
        scores = []
        sources = []
        errors = []
        location = ""
        isp = ""
        
        if vt_res:
            sources.append("VirusTotal")
            verdicts.append(vt_res.get("verdict"))
            if vt_res.get("score") is not None: scores.append(str(vt_res.get("score")))
            if vt_res.get("error"): errors.append("VT: " + vt_res.get("error"))
            
        if abuse_res:
            sources.append("AbuseIPDB")
            verdicts.append(abuse_res.get("verdict"))
            if abuse_res.get("score") is not None: scores.append(str(abuse_res.get("score")))
            if abuse_res.get("error"): errors.append("AbuseIPDB: " + abuse_res.get("error"))
            if abuse_res.get("location"): location = abuse_res.get("location")
            if abuse_res.get("isp"): isp = abuse_res.get("isp")

        # Priority: Malicious > Suspicious > Safe > Unknown
        final_verdict = "Unknown"
        if "Malicious" in verdicts:
            final_verdict = "Malicious"
        elif "Suspicious" in verdicts:
            final_verdict = "Suspicious"
        elif "Safe" in verdicts:
            final_verdict = "Safe"
            
        item["reputation_verdict"] = final_verdict
        item["enrichment_sources"] = " + ".join(sources) if sources else "None"
        item["reputation_scores"] = " | ".join(scores) if scores else ""
        item["location"] = location
        item["isp"] = isp
        item["api_errors"] = " | ".join(errors) if errors else ""
        item["type"] = ioc_type # Update with our regex classification
        
        enriched.append(item)
        
    return enriched
