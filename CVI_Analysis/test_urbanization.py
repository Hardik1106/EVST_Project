"""
Test script to verify urbanization rate calculation
"""

import os
import pandas as pd
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculate_cvi_all_districts import load_data, calculate_adaptive_capacity_index

# Load data
print("Loading data...")
data = load_data()

# Test a few districts with verbose output
test_districts = ['Central Delhi', 'Faridabad', 'Gurugram', 'Alwar', 'Meerut']

for district in test_districts:
    print("\n" + "="*80)
    print(f"TESTING URBANIZATION FOR: {district}")
    print("="*80)
    
    ac_score, ac_components = calculate_adaptive_capacity_index(data, district, verbose=True)
    
    print(f"\nAdaptive Capacity Components:")
    print(f"  Income: ₹{ac_components['income']:,.0f}")
    print(f"  Urbanization Rate: {ac_components['urbanization_rate']:.2f}%")
    print(f"  AC Score: {ac_score:.4f}")
