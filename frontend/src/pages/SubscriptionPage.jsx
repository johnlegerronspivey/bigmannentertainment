import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { apiRequest } from "../utils/apiClient";
import { toast } from "sonner";
import { Crown, Check, Zap, Shield, Star } from "lucide-react";

function SubscriptionPage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [tiers, setTiers] = useState([]);
  const [currentSub, setCurrentSub] = useState(null);
  const [loading, setLoading] = useState(true);
  const [billing, setBilling] = useState("monthly");
  const [checkoutLoading, setCheckoutLoading] = useState(null);

  useEffect(() => {
    loadData();
    // Handle return from Stripe
    const status = searchParams.get("status");
    const sessionId = searchParams.get("session_id");
    if (status === "success" && sessionId) {
      confirmSubscription(sessionId);
    } else if (status === "cancelled") {
      toast.info("Checkout was cancelled");
    }
  }, []);

  const loadData = async () => {
    try {
      const [tiersData, subData] = await Promise.all([
        apiRequest("/subscriptions/tiers"),
        apiRequest("/subscriptions/me"),
      ]);
      setTiers(tiersData.tiers || []);
      setCurrentSub(subData);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  const confirmSubscription = async (sessionId) => {
    try {
      const result = await apiRequest("/subscriptions/confirm", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (result.status === "active") {
        toast.success("Subscription activated!");
        loadData();
      }
    } catch {
      toast.error("Failed to confirm subscription");
    }
  };

  const handleCheckout = async (tierId) => {
    setCheckoutLoading(tierId);
    try {
      const result = await apiRequest("/subscriptions/checkout", {
        method: "POST",
        body: JSON.stringify({ tier_id: tierId, billing }),
      });
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
      }
    } catch (err) {
      toast.error(err.message || "Checkout failed");
    } finally {
      setCheckoutLoading(null);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm("Are you sure you want to cancel your subscription?")) return;
    try {
      await apiRequest("/subscriptions/cancel", { method: "POST" });
      toast.success("Subscription cancelled");
      loadData();
    } catch (err) {
      toast.error(err.message || "Failed to cancel");
    }
  };

  const tierIcons = { free: Star, pro: Zap, enterprise: Crown };
  const tierColors = {
    free: "border-gray-700",
    pro: "border-purple-500 ring-1 ring-purple-500/20",
    enterprise: "border-amber-500 ring-1 ring-amber-500/20",
  };
  const tierBtnColors = {
    free: "bg-gray-700 hover:bg-gray-600",
    pro: "bg-purple-600 hover:bg-purple-700",
    enterprise: "bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700",
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" />
      </div>
    );
  }

  const currentTier = currentSub?.tier || "free";

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="subscription-page">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold mb-2">Subscription Plans</h1>
          <p className="text-gray-400">Choose the plan that fits your creative needs</p>

          {/* Billing toggle */}
          <div className="flex items-center justify-center gap-3 mt-6" data-testid="billing-toggle">
            <span className={`text-sm ${billing === "monthly" ? "text-white" : "text-gray-500"}`}>Monthly</span>
            <button
              onClick={() => setBilling(billing === "monthly" ? "yearly" : "monthly")}
              className={`relative w-12 h-6 rounded-full transition-colors ${billing === "yearly" ? "bg-purple-600" : "bg-gray-700"}`}
              data-testid="billing-switch"
            >
              <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform ${billing === "yearly" ? "translate-x-6" : "translate-x-0.5"}`} />
            </button>
            <span className={`text-sm ${billing === "yearly" ? "text-white" : "text-gray-500"}`}>
              Yearly <span className="text-green-400 text-xs">(Save 17%)</span>
            </span>
          </div>
        </div>

        {/* Current subscription banner */}
        {currentTier !== "free" && (
          <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-4 mb-8 flex items-center justify-between" data-testid="current-sub-banner">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-purple-400" />
              <div>
                <p className="font-medium">
                  You're on the <span className="text-purple-400 capitalize">{currentTier}</span> plan
                </p>
                <p className="text-sm text-gray-400">Status: {currentSub?.status || "active"}</p>
              </div>
            </div>
            <button onClick={handleCancel} className="text-sm text-red-400 hover:text-red-300" data-testid="cancel-sub-btn">
              Cancel Subscription
            </button>
          </div>
        )}

        {/* Tier Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="tier-cards">
          {tiers.map((tier) => {
            const Icon = tierIcons[tier.id] || Star;
            const isCurrentTier = currentTier === tier.id;
            const price = billing === "yearly" ? tier.price_yearly : tier.price_monthly;

            return (
              <div
                key={tier.id}
                className={`bg-gray-900 border rounded-xl p-6 relative transition-all hover:shadow-lg ${tierColors[tier.id] || "border-gray-700"} ${isCurrentTier ? "ring-2 ring-green-500/30" : ""}`}
                data-testid={`tier-card-${tier.id}`}
              >
                {tier.id === "pro" && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-xs font-semibold px-3 py-1 rounded-full">
                    Most Popular
                  </div>
                )}
                {isCurrentTier && (
                  <div className="absolute -top-3 right-4 bg-green-600 text-xs font-semibold px-3 py-1 rounded-full">
                    Current Plan
                  </div>
                )}

                <div className="text-center mb-6">
                  <Icon className={`w-8 h-8 mx-auto mb-3 ${tier.id === "enterprise" ? "text-amber-400" : tier.id === "pro" ? "text-purple-400" : "text-gray-400"}`} />
                  <h3 className="text-xl font-bold">{tier.name}</h3>
                  <div className="mt-3">
                    <span className="text-3xl font-bold">${price}</span>
                    {tier.id !== "free" && <span className="text-gray-500 text-sm">/{billing === "yearly" ? "year" : "month"}</span>}
                  </div>
                </div>

                <ul className="space-y-3 mb-6">
                  {tier.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${tier.id === "enterprise" ? "text-amber-400" : "text-purple-400"}`} />
                      <span className="text-gray-300">{f}</span>
                    </li>
                  ))}
                </ul>

                {isCurrentTier ? (
                  <button disabled className="w-full py-2.5 bg-green-600/20 text-green-400 rounded-lg text-sm font-medium cursor-default" data-testid={`tier-btn-${tier.id}`}>
                    Current Plan
                  </button>
                ) : tier.id === "free" ? (
                  <button disabled className="w-full py-2.5 bg-gray-800 text-gray-500 rounded-lg text-sm font-medium cursor-default" data-testid={`tier-btn-${tier.id}`}>
                    Free Forever
                  </button>
                ) : (
                  <button
                    onClick={() => handleCheckout(tier.id)}
                    disabled={checkoutLoading === tier.id}
                    className={`w-full py-2.5 rounded-lg text-sm font-medium transition-colors ${tierBtnColors[tier.id]} disabled:opacity-50`}
                    data-testid={`tier-btn-${tier.id}`}
                  >
                    {checkoutLoading === tier.id ? "Redirecting..." : `Upgrade to ${tier.name}`}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default SubscriptionPage;
