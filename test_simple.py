"""
Simple Test Script for LexiAI Demo
Quick test without interactive menu
"""

import os
import sys

# Add the parent directory to path to import lexiai_demo
sys.path.insert(0, os.path.dirname(__file__))

from lexi_ai_demo import analyze_contract, parse_and_display_results


# Sample contract for testing
TEST_CONTRACT = """
SERVICE AGREEMENT

Company A agrees to provide data processing services to Company B.

We collect personal information including name, email, and usage data. 
We may use this information for any purpose and share it with third parties.

Company B shall be liable for all damages without limitation.

This agreement may be terminated by Company A at any time without notice.
"""

print("\n" + "="*80)
print("🧪 QUICK TEST - LexiAI Demo")
print("="*80)
print("\nTest Contract:")
print("-"*80)
print(TEST_CONTRACT)
print("-"*80)

# Run analysis
result = analyze_contract(TEST_CONTRACT)

# Display results
if result:
    parse_and_display_results(result)
else:
    print("❌ Analysis failed!")

print("\n✅ Test complete!")