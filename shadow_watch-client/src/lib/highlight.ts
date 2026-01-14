import { getSingletonHighlighter } from 'shiki';

export async function highlightPython(code: string): Promise<string> {
    const highlighter = await getSingletonHighlighter({
        themes: ['dark-plus'],
        langs: ['python'],
    });

    return highlighter.codeToHtml(code, {
        lang: 'python',
        theme: 'dark-plus',
    });
}
