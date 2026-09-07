import json
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from app.core.config import settings
from fastapi import HTTPException
from google import genai

class StructuredQuote(BaseModel):
    supplier_name: Optional[str] = None
    material: Optional[str] = None
    quoted_quantity: Optional[float] = None
    unit_price: float = Field(..., description="The quoted price per unit")
    moq: Optional[float] = Field(None, description="Minimum Order Quantity")
    lead_time_days: Optional[int] = Field(None, description="Lead time in days")
    delivery_date: Optional[str] = Field(None, description="Expected delivery date")
    validity_days: Optional[int] = Field(None, description="How long the quote is valid for")
    payment_terms: Optional[str] = None
    manufacturer_part_number: Optional[str] = None

def extract_quote_from_email(raw_text: str, material_context: dict) -> StructuredQuote:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    system_prompt = (
        "You are an AI assistant that extracts supplier quotation details from emails. "
        "Return ONLY valid JSON matching this schema, no prose, no markdown fences.\n"
        "Schema:\n"
        "{\n"
        '  "supplier_name": "string",\n'
        '  "material": "string",\n'
        '  "quoted_quantity": "number",\n'
        '  "unit_price": "number",\n'
        '  "moq": "number",\n'
        '  "lead_time_days": "integer",\n'
        '  "delivery_date": "string",\n'
        '  "validity_days": "integer",\n'
        '  "payment_terms": "string",\n'
        '  "manufacturer_part_number": "string"\n'
        "}\n"
    )
    
    prompt = f"Extract quote details from this email text:\n{raw_text}\n\nContext for material requested: {json.dumps(material_context)}"
    
    def _call_llm(p_system: str, p_user: str) -> str:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=p_user,
            config=genai.types.GenerateContentConfig(
                system_instruction=p_system,
                max_output_tokens=1024
            )
        )
        return response.text.strip()
        
    # Attempt 1
    raw_response = _call_llm(system_prompt, prompt)
    
    try:
        # Strip potential markdown fences just in case
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        data = json.loads(raw_response.strip())
        return StructuredQuote(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        # Retry once with stricter prompt
        stricter_prompt = system_prompt + "\n\nCRITICAL: YOUR PREVIOUS OUTPUT FAILED PARSING. DO NOT OUTPUT ANYTHING EXCEPT RAW JSON."
        raw_response = _call_llm(stricter_prompt, prompt)
        try:
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
            data = json.loads(raw_response.strip())
            return StructuredQuote(**data)
        except Exception as retry_e:
            raise HTTPException(status_code=400, detail=f"Failed to parse quote from email after retry: {str(retry_e)}")

def generate_recommendation_explanation(comparison_result: dict) -> str:
    """
    Takes the output of the deterministic recommendation engine and asks the LLM
    to generate a short natural-language justification.
    """
    if not settings.GEMINI_API_KEY:
        return "Recommendation generated automatically based on deterministic scoring (LLM disabled)."
        
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    system_prompt = (
        "You are an expert procurement assistant. You are given a deterministic comparison of "
        "multiple supplier quotes. Your job is to output a single, short paragraph (2-3 sentences max) "
        "explaining why the top-ranked supplier was chosen over the others, referencing price, delivery, "
        "MOQ constraints, and reliability."
    )
    
    prompt = f"Comparison Data:\n{json.dumps(comparison_result, indent=2)}\n\nPlease provide a short justification for the top choice."
    
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=200
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"Recommendation generated successfully. (LLM explanation failed: {str(e)})"

def extract_delivery_from_email(raw_text: str) -> dict:
    """
    Uses LLM to extract confirmed quantity and delivery dates from an email.
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="LLM extraction requires GEMINI_API_KEY")
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    system_prompt = (
        "You are an AI assistant parsing a supplier email confirming a purchase order. "
        "Extract the confirmed quantity and delivery dates. "
        "Return ONLY a JSON object with this exact schema (no markdown, no prose):\n"
        "{\n"
        "  \"confirmed_quantity\": float,\n"
        "  \"first_delivery_date\": \"YYYY-MM-DD\",\n"
        "  \"final_delivery_date\": \"YYYY-MM-DD\" (or null if all in one shipment)\n"
        "}"
    )
    
    prompt = f"Email Text:\n{raw_text}"
    
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=500
            )
        )
        
        raw_json = response.text.strip()
        data = json.loads(raw_json)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse delivery from email: {str(e)}")

