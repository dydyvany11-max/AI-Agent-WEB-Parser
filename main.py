#FastApi с очисткой рекомендации и ручкой(endpoint)

import logging
import re
from typing import Dict, Any, List
from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel, Field
from crawler import fetch_page
from analyzer import analyze_html
from ai_agent import generate_audit

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="AI-Agent WEB-Parsing")

class AuditResponse(BaseModel):
    audit: str = Field(..., title="Полный SEO аудит")
    recommendations: str = Field(..., title="Текст рекомендаций") 
    token_usage: Dict[str, Any] = Field(..., title="Статистика токенов")

def extract_single_text_recommendations(text: str) -> str:
    collected = []
   
    junk_pattern = re.compile(r'[*#`_~-]') 
  
    number_pattern = re.compile(r'^\s*\d+\.\s*')

    lines = text.splitlines()
    in_block = False

    for line in lines:
        line_strip = line.strip()
        
     
        if "рекомендации" in line_strip.lower():
            in_block = True
            continue
            
        if in_block:
            
            if line_strip.startswith("## ") and len(collected) > 0:
                break
            
            clean = junk_pattern.sub('', line_strip)
            clean = number_pattern.sub('', clean).strip()
            
            if len(clean) > 5:
                collected.append(clean)
    

    if not collected:
        for line in lines:
            clean = junk_pattern.sub('', line).strip()
            if len(clean) > 20:
                collected.append(clean)

 
    return " ".join(collected)

@app.post("/seo-audit", response_model=AuditResponse)
async def seo_audit(url: str = Form(..., description="URL страницы")):
    try:
        html = fetch_page(url)
        metrics = analyze_html(html)
        audit_text, usage = generate_audit(metrics)

        
        clean_recommendations = extract_single_text_recommendations(audit_text)

        return AuditResponse(
            audit=audit_text,
            recommendations=clean_recommendations,
            token_usage=usage or {}
        )
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
