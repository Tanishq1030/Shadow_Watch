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

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        // Check session on mount
        const storedUser = localStorage.getItem("shadow_watch_user");
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const login = async (email: string, password?: string) => {
        // Simulate API network delay
        await new Promise((resolve) => setTimeout(resolve, 800));

        const usersStr = localStorage.getItem("shadow_watch_users_db");
        const users = usersStr ? JSON.parse(usersStr) : [];

        const foundUser = users.find((u: any) => u.email === email);

        if (!foundUser) {
            toast.error("Account not found. Please sign up.");
            throw new Error("User not found");
        }

        if (password && foundUser.password !== password) {
            toast.error("Invalid credentials.");
            throw new Error("Invalid password");
        }

        // Success
        const activeUser = {
            name: foundUser.name,
            email: foundUser.email,
            organization: foundUser.organization
        };

        setUser(activeUser);
        localStorage.setItem("shadow_watch_user", JSON.stringify(activeUser));
        toast.success("Welcome back!");
    };

    const register = async (name: string, email: string, organization: string, password?: string) => {
        await new Promise((resolve) => setTimeout(resolve, 800));

        const usersStr = localStorage.getItem("shadow_watch_users_db");
        const users = usersStr ? JSON.parse(usersStr) : [];

        if (users.find((u: any) => u.email === email)) {
            toast.error("Email already exists. Please sign in.");
            throw new Error("Email exists");
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            toast.error("Please enter a valid email address.");
            throw new Error("Invalid email");
        }

        // Stricter Password Validation
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
        if (password && !passwordRegex.test(password)) {
            toast.error("Password must be at least 8 chars, with 1 uppercase, 1 number, and 1 special char.");
            throw new Error("Weak password");
        }

        const newUser = { name, email, organization, password }; // Storing password in plaintext for MOCK ONLY
        users.push(newUser);
        localStorage.setItem("shadow_watch_users_db", JSON.stringify(users));

        const activeUser = { name, email, organization };
        setUser(activeUser);
        localStorage.setItem("shadow_watch_user", JSON.stringify(activeUser));
        toast.success("Account created successfully!");
    };

    const socialLogin = async (provider: "google" | "microsoft" | "x") => {
        await new Promise((resolve) => setTimeout(resolve, 800));

        // Simulate social login success
        const mockUser = {
            name: "Demo User",
            email: `user@${provider}.com`,
            organization: `${provider.charAt(0).toUpperCase() + provider.slice(1)} Login`,
        };

        setUser(mockUser);
        localStorage.setItem("shadow_watch_user", JSON.stringify(mockUser));
        toast.success(`Signed in with ${provider.charAt(0).toUpperCase() + provider.slice(1)}`);
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem("shadow_watch_user");
        toast.success("Logged out successfully");
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
