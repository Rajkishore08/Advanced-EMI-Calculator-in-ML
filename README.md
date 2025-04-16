# Advanced EMI Calculator with Feasibility Detection in ML

The **Advanced EMI Calculator** is a machine learning-driven tool that calculates Equated Monthly Installments (EMIs) for loans while assessing the feasibility of a loan based on credit score, loan amount, tenure, and market trends. It helps users understand their loan repayment capacity and make informed financial decisions.

## Features
- **EMI Calculation**: Automatically calculates the EMI based on user input (loan amount, tenure, interest rate).
- **Loan Feasibility Detection**: Uses machine learning models (Scikit-learn) to predict the feasibility of loan approval based on the user's credit score, loan amount, tenure, and market trends.
- **User-Friendly Interface**: Built with React.js for a dynamic and responsive frontend, allowing users to input data easily and get instant feedback.
- **Responsive Design**: Optimized for both desktop and mobile devices to ensure a seamless experience across platforms.

## Tech Stack
- **Frontend**: React.js, HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Machine Learning**: Scikit-learn (Python)
- **Database**: None (Local state management via React)
- **API**: RESTful API for communication between frontend and backend
- **Styling**: Custom CSS for layout and design

## Setup Instructions

### Prerequisites
- **Node.js** (for React frontend)
- **Python 3.x** (for Flask backend)
- **pip** (for installing Python packages)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/advanced-emi-calculator.git
cd advanced-emi-calculator
```
### 2. Install Backend Dependencies
Navigate to the backend folder and install the required Python packages:
```bash
cd backend
pip install -r requirements.txt
```
### 3. Install Frontend Dependencies
Navigate to the frontend folder and install the required npm packages:
```bash
cd frontend
npm install
```
### 4. Running the Application
Backend
Start the Flask backend:
```bash
cd backend
python app.py
```
Frontend
Start the React development server:
```bash
cd frontend
npm start
```
The frontend will be available at http://localhost:3000 and the backend at http://localhost:5000.

### 5. Machine Learning Model
The machine learning model is built using Scikit-learn and is integrated into the Flask backend. It predicts loan feasibility based on input features (credit score, loan amount, tenure, and market trends). The model is trained using historical data to provide accurate predictions.

### Usage
Open the application in a browser.

Input the loan details such as loan amount, tenure, and credit score.

The EMI and loan feasibility status will be calculated and displayed.

The tool provides a prediction on whether the loan is feasible based on the input data and market trends.
