import React, { createContext, useContext, useState, useEffect } from "react";
import { toast } from "sonner";

interface User {
    name: string;
    email: string;
    organization: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password?: string) => Promise<void>;
    register: (name: string, email: string, organization: string, password?: string) => Promise<void>;
    logout: () => void;
    socialLogin: (provider: "google" | "microsoft" | "x") => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = "https://shadow-watch-ten.vercel.app";

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        const storedUser = localStorage.getItem("shadow_watch_user");
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const login = async (email: string, password?: string) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.detail || "Login failed");
                throw new Error(data.detail || "Login failed");
            }

            setUser(data.user);
            localStorage.setItem("shadow_watch_user", JSON.stringify(data.user));
            toast.success("Welcome back!");
        } catch (error: any) {
            if (!(error instanceof Error)) throw error;
            throw error;
        }
    };

    const register = async (name: string, email: string, organization: string, password?: string) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, organization, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.detail || "Registration failed");
                throw new Error(data.detail || "Registration failed");
            }

            setUser(data.user);
            localStorage.setItem("shadow_watch_user", JSON.stringify(data.user));
            toast.success("Account created successfully!");
        } catch (error: any) {
            if (!(error instanceof Error)) throw error;
            throw error;
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem("shadow_watch_user");
        toast.success("Logged out successfully");
    };

    const socialLogin = async () => {
        toast.info("Social login is currently disabled. Please use the form.");
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, register, logout, socialLogin }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
