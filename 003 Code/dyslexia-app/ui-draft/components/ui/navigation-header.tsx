
import { Button } from "@/components/ui/button";
import { useNavigate, useLocation } from "react-router-dom";
import { Book, User, Users, FolderOpen, BarChart3, Store } from "lucide-react";

interface NavigationHeaderProps {
  userType: "guardian" | "student";
}

const NavigationHeader = ({ userType }: NavigationHeaderProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const guardianNavItems = [
    { path: "/guardian/dashboard", label: "대시보드", icon: BarChart3 },
    { path: "/guardian/store", label: "교안 스토어", icon: Store },
    { path: "/guardian/students", label: "학생 관리", icon: Users },
    { path: "/guardian/documents", label: "교안 보관함", icon: FolderOpen },
    { path: "/guardian/profile", label: "내 정보", icon: User },
  ];

  const navItems = userType === "guardian" ? guardianNavItems : [];

  const isActive = (path: string) => {
    return location.pathname === path || 
           (path === "/guardian/store" && location.pathname.startsWith("/guardian/store"));
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
              <Book className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">리딩브릿지</h1>
              <p className="text-sm text-gray-600">
                {userType === "guardian" ? "보호자 대시보드" : "나의 책장"}
              </p>
            </div>
          </div>

          {/* Navigation Menu */}
          {userType === "guardian" && (
            <nav className="hidden md:flex space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.path}
                    onClick={() => navigate(item.path)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                      isActive(item.path)
                        ? "bg-primary/10 text-primary"
                        : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{item.label}</span>
                  </button>
                );
              })}
            </nav>
          )}

          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={() => navigate("/login")}>
              로그아웃
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default NavigationHeader;
