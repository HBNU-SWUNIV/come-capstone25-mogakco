
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, Phone, Calendar, Bell, LogOut } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
import NavigationHeader from "@/components/ui/navigation-header";

const GuardianProfile = () => {
  const { toast } = useToast();
  const navigate = useNavigate();

  // Mock user data
  const [userInfo, setUserInfo] = useState({
    name: "김영희",
    email: "younghee.kim@email.com",
    phone: "010-1234-5678",
    joinDate: "2024-01-01",
    connectedStudents: 2
  });

  const [notifications, setNotifications] = useState({
    learningProgress: true,
    weeklyReport: true,
    aiInsights: true
  });

  const handleSaveNotifications = () => {
    toast({
      title: "알림 설정이 저장되었습니다",
      description: "알림 설정이 성공적으로 변경되었습니다.",
    });
  };

  const handleLogout = () => {
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      <NavigationHeader userType="guardian" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800">내 정보</h2>
          <p className="text-gray-600 mt-2">프로필 정보와 설정을 관리해보세요</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Profile Card */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-gray-200 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="w-5 h-5" />
                  <span>기본 정보</span>
                </CardTitle>
                <CardDescription>
                  카카오 로그인으로 연결된 정보입니다
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">이름</Label>
                    <Input
                      id="name"
                      value={userInfo.name}
                      readOnly
                      className="bg-gray-50 cursor-not-allowed"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">이메일</Label>
                    <Input
                      id="email"
                      type="email"
                      value={userInfo.email}
                      readOnly
                      className="bg-gray-50 cursor-not-allowed"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">전화번호</Label>
                  <Input
                    id="phone"
                    value={userInfo.phone}
                    onChange={(e) => setUserInfo({...userInfo, phone: e.target.value})}
                  />
                </div>
                <div className="flex justify-end">
                  <Button onClick={() => toast({ title: "전화번호가 저장되었습니다" })} className="bg-primary hover:bg-primary/90">
                    전화번호 저장
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Notification Settings */}
            <Card className="border-gray-200 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bell className="w-5 h-5" />
                  <span>알림 설정</span>
                </CardTitle>
                <CardDescription>
                  받고 싶은 알림을 설정해보세요
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">학습 진행 알림</h4>
                      <p className="text-sm text-gray-600">학생의 학습 활동을 실시간으로 알려드립니다</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={notifications.learningProgress}
                      onChange={(e) => setNotifications({...notifications, learningProgress: e.target.checked})}
                      className="w-4 h-4"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">주간 리포트</h4>
                      <p className="text-sm text-gray-600">매주 학습 현황 요약을 보내드립니다</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={notifications.weeklyReport}
                      onChange={(e) => setNotifications({...notifications, weeklyReport: e.target.checked})}
                      className="w-4 h-4"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">AI 분석 인사이트</h4>
                      <p className="text-sm text-gray-600">AI가 분석한 학습 개선 제안을 알려드립니다</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={notifications.aiInsights}
                      onChange={(e) => setNotifications({...notifications, aiInsights: e.target.checked})}
                      className="w-4 h-4"
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button onClick={handleSaveNotifications} variant="outline">
                    알림 설정 저장
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Account Summary Sidebar */}
          <div className="space-y-6">
            {/* Account Summary */}
            <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
              <CardHeader>
                <CardTitle className="text-lg">계정 현황</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-primary" />
                      <span>가입일</span>
                    </div>
                    <span className="font-medium">{userInfo.joinDate}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <User className="w-4 h-4 text-primary" />
                      <span>연결된 학생</span>
                    </div>
                    <span className="font-medium">{userInfo.connectedStudents}명</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Security Settings */}
            <Card className="border-gray-200 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <LogOut className="w-5 h-5" />
                  <span>계정</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={handleLogout}
                  variant="outline" 
                  className="w-full justify-start text-red-600 border-red-200 hover:bg-red-50"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  로그아웃
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GuardianProfile;
