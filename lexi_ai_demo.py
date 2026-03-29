"""
LexiAI - Quick Demo Version
Legal Contract Risk Analysis using Hugging Face LLM
"""

import os
import requests
import json
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"   # choose any free chat model


# Get HF token from environment variable
# Set this before running: export HF_API_TOKEN="your_token_here"
# ============================================================================
# HARDCODED HUGGING FACE TOKEN  (NO ENVIRONMENT NEEDED)
# ============================================================================

# ❗ IMPORTANT: Replace YOUR_TOKEN_HERE with your real HF token.
# Keep the quotes exactly as shown.

import os
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

if HF_API_TOKEN.strip() == "" :
    print("❌ ERROR: Hugging Face API token is not set.")
    sys.exit(1)


# ============================================================================
# HARDCODED RULES & NORMS
# ============================================================================

RULES = [
    {
        "id": "PRIVACY_CONSENT",
        "area": "data_privacy",
        "severity": "High",
        "description": "If contract collects or processes personal data, it should mention consent, purpose, and user rights."
    },
    {
        "id": "THIRD_PARTY_SHARING",
        "area": "data_privacy",
        "severity": "High",
        "description": "If contract allows data sharing with third parties, it should clearly mention who, why, and what safeguards are applied."
    },
    {
        "id": "LIMITATION_OF_LIABILITY",
        "area": "liability",
        "severity": "High",
        "description": "Contract should include reasonable limitation of liability for both parties and should avoid unlimited liability for ordinary breaches."
    },
    {
        "id": "TERMINATION_NOTICE",
        "area": "termination",
        "severity": "Medium",
        "description": "Termination clause should clearly state grounds and reasonable notice period for each party."
    },
    {
        "id": "GOVERNING_LAW",
        "area": "governing_law",
        "severity": "Medium",
        "description": "Contract should mention applicable governing law (jurisdiction)."
    }
]

# ============================================================================
# PROMPT TEMPLATE
# ============================================================================

def build_analysis_prompt(contract_text):
    """Build the complete prompt for the LLM with rules and contract text"""
    
    rules_text = "\n\n".join([
        f"[id: {r['id']}, area: {r['area']}, severity: {r['severity']}]\n{r['description']}"
        for r in RULES
    ])
    
    prompt = f"""You are LexiAI, a legal contract risk assistant.
You will receive:
1. A list of legal/compliance rules.
2. A contract or clause text.

Your job:
- Identify what types of clauses are present (e.g., data privacy, termination, liability, governing law).
- Check the contract text against each rule.
- For every rule, say:
  * rule_id
  * status: "compliant" / "partially_compliant" / "non_compliant" / "not_applicable"
  * severity: use the severity from the rule
  * short_explanation: 1-3 lines in simple English
  * suggested_fix: if non_compliant or partially_compliant, give a safer rewrite. Otherwise "N/A"

RULES:

{rules_text}

CONTRACT TEXT:
\"\"\"
{contract_text}
\"\"\"

Now analyze and respond ONLY in the following JSON format (no extra text):

{{
  "clause_types_detected": ["list of clause types you found"],
  "overall_comment": "brief summary of contract's risk level",
  "rules_analysis": [
    {{
      "rule_id": "RULE_ID",
      "status": "compliant/partially_compliant/non_compliant/not_applicable",
      "severity": "High/Medium/Low",
      "short_explanation": "your explanation here",
      "suggested_fix": "your suggestion or N/A"
    }}
  ]
}}"""
    
    return prompt

# ============================================================================
# HUGGING FACE API CALL
# ============================================================================

def analyze_contract(contract_text):
    """Send contract to HF Chat Completions API"""

    prompt = build_analysis_prompt(contract_text)

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.3
    }

    print("\n🔄 Analyzing contract with LexiAI...")
    print("   (This may take 10-30 seconds)\n")

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"❌ Error calling Hugging Face API: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return None


# ============================================================================
# RESULT PARSING & DISPLAY
# ============================================================================

def parse_and_display_results(raw_response):
    """Parse the LLM response and display formatted results"""

    if not raw_response:
        print("❌ No response received from API")
        return

    # raw_response is now already a clean JSON string returned by the model
    try:
        analysis = json.loads(raw_response)
    except Exception:
        print("⚠️ Could not parse JSON. Raw response:")
        print(raw_response)
        return

    # Display results
    print("=" * 80)
    print("📊 LEXIAI CONTRACT RISK ANALYSIS REPORT")
    print("=" * 80)

    # Clause types
    clause_types = analysis.get("clause_types_detected", [])
    print(f"\n📋 Clause Types Detected: {', '.join(clause_types) if clause_types else 'None specified'}")

    # Overall comment
    overall = analysis.get("overall_comment", "N/A")
    print(f"\n💬 Overall Assessment:\n   {overall}")

    # Calculate risk level
    rules_analysis = analysis.get("rules_analysis", [])
    high_severity_issues = sum(
        1 for r in rules_analysis 
        if r.get('severity') == 'High' 
        and r.get('status') in ['non_compliant', 'partially_compliant']
    )

    if high_severity_issues >= 2:
        risk_level = "🔴 HIGH RISK"
    elif high_severity_issues == 1:
        risk_level = "🟡 MEDIUM RISK"
    else:
        risk_level = "🟢 LOW RISK"

    print(f"\n⚠️  Overall Risk Level: {risk_level}")
    print(f"   (Found {high_severity_issues} high-severity issues)\n")

    # Rules analysis
    print("=" * 80)
    print("🔍 DETAILED RULE-BY-RULE ANALYSIS")
    print("=" * 80)

    for i, rule in enumerate(rules_analysis, 1):
        rule_id = rule.get('rule_id', 'Unknown')
        status = rule.get('status', 'unknown')
        severity = rule.get('severity', 'Unknown')
        explanation = rule.get('short_explanation', 'No explanation provided')
        suggested_fix = rule.get('suggested_fix', 'N/A')

        status_emoji = {
            'compliant': '✅',
            'partially_compliant': '⚠️',
            'non_compliant': '❌',
            'not_applicable': '➖'
        }.get(status, '❓')

        print(f"\n{i}. {status_emoji} {rule_id}")
        print(f"   Status: {status.upper().replace('_', ' ')}")
        print(f"   Severity: {severity}")
        print(f"   Explanation: {explanation}")

        if suggested_fix and suggested_fix != "N/A":
            print(f"   💡 Suggested Fix:\n      {suggested_fix}")

    print("\n" + "=" * 80)
    print("✅ Analysis Complete")
    print("=" * 80)


# ============================================================================
# SAMPLE CONTRACTS FOR DEMO
# ============================================================================

SAMPLE_CONTRACTS = {
    "1": {
        "name": "Good NDA (Mostly Compliant)",
        "text": """
NON-DISCLOSURE AGREEMENT

This Agreement is made between Company A and Company B.

DATA PRIVACY: Any personal data collected will be processed with explicit consent, 
for the purpose of fulfilling this agreement, and users have the right to access, 
modify, or delete their data at any time.

LIABILITY: Each party's liability under this Agreement shall be limited to direct 
damages not exceeding $50,000 for ordinary breaches. Neither party shall be liable 
for indirect, incidental, or consequential damages.

TERMINATION: Either party may terminate this Agreement with 30 days written notice. 
Upon termination, all confidential information must be returned or destroyed.

GOVERNING LAW: This Agreement shall be governed by the laws of the State of California, USA.
"""
    },
    "2": {
        "name": "Risky Contract (Multiple Issues)",
        "text": """
SERVICE AGREEMENT

Company A agrees to provide services to Company B.

We may collect your personal information and use it as we see fit. We may share 
your data with our partners and affiliates without restriction.

Company B agrees to unlimited liability for any and all damages, losses, or 
claims arising from this agreement, with no cap or limitation.

This agreement continues indefinitely and can be terminated by Company A at any time 
without notice.
"""
    },
    "3": {
        "name": "Privacy Policy Fragment (Partial Compliance)",
        "text": """
PRIVACY POLICY

We collect personal information including name, email, phone number, and location data 
when you use our services. This information is used to provide and improve our services.

We may share your information with third-party service providers who help us operate 
our business, including analytics providers, marketing partners, and cloud hosting services.

We reserve the right to modify this policy at any time. Your continued use of our services 
constitutes acceptance of any changes.

This policy is governed by the laws of India.
"""
    }
}

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def display_menu():
    """Display sample contract options"""
    print("\n" + "=" * 80)
    print("🤖 LEXIAI - Legal Contract Risk Analysis Demo")
    print("=" * 80)
    print("\nChoose an option:")
    print("\n1. Good NDA (Mostly Compliant)")
    print("2. Risky Contract (Multiple Issues)")
    print("3. Privacy Policy Fragment (Partial Compliance)")
    print("4. Paste your own contract text")
    print("5. Exit")
    print("\n" + "-" * 80)

def get_contract_input():
    """Get contract text from user"""
    display_menu()
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice in ["1", "2", "3"]:
        sample = SAMPLE_CONTRACTS[choice]
        print(f"\n✅ Selected: {sample['name']}")
        print(f"\nContract Preview:")
        print("-" * 80)
        print(sample['text'][:300] + "..." if len(sample['text']) > 300 else sample['text'])
        print("-" * 80)
        return sample['text']
    
    elif choice == "4":
        print("\n📝 Paste your contract text (type 'END' on a new line when done):")
        print("-" * 80)
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            except EOFError:
                break
        return "\n".join(lines)
    
    elif choice == "5":
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice. Please try again.")
        return get_contract_input()

def main():
    """Main program loop"""
    print("\n🚀 Starting LexiAI Demo...")
    print(f"📡 Using Model: {MODEL_ID}")
    
    while True:
        contract_text = get_contract_input()
        
        if not contract_text or not contract_text.strip():
            print("\n❌ No contract text provided. Please try again.")
            continue
        
        # Analyze the contract
        result = analyze_contract(contract_text)
        
        # Display results
        if result:
            parse_and_display_results(result)
        
        # Ask to continue
        print("\n" + "=" * 80)
        again = input("\n🔄 Analyze another contract? (y/n): ").strip().lower()
        if again != 'y':
            print("\n✅ Thank you for using LexiAI!")
            print("💡 Remember: This is an MVP demo. Full system will include:")
            print("   • Larger rules knowledge base (DPDP, GDPR, Contract law)")
            print("   • Vector DB for retrieval")
            print("   • Document chunking & indexing")
            print("   • Web UI integration")
            print("\n👋 Goodbye!\n")
            break

if __name__ == "__main__":
    main()