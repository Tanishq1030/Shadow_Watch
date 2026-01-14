import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import "./styles/terminal-styles.css";
import "./styles/code-syntax.css";
import { ThemeProvider } from "next-themes";

createRoot(document.getElementById("root")!).render(
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
        <App />
    </ThemeProvider>
);
