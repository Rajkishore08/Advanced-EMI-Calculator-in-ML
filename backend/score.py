import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

def load_data():
    """Load data from the Excel file."""
    data = pd.ExcelFile('loan_data.xlsx')
    feasibility_df = data.parse('FeasibilityData')
    interest_df = data.parse('InterestData')
    return feasibility_df, interest_df

# Load datasets
feasibility_df, interest_df = load_data()

# ------------------------
# Feasibility Model Training
# ------------------------
print("\n--- Feasibility Model Training ---")
X_feasibility = feasibility_df[['CIBILScore', 'MonthlyIncome', 'AvgMonthlyExpense', 'LoanAmount']]
y_feasibility = feasibility_df['Feasible']

# Split the data into training and testing sets (80% train, 20% test)
X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(X_feasibility, y_feasibility, test_size=0.2, random_state=42)

# Train the RandomForest model
feasibility_model = RandomForestClassifier(random_state=42)
feasibility_model.fit(X_train_f, y_train_f)

# Make predictions and calculate accuracy
y_pred_f = feasibility_model.predict(X_test_f)
feasibility_accuracy = accuracy_score(y_test_f, y_pred_f)

print(f"Feasibility Model Accuracy: {feasibility_accuracy * 100:.2f}%")

# ------------------------
# Interest Rate Model Training
# ------------------------
print("\n--- Interest Rate Model Training ---")
X_interest = interest_df[['LoanAmount', 'TenureMonths']]
y_interest = interest_df['InterestRate']

# Split the data into training and testing sets (80% train, 20% test)
X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(X_interest, y_interest, test_size=0.2, random_state=42)

# Train the Linear Regression model
interest_model = LinearRegression()
interest_model.fit(X_train_i, y_train_i)

# Make predictions and calculate performance metrics
y_pred_i = interest_model.predict(X_test_i)
mse = mean_squared_error(y_test_i, y_pred_i)
r2 = r2_score(y_test_i, y_pred_i)

print(f"Interest Rate Model Mean Squared Error (MSE): {mse:.2f}")

# ------------------------
# Summary of Results
# ------------------------
print("\n--- Summary of Model Performance ---")
print(f"Feasibility Model Accuracy: {feasibility_accuracy * 100:.2f}%")
print(f"Interest Rate Model MSE: {mse:.2f}")

