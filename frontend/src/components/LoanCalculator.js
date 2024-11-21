import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import '../App.css';

const LoanCalculator = () => {
    const [cibil, setCibil] = useState('');
    const [income, setIncome] = useState('');
    const [expense, setExpense] = useState('');
    const [loanAmount, setLoanAmount] = useState('');
    const [tenure, setTenure] = useState('');
    const [interestRate, setInterestRate] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [interestInsight, setInterestInsight] = useState({}); // Initialize as an object
    const [loading, setLoading] = useState(false); // New loading state

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true); // Start loading

        if (!cibil || !income || !expense || !loanAmount || !tenure) {
            setError('Please fill in all fields');
            setLoading(false); // Stop loading
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/calculate-emi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cibil: parseFloat(cibil),
                    income: parseFloat(income),
                    expense: parseFloat(expense),
                    loanAmount: parseFloat(loanAmount),
                    tenureYears: parseFloat(tenure),
                    interest_rate: interestRate ? parseFloat(interestRate) : null,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                setResult(data);
                setInterestInsight(data.interestInsight || {}); // Safely set to an empty object if undefined
            } else {
                setError(data.error || 'An error occurred');
            }
        } catch (err) {
            setError('Failed to fetch data');
        } finally {
            setLoading(false); // Stop loading
        }
    };

    useEffect(() => {
        const fetchInterestInsight = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/interest-insight');
                const data = await response.json();
                setInterestInsight(data); // Set the fetched insights
            } catch (err) {
                console.error('Error fetching interest insight:', err);
            }
        };

        fetchInterestInsight();
    }, []);

    return (
        <Card className="p-4 m-3 shadow">
            <h2 className="text-center mb-4">Loan EMI Calculator</h2>
            <Form onSubmit={handleSubmit}>
                <Form.Group controlId="formCibil">
                    <Form.Label>CIBIL Score</Form.Label>
                    <Form.Control
                        type="number"
                        value={cibil}
                        onChange={(e) => setCibil(e.target.value)}
                        required
                    />
                </Form.Group>

                <Form.Group controlId="formIncome">
                    <Form.Label>Monthly Income</Form.Label>
                    <Form.Control
                        type="number"
                        value={income}
                        onChange={(e) => setIncome(e.target.value)}
                        required
                    />
                </Form.Group>

                <Form.Group controlId="formExpense">
                    <Form.Label>Monthly Expense</Form.Label>
                    <Form.Control
                        type="number"
                        value={expense}
                        onChange={(e) => setExpense(e.target.value)}
                        required
                    />
                </Form.Group>

                <Form.Group controlId="formLoanAmount">
                    <Form.Label>Loan Amount</Form.Label>
                    <Form.Control
                        type="number"
                        value={loanAmount}
                        onChange={(e) => setLoanAmount(e.target.value)}
                        required
                    />
                </Form.Group>

                <Form.Group controlId="formTenure">
                    <Form.Label>Tenure (Years)</Form.Label>
                    <Form.Control
                        type="number"
                        value={tenure}
                        onChange={(e) => setTenure(e.target.value)}
                        required
                    />
                </Form.Group>

                <Form.Group controlId="formInterestRate">
                    <Form.Label>Interest Rate (optional)</Form.Label>
                    <Form.Control
                        type="number"
                        value={interestRate}
                        onChange={(e) => setInterestRate(e.target.value)}
                    />
                </Form.Group>

                <Button variant="primary" type="submit" className="mt-3" disabled={loading}>
                    {loading ? <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> : 'Calculate'}
                </Button>
            </Form>

            {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            {result && (
                <div className="results mt-4">
                    <h5>Results:</h5>
                    <p><strong>EMI:</strong> ₹{result.emi.toFixed(2)}</p>
                    <p><strong>Total Repayment:</strong> ₹{result.totalRepayment.toFixed(2)}</p>
                    <p><strong>Total Interest:</strong> ₹{result.totalInterest.toFixed(2)}</p>
                    <p><strong>Feasibility:</strong> {result.feasible ? 'Yes' : 'No'}</p>
                    {result.feasible === false && result.feasibilityInsights && (
                        <div>
                            <h6>Feasibility Insights:</h6>
                            <ul>
                                {result.feasibilityInsights.map((insight, index) => (
                                    <li key={index}>{insight}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {interestInsight && (
                <div className="mt-4">
                    <h5>Interest Rate Insights:</h5>
                    <p>{interestInsight.description || 'No description available.'}</p>
                    <ul>
                        {Array.isArray(interestInsight.factors) && interestInsight.factors.length > 0 ? (
                            interestInsight.factors.map((factor, index) => (
                                <li key={index}>{factor}</li>
                            ))
                        ) : (
                            <li>No insights available.</li> // If there are no factors, display this
                        )}
                    </ul>
                </div>
            )}
        </Card>
    );
};

export default LoanCalculator;
