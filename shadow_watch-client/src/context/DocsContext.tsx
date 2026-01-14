import { createContext, useContext } from 'react';

interface DocsContextType {
    mainRef: React.RefObject<HTMLElement>;
}

export const DocsContext = createContext<DocsContextType | null>(null);

export const useDocsContext = () => {
    const context = useContext(DocsContext);
    if (!context) {
        throw new Error('useDocsContext must be used within DocsLayout');
    }
    return context;
};
