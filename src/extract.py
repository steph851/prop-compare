#!/usr/bin/env python3
"""
Phase 6 - Step 2: Extract & normalize firm data with Claude
"""
import os
import json
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
load_dotenv('.env.local')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = Anthropic()
# Reference schema (from your FundedNext JSON)
REFERENCE_SCHEMA = {
    "firm_name": "",
    "division": "Futures",
    "last_verified": "",
    "verified_by": "Steph",
    "source_urls": [],
    "?? FIRM PROFILE": {
        "country_headquarters": "",
        "year_founded": 0,
        "ceo": "",
        "platforms_offered": [],
        "brokers": [],
        "review_score_avg": 0,
        "review_count": 0,
    },
    "?? PRICING & OFFERS": {
        "challenge_fees_usd": {},
        "monthly_fees_usd": 0,
        "commission_structure": {},
        "leverage_offered": {},
    },
    "?? CHALLENGE MODELS": [],
    "?? AGGREGATE METRICS": {}
}
def extract_with_claude(firm_data):
    """
    Use Claude to extract and normalize firm data
    """
    prompt = f"""
    You are a trading firm data extraction expert.
    I have discovered data for a trading firm. Extract and normalize it to match THIS schema EXACTLY:
    {json.dumps(REFERENCE_SCHEMA, indent=2)}
    Firm data to extract:
    {json.dumps(firm_data, indent=2)}
    IMPORTANT:
    1. Use the EXACT keys from the reference schema
    2. If data is missing, use null or empty arrays
    3. Return ONLY valid JSON, no explanations
    4. Keep all emoji prefixes in section names
    Return ONLY the JSON object.
    """
    try:
        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            messages=[
                {{"role": "user", "content": prompt}}
            ]
        )
        # Extract JSON from response
        response_text = message.content[0].text
        # Try to parse JSON
        try:
            extracted_data = json.loads(response_text)
            return extracted_data
        except json.JSONDecodeError:
            # Try to find JSON in response
            start = response_text.find('{{')
            end = response_text.rfind('}}') + 1
            if start >= 0 and end > start:
                extracted_data = json.loads(response_text[start:end])
                return extracted_data
            else:
                print('Error: Could not parse Claude response as JSON')
                print(f'Response: {{response_text}}')
                return None
    except Exception as e:
        print(f'Error calling Claude API: {{str(e)}}')
        return None
def main():
    # Read firm data from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            firm_data = json.load(f)
    else:
        firm_data = json.load(sys.stdin)
    result = extract_with_claude(firm_data)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print('{{}}')
        exit(1)
if __name__ == '__main__':
    main()
