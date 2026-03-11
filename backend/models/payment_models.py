from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums for better type safety
class PaymentStatus(str, Enum):
    PENDING = "pending"
    INITIATED = "initiated"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    EXPIRED = "expired"

class PaymentMethod(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"

class TransactionType(str, Enum):
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"
    ROYALTY_PAYMENT = "royalty_payment"
    PLATFORM_FEE = "platform_fee"
    REFUND = "refund"

class BankAccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    BUSINESS = "business"

class PayoutSchedule(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"

class RoyaltySplitType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

# Payment Transaction Model
class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    email: Optional[str] = None
    session_id: Optional[str] = None
    payment_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    payment_method: PaymentMethod
    transaction_type: TransactionType
    status: PaymentStatus
    payment_status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

# Bank Account Model
class BankAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    account_name: str
    account_number: str
    routing_number: str
    bank_name: str
    account_type: BankAccountType
    is_primary: bool = False
    is_verified: bool = False
    country: str = "US"
    currency: str = "USD"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Digital Wallet Model  
class DigitalWallet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    wallet_type: str  # paypal, venmo, cashapp, crypto
    wallet_address: str
    wallet_name: str
    is_primary: bool = False
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Royalty Split Model
class RoyaltySplit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    media_id: str
    recipient_id: str
    recipient_email: str
    recipient_name: str
    split_type: RoyaltySplitType
    percentage: Optional[float] = None  # For percentage splits
    fixed_amount: Optional[float] = None  # For fixed amount splits
    role: str  # artist, producer, label, platform
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Royalty Payment Model
class RoyaltyPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    media_id: str
    original_transaction_id: str
    recipient_id: str
    recipient_email: str
    amount: float
    currency: str = "usd"
    split_percentage: float
    status: PaymentStatus = PaymentStatus.PENDING
    payout_method: Optional[str] = None  # bank_transfer, paypal, etc.
    payout_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

# User Earnings Model
class UserEarnings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    total_earnings: float = 0.0
    available_balance: float = 0.0
    pending_balance: float = 0.0
    total_paid_out: float = 0.0
    currency: str = "usd"
    minimum_payout_threshold: float = 10.0
    payout_schedule: PayoutSchedule = PayoutSchedule.MONTHLY
    last_payout_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Payout Request Model
class PayoutRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    currency: str = "usd"
    payout_method: str  # bank_transfer, paypal, etc.
    bank_account_id: Optional[str] = None
    wallet_id: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    reference_number: Optional[str] = None

# Platform Revenue Model
class PlatformRevenue(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    revenue_type: str  # commission, subscription, transaction_fee
    amount: float
    currency: str = "usd"
    percentage: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Tax Document Model
class TaxDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tax_year: int
    document_type: str  # 1099, W9, etc.
    total_earnings: float
    document_url: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

# Request/Response Models for API
class CreateCheckoutSessionRequest(BaseModel):
    package_id: Optional[str] = None
    media_id: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "usd"
    stripe_price_id: Optional[str] = None
    quantity: int = 1
    origin_url: str
    metadata: Optional[Dict[str, str]] = None

class CreateCheckoutSessionResponse(BaseModel):
    url: str
    session_id: str
    amount: float
    currency: str

class PaymentStatusResponse(BaseModel):
    status: str
    payment_status: str
    amount_total: float
    currency: str
    metadata: Dict[str, str]

class BankAccountRequest(BaseModel):
    account_name: str
    account_number: str
    routing_number: str
    bank_name: str
    account_type: BankAccountType
    is_primary: bool = False

class DigitalWalletRequest(BaseModel):
    wallet_type: str
    wallet_address: str
    wallet_name: str
    is_primary: bool = False

class RoyaltySplitRequest(BaseModel):
    media_id: str
    recipient_email: str
    recipient_name: str
    split_type: RoyaltySplitType
    percentage: Optional[float] = None
    fixed_amount: Optional[float] = None
    role: str

class PayoutRequestModel(BaseModel):
    amount: float
    payout_method: str
    bank_account_id: Optional[str] = None
    wallet_id: Optional[str] = None

# Dashboard Models
class EarningsSummary(BaseModel):
    total_earnings: float
    available_balance: float
    pending_balance: float
    total_paid_out: float
    recent_transactions: List[Dict[str, Any]]
    top_earning_content: List[Dict[str, Any]]

class PaymentPackage(BaseModel):
    id: str
    name: str
    description: str
    amount: float
    currency: str = "usd"
    stripe_price_id: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    is_subscription: bool = False
    interval: Optional[str] = None  # month, year for subscriptions