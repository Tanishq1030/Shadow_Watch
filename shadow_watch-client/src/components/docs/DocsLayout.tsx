import { Outlet } from 'react-router-dom';
import { DocsSidebar } from './DocsSidebar';
import { ParallaxBackground } from '../ParallaxBackground';
import { useRef } from 'react';
import { DocsContext } from '@/context/DocsContext';
import { ScrollToTop } from '../ScrollToTop';

export const DocsLayout = () => {
    const mainRef = useRef<HTMLElement>(null);

    return (
        <DocsContext.Provider value={{ mainRef }}>
            <ScrollToTop mainRef={mainRef} />
            <div className="min-h-screen bg-black text-white flex relative">
                <ParallaxBackground />

                {/* Left Sidebar */}
                <DocsSidebar />

                {/* Main Content - Responsive */}
                <main ref={mainRef} className="flex-1 px-4 py-6 md:px-8 md:py-8 lg:px-16 lg:py-12 mt-16 md:mt-0">
                    <Outlet />
                </main>
            </div>
        </DocsContext.Provider>
    );
};
