import React, { useState, useEffect } from 'react';
import './Payment.css';
import PayPalPaymentComponent from './PayPalPaymentComponent';

const PaymentComponent = () => {
    const [packages, setPackages] = useState({});
    const [selectedPackage, setSelectedPackage] = useState('');
    const [customAmount, setCustomAmount] = useState('');
    const [paymentType, setPaymentType] = useState('package'); // package or custom
    const [paymentMethod, setPaymentMethod] = useState('stripe'); // stripe or paypal
    const [showPayPal, setShowPayPal] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [userCredits, setUserCredits] = useState(null);
    const [transactions, setTransactions] = useState([]);

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    useEffect(() => {
        fetchPaymentPackages();
        fetchUserCredits();
        fetchTransactions();
        checkReturnFromStripe();
    }, []);

    const fetchPaymentPackages = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/payments/packages`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setPackages(data.packages);
            }
        } catch (error) {
            console.error('Error fetching packages:', error);
        }
    };

    const fetchUserCredits = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/payments/user/credits`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUserCredits(data);
            }
        } catch (error) {
            console.error('Error fetching user credits:', error);
        }
    };

    const fetchTransactions = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/payments/transactions`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setTransactions(data.transactions);
            }
        } catch (error) {
            console.error('Error fetching transactions:', error);
        }
    };

    const initiatePayment = async () => {
        if (paymentType === 'package' && !selectedPackage) {
            setError('Please select a payment package');
            return;
        }

        if (paymentType === 'custom' && (!customAmount || parseFloat(customAmount) <= 0)) {
            setError('Please enter a valid amount greater than 0');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            const currentUrl = window.location.origin;
            
            const requestBody = {
                origin_url: currentUrl,
                currency: 'usd',
                quantity: 1,
                metadata: {
                    source: 'payment_component',
                    payment_type: paymentType
                }
            };

            if (paymentType === 'package') {
                requestBody.package_id = selectedPackage;
            } else {
                requestBody.amount = parseFloat(customAmount);
            }

            const response = await fetch(`${backendUrl}/api/payments/checkout/session`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create checkout session');
            }

            const data = await response.json();
            
            // Redirect to Stripe Checkout
            if (data.url) {
                window.location.href = data.url;
            } else {
                throw new Error('No checkout URL received');
            }
        } catch (error) {
            setError(error.message);
            console.error('Payment error:', error);
        } finally {
            setLoading(false);
        }
    };

    // Function to get URL parameters
    const getUrlParameter = (name) => {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(window.location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    };

    // Function to update status display
    const updateStatus = (message, type) => {
        setError(type === 'error' ? message : '');
        if (type === 'success') {
            // Refresh data after successful payment
            fetchUserCredits();
            fetchTransactions();
        }
    };

    // Function to poll payment status
    const pollPaymentStatus = async (sessionId, attempts = 0) => {
        const maxAttempts = 5;
        const pollInterval = 2000; // 2 seconds

        if (attempts >= maxAttempts) {
            updateStatus('Payment status check timed out. Please check your email for confirmation.', 'error');
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/payments/checkout/status/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to check payment status');
            }

            const data = await response.json();
            
            if (data.payment_status === 'paid') {
                updateStatus('Payment successful! Thank you for your purchase.', 'success');
                return;
            } else if (data.status === 'expired') {
                updateStatus('Payment session expired. Please try again.', 'error');
                return;
            }

            // If payment is still pending, continue polling
            setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
        } catch (error) {
            console.error('Error checking payment status:', error);
            updateStatus('Error checking payment status. Please try again.', 'error');
        }
    };

    // Function to check if we're returning from Stripe
    const checkReturnFromStripe = () => {
        const sessionId = getUrlParameter('session_id');
        if (sessionId) {
            updateStatus('Checking payment status...', 'pending');
            pollPaymentStatus(sessionId);
            
            // Clean URL
            const url = new URL(window.location);
            url.searchParams.delete('session_id');
            window.history.replaceState({}, document.title, url);
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const getPaymentAmount = () => {
        if (paymentType === 'package' && selectedPackage && packages[selectedPackage]) {
            return packages[selectedPackage].amount;
        } else if (paymentType === 'custom' && customAmount) {
            return parseFloat(customAmount);
        }
        return 0;
    };

    const getPaymentDescription = () => {
        if (paymentType === 'package' && selectedPackage && packages[selectedPackage]) {
            return `Big Mann Entertainment - ${packages[selectedPackage].name}`;
        } else if (paymentType === 'custom') {
            return `Big Mann Entertainment - Custom Payment`;
        }
        return 'Big Mann Entertainment Service';
    };

    const handlePayPalSuccess = async (paymentData) => {
        setLoading(false);
        setShowPayPal(false);
        updateStatus('PayPal payment successful! Thank you for your purchase.', 'success');
        
        // Refresh user data
        await fetchUserCredits();
        await fetchTransactions();
    };

    const handlePayPalError = (errorData) => {
        setLoading(false);
        setShowPayPal(false);
        setError(`PayPal payment failed: ${errorData.error || 'Unknown error'}`);
        updateStatus('PayPal payment failed. Please try again.', 'error');
    };

    const handlePayPalCancel = () => {
        setLoading(false);
        setShowPayPal(false);
        updateStatus('PayPal payment was cancelled.', 'info');
    };

    return (
        <div className="payment-container">
            <div className="payment-header">
                <img 
                    src="/big-mann-logo.png" 
                    alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
                    className="payment-logo"
                />
                <h2>🎵 Payment & Credits</h2>
                <p>Purchase credits and manage your Big Mann Entertainment account</p>
            </div>

            {/* User Credits Section */}
            {userCredits && (
                <div className="credits-section">
                    <h3>Your Current Credits</h3>
                    <div className="credits-grid">
                        <div className="credit-item">
                            <span className="credit-label">Upload Credits:</span>
                            <span className="credit-value">{userCredits.upload_credits || 0}</span>
                        </div>
                        <div className="credit-item">
                            <span className="credit-label">Distribution Credits:</span>
                            <span className="credit-value">{userCredits.distribution_credits || 0}</span>
                        </div>
                        <div className="credit-item">
                            <span className="credit-label">Premium Features:</span>
                            <span className={`credit-value ${userCredits.premium_features ? 'active' : 'inactive'}`}>
                                {userCredits.premium_features ? '✅ Active' : '❌ Inactive'}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Payment Type Selection */}
            <div className="payment-type-section">
                <h3>Select Payment Type</h3>
                <div className="payment-type-options">
                    <label className="payment-type-option">
                        <input
                            type="radio"
                            name="paymentType"
                            value="package"
                            checked={paymentType === 'package'}
                            onChange={(e) => setPaymentType(e.target.value)}
                        />
                        <span>Choose Package</span>
                    </label>
                    <label className="payment-type-option">
                        <input
                            type="radio"
                            name="paymentType"
                            value="custom"
                            checked={paymentType === 'custom'}
                            onChange={(e) => setPaymentType(e.target.value)}
                        />
                        <span>Custom Amount</span>
                    </label>
                </div>
            </div>

            {/* Package Selection */}
            {paymentType === 'package' && (
                <div className="packages-section">
                    <h3>Available Packages</h3>
                    <div className="packages-grid">
                        {Object.entries(packages).map(([packageId, packageInfo]) => (
                            <div
                                key={packageId}
                                className={`package-card ${selectedPackage === packageId ? 'selected' : ''}`}
                                onClick={() => setSelectedPackage(packageId)}
                            >
                                <div className="package-header">
                                    <h4>{packageInfo.name}</h4>
                                    <div className="package-price">{formatCurrency(packageInfo.amount)}</div>
                                </div>
                                <div className="package-description">
                                    {packageInfo.description}
                                </div>
                                <div className="package-features">
                                    {packageInfo.features.map((feature, index) => (
                                        <div key={index} className="feature-item">
                                            ✓ {feature}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Custom Amount */}
            {paymentType === 'custom' && (
                <div className="custom-amount-section">
                    <h3>Custom Amount</h3>
                    <div className="amount-input-container">
                        <span className="currency-symbol">$</span>
                        <input
                            type="number"
                            min="1"
                            step="0.01"
                            placeholder="Enter amount"
                            value={customAmount}
                            onChange={(e) => setCustomAmount(e.target.value)}
                            className="amount-input"
                        />
                        <span className="currency-code">USD</span>
                    </div>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {/* Payment Method Selection */}
            <div className="payment-method-section">
                <h3>Select Payment Method</h3>
                <div className="payment-method-options">
                    <label className="payment-method-option">
                        <input
                            type="radio"
                            name="paymentMethod"
                            value="stripe"
                            checked={paymentMethod === 'stripe'}
                            onChange={(e) => {
                                setPaymentMethod(e.target.value);
                                setShowPayPal(false);
                            }}
                        />
                        <div className="method-info">
                            <img 
                                src="https://stripe.com/img/v3/home/social.png" 
                                alt="Stripe" 
                                className="payment-method-logo"
                            />
                            <span>Credit/Debit Card (Stripe)</span>
                        </div>
                    </label>
                    <label className="payment-method-option">
                        <input
                            type="radio"
                            name="paymentMethod"
                            value="paypal"
                            checked={paymentMethod === 'paypal'}
                            onChange={(e) => {
                                setPaymentMethod(e.target.value);
                                setShowPayPal(false);
                            }}
                        />
                        <div className="method-info">
                            <img 
                                src="https://www.paypalobjects.com/webstatic/mktg/Logo/pp-logo-100px.png" 
                                alt="PayPal" 
                                className="payment-method-logo"
                            />
                            <span>PayPal</span>
                        </div>
                    </label>
                </div>
            </div>

            {/* Payment Processing */}
            {paymentMethod === 'stripe' && (
                <div className="payment-button-section">
                    <button
                        onClick={initiatePayment}
                        disabled={loading || (paymentType === 'package' && !selectedPackage) || (paymentType === 'custom' && !customAmount)}
                        className="payment-button stripe-button"
                    >
                        {loading ? 'Processing...' : 'Pay with Stripe'}
                    </button>
                </div>
            )}

            {paymentMethod === 'paypal' && (
                <div className="payment-button-section">
                    <button
                        onClick={() => setShowPayPal(true)}
                        disabled={loading || (paymentType === 'package' && !selectedPackage) || (paymentType === 'custom' && !customAmount)}
                        className="payment-button paypal-button"
                    >
                        Pay with PayPal
                    </button>

                    {showPayPal && (
                        <div className="paypal-integration">
                            <PayPalPaymentComponent
                                amount={getPaymentAmount()}
                                description={getPaymentDescription()}
                                onSuccess={handlePayPalSuccess}
                                onError={handlePayPalError}
                                onCancel={handlePayPalCancel}
                            />
                        </div>
                    )}
                </div>
            )}

            {/* Transaction History */}
            {transactions.length > 0 && (
                <div className="transactions-section">
                    <h3>Recent Transactions</h3>
                    <div className="transactions-list">
                        {transactions.slice(0, 5).map((transaction) => (
                            <div key={transaction.id} className="transaction-item">
                                <div className="transaction-info">
                                    <div className="transaction-package">
                                        {transaction.metadata?.package_name || 'Custom Payment'}
                                    </div>
                                    <div className="transaction-amount">
                                        {formatCurrency(transaction.amount)}
                                    </div>
                                </div>
                                <div className="transaction-meta">
                                    <div className={`transaction-status ${transaction.status}`}>
                                        {transaction.status}
                                    </div>
                                    <div className="transaction-date">
                                        {new Date(transaction.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PaymentComponent;