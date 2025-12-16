import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useNavigate } from "react-router-dom";
import { User, Calendar, Clock, Book, Plus, Eye, Users } from "lucide-react";
import NavigationHeader from "@/components/ui/navigation-header";

const GuardianStudents = () => {
  const navigate = useNavigate();

  // Mock data for students
  const [students] = useState([
    {
      id: 1,
      name: "김민지",
      age: 8,
      profileColor: "bg-warm-400",
      totalProgress: 65,
      lastActivity: "2일 전",
      documentsAssigned: 3,
      totalReadingTime: "2시간 30분",
      averageScore: 85,
      completedDocuments: 2
    },
    {
      id: 2,
      name: "이준호",
      age: 10,
      profileColor: "bg-soft-400",
      totalProgress: 45,
      lastActivity: "1일 전",
      documentsAssigned: 2,
      totalReadingTime: "1시간 45분",
      averageScore: 78,
      completedDocuments: 1
    }
  ]);

  const handleViewAnalytics = (studentId: number) => {
    navigate(`/guardian/students/${studentId}/analytics`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      <NavigationHeader userType="guardian" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-800">학생 관리</h2>
            <p className="text-gray-600 mt-2">등록된 학생들의 학습 현황을 관리하고 분석해보세요</p>
          </div>
          <Button onClick={() => navigate("/guardian/dashboard")} variant="outline">
            <Plus className="w-4 h-4 mr-2" />
            학생 초대하기
          </Button>
        </div>

        {/* Students Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {students.map((student) => (
            <Card key={student.id} className="border-gray-200 hover:border-primary/30 hover:shadow-lg transition-all duration-300">
              <CardHeader className="pb-4">
                <div className="flex items-center space-x-4">
                  <div className={`w-16 h-16 ${student.profileColor} rounded-full flex items-center justify-center`}>
                    <User className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-xl">{student.name}</CardTitle>
                    <CardDescription>{student.age}세</CardDescription>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Progress Overview */}
                <div>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">전체 진행률</span>
                    <span className="font-medium text-primary">{student.totalProgress}%</span>
                  </div>
                  <Progress value={student.totalProgress} className="h-2" />
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <div className="font-medium text-blue-700">평균 점수</div>
                    <div className="text-blue-600">{student.averageScore}점</div>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="font-medium text-green-700">완료 교안</div>
                    <div className="text-green-600">{student.completedDocuments}권</div>
                  </div>
                </div>

                {/* Additional Info */}
                <div className="space-y-2 text-xs text-gray-500 border-t pt-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-3 h-3" />
                      <span>최근 활동</span>
                    </div>
                    <span>{student.lastActivity}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <Book className="w-3 h-3" />
                      <span>할당 교안</span>
                    </div>
                    <span>{student.documentsAssigned}권</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>총 학습시간</span>
                    </div>
                    <span>{student.totalReadingTime}</span>
                  </div>
                </div>

                {/* Action Button */}
                <Button 
                  onClick={() => handleViewAnalytics(student.id)}
                  className="w-full mt-4"
                  variant="outline"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  상세 분석 보기
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State when no students */}
        {students.length === 0 && (
          <Card className="border-dashed border-2 border-gray-300">
            <CardContent className="p-12 text-center">
              <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">아직 등록된 학생이 없습니다</h3>
              <p className="text-gray-500 mb-4">학생을 초대하여 학습 관리를 시작해보세요</p>
              <Button onClick={() => navigate("/guardian/dashboard")}>
                <Plus className="w-4 h-4 mr-2" />
                학생 초대하기
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default GuardianStudents;
