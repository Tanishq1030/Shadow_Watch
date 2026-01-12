import { ArrowRight, Github, LogOut, User } from "lucide-react";
import { Button } from "./ui/button";
import GitHubStars from "./GitHubStars";
import SearchBox from "./SearchBox";
import { ThemeToggle } from "./ThemeToggle";
import { useAuth } from "@/context/AuthContext";
import { Link, useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex items-center justify-center">
              <img
                src="/shadow-watch-logo.png"
                alt="Shadow Watch Logo"
                className="h-10 w-10 object-contain drop-shadow-[0_0_15px_rgba(168,85,247,0.5)]"
              />
            </div>
            <span className="text-lg font-semibold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">Shadow Watch</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <a href="https://github.com/Tanishq1030/Shadow_Watch/tree/main/docs" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Docs
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Learn
            </a>
            <Link to="/get-license" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Get License Key
            </Link>
            <a
              href="https://github.com/Tanishq1030/Shadow_Watch"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              GitHub
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Case Study
            </a>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <SearchBox />
          <ThemeToggle />
          <GitHubStars />

          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="gap-2 px-2 hover:bg-muted/50">
                  <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-semibold text-primary">
                    {user?.name?.charAt(0) || "U"}
                  </div>
                  <span className="text-sm font-medium hidden sm:inline-block max-w-[100px] truncate">
                    {user?.name}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate("/get-license")}>
                  License Key
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-500 focus:text-red-500">
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/signin">Sign In</Link>
              </Button>
              <Button variant="default" size="sm" className="gap-2" asChild>
                <Link to="/signup">
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
