from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load Data and Train Models
def load_data():
    """Load training data from Excel."""
    data = pd.ExcelFile('loan_data.xlsx')
    feasibility_df = data.parse('FeasibilityData')
    interest_df = data.parse('InterestData')
    return feasibility_df, interest_df

feasibility_df, interest_df = load_data()

# Train models
X_feasibility = feasibility_df[['CIBILScore', 'MonthlyIncome', 'AvgMonthlyExpense', 'LoanAmount']]
y_feasibility = feasibility_df['Feasible']
feasibility_model = RandomForestClassifier().fit(X_feasibility, y_feasibility)

X_interest = interest_df[['LoanAmount', 'TenureMonths']]
y_interest = interest_df['InterestRate']
interest_model = LinearRegression().fit(X_interest, y_interest)

# Helper Functions
def calculate_emi(principal, annual_rate, tenure_months):
    """Calculate EMI using the correct formula."""
    if principal <= 0 or tenure_months <= 0:
        return 0  # Return 0 EMI for invalid input

    monthly_rate = annual_rate / (12 * 100)  # Convert annual rate to monthly
    if monthly_rate == 0:  # Handle 0% interest rate case
        emi = principal / tenure_months
    else:
        emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / (
            (1 + monthly_rate) ** tenure_months - 1
        )
    return round(emi, 2)

@app.route('/api/calculate-emi', methods=['POST'])
def calculate_emi_route():
    data = request.json
    loan = float(data.get('loanAmount', 0))
    tenure_years = float(data.get('tenureYears', 0))
    interest_rate = data.get('interest')  # Annual interest rate in %

    if loan <= 0 or tenure_years <= 0:
        return jsonify({'error': 'Invalid loan amount or tenure'}), 400

    tenure_months = int(tenure_years * 12)

    # Predict interest rate if not provided
    if not interest_rate or interest_rate == '':
        predicted_rate = interest_model.predict(np.array([[loan, tenure_months]]))[0]
        annual_rate = predicted_rate
    else:
        annual_rate = float(interest_rate)

    # Calculate EMI
    emi = calculate_emi(loan, annual_rate, tenure_months)

    # Calculate total repayment and total interest
    total_repayment = round(emi * tenure_months, 2)
    total_interest = max(round(total_repayment - loan, 2), 0)  # Ensure total interest is not negative

    return jsonify({
        'emi': emi,
        'totalRepayment': total_repayment,
        'totalInterest': total_interest,
        'predictedInterestRate': round(annual_rate, 2),
        'suggestion': "Try reducing your loan amount or tenure to Reduce Overall Interest"
    })

def generate_graph(loan_amount, tenure_months, emi):
    """Generate a repayment breakdown graph."""
    months = np.arange(1, tenure_months + 1)  # Array of months
    total_paid = emi * months  # Cumulative total paid over time
    interest_paid = total_paid - loan_amount  # Interest portion over time

    # Generate the plot
    plt.figure(figsize=(10, 6))
    plt.plot(months, total_paid, label='Total Repayment (Principal + Interest)', color='green', linewidth=2)
    plt.plot(months, interest_paid, label='Interest Paid', color='red', linestyle='--')
    plt.xlabel('Months')
    plt.ylabel('Amount (INR)')
    plt.title('Loan Repayment Breakdown')
    plt.legend(loc='upper left')
    plt.grid(True)

    # Save plot to BytesIO buffer
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')  # Save graph as PNG
    img.seek(0)  # Reset buffer to beginning
    plt.close()  # Close the plot to free memory
    return img

@app.route('/api/graph', methods=['POST'])
def repayment_graph():
    data = request.json
    loan_amount = float(data.get('loanAmount', 0))
    tenure_years = float(data.get('tenureYears', 0))
    interest_rate = float(data.get('interest', 0))

    if loan_amount <= 0 or tenure_years <= 0 or interest_rate < 0:
        return jsonify({'error': 'Invalid loan amount, tenure, or interest rate'}), 400

    tenure_months = int(tenure_years * 12)
    emi = calculate_emi(loan_amount, interest_rate, tenure_months)

    # Generate graph and send it as a response
    img = generate_graph(loan_amount, tenure_months, emi)
    return send_file(img, mimetype='image/png')

@app.route('/api/predict-feasibility', methods=['POST'])
def predict_feasibility():
    data = request.json
    cibil = data.get('cibil', 0)
    income = data.get('income', 0)
    expense = data.get('expense', 0)
    loan_amount = data.get('loanAmount', 0)

    # Validate CIBIL score
    if not (300 <= cibil <= 900):
        return jsonify({'error': 'CIBIL score must be a three-digit number between 300 and 900.'}), 400

    # Validate expenses
    if expense > income:
        return jsonify({'error': 'Monthly expenses cannot exceed monthly income.'}), 400

    tenure_months = 12 * 5  # Example: 5 years tenure (can be dynamic)
    predicted_interest_rate = interest_model.predict(np.array([[loan_amount, tenure_months]]))[0]
    emi = calculate_emi(loan_amount, predicted_interest_rate, tenure_months)

    # Check if (Expense + EMI) exceeds 70% of income
    if (expense + emi) > (0.7 * income):
        feasible = False
        message = "Loan is not feasible. Expenses and EMI exceed 70% of your income."
        suggestions = [
            "Consider reducing the loan amount or tenure.",
            "Lower your expenses to meet eligibility.",
        ]
    else:
        # RandomForest model prediction for additional check
        features = np.array([[cibil, income, expense, loan_amount]])
        feasible = bool(feasibility_model.predict(features)[0])
        message = "Loan is feasible!" if feasible else "Loan is not feasible."
        suggestions = [] if feasible else [
            "Improve your CIBIL score.",
            "Ensure your income exceeds your expenses by a larger margin."
        ]

    insights = generate_dynamic_insights(emi, income, expense)

    return jsonify({
        'feasible': feasible,
        'message': message,
        'suggestions': suggestions,
        'insights': insights,
        'emi': emi  
    })

def generate_dynamic_insights(emi, income, expense):
    insights = []
    if emi > 0.5 * income:
        insights.append("Your EMI is significantly high compared to your income. Consider reducing your loan amount.")
    if expense > 0.6 * income:
        insights.append("Your expenses are quite high. It's advisable to cut down on non-essential spending.")
    return insights

@app.route('/api/interest-insight', methods=['GET'])
def interest_insight():
    """Provides insights about interest rates."""
    insights = {
        "description": "Interest rates are determined by several factors including:",
        "factors": [
            "1. Credit Score: A higher CIBIL score generally leads to lower interest rates.",
            "2. Loan Amount: Larger loans may have different rates compared to smaller ones.",
            "3. Loan Tenure: Longer tenures may result in higher interest costs over time.",
            "4. Market Conditions: Economic factors and central bank policies can affect interest rates.",
            "5. Lender Policies: Different financial institutions may have varying criteria for interest rates.",
        ]
    }
    return jsonify(insights)

# Main
if __name__ == '__main__':
    app.run(debug=True)
