import React, { useState } from 'react';
import axios from 'axios';
import 'chart.js/auto';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

const App = () => {
    const [cibil, setCibil] = useState('');
    const [income, setIncome] = useState('');
    const [expense, setExpense] = useState('');
    const [loanAmount, setLoanAmount] = useState('');
    const [tenureYears, setTenureYears] = useState('');
    const [interestRate, setInterestRate] = useState('');
    const [emi, setEmi] = useState(null);
    const [totalRepayment, setTotalRepayment] = useState(null);
    const [totalInterest, setTotalInterest] = useState(null);
    const [feasibility, setFeasibility] = useState(null);
    const [message, setMessage] = useState('');
    const [suggestions, setSuggestions] = useState([]); 
    const [graphData, setGraphData] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleFeasibilityCheck = async (e) => {
        e.preventDefault();
        if (!isValidInputs()) return; // Check input validity

        try {
            const response = await axios.post('http://localhost:5000/api/predict-feasibility', {
                cibil: parseFloat(cibil),
                income: parseFloat(income),
                expense: parseFloat(expense),
                loanAmount: parseFloat(loanAmount),
            });
            setFeasibility(response.data.feasible);
            setMessage(response.data.message);
            setSuggestions(response.data.suggestions || []); // Update suggestions here
        } catch (error) {
            console.error('Feasibility Check Error:', error);
            setMessage('An error occurred while checking feasibility. Please try again.');
        }
    };

    const handleEmiCalculation = async (e) => {
        e.preventDefault();
        if (!isValidInputs()) return; // Check input validity

        try {
            const response = await axios.post('http://localhost:5000/api/calculate-emi', {
                loanAmount: parseFloat(loanAmount),
                tenureYears: parseFloat(tenureYears),
                interest: interestRate ? parseFloat(interestRate) : 0,
            });

            setEmi(response.data.emi);
            setTotalRepayment(response.data.totalRepayment);
            setTotalInterest(response.data.totalInterest);
            setMessage(response.data.suggestion);
            setSuggestions(response.data.suggestions || []); // Update suggestions here
        } catch (error) {
            console.error('Error calculating EMI:', error);
            setMessage('Error calculating EMI. Please try again.');
        }
    };

    const fetchGraph = async () => {
        setLoading(true);
        try {
            const response = await axios.post(
                'http://localhost:5000/api/graph',
                {
                    loanAmount: parseFloat(loanAmount),
                    tenureYears: parseFloat(tenureYears),
                    interest: interestRate ? parseFloat(interestRate) : 0,
                },
                { responseType: 'blob' }
            );
            const imgSrc = URL.createObjectURL(response.data);
            setGraphData(imgSrc);
        } catch (error) {
            console.error('Error generating graph:', error);
        } finally {
            setLoading(false);
        }
    };

    const resetInputs = () => {
        setCibil('');
        setIncome('');
        setExpense('');
        setLoanAmount('');
        setTenureYears('');
        setInterestRate('');
        setEmi(null);
        setTotalRepayment(null);
        setTotalInterest(null);
        setFeasibility(null);
        setMessage('');
        setSuggestions([]); // Reset suggestions
        setGraphData(null);
    };

    const isValidInputs = () => {
        const positiveNumber = (value) => !isNaN(value) && parseFloat(value) > 0;

        if (
            !positiveNumber(cibil) || cibil < 300 || cibil > 900 ||
            !positiveNumber(income) ||
            !positiveNumber(expense) ||
            !positiveNumber(loanAmount) ||
            !positiveNumber(tenureYears) ||
            (interestRate && (!positiveNumber(interestRate) || interestRate > 100))
        ) {
            setMessage('Please fill in all fields correctly with valid positive numbers. CIBIL should be between 300-900, and interest rate (if provided) must not exceed 100%.');
            return false;
        }

        if (parseFloat(expense) >= parseFloat(income)) {
            setMessage('Monthly expenses cannot exceed or match monthly income.');
            return false;
        }

        return true;
    };

    return (
        <div className="container">
            <h1 className="mb-4">EMI Calculator</h1>

            <div className="card">
                <form onSubmit={handleFeasibilityCheck} className="row g-3">
                    <h2>Feasibility Check</h2>
                    <div className="col-md-6">
                        <label className="form-label">CIBIL Score</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={cibil} 
                            onChange={(e) => setCibil(e.target.value)} 
                            placeholder="Enter your CIBIL Score" 
                            required 
                        />
                    </div>
                    <div className="col-md-6">
                        <label className="form-label">Monthly Income</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={income} 
                            onChange={(e) => setIncome(e.target.value)} 
                            placeholder="Enter your Monthly Income" 
                            required 
                        />
                    </div>
                    <div className="col-md-6">
                        <label className="form-label">Monthly Expenses</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={expense} 
                            onChange={(e) => setExpense(e.target.value)} 
                            placeholder="Enter your Monthly Expenses" 
                            required 
                        />
                    </div>
                    <div className="col-md-6">
                        <label className="form-label">Loan Amount</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={loanAmount} 
                            onChange={(e) => setLoanAmount(e.target.value)} 
                            placeholder="Enter the Loan Amount" 
                            required 
                        />
                    </div>
                    <button type="submit" className="btn btn-primary mt-3">Check Feasibility</button>
                </form>
            </div>

            {message && <div className="alert alert-info mt-3">{message}</div>}
            {feasibility !== null && (
                <div className={`alert mt-2 ${feasibility ? 'alert-success' : 'alert-danger'}`}>
                    Feasibility: {feasibility ? 'Feasible' : 'Not Feasible'}
                </div>
            )}

            {/* Display Suggestions */}
            {suggestions.length > 0 && (
                <div className="suggestions mt-3">
                    <h3>Suggestions:</h3>
                    <ul>
                        {suggestions.map((suggestion, index) => (
                            <li key={index}>{suggestion}</li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="card mt-4">
                <form onSubmit={handleEmiCalculation} className="row g-3">
                    <h2>Calculate EMI</h2>
                    <div className="col-md-6">
                        <label className="form-label">Loan Amount</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={loanAmount} 
                            onChange={(e) => setLoanAmount(e.target.value)} 
                            placeholder="Enter the Loan Amount" 
                            required 
                        />
                    </div>
                    <div className="col-md-6">
                        <label className="form-label">Tenure (Years)</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={tenureYears} 
                            onChange={(e) => setTenureYears(e.target.value)} 
                            placeholder="Enter Tenure in Years" 
                            required 
                        />
                    </div>
                    <div className="col-md-6">
                        <label className="form-label">Interest Rate (Optional)</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={interestRate} 
                            onChange={(e) => setInterestRate(e.target.value)} 
                            placeholder="Enter Interest Rate (if any)" 
                        />
                    </div>
                    <button type="submit" className="btn btn-primary mt-3">Calculate EMI</button>
                </form>
            </div>

            {emi && (
                <div className="results mt-3">
                    <h3>EMI : ₹{emi}</h3>
                    <h3>Total Repayment: ₹{totalRepayment}</h3>
                    <h3>Total Interest: ₹{totalInterest}</h3>
                </div>
            )}

            <button className="btn btn-secondary mt-3" onClick={fetchGraph}>
                {loading ? 'Generating Graph...' : 'Generate Repayment Graph'}
            </button>

            {graphData && <img src={graphData} alt="Graph" className="mt-3" />}

            <button className="btn btn-danger mt-3" onClick={resetInputs}>Reset Inputs</button>

            {/* Insights Section */}
            <div className="insights mt-4">
                <h2>Insights on Loan Eligibility</h2>
                <p>Here are some important factors that influence your loan eligibility:</p>
                <ul>
                    <li><strong>CIBIL Score:</strong> A higher score increases your chances of approval.</li>
                    <li><strong>Income Stability:</strong> Consistent income over time improves feasibility.</li>
                    <li><strong>Debt-to-Income Ratio:</strong> Lower ratio enhances your chances of getting a loan.</li>
                    <li><strong>Loan Amount:</strong> Ensure the loan amount aligns with your repayment capacity.</li>
                    <li><strong>Market Conditions:</strong> Economic factors can affect interest rates and approvals.</li>
                    <li><strong>Lender Policies:</strong> Different lenders have varying requirements.</li>
                </ul>
            </div>
        </div>
    );
};

export default App;
