import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import { AuthProvider } from "./context/AuthContext";
import SignUp from "./pages/auth/SignUp";
import SignIn from "./pages/auth/SignIn";
import GetLicense from "./pages/GetLicense";
import { DocsLayout } from "./components/docs/DocsLayout";
import { ScrollToTop } from "./components/ScrollToTop";
import { useRef } from "react";
import { GettingStarted } from "./pages/docs/GettingStarted";
import { BehavioralIntelligence } from "./pages/docs/BehavioralIntelligence";
import { Installation } from "./pages/docs/Installation";
import { CoreConcepts } from "./pages/docs/CoreConcepts";
import { FastAPIIntegration } from "./pages/docs/FastAPIIntegration";
import { StandaloneUsage } from "./pages/docs/StandaloneUsage";
import { EcommerceUseCase } from "./pages/docs/EcommerceUseCase";
import { GamingPlatform } from "./pages/docs/GamingPlatform";
import { SocialMedia } from "./pages/docs/SocialMedia";
import { PostgreSQLSetup } from "./pages/docs/PostgreSQLSetup";
import { RedisCaching } from "./pages/docs/RedisCaching";
import { MySQLConfiguration } from "./pages/docs/MySQLConfiguration";
import { ExtendingShadowWatch } from "./pages/docs/ExtendingShadowWatch";
import { EntropyEngine } from "./pages/docs/EntropyEngine";
import { FingerprintVerification } from "./pages/docs/FingerprintVerification";
import { TrustScoreAlgorithm } from "./pages/docs/TrustScoreAlgorithm";
import { LicenseManagement } from "./pages/docs/LicenseManagement";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/signin" element={<SignIn />} />
            <Route path="/get-license" element={<GetLicense />} />

            {/* Documentation */}
            <Route path="/docs" element={<DocsLayout />}>
              <Route index element={<GettingStarted />} />
              {/* Intelligence Hub */}
              <Route path="getting-started" element={<GettingStarted />} />
              <Route path="behavioral-intelligence" element={<BehavioralIntelligence />} />
              <Route path="installation" element={<Installation />} />
              <Route path="core-concepts" element={<CoreConcepts />} />
              {/* Deploy Watchers */}
              <Route path="fastapi-integration" element={<FastAPIIntegration />} />
              <Route path="standalone-usage" element={<StandaloneUsage />} />
              <Route path="ecommerce" element={<EcommerceUseCase />} />
              <Route path="gaming" element={<GamingPlatform />} />
              <Route path="social-media" element={<SocialMedia />} />
              {/* Memory Vault */}
              <Route path="postgresql" element={<PostgreSQLSetup />} />
              <Route path="redis" element={<RedisCaching />} />
              <Route path="mysql" element={<MySQLConfiguration />} />
              <Route path="extending" element={<ExtendingShadowWatch />} />
              {/* Mastery */}
              <Route path="entropy-engine" element={<EntropyEngine />} />
              <Route path="fingerprint-verification" element={<FingerprintVerification />} />
              <Route path="trust-score" element={<TrustScoreAlgorithm />} />
              <Route path="license-management" element={<LicenseManagement />} />
            </Route>

            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
