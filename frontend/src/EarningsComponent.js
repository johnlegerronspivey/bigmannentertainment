import React, { useState, useEffect } from 'react';
import './Earnings.css';

const EarningsComponent = () => {
    const [earnings, setEarnings] = useState(null);
    const [revenueShares, setRevenueShares] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [payoutAmount, setPayoutAmount] = useState('');
    const [payoutMethod, setPayoutMethod] = useState('bank_transfer');
    const [payoutLoading, setPayoutLoading] = useState(false);
    const [payoutSuccess, setPayoutSuccess] = useState('');

    const backendUrl = process.env.REACT_APP_BACKEND_URL;

    useEffect(() => {
        fetchEarnings();
    }, []);

    const fetchEarnings = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/payments/earnings`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setEarnings(data.earnings);
                setRevenueShares(data.recent_revenue_shares || []);
            } else {
                setError('Failed to fetch earnings data');
            }
        } catch (error) {
            console.error('Error fetching earnings:', error);
            setError('Error loading earnings data');
        } finally {
            setLoading(false);
        }
    };

    const requestPayout = async () => {
        if (!payoutAmount || parseFloat(payoutAmount) <= 0) {
            setError('Please enter a valid payout amount');
            return;
        }

        if (!earnings || parseFloat(payoutAmount) > earnings.available_balance) {
            setError('Payout amount exceeds available balance');
            return;
        }

        setPayoutLoading(true);
        setError('');
        setPayoutSuccess('');

        try {
            const token = localStorage.getItem('token');
            const formData = new FormData();
            formData.append('amount', payoutAmount);
            formData.append('payout_method', payoutMethod);

            const response = await fetch(`${backendUrl}/api/payments/payout/request`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                setPayoutSuccess(data.message);
                setPayoutAmount('');
                // Refresh earnings data
                fetchEarnings();
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to request payout');
            }
        } catch (error) {
            console.error('Error requesting payout:', error);
            setError('Error processing payout request');
        } finally {
            setPayoutLoading(false);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount || 0);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="earnings-container">
                <div className="loading-spinner">Loading earnings data...</div>
            </div>
        );
    }

    return (
        <div className="earnings-container">
            <div className="earnings-header">
                <img 
                    src="/big-mann-logo.png" 
                    alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
                    className="earnings-logo"
                />
                <h2>💰 Creator Earnings</h2>
                <p>Track your revenue and manage payouts</p>
            </div>

            {/* Earnings Summary */}
            <div className="earnings-summary">
                <div className="summary-card">
                    <div className="summary-icon">💰</div>
                    <div className="summary-content">
                        <h3>Total Earnings</h3>
                        <div className="summary-amount">{formatCurrency(earnings?.total_earnings)}</div>
                    </div>
                </div>

                <div className="summary-card">
                    <div className="summary-icon">✅</div>
                    <div className="summary-content">
                        <h3>Available Balance</h3>
                        <div className="summary-amount available">{formatCurrency(earnings?.available_balance)}</div>
                    </div>
                </div>

                <div className="summary-card">
                    <div className="summary-icon">⏳</div>
                    <div className="summary-content">
                        <h3>Pending Balance</h3>
                        <div className="summary-amount pending">{formatCurrency(earnings?.pending_balance)}</div>
                    </div>
                </div>

                <div className="summary-card">
                    <div className="summary-icon">💸</div>
                    <div className="summary-content">
                        <h3>Total Paid Out</h3>
                        <div className="summary-amount">{formatCurrency(earnings?.total_paid_out)}</div>
                    </div>
                </div>
            </div>

            {/* Payout Request Section */}
            <div className="payout-section">
                <h3>Request Payout</h3>
                <p>Minimum payout amount: $10.00</p>
                
                <div className="payout-form">
                    <div className="form-group">
                        <label htmlFor="payoutAmount">Payout Amount</label>
                        <div className="amount-input-container">
                            <span className="currency-symbol">$</span>
                            <input
                                id="payoutAmount"
                                type="number"
                                min="10"
                                step="0.01"
                                placeholder="Enter amount"
                                value={payoutAmount}
                                onChange={(e) => setPayoutAmount(e.target.value)}
                                className="amount-input"
                                max={earnings?.available_balance || 0}
                            />
                            <span className="currency-code">USD</span>
                        </div>
                        <div className="balance-info">
                            Available: {formatCurrency(earnings?.available_balance)}
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="payoutMethod">Payout Method</label>
                        <select
                            id="payoutMethod"
                            value={payoutMethod}
                            onChange={(e) => setPayoutMethod(e.target.value)}
                            className="payout-method-select"
                        >
                            <option value="bank_transfer">Bank Transfer</option>
                            <option value="paypal">PayPal</option>
                            <option value="venmo">Venmo</option>
                            <option value="cashapp">Cash App</option>
                        </select>
                    </div>

                    {error && <div className="error-message">{error}</div>}
                    {payoutSuccess && <div className="success-message">{payoutSuccess}</div>}

                    <button
                        onClick={requestPayout}
                        disabled={payoutLoading || !payoutAmount || parseFloat(payoutAmount) < 10}
                        className="payout-button"
                    >
                        {payoutLoading ? 'Processing...' : 'Request Payout'}
                    </button>
                </div>
            </div>

            {/* Revenue Shares */}
            {revenueShares.length > 0 && (
                <div className="revenue-shares-section">
                    <h3>Recent Revenue Shares</h3>
                    <div className="revenue-shares-list">
                        {revenueShares.map((share) => (
                            <div key={share.id} className="revenue-share-item">
                                <div className="share-info">
                                    <div className="share-amount">
                                        {formatCurrency(share.creator_amount)}
                                    </div>
                                    <div className="share-details">
                                        <div className="share-percentage">
                                            Your share: {share.creator_percentage}%
                                        </div>
                                        <div className="share-total">
                                            Total transaction: {formatCurrency(share.total_amount)}
                                        </div>
                                    </div>
                                </div>
                                <div className="share-meta">
                                    <div className={`share-status ${share.status}`}>
                                        {share.status}
                                    </div>
                                    <div className="share-date">
                                        {formatDate(share.created_at)}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Earnings Info */}
            <div className="earnings-info">
                <h3>How Revenue Sharing Works</h3>
                <div className="info-grid">
                    <div className="info-item">
                        <div className="info-icon">🎵</div>
                        <div className="info-content">
                            <h4>Content Sales</h4>
                            <p>Earn 85% revenue share from your content sales and distributions</p>
                        </div>
                    </div>
                    <div className="info-item">
                        <div className="info-icon">💳</div>
                        <div className="info-content">
                            <h4>Automatic Tracking</h4>
                            <p>All revenue is automatically tracked and allocated to your account</p>
                        </div>
                    </div>
                    <div className="info-item">
                        <div className="info-icon">📊</div>
                        <div className="info-content">
                            <h4>Transparent Reporting</h4>
                            <p>View detailed breakdowns of all your earnings and transactions</p>
                        </div>
                    </div>
                    <div className="info-item">
                        <div className="info-icon">🏦</div>
                        <div className="info-content">
                            <h4>Flexible Payouts</h4>
                            <p>Request payouts anytime with multiple payment method options</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EarningsComponent;