import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, User, Award, Clock, Book, TrendingUp, Volume2, Eye } from "lucide-react";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import NavigationHeader from "@/components/ui/navigation-header";
import WritingPracticeResult from "@/components/WritingPracticeResult";

const GuardianStudentAnalytics = () => {
  const navigate = useNavigate();
  const { studentId } = useParams();

  // Mock student data
  const [student] = useState({
    id: 1,
    name: "김민지",
    age: 8,
    profileColor: "bg-warm-400",
    compositeScore: 82,
    progressRate: 65,
    comprehensionScore: 85,
    fluencyScore: 78,
    participationScore: 88
  });

  // Mock reading speed data
  const readingSpeedData = [
    { page: 1, wpm: 45 },
    { page: 2, wpm: 52 },
    { page: 3, wpm: 38 },
    { page: 4, wpm: 47 },
    { page: 5, wpm: 55 },
    { page: 6, wpm: 51 },
    { page: 7, wpm: 42 },
    { page: 8, wpm: 58 }
  ];

  // Mock difficult vocabulary data
  const difficultWords = [
    { word: "광합성", frequency: 12, phonemes: ["ㄱ", "ㅗ", "ㅏ", "ㅇ", "ㅎ", "ㅏ", "ㅂ", "ㅅ", "ㅓ", "ㅇ"] },
    { word: "생태계", frequency: 8, phonemes: ["ㅅ", "ㅐ", "ㅇ", "ㅌ", "ㅐ", "ㄱ", "ㅖ"] },
    { word: "엽록소", frequency: 6, phonemes: ["ㅇ", "ㅕ", "ㅂ", "ㄹ", "ㅗ", "ㄱ", "ㅅ", "ㅗ"] },
    { word: "산소", frequency: 5, phonemes: ["ㅅ", "ㅏ", "ㄴ", "ㅅ", "ㅗ"] },
    { word: "이산화탄소", frequency: 4, phonemes: ["ㅇ", "ㅣ", "ㅅ", "ㅏ", "ㄴ", "ㅎ", "ㅗ", "ㅏ", "ㅌ", "ㅏ", "ㄴ", "ㅅ", "ㅗ"] }
  ];

  // Mock assigned documents
  const assignedDocuments = [
    { id: 1, title: "우리 동네 동물들", progress: 100, totalPages: 20, currentPage: 20 },
    { id: 2, title: "우주 탐험 이야기", progress: 65, totalPages: 25, currentPage: 16 },
    { id: 3, title: "마법의 숲 모험", progress: 0, totalPages: 18, currentPage: 1 }
  ];

  const scoreData = [
    { name: "이해도", value: student.comprehensionScore, color: "#8B5CF6" },
    { name: "유창성", value: student.fluencyScore, color: "#06B6D4" },
    { name: "참여도", value: student.participationScore, color: "#10B981" }
  ];

  const chartConfig = {
    wpm: {
      label: "읽기 속도 (WPM)",
      color: "#8B5CF6"
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      <NavigationHeader userType="guardian" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={() => navigate("/guardian/students")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              학생 목록으로
            </Button>
            <div className="flex items-center space-x-3">
              <div className={`w-12 h-12 ${student.profileColor} rounded-full flex items-center justify-center`}>
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-800">{student.name} 학습 분석</h2>
                <p className="text-gray-600">{student.age}세 • 상세 학습 현황</p>
              </div>
            </div>
          </div>
          <Button className="bg-primary hover:bg-primary/90">
            <Award className="w-4 h-4 mr-2" />
            AI 지도 보고서 생성
          </Button>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">개요</TabsTrigger>
            <TabsTrigger value="fluency">유창성 분석</TabsTrigger>
            <TabsTrigger value="vocabulary">어휘 및 음운 능력</TabsTrigger>
            <TabsTrigger value="writing">쓰기 연습 결과</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Composite Score */}
              <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
                <CardHeader>
                  <CardTitle className="text-lg">학습 종합 점수</CardTitle>
                  <CardDescription>이해도, 유창성, 참여도 종합 평가</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-primary mb-2">{student.compositeScore}</div>
                    <div className="text-sm text-gray-600">/ 100점</div>
                    <Progress value={student.compositeScore} className="mt-4" />
                  </div>
                </CardContent>
              </Card>

              {/* Progress Rate */}
              <Card className="border-green-200/50 bg-gradient-to-br from-green-50/50 to-green-100/50">
                <CardHeader>
                  <CardTitle className="text-lg">교안 진행률</CardTitle>
                  <CardDescription>참여도와 노력을 반영한 진행률</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-green-600 mb-2">{student.progressRate}%</div>
                    <div className="text-sm text-gray-600">평균 진행률</div>
                    <Progress value={student.progressRate} className="mt-4" />
                  </div>
                </CardContent>
              </Card>

              {/* Score Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">세부 점수</CardTitle>
                  <CardDescription>영역별 상세 분석</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {scoreData.map((score) => (
                      <div key={score.name} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{score.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-16 h-2 bg-gray-200 rounded-full">
                            <div 
                              className="h-2 rounded-full" 
                              style={{ 
                                width: `${score.value}%`, 
                                backgroundColor: score.color 
                              }}
                            />
                          </div>
                          <span className="text-sm font-medium">{score.value}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Assigned Documents */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">할당된 교안 목록</CardTitle>
                <CardDescription>현재 학습 중인 교안들의 진행 상황</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {assignedDocuments.map((doc) => (
                    <Card key={doc.id} className="border-gray-100">
                      <CardContent className="p-4">
                        <h4 className="font-semibold mb-2">{doc.title}</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">진행률</span>
                            <span className="font-medium">{doc.progress}%</span>
                          </div>
                          <Progress value={doc.progress} className="h-1" />
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>{doc.currentPage}/{doc.totalPages} 페이지</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Fluency Analysis Tab */}
          <TabsContent value="fluency" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">페이지별 읽기 속도 변화</CardTitle>
                <CardDescription>읽기 유창성 발달 과정을 확인해보세요</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={readingSpeedData}>
                      <XAxis dataKey="page" />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line 
                        type="monotone" 
                        dataKey="wpm" 
                        stroke="var(--color-wpm)" 
                        strokeWidth={2}
                        dot={{ fill: "var(--color-wpm)" }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Vocabulary Tab */}
          <TabsContent value="vocabulary" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Difficult Words */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">도움이 필요했던 어휘</CardTitle>
                  <CardDescription>자주 찾아본 단어들 (빈도순)</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {difficultWords.map((word, index) => (
                      <div key={word.word} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                        <div className="flex items-center space-x-3">
                          <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">
                            {index + 1}
                          </div>
                          <span className="font-medium">{word.word}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">{word.frequency}회</span>
                          <Volume2 className="w-4 h-4 text-gray-400" />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Phoneme Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">음운 학습 카드</CardTitle>
                  <CardDescription>단어를 클릭하여 음운 분석 결과를 확인하세요</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <h4 className="font-bold text-lg mb-4 text-center">광합성</h4>
                    <div className="grid grid-cols-5 gap-2 mb-4">
                      {difficultWords[0].phonemes.map((phoneme, index) => (
                        <div key={index} className="w-8 h-8 bg-white rounded-lg flex items-center justify-center font-bold text-blue-600 border border-blue-200">
                          {phoneme}
                        </div>
                      ))}
                    </div>
                    <div className="text-center space-y-2">
                      <p className="text-sm text-gray-600">자소-음소 대응 연습</p>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => navigate(`/guardian/students/${studentId}/writing-practice`)}
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        쓰기 연습 결과 보기
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Learning Style Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">학습 태도 및 환경 리포트</CardTitle>
                <CardDescription>나만의 학습법 분석</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-semibold text-green-800 mb-2">선호하는 학습 방식</h4>
                    <p className="text-sm text-green-700">TTS 듣기 기능을 자주 사용해요</p>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-2">집중 시간대</h4>
                    <p className="text-sm text-blue-700">오후 2-4시에 가장 활발해요</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-semibold text-purple-800 mb-2">화면 설정</h4>
                    <p className="text-sm text-purple-700">큰 글씨, 세피아 톤을 선호해요</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Writing Practice Results Tab */}
          <TabsContent value="writing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">쓰기 연습 결과 보기</CardTitle>
                <CardDescription>학생이 어휘 학습 중 연습한 쓰기 결과를 확인하세요</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">쓰기 연습 결과를 더 자세히 보시려면 아래 버튼을 클릭하세요.</p>
                  <Button 
                    onClick={() => navigate(`/guardian/students/${studentId}/writing-practice`)}
                    className="bg-primary hover:bg-primary/90"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    쓰기 연습 결과 전체 보기
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default GuardianStudentAnalytics;
