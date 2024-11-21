import React, { useState } from 'react';
import axiosInstance from '../axiosInstance';

const EmiForm = () => {
  const [formData, setFormData] = useState({
    loan_amount: '',
    tenure_years: '',
    interest_rate: '',
    monthly_income: '',
    monthly_expenses: '',
  });

  const [emiResult, setEmiResult] = useState(null);
  const [feasibility, setFeasibility] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const calculateEMI = async () => {
    try {
      const response = await axiosInstance.post('/calculate-emi', {
        loan_amount: parseFloat(formData.loan_amount),
        tenure_years: parseInt(formData.tenure_years),
        interest_rate: parseFloat(formData.interest_rate),
      });
      setEmiResult(response.data);
    } catch (error) {
      console.error('Error calculating EMI:', error);
    }
  };

  const checkFeasibility = async () => {
    try {
      const response = await axiosInstance.post('/predict-feasibility', {
        monthly_income: parseFloat(formData.monthly_income),
        monthly_expenses: parseFloat(formData.monthly_expenses),
        emi: emiResult.emi,
      });
      setFeasibility(response.data);
    } catch (error) {
      console.error('Error checking feasibility:', error);
    }
  };

  return (
    <div>
      <h1>EMI Calculator</h1>
      <input type="number" name="loan_amount" placeholder="Loan Amount" onChange={handleChange} />
      <input type="number" name="tenure_years" placeholder="Tenure (Years)" onChange={handleChange} />
      <input type="number" name="interest_rate" placeholder="Interest Rate (%)" onChange={handleChange} />
      <button onClick={calculateEMI}>Calculate EMI</button>

      {emiResult && (
        <div>
          <p>EMI: {emiResult.emi}</p>
          <p>Total Repayment: {emiResult.total_repayment}</p>
          <p>Total Interest: {emiResult.total_interest}</p>
        </div>
      )}

      <h2>Feasibility Check</h2>
      <input type="number" name="monthly_income" placeholder="Monthly Income" onChange={handleChange} />
      <input type="number" name="monthly_expenses" placeholder="Monthly Expenses" onChange={handleChange} />
      <button onClick={checkFeasibility}>Check Feasibility</button>

      {feasibility && <p>{feasibility.message}</p>}
    </div>
  );
};

export default EmiForm;
