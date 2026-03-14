import React, { lazy, Suspense } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, useNavigate, useParams } from "react-router-dom";
import { PageLoadingOverlay } from "./components/LoadingSkeleton";
import { ChunkErrorBoundary } from "./components/ChunkErrorBoundary";
import { Toaster } from "sonner";
import { useAuth, AuthProvider, ProtectedRoute, AdminRoute } from "./contexts/AuthContext";
import NavigationBar from "./components/layout/NavigationBar";

// Page component lazy imports
const HomePage = lazy(() => import("./pages/HomePage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));
const ForgotPasswordPage = lazy(() => import("./pages/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("./pages/ResetPasswordPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const DistributionHubPage = lazy(() => import("./pages/DistributionHubPage"));
const AdminNotificationsPage = lazy(() => import("./pages/AdminNotificationsPage"));
const LibraryPage = lazy(() => import("./pages/LibraryPage"));
const DistributePage = lazy(() => import("./pages/DistributePage"));
const PlatformsPage = lazy(() => import("./pages/PlatformsPage"));
const PricingPage = lazy(() => import("./pages/PricingPage"));

// Feature component lazy imports
const DDEXERNCreator = lazy(() => import("./DDEXComponents").then(m => ({ default: m.DDEXERNCreator })));
const DDEXCWRCreator = lazy(() => import("./DDEXComponents").then(m => ({ default: m.DDEXCWRCreator })));
const DDEXMessageList = lazy(() => import("./DDEXComponents").then(m => ({ default: m.DDEXMessageList })));
const DDEXIdentifierGenerator = lazy(() => import("./DDEXComponents").then(m => ({ default: m.DDEXIdentifierGenerator })));
const DDEXAdminDashboard = lazy(() => import("./DDEXComponents").then(m => ({ default: m.DDEXAdminDashboard })));
const MusicReportsDashboard = lazy(() => import("./MusicReportsComponents").then(m => ({ default: m.MusicReportsDashboard })));
const EnhancedUserDashboard = lazy(() => import("./WorkflowEnhancementComponents").then(m => ({ default: m.EnhancedUserDashboard })));
const AgencyRegistrationWizard = lazy(() => import("./AgencyOnboardingComponents").then(m => ({ default: m.AgencyRegistrationWizard })));
const AgencyDashboard = lazy(() => import("./AgencyOnboardingComponents").then(m => ({ default: m.AgencyDashboard })));
const LicenseBuilder = lazy(() => import("./LicensingWorkflowComponents").then(m => ({ default: m.LicenseBuilder })));
const RoyaltyTracker = lazy(() => import("./LicensingWorkflowComponents").then(m => ({ default: m.RoyaltyTracker })));
const SponsorshipDashboard = lazy(() => import("./SponsorshipComponents").then(m => ({ default: m.SponsorshipDashboard })));
const SponsorshipDealCreator = lazy(() => import("./SponsorshipComponents").then(m => ({ default: m.SponsorshipDealCreator })));
const MetricsRecorder = lazy(() => import("./SponsorshipComponents").then(m => ({ default: m.MetricsRecorder })));
const AdminSponsorshipOverview = lazy(() => import("./SponsorshipComponents").then(m => ({ default: m.AdminSponsorshipOverview })));
const TaxDashboard = lazy(() => import("./TaxComponents").then(m => ({ default: m.TaxDashboard })));
const Form1099Management = lazy(() => import("./TaxComponents").then(m => ({ default: m.Form1099Management })));
const TaxReports = lazy(() => import("./TaxComponents").then(m => ({ default: m.TaxReports })));
const BusinessTaxInfo = lazy(() => import("./TaxComponents").then(m => ({ default: m.BusinessTaxInfo })));
const BusinessLicenseManagement = lazy(() => import("./TaxComponents").then(m => ({ default: m.BusinessLicenseManagement })));
const ComplianceDashboard = lazy(() => import("./TaxComponents").then(m => ({ default: m.ComplianceDashboard })));
const BusinessIdentifiers = lazy(() => import("./BusinessComponents").then(m => ({ default: m.BusinessIdentifiers })));
const UPCGenerator = lazy(() => import("./BusinessComponents").then(m => ({ default: m.UPCGenerator })));
const ISRCGenerator = lazy(() => import("./BusinessComponents").then(m => ({ default: m.ISRCGenerator })));
const ProductManagement = lazy(() => import("./BusinessComponents").then(m => ({ default: m.ProductManagement })));
const IndustryDashboard = lazy(() => import("./IndustryComponents").then(m => ({ default: m.IndustryDashboard })));
const IndustryPartners = lazy(() => import("./IndustryComponents").then(m => ({ default: m.IndustryPartners })));
const GlobalDistribution = lazy(() => import("./IndustryComponents").then(m => ({ default: m.GlobalDistribution })));
const IndustryCoverage = lazy(() => import("./IndustryComponents").then(m => ({ default: m.IndustryCoverage })));
const IPIManagement = lazy(() => import("./IndustryComponents").then(m => ({ default: m.IPIManagement })));
const IndustryIdentifiersManagement = lazy(() => import("./IndustryComponents").then(m => ({ default: m.IndustryIdentifiersManagement })));
const EnhancedEntertainmentDashboard = lazy(() => import("./IndustryComponents").then(m => ({ default: m.EnhancedEntertainmentDashboard })));
const PhotographyServices = lazy(() => import("./IndustryComponents").then(m => ({ default: m.PhotographyServices })));
const VideoProductionServices = lazy(() => import("./IndustryComponents").then(m => ({ default: m.VideoProductionServices })));
const MonetizationOpportunities = lazy(() => import("./IndustryComponents").then(m => ({ default: m.MonetizationOpportunities })));
const MusicDataExchange = lazy(() => import("./IndustryComponents").then(m => ({ default: m.MusicDataExchange })));
const MechanicalLicensingCollective = lazy(() => import("./IndustryComponents").then(m => ({ default: m.MechanicalLicensingCollective })));
const LabelDashboard = lazy(() => import("./LabelComponents").then(m => ({ default: m.LabelDashboard })));
const LabelDirectory = lazy(() => import("./LabelComponents").then(m => ({ default: m.LabelDirectory })));
const ULNDashboard = lazy(() => import("./ULNComponents").then(m => ({ default: m.ULNDashboard })));
const ProjectManagement = lazy(() => import("./LabelExtendedComponents").then(m => ({ default: m.ProjectManagement })));
const MarketingManagement = lazy(() => import("./LabelExtendedComponents").then(m => ({ default: m.MarketingManagement })));
const FinancialManagement = lazy(() => import("./LabelExtendedComponents").then(m => ({ default: m.FinancialManagement })));
const PaymentPackages = lazy(() => import("./PaymentComponents").then(m => ({ default: m.PaymentPackages })));
const PaymentCheckout = lazy(() => import("./PaymentComponents").then(m => ({ default: m.PaymentCheckout })));
const PaymentStatus = lazy(() => import("./PaymentComponents").then(m => ({ default: m.PaymentStatus })));
const BankAccountManager = lazy(() => import("./PaymentComponents").then(m => ({ default: m.BankAccountManager })));
const DigitalWalletManager = lazy(() => import("./PaymentComponents").then(m => ({ default: m.DigitalWalletManager })));
const EarningsDashboard = lazy(() => import("./EarningsComponents").then(m => ({ default: m.EarningsDashboard })));
const RoyaltySplitManager = lazy(() => import("./EarningsComponents").then(m => ({ default: m.RoyaltySplitManager })));
const PaymentComponent = lazy(() => import("./PaymentComponent"));
const EarningsComponent = lazy(() => import("./EarningsComponent"));
const LicensingDashboard = lazy(() => import("./LicensingComponents").then(m => ({ default: m.LicensingDashboard })));
const PlatformLicenseManager = lazy(() => import("./LicensingComponents").then(m => ({ default: m.PlatformLicenseManager })));
const LicensingStatus = lazy(() => import("./LicensingComponents").then(m => ({ default: m.LicensingStatus })));
const GS1Dashboard = lazy(() => import("./GS1Components").then(m => ({ default: m.GS1Dashboard })));
const ComprehensiveLicensingComponents = lazy(() => import("./ComprehensiveLicensingComponents"));
const ContentRemovalDashboard = lazy(() => import("./ContentRemovalComponents"));
const AboutPage = lazy(() => import("./AboutPage"));
const EnhancedUploadComponent = lazy(() => import("./EnhancedUploadComponent"));
const ImageUploadComponent = lazy(() => import("./ImageUploadComponent"));
const RightsComplianceComponent = lazy(() => import("./RightsComplianceComponent"));
const SmartContractComponent = lazy(() => import("./SmartContractComponent"));
const AuditTrailComponent = lazy(() => import("./AuditTrailComponent"));
const MediaUploadComponent = lazy(() => import("./MediaUploadComponent"));
const SocialMediaStrategyDashboard = lazy(() => import("./SocialMediaStrategyComponents").then(m => ({ default: m.SocialMediaStrategyDashboard })));
const ContentIngestionDashboard = lazy(() => import("./ContentIngestionComponents").then(m => ({ default: m.ContentIngestionDashboard })));
const ComprehensiveWorkflowDashboard = lazy(() => import("./ComprehensiveWorkflowComponents").then(m => ({ default: m.ComprehensiveWorkflowDashboard })));
const SocialMediaPhases5To10Dashboard = lazy(() => import("./SocialMediaPhases5To10Components").then(m => ({ default: m.SocialMediaPhases5To10Dashboard })));
const RealTimeRoyaltyDashboard = lazy(() => import("./RealTimeRoyaltyComponents").then(m => ({ default: m.RealTimeRoyaltyDashboard })));
const ComprehensivePlatform = lazy(() => import("./ComprehensivePlatformComponents").then(m => ({ default: m.ComprehensivePlatform })));
const WorkflowIntegrationDashboard = lazy(() => import("./WorkflowIntegrationComponents").then(m => ({ default: m.WorkflowIntegrationDashboard })));
const SupportSystemDashboard = lazy(() => import("./SupportSystemComponents").then(m => ({ default: m.SupportSystemDashboard })));
const EnhancedFeaturesDashboard = lazy(() => import("./EnhancedFeaturesComponents"));
const EnterprisePhase1Dashboard = lazy(() => import("./EnterprisePhase1Components"));
const DigitalTwinDashboard = lazy(() => import("./DigitalTwinComponents"));
const RoyaltyMarketplaceDashboard = lazy(() => import("./RoyaltyMarketplaceComponents"));
const ListingDetailPage = lazy(() => import("./RoyaltyMarketplaceComponents").then(m => ({ default: m.ListingDetailPage })));
const CreatorProfilePage = lazy(() => import("./CreatorProfile"));
const ProfileSettings = lazy(() => import("./ProfileSettings"));
const DAOGovernance = lazy(() => import("./DAOGovernance"));
const SocialMediaDashboard = lazy(() => import("./SocialMediaDashboardEnhanced"));
const ProposalDetail = lazy(() => import("./ProposalDetail"));
const AWSOrganizationsComponent = lazy(() => import("./AWSOrganizationsComponent"));
const AWSEnterpriseMapping = lazy(() => import("./AWSEnterpriseMappingComponents"));
const AgencySuccessAutomationDashboard = lazy(() => import("./AgencySuccessAutomationComponents"));
const ContractDeploymentUI = lazy(() => import("./EthereumAdvancedFeatures").then(m => ({ default: m.ContractDeploymentUI })));
const TransactionHistoryViewer = lazy(() => import("./EthereumAdvancedFeatures").then(m => ({ default: m.TransactionHistoryViewer })));
const DAOVotingDashboard = lazy(() => import("./EthereumAdvancedFeatures").then(m => ({ default: m.DAOVotingDashboard })));
const DAOGovernanceV2Dashboard = lazy(() => import("./DAOGovernanceV2Components"));
const CreativeStudioDashboard = lazy(() => import("./CreativeStudioComponents"));
const MacieDashboard = lazy(() => import("./MacieComponents"));
const GuardDutyDashboard = lazy(() => import("./GuardDutyComponents"));
const QLDBDashboard = lazy(() => import("./QLDBComponents"));
const UsageAnalyticsDashboard = lazy(() => import("./UsageAnalyticsDashboard"));
const AWSCloudWatchDashboard = lazy(() => import("./AWSCloudWatchComponents"));
const SecurityAuditDashboard = lazy(() => import("./SecurityAuditDashboard"));
const CVEManagementDashboard = lazy(() => import("./CVEManagementDashboard"));
const TenantManagement = lazy(() => import("./TenantManagement"));
const ContentModerationComponent = lazy(() => import("./ContentModerationComponent"));
const DomainConfigPage = lazy(() => import("./admin/DomainConfigPage"));
const RDSUpgradePage = lazy(() => import("./pages/RDSUpgradePage"));
const CreatorProfilesPage = lazy(() => import("./pages/CreatorProfilesPage"));
const WatermarkPage = lazy(() => import("./pages/WatermarkPage"));
const SubscriptionPage = lazy(() => import("./pages/SubscriptionPage"));
const ContentManagementPage = lazy(() => import("./pages/ContentManagementPage"));
const MessagingPage = lazy(() => import("./pages/MessagingPage"));
const CreatorAnalyticsPage = lazy(() => import("./pages/CreatorAnalyticsPage"));
const NotificationsPage = lazy(() => import("./pages/NotificationsPage"));
const LiveIntegrationsPage = lazy(() => import("./pages/LiveIntegrationsPage"));
const OAuthCallbackPage = lazy(() => import("./pages/OAuthCallbackPage"));
const AWSMediaProcessingPage = lazy(() => import("./pages/AWSMediaProcessingPage"));
const AWSLiveStreamingPage = lazy(() => import("./pages/AWSLiveStreamingPage"));
const AWSWorkMailPinpointPage = lazy(() => import("./pages/AWSWorkMailPinpointPage"));
const AWSWafSecretsPage = lazy(() => import("./pages/AWSWafSecretsPage"));

// Re-export useAuth for backward compatibility
export { useAuth } from "./contexts/AuthContext";

// Small inline wrapper components
const RightsComplianceWrapper = () => {
  const { user } = useAuth();
  return <RightsComplianceComponent currentUser={user} />;
};

const EnhancedPaymentCheckout = () => {
  const { packageId } = useParams();
  const navigate = useNavigate();
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <button 
          onClick={() => navigate('/pricing')}
          className="text-blue-600 hover:text-blue-800 flex items-center"
        >
          ← Back to Pricing
        </button>
      </div>
      <PaymentCheckout 
        packageId={packageId}
        onSuccess={() => navigate('/payment/success')}
        onCancel={() => navigate('/pricing')}
      />
    </div>
  );
};

const AdminUsers = () => <div className="p-8"><h1 className="text-2xl font-bold">User Management</h1><p>Admin users management.</p></div>;
const AdminContent = () => <div className="p-8"><h1 className="text-2xl font-bold">Content Moderation</h1><p>Admin content moderation.</p></div>;
const AdminAnalytics = () => <div className="p-8"><h1 className="text-2xl font-bold">Analytics</h1><p>Platform analytics and insights.</p></div>;

// Main App Component
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="App">
          <NavigationBar />
          <ChunkErrorBoundary variant="page">
          <Suspense fallback={<PageLoadingOverlay message="Loading page..." />}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/platforms" element={<PlatformsPage />} />
            <Route path="/pricing" element={<PricingPage />} />

            {/* Protected routes */}
            <Route path="/library" element={<ProtectedRoute><LibraryPage /></ProtectedRoute>} />
            <Route path="/upload" element={<ProtectedRoute><MediaUploadComponent /></ProtectedRoute>} />
            <Route path="/rights-compliance" element={<ProtectedRoute><RightsComplianceWrapper /></ProtectedRoute>} />
            <Route path="/smart-contracts" element={<ProtectedRoute><SmartContractComponent /></ProtectedRoute>} />
            <Route path="/audit-trail" element={<ProtectedRoute><AuditTrailComponent /></ProtectedRoute>} />
            <Route path="/distribute" element={<ProtectedRoute><DistributePage /></ProtectedRoute>} />
            <Route path="/distribution-hub" element={<ProtectedRoute><DistributionHubPage /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><ProfileSettings /></ProtectedRoute>} />
            <Route path="/profile/settings" element={<ProtectedRoute><ProfileSettings /></ProtectedRoute>} />
            <Route path="/creator/:username" element={<CreatorProfilePage />} />
            <Route path="/dao" element={<ProtectedRoute><DAOGovernance /></ProtectedRoute>} />
            <Route path="/dao/proposal/:proposalId" element={<ProtectedRoute><ProposalDetail /></ProtectedRoute>} />
            
            {/* Advanced Ethereum Features */}
            <Route path="/ethereum/deploy" element={<ProtectedRoute><ContractDeploymentUI /></ProtectedRoute>} />
            <Route path="/ethereum/transactions" element={<ProtectedRoute><TransactionHistoryViewer /></ProtectedRoute>} />
            <Route path="/ethereum/dao-voting" element={<ProtectedRoute><DAOVotingDashboard /></ProtectedRoute>} />
            <Route path="/social" element={<ProtectedRoute><SocialMediaDashboard /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><EnhancedUserDashboard /></ProtectedRoute>} />
            <Route path="/enhanced-features" element={<ProtectedRoute><EnhancedFeaturesDashboard token={localStorage.getItem('token')} /></ProtectedRoute>} />
            <Route path="/enterprise" element={<ProtectedRoute><EnterprisePhase1Dashboard /></ProtectedRoute>} />
            <Route path="/digital-twins" element={<ProtectedRoute><DigitalTwinDashboard /></ProtectedRoute>} />
            <Route path="/marketplace" element={<ProtectedRoute><RoyaltyMarketplaceDashboard /></ProtectedRoute>} />
            <Route path="/marketplace/listing/:listingId" element={<ProtectedRoute><ListingDetailPage /></ProtectedRoute>} />
            <Route path="/aws-organizations" element={<ProtectedRoute><AWSOrganizationsComponent /></ProtectedRoute>} />
            <Route path="/aws-enterprise" element={<ProtectedRoute><AWSEnterpriseMapping /></ProtectedRoute>} />
            <Route path="/agency-automation" element={<ProtectedRoute><AgencySuccessAutomationDashboard /></ProtectedRoute>} />
            <Route path="/dao-v2" element={<ProtectedRoute><DAOGovernanceV2Dashboard /></ProtectedRoute>} />
            <Route path="/creative-studio" element={<ProtectedRoute><CreativeStudioDashboard /></ProtectedRoute>} />
            <Route path="/macie" element={<ProtectedRoute><MacieDashboard /></ProtectedRoute>} />
            <Route path="/guardduty" element={<ProtectedRoute><GuardDutyDashboard /></ProtectedRoute>} />
            <Route path="/qldb" element={<ProtectedRoute><QLDBDashboard /></ProtectedRoute>} />
            <Route path="/usage-analytics" element={<ProtectedRoute><UsageAnalyticsDashboard /></ProtectedRoute>} />
            <Route path="/cloudwatch" element={<ProtectedRoute><AWSCloudWatchDashboard /></ProtectedRoute>} />
            <Route path="/security-audit" element={<ProtectedRoute><SecurityAuditDashboard /></ProtectedRoute>} />
            <Route path="/cve-management" element={<ProtectedRoute><CVEManagementDashboard /></ProtectedRoute>} />
            <Route path="/tenant-management" element={<ProtectedRoute><TenantManagement /></ProtectedRoute>} />
            <Route path="/earnings" element={<ProtectedRoute><EarningsComponent /></ProtectedRoute>} />
            <Route path="/earnings/dashboard" element={<ProtectedRoute><EarningsDashboard /></ProtectedRoute>} />
            <Route path="/image-upload" element={<ProtectedRoute><ImageUploadComponent /></ProtectedRoute>} />
            <Route path="/creator-profiles" element={<ProtectedRoute><CreatorProfilesPage /></ProtectedRoute>} />
            <Route path="/watermark" element={<ProtectedRoute><WatermarkPage /></ProtectedRoute>} />
            <Route path="/subscription" element={<ProtectedRoute><SubscriptionPage /></ProtectedRoute>} />
            <Route path="/content-management" element={<ProtectedRoute><ContentManagementPage /></ProtectedRoute>} />
            <Route path="/messages" element={<ProtectedRoute><MessagingPage /></ProtectedRoute>} />
            <Route path="/creator-analytics" element={<ProtectedRoute><CreatorAnalyticsPage /></ProtectedRoute>} />
            <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
            <Route path="/integrations" element={<ProtectedRoute><LiveIntegrationsPage /></ProtectedRoute>} />
            <Route path="/aws-media" element={<ProtectedRoute><AWSMediaProcessingPage /></ProtectedRoute>} />
            <Route path="/aws-livestream" element={<ProtectedRoute><AWSLiveStreamingPage /></ProtectedRoute>} />
            <Route path="/aws-comms" element={<ProtectedRoute><AWSWorkMailPinpointPage /></ProtectedRoute>} />
            <Route path="/aws-security" element={<ProtectedRoute><AWSWafSecretsPage /></ProtectedRoute>} />
            <Route path="/oauth/callback" element={<OAuthCallbackPage />} />

            {/* Business routes */}
            <Route path="/business" element={<ProtectedRoute><BusinessIdentifiers /></ProtectedRoute>} />
            <Route path="/business/upc" element={<ProtectedRoute><UPCGenerator /></ProtectedRoute>} />
            <Route path="/business/isrc" element={<ProtectedRoute><ISRCGenerator /></ProtectedRoute>} />
            <Route path="/business/products" element={<ProtectedRoute><ProductManagement /></ProtectedRoute>} />

            {/* DDEX routes */}
            <Route path="/ddex" element={<ProtectedRoute><DDEXERNCreator /></ProtectedRoute>} />
            <Route path="/ddex/ern" element={<ProtectedRoute><DDEXERNCreator /></ProtectedRoute>} />
            <Route path="/ddex/cwr" element={<ProtectedRoute><DDEXCWRCreator /></ProtectedRoute>} />
            <Route path="/ddex/messages" element={<ProtectedRoute><DDEXMessageList /></ProtectedRoute>} />
            <Route path="/ddex/identifiers" element={<ProtectedRoute><DDEXIdentifierGenerator /></ProtectedRoute>} />

            {/* Music Reports routes */}
            <Route path="/music-reports" element={<ProtectedRoute><MusicReportsDashboard /></ProtectedRoute>} />
            <Route path="/music-reports/dashboard" element={<ProtectedRoute><MusicReportsDashboard /></ProtectedRoute>} />

            {/* Agency Onboarding routes */}
            <Route path="/agency/register" element={<ProtectedRoute><AgencyRegistrationWizard /></ProtectedRoute>} />
            <Route path="/agency/dashboard" element={<ProtectedRoute><AgencyDashboard /></ProtectedRoute>} />
            <Route path="/agency/license-builder" element={<ProtectedRoute><LicenseBuilder /></ProtectedRoute>} />
            <Route path="/agency/royalty-tracker" element={<ProtectedRoute><RoyaltyTracker /></ProtectedRoute>} />

            {/* Sponsorship routes */}
            <Route path="/sponsorship" element={<ProtectedRoute><SponsorshipDashboard /></ProtectedRoute>} />
            <Route path="/sponsorship/deals" element={<ProtectedRoute><SponsorshipDealCreator /></ProtectedRoute>} />
            <Route path="/sponsorship/metrics" element={<ProtectedRoute><MetricsRecorder /></ProtectedRoute>} />

            {/* Tax routes */}
            <Route path="/tax" element={<ProtectedRoute><TaxDashboard /></ProtectedRoute>} />
            <Route path="/tax/1099" element={<ProtectedRoute><Form1099Management /></ProtectedRoute>} />
            <Route path="/tax/reports" element={<ProtectedRoute><TaxReports /></ProtectedRoute>} />
            <Route path="/tax/business" element={<ProtectedRoute><BusinessTaxInfo /></ProtectedRoute>} />
            <Route path="/tax/licenses" element={<ProtectedRoute><BusinessLicenseManagement /></ProtectedRoute>} />
            <Route path="/tax/compliance" element={<ProtectedRoute><ComplianceDashboard /></ProtectedRoute>} />
            <Route path="/social-strategy" element={<ProtectedRoute><SocialMediaStrategyDashboard /></ProtectedRoute>} />
            <Route path="/content-ingestion" element={<ProtectedRoute><ContentIngestionDashboard /></ProtectedRoute>} />
            <Route path="/comprehensive-workflow" element={<ProtectedRoute><ComprehensiveWorkflowDashboard /></ProtectedRoute>} />
            <Route path="/social-media-phases-5-10" element={<ProtectedRoute><SocialMediaPhases5To10Dashboard /></ProtectedRoute>} />
            <Route path="/real-time-royalty-engine" element={<ProtectedRoute><RealTimeRoyaltyDashboard /></ProtectedRoute>} />
            <Route path="/workflow-integration" element={<ProtectedRoute><WorkflowIntegrationDashboard /></ProtectedRoute>} />
            <Route path="/support-center" element={<ProtectedRoute><SupportSystemDashboard /></ProtectedRoute>} />
            <Route path="/comprehensive-platform" element={<ProtectedRoute><ComprehensivePlatform /></ProtectedRoute>} />
            <Route path="/comprehensive-licensing" element={<ProtectedRoute><ComprehensiveLicensingComponents /></ProtectedRoute>} />
            <Route path="/content-removal" element={<ProtectedRoute><ContentRemovalDashboard /></ProtectedRoute>} />
            <Route path="/about" element={<AboutPage />} />

            {/* Industry routes */}
            <Route path="/industry" element={<ProtectedRoute><IndustryDashboard /></ProtectedRoute>} />
            <Route path="/industry/partners" element={<ProtectedRoute><IndustryPartners /></ProtectedRoute>} />
            <Route path="/industry/distribution" element={<ProtectedRoute><GlobalDistribution /></ProtectedRoute>} />
            <Route path="/industry/coverage" element={<ProtectedRoute><IndustryCoverage /></ProtectedRoute>} />
            <Route path="/industry/ipi" element={<ProtectedRoute><IPIManagement /></ProtectedRoute>} />
            <Route path="/industry/identifiers" element={<ProtectedRoute><IndustryIdentifiersManagement /></ProtectedRoute>} />
            <Route path="/industry/entertainment" element={<ProtectedRoute><EnhancedEntertainmentDashboard /></ProtectedRoute>} />
            <Route path="/industry/photography" element={<ProtectedRoute><PhotographyServices /></ProtectedRoute>} />
            <Route path="/industry/video" element={<ProtectedRoute><VideoProductionServices /></ProtectedRoute>} />
            <Route path="/industry/monetization" element={<ProtectedRoute><MonetizationOpportunities /></ProtectedRoute>} />
            <Route path="/industry/mdx" element={<ProtectedRoute><MusicDataExchange /></ProtectedRoute>} />
            <Route path="/industry/mlc" element={<ProtectedRoute><MechanicalLicensingCollective /></ProtectedRoute>} />

            {/* Label routes */}
            <Route path="/label/dashboard" element={<ProtectedRoute><LabelDashboard /></ProtectedRoute>} />
            <Route path="/label/directory" element={<ProtectedRoute><LabelDirectory /></ProtectedRoute>} />
            <Route path="/uln" element={<ProtectedRoute><ULNDashboard /></ProtectedRoute>} />
            <Route path="/label/projects" element={<ProtectedRoute><ProjectManagement /></ProtectedRoute>} />
            <Route path="/label/marketing" element={<ProtectedRoute><MarketingManagement /></ProtectedRoute>} />
            <Route path="/label/financial" element={<ProtectedRoute><FinancialManagement /></ProtectedRoute>} />
            <Route path="/label/royalties" element={<ProtectedRoute><RoyaltySplitManager /></ProtectedRoute>} />

            {/* Payment routes */}
            <Route path="/payments" element={<ProtectedRoute><PaymentComponent /></ProtectedRoute>} />
            <Route path="/payment/packages" element={<ProtectedRoute><PaymentPackages /></ProtectedRoute>} />
            <Route path="/payment/checkout/:packageId" element={<ProtectedRoute><EnhancedPaymentCheckout /></ProtectedRoute>} />
            <Route path="/payment/status" element={<ProtectedRoute><PaymentStatus /></ProtectedRoute>} />
            <Route path="/payment/success" element={<ProtectedRoute><div className="p-8"><h1 className="text-2xl font-bold text-green-600">Payment Successful!</h1><p>Your payment has been processed successfully.</p></div></ProtectedRoute>} />
            <Route path="/payment/cancel" element={<ProtectedRoute><div className="p-8"><h1 className="text-2xl font-bold text-red-600">Payment Cancelled</h1><p>Your payment was cancelled. You can try again.</p></div></ProtectedRoute>} />
            <Route path="/payment/bank" element={<ProtectedRoute><BankAccountManager /></ProtectedRoute>} />
            <Route path="/payment/wallet" element={<ProtectedRoute><DigitalWalletManager /></ProtectedRoute>} />

            {/* Licensing routes */}
            <Route path="/licensing" element={<ProtectedRoute><LicensingDashboard /></ProtectedRoute>} />
            <Route path="/licensing/platforms" element={<ProtectedRoute><PlatformLicenseManager /></ProtectedRoute>} />
            <Route path="/licensing/status" element={<ProtectedRoute><LicensingStatus /></ProtectedRoute>} />

            {/* GS1 routes */}
            <Route path="/gs1" element={<ProtectedRoute><GS1Dashboard /></ProtectedRoute>} />

            {/* Admin routes */}
            <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
            <Route path="/admin/content" element={<AdminRoute><ContentModerationComponent /></AdminRoute>} />
            <Route path="/admin/analytics" element={<AdminRoute><AdminAnalytics /></AdminRoute>} />
            <Route path="/admin/notifications" element={<AdminRoute><AdminNotificationsPage /></AdminRoute>} />
            <Route path="/admin/ddex" element={<AdminRoute><DDEXAdminDashboard /></AdminRoute>} />
            <Route path="/admin/sponsorship" element={<AdminRoute><AdminSponsorshipOverview /></AdminRoute>} />
            <Route path="/admin/industry" element={<AdminRoute><IndustryDashboard /></AdminRoute>} />
            <Route path="/admin/domain" element={<AdminRoute><DomainConfigPage /></AdminRoute>} />
            <Route path="/admin/rds-upgrade" element={<AdminRoute><RDSUpgradePage /></AdminRoute>} />
            
            {/* 404 Route - Must be last */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
          </Suspense>
          </ChunkErrorBoundary>
          
          {/* Footer */}
          <footer className="bg-gray-800 text-white py-8 mt-16">
            <div className="max-w-7xl mx-auto px-4">
              <div className="text-center">
                <img 
                  src="/big-mann-logo.png" 
                  alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
                  className="w-16 h-16 object-contain mx-auto mb-4"
                />
                <h3 className="text-xl font-bold mb-2">Big Mann Entertainment</h3>
                <p className="text-gray-400 mb-4">
                  Founded and owned by John LeGerron Spivey, Big Mann Entertainment is your complete media distribution empire, connecting artists with over 114 global platforms.
                </p>
                <div className="border-t border-gray-700 pt-4">
                  <p className="text-sm text-gray-500">
                    © 2026 Big Mann Entertainment. All rights reserved. Owned and operated by John LeGerron Spivey.
                  </p>
                </div>
              </div>
            </div>
          </footer>
        </div>
        <Toaster position="top-right" richColors closeButton />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
