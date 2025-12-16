import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useNavigate } from "react-router-dom";
import { Book, User, Star, Calendar, Palette, Clock, Award, Target } from "lucide-react";
import PraiseDetailModal from "@/components/PraiseDetailModal";

interface Praise {
  id: number;
  content: string;
  stickers: number;
  date: string;
  guardianName: string;
}

const StudentDashboard = () => {
  const navigate = useNavigate();
  
  // Mock data for assigned books
  const [books] = useState([
    {
      id: 1,
      title: "우리 동네 동물들",
      coverColor: "bg-gradient-to-br from-warm-400 to-warm-500",
      progress: 65,
      totalPages: 20,
      currentPage: 13,
      lastRead: "어제"
    },
    {
      id: 2, 
      title: "우주 탐험 이야기",
      coverColor: "bg-gradient-to-br from-soft-400 to-soft-500",
      progress: 30,
      totalPages: 25,
      currentPage: 8,
      lastRead: "3일 전"
    },
    {
      id: 3,
      title: "마법의 숲 모험",
      coverColor: "bg-gradient-to-br from-green-400 to-green-500",
      progress: 0,
      totalPages: 18,
      currentPage: 1,
      lastRead: "아직 읽지 않음"
    }
  ]);

  const [studentName] = useState("현정");
  const [todayStickers] = useState(3);

  // Mock data for recent praises
  const [recentPraises] = useState<Praise[]>([
    {
      id: 1,
      content: "오늘 '우리 동네 동물들' 책을 정말 열심히 읽었네요! 특히 강아지가 나오는 부분을 읽을 때 표정이 너무 밝았어요. 계속 이렇게 열심히 해주세요!",
      stickers: 3,
      date: "오늘",
      guardianName: "엄마"
    },
    {
      id: 2,
      content: "어제 숙제를 끝까지 포기하지 않고 완성해서 정말 대단해요! 어려운 부분도 스스로 해결하려고 노력하는 모습이 훌륭했어요.",
      stickers: 2,
      date: "어제",
      guardianName: "아빠"
    },
    {
      id: 3,
      content: "책 읽기 시간에 집중력이 정말 좋아졌어요. 10분 동안 한 번도 딴짓하지 않고 책에 집중하는 모습이 감동적이었어요!",
      stickers: 2,
      date: "2일 전",
      guardianName: "엄마"
    }
  ]);

  const [selectedPraise, setSelectedPraise] = useState<Praise | null>(null);
  const [isPraiseDetailOpen, setIsPraiseDetailOpen] = useState(false);

  const handleReadBook = (bookId: number, currentPage: number) => {
    navigate(`/student/reader/${bookId}/${currentPage}`);
  };

  const handlePraiseClick = (praise: Praise) => {
    setSelectedPraise(praise);
    setIsPraiseDetailOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 font-dyslexic">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-md">
                <Book className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">리딩브릿지</h1>
                <p className="text-sm text-gray-600">나의 책장</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline" 
                onClick={() => navigate("/student/buddy")}
                className="border-warm-400 text-warm-600 hover:bg-warm-50 rounded-xl"
              >
                <Palette className="w-4 h-4 mr-2" />
                AI 친구
              </Button>
              <div className="w-10 h-10 bg-gradient-to-br from-warm-400 to-warm-500 rounded-xl flex items-center justify-center shadow-md">
                <User className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Welcome Card - spans 3 columns */}
          <Card className="lg:col-span-3 border-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 p-[1px] rounded-2xl shadow-lg">
            <div className="bg-white rounded-2xl h-full">
              <CardContent className="p-8">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-800 mb-2">
                      안녕하세요, {studentName}님! 👋
                    </h2>
                    <p className="text-gray-600 text-lg leading-dyslexic tracking-dyslexic">
                      오늘도 즐거운 읽기 시간을 가져봐요
                    </p>
                  </div>
                  <div className="text-center bg-gradient-to-br from-yellow-50 to-orange-50 p-6 rounded-2xl">
                    <div className="flex items-center justify-center space-x-1 mb-3">
                      {Array.from({length: todayStickers}).map((_, i) => (
                        <Star key={i} className="w-8 h-8 text-yellow-400 fill-current animate-soft-pulse" />
                      ))}
                    </div>
                    <p className="text-lg font-semibold text-gray-700">오늘의 칭찬 스티커</p>
                  </div>
                </div>
              </CardContent>
            </div>
          </Card>

          {/* Today's Progress Card */}
          <Card className="border-0 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl shadow-lg text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <Target className="w-8 h-8 opacity-80" />
                <span className="text-3xl font-bold">65%</span>
              </div>
              <h3 className="text-lg font-semibold mb-1">오늘의 목표</h3>
              <p className="text-green-100 text-sm">13/20 페이지 완료</p>
            </CardContent>
          </Card>

          {/* Book Collection - spans 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-gray-800">나의 책들</h3>
              <span className="px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-medium">
                {books.length}권의 책
              </span>
            </div>

            <div className="grid gap-4">
              {books.map((book) => (
                <Card key={book.id} className="border-0 shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer group rounded-2xl overflow-hidden">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      {/* Book Cover */}
                      <div className={`${book.coverColor} w-16 h-20 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-300 flex-shrink-0`}>
                        <Book className="w-6 h-6 text-white opacity-80" />
                      </div>

                      {/* Book Info */}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-bold text-lg text-gray-800 mb-2 truncate">{book.title}</h4>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">진행률</span>
                            <span className="font-medium text-primary">{book.progress}%</span>
                          </div>
                          <Progress value={book.progress} className="h-2" />
                          
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <div className="flex items-center space-x-1">
                              <Calendar className="w-3 h-3" />
                              <span>{book.lastRead}</span>
                            </div>
                            <span>{book.currentPage}/{book.totalPages} 페이지</span>
                          </div>
                        </div>
                      </div>

                      {/* Action Button */}
                      <Button 
                        onClick={() => handleReadBook(book.id, book.currentPage)}
                        className="bg-primary hover:bg-primary/90 rounded-xl flex-shrink-0"
                        size="sm"
                      >
                        {book.progress === 0 ? '시작' : '계속'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Recent Praises - spans 2 columns */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-800">최근 받은 칭찬 ⭐</h3>
            </div>
            
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {recentPraises.map((praise) => (
                <Card 
                  key={praise.id} 
                  className="border-0 bg-gradient-to-r from-yellow-50 to-orange-50 cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-[1.02] rounded-2xl"
                  onClick={() => handlePraiseClick(praise)}
                >
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-1">
                        {Array.from({length: praise.stickers}).map((_, i) => (
                          <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                        ))}
                      </div>
                      <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded-full">{praise.date}</span>
                    </div>
                    
                    <p className="text-sm text-gray-700 line-clamp-2 leading-relaxed font-dyslexic tracking-dyslexic mb-3">
                      {praise.content}
                    </p>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600 bg-white px-3 py-1 rounded-full">👩‍👧‍👦 {praise.guardianName}</span>
                      <span className="text-xs text-primary font-medium">자세히 보기 →</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Achievement Section - White theme with internal cards */}
          <Card className="lg:col-span-4 border-0 bg-white rounded-2xl shadow-lg">
            <CardContent className="p-8">
              <div className="text-center mb-8">
                <h4 className="text-2xl font-bold text-gray-800 mb-2">이번 주 성취</h4>
                <p className="text-gray-600">열심히 노력한 결과를 확인해보세요</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="border border-gray-100 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="w-16 h-16 bg-yellow-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                      <Book className="w-8 h-8 text-white" />
                    </div>
                    <p className="text-sm text-gray-600 mb-1">완료한 페이지</p>
                    <p className="text-2xl font-bold text-yellow-600">15페이지</p>
                  </CardContent>
                </Card>
                
                <Card className="border border-gray-100 bg-gradient-to-br from-green-50 to-green-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="w-16 h-16 bg-green-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                      <Clock className="w-8 h-8 text-white" />
                    </div>
                    <p className="text-sm text-gray-600 mb-1">읽은 시간</p>
                    <p className="text-2xl font-bold text-green-600">2시간 30분</p>
                  </CardContent>
                </Card>
                
                <Card className="border border-gray-100 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="w-16 h-16 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                      <Award className="w-8 h-8 text-white" />
                    </div>
                    <p className="text-sm text-gray-600 mb-1">받은 스티커</p>
                    <p className="text-2xl font-bold text-blue-600">12개</p>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>

      {/* Praise Detail Modal */}
      <PraiseDetailModal
        isOpen={isPraiseDetailOpen}
        onClose={() => setIsPraiseDetailOpen(false)}
        praise={selectedPraise}
      />
    </div>
  );
};

export default StudentDashboard;
