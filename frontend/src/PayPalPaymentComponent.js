import React, { useState, useEffect } from 'react';

const PayPalPaymentComponent = ({ 
    amount = 10.00, 
    currency = "USD", 
    description = "Big Mann Entertainment Service",
    onSuccess,
    onError,
    onCancel 
}) => {
    const [paypalConfig, setPaypalConfig] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [paymentData, setPaymentData] = useState(null);

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    useEffect(() => {
        fetchPayPalConfig();
    }, []);

    const fetchPayPalConfig = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/paypal/config`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    setPaypalConfig(data.config);
                }
            }
        } catch (error) {
            console.error('Failed to fetch PayPal config:', error);
        }
    };

    const createPayment = async () => {
        setIsLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/paypal/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    amount: parseFloat(amount),
                    currency: currency,
                    description: description,
                    return_url: `${window.location.origin}/payment/success`,
                    cancel_url: `${window.location.origin}/payment/cancel`
                })
            });

            const data = await response.json();

            if (data.success && data.approval_url) {
                setPaymentData(data);
                // Redirect to PayPal for approval
                window.location.href = data.approval_url;
            } else {
                setError('Failed to create PayPal payment: ' + (data.error || 'Unknown error'));
                if (onError) onError(data);
            }
        } catch (error) {
            setError('Network error: ' + error.message);
            if (onError) onError({ error: error.message });
        } finally {
            setIsLoading(false);
        }
    };

    const handlePaymentSuccess = async (paymentId, payerId) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/paypal/orders/${paymentId}/capture`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ payer_id: payerId })
            });

            const data = await response.json();

            if (data.success) {
                if (onSuccess) onSuccess(data);
            } else {
                if (onError) onError(data);
            }
        } catch (error) {
            if (onError) onError({ error: error.message });
        }
    };

    // Check for return from PayPal
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const paymentId = urlParams.get('paymentId');
        const payerId = urlParams.get('PayerID');
        const token = urlParams.get('token');

        if (paymentId && payerId) {
            handlePaymentSuccess(paymentId, payerId);
        } else if (urlParams.get('cancelled') === 'true') {
            if (onCancel) onCancel();
        }
    }, []);

    if (!paypalConfig) {
        return (
            <div className="paypal-loading">
                <div className="loading-spinner"></div>
                <p>Loading PayPal configuration...</p>
            </div>
        );
    }

    return (
        <div className="paypal-payment-component">
            <div className="payment-details">
                <h3>PayPal Payment</h3>
                <div className="amount-display">
                    <span className="currency">{currency}</span>
                    <span className="amount">${parseFloat(amount).toFixed(2)}</span>
                </div>
                <p className="description">{description}</p>
            </div>

            {error && (
                <div className="error-message">
                    <p>{error}</p>
                </div>
            )}

            <div className="payment-actions">
                <button 
                    onClick={createPayment}
                    disabled={isLoading}
                    className="paypal-button"
                >
                    {isLoading ? (
                        <>
                            <div className="loading-spinner small"></div>
                            Processing...
                        </>
                    ) : (
                        <>
                            <img 
                                src="https://www.paypalobjects.com/webstatic/mktg/Logo/pp-logo-100px.png" 
                                alt="PayPal"
                                className="paypal-logo"
                            />
                            Pay with PayPal
                        </>
                    )}
                </button>
            </div>

            <div className="payment-info">
                <p className="security-note">
                    🔒 Secure payment processing by PayPal
                </p>
                <p className="environment-note">
                    {paypalConfig.environment === 'sandbox' && (
                        <span className="sandbox-badge">Sandbox Mode</span>
                    )}
                </p>
            </div>

            <style jsx>{`
                .paypal-payment-component {
                    max-width: 400px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 12px;
                    background: #fff;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }

                .payment-details {
                    text-align: center;
                    margin-bottom: 20px;
                }

                .payment-details h3 {
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.5rem;
                }

                .amount-display {
                    display: flex;
                    justify-content: center;
                    align-items: baseline;
                    margin-bottom: 10px;
                }

                .currency {
                    font-size: 1rem;
                    color: #666;
                    margin-right: 5px;
                }

                .amount {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #0070ba;
                }

                .description {
                    color: #666;
                    font-size: 0.95rem;
                    margin: 0;
                }

                .error-message {
                    background: #fee;
                    border: 1px solid #fcc;
                    border-radius: 6px;
                    padding: 10px;
                    margin-bottom: 15px;
                    color: #c33;
                    text-align: center;
                }

                .payment-actions {
                    margin-bottom: 20px;
                }

                .paypal-button {
                    width: 100%;
                    background: linear-gradient(135deg, #0070ba 0%, #005ea6 100%);
                    color: white;
                    border: none;
                    padding: 15px 20px;
                    border-radius: 8px;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                }

                .paypal-button:hover:not(:disabled) {
                    background: linear-gradient(135deg, #005ea6 0%, #004182 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(0, 112, 186, 0.4);
                }

                .paypal-button:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                    transform: none;
                    box-shadow: none;
                }

                .paypal-logo {
                    height: 20px;
                    width: auto;
                }

                .payment-info {
                    text-align: center;
                    font-size: 0.85rem;
                    color: #666;
                }

                .security-note {
                    margin-bottom: 10px;
                }

                .environment-note {
                    margin: 0;
                }

                .sandbox-badge {
                    background: #ff9500;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    font-weight: 600;
                }

                .paypal-loading {
                    text-align: center;
                    padding: 40px 20px;
                }

                .loading-spinner {
                    display: inline-block;
                    width: 30px;
                    height: 30px;
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #0070ba;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 15px;
                }

                .loading-spinner.small {
                    width: 16px;
                    height: 16px;
                    border-width: 2px;
                    margin-bottom: 0;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                @media (max-width: 768px) {
                    .paypal-payment-component {
                        margin: 10px;
                        padding: 15px;
                    }

                    .amount {
                        font-size: 1.8rem;
                    }

                    .paypal-button {
                        padding: 12px 16px;
                        font-size: 1rem;
                    }
                }
            `}</style>
        </div>
    );
};

// Payment Success Page Component
export const PayPalSuccessPage = () => {
    const [paymentDetails, setPaymentDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const paymentId = urlParams.get('paymentId');
        const payerId = urlParams.get('PayerID');
        
        if (paymentId && payerId) {
            setPaymentDetails({
                paymentId,
                payerId,
                status: 'completed'
            });
        }
        setIsLoading(false);
    }, []);

    if (isLoading) {
        return (
            <div className="success-page loading">
                <div className="loading-spinner"></div>
                <p>Processing payment...</p>
            </div>
        );
    }

    return (
        <div className="success-page">
            <div className="success-content">
                <div className="success-icon">✅</div>
                <h2>Payment Successful!</h2>
                <p>Thank you for your payment to Big Mann Entertainment.</p>
                
                {paymentDetails && (
                    <div className="payment-summary">
                        <h3>Payment Details</h3>
                        <p><strong>Payment ID:</strong> {paymentDetails.paymentId}</p>
                        <p><strong>Status:</strong> {paymentDetails.status}</p>
                    </div>
                )}
                
                <div className="actions">
                    <button 
                        onClick={() => window.location.href = '/dashboard'}
                        className="return-button"
                    >
                        Return to Dashboard
                    </button>
                </div>
            </div>

            <style jsx>{`
                .success-page {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                }

                .success-content {
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    max-width: 500px;
                }

                .success-icon {
                    font-size: 4rem;
                    margin-bottom: 20px;
                }

                .success-content h2 {
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 2rem;
                }

                .payment-summary {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: left;
                }

                .payment-summary h3 {
                    margin-bottom: 15px;
                    color: #333;
                }

                .return-button {
                    background: linear-gradient(135deg, #0070ba 0%, #005ea6 100%);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }

                .return-button:hover {
                    background: linear-gradient(135deg, #005ea6 0%, #004182 100%);
                    transform: translateY(-2px);
                }

                .loading {
                    flex-direction: column;
                    color: white;
                }

                .loading-spinner {
                    width: 40px;
                    height: 40px;
                    border: 4px solid rgba(255, 255, 255, 0.3);
                    border-top: 4px solid white;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 20px;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

// Payment Cancel Page Component
export const PayPalCancelPage = () => {
    return (
        <div className="cancel-page">
            <div className="cancel-content">
                <div className="cancel-icon">❌</div>
                <h2>Payment Cancelled</h2>
                <p>Your PayPal payment was cancelled. No charges were made.</p>
                
                <div className="actions">
                    <button 
                        onClick={() => window.location.href = '/dashboard'}
                        className="return-button"
                    >
                        Return to Dashboard
                    </button>
                    <button 
                        onClick={() => window.history.back()}
                        className="retry-button"
                    >
                        Try Again
                    </button>
                </div>
            </div>

            <style jsx>{`
                .cancel-page {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
                    padding: 20px;
                }

                .cancel-content {
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    max-width: 500px;
                }

                .cancel-icon {
                    font-size: 4rem;
                    margin-bottom: 20px;
                }

                .cancel-content h2 {
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 2rem;
                }

                .actions {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 20px;
                }

                .return-button, .retry-button {
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }

                .return-button {
                    background: #6c757d;
                    color: white;
                }

                .retry-button {
                    background: linear-gradient(135deg, #0070ba 0%, #005ea6 100%);
                    color: white;
                }

                .return-button:hover {
                    background: #5a6268;
                    transform: translateY(-2px);
                }

                .retry-button:hover {
                    background: linear-gradient(135deg, #005ea6 0%, #004182 100%);
                    transform: translateY(-2px);
                }

                @media (max-width: 768px) {
                    .actions {
                        flex-direction: column;
                    }

                    .return-button, .retry-button {
                        width: 100%;
                    }
                }
            `}</style>
        </div>
    );
};

export default PayPalPaymentComponent;