
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import NavigationHeader from "@/components/ui/navigation-header";
import { 
  Users, 
  BookOpen, 
  TrendingUp, 
  Clock, 
  FileText, 
  Star,
  Store,
  Plus,
  UserPlus,
  BarChart3,
  Upload
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import PraiseModal from "@/components/PraiseModal";
import StudentInviteModal from "@/components/StudentInviteModal";
import { useToast } from "@/hooks/use-toast";

const GuardianDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Mock data
  const [students] = useState([
    {
      id: 1,
      name: "민지",
      grade: "초등학교 2학년",
      currentBook: "우리 동네 동물들",
      progress: 65,
      weeklyReadingTime: 120, // minutes
      status: "active",
      lastActivity: "2시간 전"
    },
    {
      id: 2,
      name: "준호",
      grade: "초등학교 1학년", 
      currentBook: "마법의 숲 모험",
      progress: 30,
      weeklyReadingTime: 85,
      status: "needs_attention",
      lastActivity: "1일 전"
    },
  ]);

  const [recentDocuments] = useState([
    {
      id: 1,
      title: "우리 동네 동물들",
      type: "자체 제작",
      uploadDate: "2024-01-15",
      status: "processing"
    },
    {
      id: 2,
      title: "우주 탐험 이야기", 
      type: "스토어 구매",
      uploadDate: "2024-01-10",
      status: "completed"
    }
  ]);

  const [recentActivities] = useState([
    {
      id: 1,
      type: "praise",
      student: "민지",
      description: "독서 목표 달성",
      time: "30분 전",
      icon: Star
    },
    {
      id: 2,
      type: "document",
      student: "준호",
      description: "새 교안 배정: 마법의 숲 모험",
      time: "2시간 전",
      icon: BookOpen
    },
    {
      id: 3,
      type: "progress",
      student: "민지",
      description: "학습 진도 80% 달성",
      time: "4시간 전",
      icon: TrendingUp
    }
  ]);

  const [isPraiseModalOpen, setIsPraiseModalOpen] = useState(false);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<{id: number, name: string} | null>(null);

  const handlePraiseStudent = (studentId: number, studentName: string) => {
    setSelectedStudent({id: studentId, name: studentName});
    setIsPraiseModalOpen(true);
  };

  const handleSavePraise = (praise: string, stickers: number) => {
    console.log('Saving praise:', { studentId: selectedStudent?.id, praise, stickers });
    toast({
      title: "칭찬이 전달되었습니다! ⭐",
      description: `${selectedStudent?.name}에게 ${stickers}개의 스티커와 함께 칭찬을 보냈습니다.`,
    });
  };

  const handleStudentInvite = () => {
    setIsInviteModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-25 via-indigo-25 to-purple-25">
      <NavigationHeader userType="guardian" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">대시보드</h1>
          <p className="text-gray-600">학생들의 학습 현황을 한눈에 확인하세요</p>
        </div>

        {/* Quick Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate("/guardian/documents")}>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Upload className="w-6 h-6 text-blue-600" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="font-semibold text-gray-900">새 교안 업로드</h3>
                  <p className="text-sm text-gray-600">PDF를 업로드하여 AI 변환</p>
                </div>
                <Button size="sm" className="ml-auto">
                  업로드
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={handleStudentInvite}>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-3 bg-green-100 rounded-lg">
                  <UserPlus className="w-6 h-6 text-green-600" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="font-semibold text-gray-900">학생 초대</h3>
                  <p className="text-sm text-gray-600">새로운 학생을 초대</p>
                </div>
                <Button size="sm" variant="outline" className="ml-auto">
                  링크 복사
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate("/guardian/students")}>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-orange-600" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="font-semibold text-gray-900">학습 분석</h3>
                  <p className="text-sm text-gray-600">상세 학습 데이터 확인</p>
                </div>
                <Button size="sm" variant="outline" className="ml-auto">
                  분석
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Recent Activity + Students Overview */}
          <div className="lg:col-span-2 space-y-6">
            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>최근 활동</span>
                </CardTitle>
                <p className="text-sm text-gray-600">최근 7일간의 학습 활동을 확인해보세요</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivities.map((activity) => {
                    const IconComponent = activity.icon;
                    return (
                      <div key={activity.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                        <div className="p-2 bg-white rounded-lg shadow-sm">
                          <IconComponent className="w-4 h-4 text-gray-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              {activity.student}
                            </span>
                            <span className="text-xs text-gray-500">{activity.time}</span>
                          </div>
                          <p className="text-sm text-gray-900 mt-1">{activity.description}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Students Overview */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>학생 현황</span>
                </CardTitle>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => navigate("/guardian/students")}
                >
                  전체 보기
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {students.map((student) => (
                    <div key={student.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                          <span className="text-white font-semibold">{student.name.charAt(0)}</span>
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{student.name}</h3>
                          <p className="text-sm text-gray-600">{student.grade}</p>
                          <p className="text-sm text-gray-500">현재 도서: {student.currentBook}</p>
                        </div>
                      </div>
                      <div className="text-right space-y-2">
                        <div className="flex items-center space-x-2">
                          <Badge variant={student.status === 'active' ? 'default' : 'secondary'}>
                            {student.status === 'active' ? '활발' : '관심 필요'}
                          </Badge>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handlePraiseStudent(student.id, student.name)}
                            className="border-yellow-400 text-yellow-600 hover:bg-yellow-50"
                          >
                            <Star className="w-4 h-4 mr-1" />
                            칭찬하기
                          </Button>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-24">
                            <Progress value={student.progress} className="h-2" />
                          </div>
                          <span className="text-sm font-medium">{student.progress}%</span>
                        </div>
                        <p className="text-xs text-gray-500">마지막 활동: {student.lastActivity}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>빠른 작업</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full justify-start" onClick={() => navigate("/guardian/documents")}>
                  <Plus className="w-4 h-4 mr-2" />
                  새 교안 업로드
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={() => navigate("/guardian/store")}>
                  <Store className="w-4 h-4 mr-2" />
                  교안 스토어 둘러보기
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={() => navigate("/guardian/students")}>
                  <Users className="w-4 h-4 mr-2" />
                  학생 관리
                </Button>
              </CardContent>
            </Card>

            {/* Recent Documents */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <BookOpen className="w-5 h-5" />
                  <span>최근 교안</span>
                </CardTitle>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => navigate("/guardian/documents")}
                >
                  전체 보기
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentDocuments.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-sm">{doc.title}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {doc.type}
                          </Badge>
                          <span className="text-xs text-gray-500">{doc.uploadDate}</span>
                        </div>
                      </div>
                      <Badge 
                        variant={doc.status === 'completed' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {doc.status === 'completed' ? '완료' : '처리중'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Praise Modal */}
      <PraiseModal
        isOpen={isPraiseModalOpen}
        onClose={() => setIsPraiseModalOpen(false)}
        onSavePraise={handleSavePraise}
        studentName={selectedStudent?.name}
      />

      {/* Student Invite Modal */}
      <StudentInviteModal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
      />
    </div>
  );
};

export default GuardianDashboard;
