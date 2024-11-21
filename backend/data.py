import pandas as pd
import numpy as np

# Generate Random Data for Feasibility Model
np.random.seed(42)
num_samples = 15000

cibil_scores = np.random.randint(300, 900, num_samples)
monthly_incomes = np.random.randint(30000, 200000, num_samples)
avg_monthly_expenses = np.random.randint(10000, 120000, num_samples)
loan_amounts = np.random.randint(50000, 1000000, num_samples)
tenure_months = np.random.randint(12, 60, num_samples)  # 1-5 years

# Assume a static interest rate of 12% for EMI calculation
interest_rate = 12

# Function to Calculate EMI
def calculate_emi(principal, rate, tenure):
    monthly_rate = rate / (12 * 100)
    emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure) / (
        (1 + monthly_rate) ** tenure - 1
    )
    return emi

# Generate Feasibility Labels Based on the New Logic
feasible_labels = []
for i in range(num_samples):
    # Automatically mark infeasible if CIBIL score is below 600
    if cibil_scores[i] < 500:
        feasible = 0
    else:
        emi = calculate_emi(loan_amounts[i], interest_rate, tenure_months[i])
        total_expense = avg_monthly_expenses[i] + emi
        income_threshold = 0.7 * monthly_incomes[i]
        feasible = int(total_expense <= income_threshold)
    
    feasible_labels.append(feasible)

# Create DataFrame for Feasibility Data
feasibility_data = pd.DataFrame({
    'CIBILScore': cibil_scores,
    'MonthlyIncome': monthly_incomes,
    'AvgMonthlyExpense': avg_monthly_expenses,
    'LoanAmount': loan_amounts,
    'Feasible': feasible_labels
})

# Generate Random Data for Interest Rate Model
loan_amounts_interest = np.random.randint(50000, 1000000, num_samples)
tenure_months_interest = np.random.randint(12, 60, num_samples)
interest_rates = np.random.uniform(5, 15, num_samples)  # Interest rates between 5% and 15%

# Create DataFrame for Interest Data
interest_data = pd.DataFrame({
    'LoanAmount': loan_amounts_interest,
    'TenureMonths': tenure_months_interest,
    'InterestRate': interest_rates
})

# Save Data to Excel
with pd.ExcelWriter('loan_data.xlsx') as writer:
    feasibility_data.to_excel(writer, sheet_name='FeasibilityData', index=False)
    interest_data.to_excel(writer, sheet_name='InterestData', index=False)

print("Excel file generated successfully.")
