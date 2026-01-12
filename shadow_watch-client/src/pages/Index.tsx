import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import LogoScroll from "@/components/LogoScroll";
import DataFlowDemo from "@/components/DataFlowDemo";
import CodeDemo from "@/components/CodeDemo";
import BenchmarkSection from "@/components/BenchmarkSection";
import FeaturesGrid from "@/components/FeaturesGrid";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      <LogoScroll />
      {/* <DataFlowDemo /> */}
      <CodeDemo />
      <BenchmarkSection />
      <FeaturesGrid />
      <Footer />
    </div>
  );
};

export default Index;
