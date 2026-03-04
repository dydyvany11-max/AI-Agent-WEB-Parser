import logging
import re
from typing import Dict, Any, List
from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel, Field
from crawler import fetch_page
from analyzer import analyze_html
from ai_agent import generate_audit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="AI-Agent WEB-Parsing")

class AuditResponse(BaseModel):
    audit: str = Field(..., title="Полный SEO аудит")
    recommendations: List[str] = Field(..., title="Список рекомендаций")
    token_usage: Dict[str, Any] = Field(..., title="Статистика токенов")

def extract_clean_recommendations(text: str) -> List[str]:
   
    recommendations = []
    lines = text.splitlines()
    in_block = False
    
    # Регулярка для удаления символов
    marker_pattern = re.compile(r'^(\s*[-*>]|\d+\.)\s*')

    for line in lines:
        line_strip = line.strip()
        
        if line_strip.startswith("###") and "рекомендации" in line_strip.lower():
            in_block = True
            continue
        
       
        if in_block and line_strip.startswith("---"):
            break
            
        if in_block:
            if not line_strip or line_strip.startswith("#"):
                continue
            
            clean_line = marker_pattern.sub('', line_strip)
            clean_line = clean_line.replace("**", "").strip()
            
            if len(clean_line) > 5:
                recommendations.append(clean_line)
                
    return recommendations

@app.post("/seo-audit", response_model=AuditResponse)
async def seo_audit(
    url: str = Form(..., description="Введите URL страницы для SEO аудита")
):
   
    try:
        html = fetch_page(url)
        
      
        metrics = analyze_html(html)

        # Генерируем ПОЛНЫЙ отчет от AI агента
        audit_text, usage = generate_audit(metrics)

        recommendations = extract_clean_recommendations(audit_text)

        return AuditResponse(
            audit=audit_text,  
            recommendations=recommendations,
            token_usage=usage or {}
        )

    except Exception as e:
        logging.error(f"Ошибка при SEO аудите: {e}")
        raise HTTPException(status_code=500, detail=str(e))