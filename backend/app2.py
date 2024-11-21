from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
import matplotlib
matplotlib.use('Agg')  # To avoid GUI issues
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

# Train and Evaluate Feasibility Model
X_feasibility = feasibility_df[['CIBILScore', 'MonthlyIncome', 'AvgMonthlyExpense', 'LoanAmount']]
y_feasibility = feasibility_df['Feasible']

X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(X_feasibility, y_feasibility, test_size=0.2, random_state=42)
feasibility_model = RandomForestClassifier().fit(X_train_f, y_train_f)

# Calculate accuracy for the feasibility model
y_pred_f = feasibility_model.predict(X_test_f)
feasibility_accuracy = accuracy_score(y_test_f, y_pred_f)

# Train and Evaluate Interest Rate Model
X_interest = interest_df[['LoanAmount', 'TenureMonths']]
y_interest = interest_df['InterestRate']

X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(X_interest, y_interest, test_size=0.2, random_state=42)
interest_model = LinearRegression().fit(X_train_i, y_train_i)

# Calculate R² score for the interest rate model
y_pred_i = interest_model.predict(X_test_i)
interest_r2_score = r2_score(y_test_i, y_pred_i)

# Helper Functions
def calculate_emi(principal, annual_rate, tenure_months):
    """Calculate EMI using the correct formula."""
    if principal <= 0 or tenure_months <= 0:
        return 0  # Return 0 EMI for invalid input

    monthly_rate = annual_rate / (12 * 100)  # Convert annual rate to monthly
    if monthly_rate == 0:
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
    interest_rate = data.get('interest')

    if loan <= 0 or tenure_years <= 0:
        return jsonify({'error': 'Invalid loan amount or tenure'}), 400

    tenure_months = int(tenure_years * 12)

    if not interest_rate or interest_rate == '':
        predicted_rate = interest_model.predict(np.array([[loan, tenure_months]]))[0]
        annual_rate = predicted_rate
    else:
        annual_rate = float(interest_rate)

    emi = calculate_emi(loan, annual_rate, tenure_months)
    total_repayment = round(emi * tenure_months, 2)
    total_interest = max(round(total_repayment - loan, 2), 0)

    return jsonify({
        'emi': emi,
        'totalRepayment': total_repayment,
        'totalInterest': total_interest,
        'predictedInterestRate': round(annual_rate, 2),
        'interestModelR2Score': round(interest_r2_score, 2),
        'suggestion': "Try reducing your loan amount or tenure to reduce overall interest."
    })

@app.route('/api/predict-feasibility', methods=['POST'])
def predict_feasibility():
    data = request.json
    cibil = data.get('cibil', 0)
    income = data.get('income', 0)
    expense = data.get('expense', 0)
    loan_amount = data.get('loanAmount', 0)

    if not (300 <= cibil <= 900):
        return jsonify({'error': 'CIBIL score must be a three-digit number between 300 and 900.'}), 400

    if expense > income:
        return jsonify({'error': 'Monthly expenses cannot exceed monthly income.'}), 400

    tenure_months = 12 * 5  # Example: 5 years tenure
    predicted_interest_rate = interest_model.predict(np.array([[loan_amount, tenure_months]]))[0]
    emi = calculate_emi(loan_amount, predicted_interest_rate, tenure_months)

    if (expense + emi) > (0.7 * income):
        feasible = False
        message = "Loan is not feasible. Expenses and EMI exceed 70% of your income."
        suggestions = ["Consider reducing the loan amount or tenure.", "Lower your expenses."]
    else:
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
        'emi': emi,
        'feasibilityModelAccuracy': round(feasibility_accuracy * 100, 2)  # Percentage accuracy
    })

def generate_dynamic_insights(emi, income, expense):
    insights = []
    if emi > 0.5 * income:
        insights.append("Your EMI is significantly high compared to your income. Consider reducing your loan amount.")
    if expense > 0.6 * income:
        insights.append("Your expenses are quite high. It's advisable to cut down on non-essential spending.")
    return insights

# Main
if __name__ == '__main__':
    app.run(debug=True)
