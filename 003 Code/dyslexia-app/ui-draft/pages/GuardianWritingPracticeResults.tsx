
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Calendar, Eye, Sparkles, User } from "lucide-react";
import NavigationHeader from "@/components/ui/navigation-header";

interface PracticeImage {
  type: "phoneme" | "syllable" | "word";
  character: string;
  imageUrl: string;
}

interface WritingPracticeLog {
  id: number;
  vocabulary: string;
  practicedAt: string;
  practiceImages: PracticeImage[];
}

const GuardianWritingPracticeResults = () => {
  const navigate = useNavigate();
  const { studentId } = useParams();

  // Mock student data
  const [student] = useState({
    id: parseInt(studentId || "1"),
    name: "김민지",
    age: 8,
    profileColor: "bg-warm-400"
  });

  // Mock data - 실제로는 API에서 받아올 데이터
  const [practiceResults] = useState<WritingPracticeLog[]>([
    {
      id: 1,
      vocabulary: "고래",
      practicedAt: "2025-06-14T10:30:00",
      practiceImages: [
        { type: "phoneme", character: "ㄱ", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅗ", imageUrl: "/placeholder.svg" },
        { type: "syllable", character: "고", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㄹ", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅐ", imageUrl: "/placeholder.svg" },
        { type: "syllable", character: "래", imageUrl: "/placeholder.svg" },
        { type: "word", character: "고래", imageUrl: "/placeholder.svg" }
      ]
    },
    {
      id: 2,
      vocabulary: "사과",
      practicedAt: "2025-06-13T15:20:00",
      practiceImages: [
        { type: "phoneme", character: "ㅅ", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅏ", imageUrl: "/placeholder.svg" },
        { type: "syllable", character: "사", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㄱ", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅗ", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅏ", imageUrl: "/placeholder.svg" },
        { type: "syllable", character: "과", imageUrl: "/placeholder.svg" },
        { type: "word", character: "사과", imageUrl: "/placeholder.svg" }
      ]
    },
    {
      id: 3,
      vocabulary: "나무",
      practicedAt: "2025-06-12T09:15:00",
      practiceImages: [
        { type: "phoneme", character: "ㄴ", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅏ", imageUrl: "/placeholder.svg" },
        { type: "syllable", character: "나", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅁ", imageUrl: "/placeholder.svg" },
        { type: "phoneme", character: "ㅜ", imageUrl: "/placeholder.svg" },
        { type: "syllable", character: "무", imageUrl: "/placeholder.svg" },
        { type: "word", character: "나무", imageUrl: "/placeholder.svg" }
      ]
    }
  ]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getThumbnailImages = (images: PracticeImage[]) => {
    // 썸네일로 보여줄 이미지들 (음절과 완성된 단어 위주)
    const thumbnails = images.filter(img => img.type === "syllable" || img.type === "word");
    return thumbnails.slice(0, 4);
  };

  const PracticeWordCard = ({ practice }: { practice: WritingPracticeLog }) => {
    const thumbnails = getThumbnailImages(practice.practiceImages);
    const remainingCount = practice.practiceImages.length - thumbnails.length;

    return (
      <Card className="border-gray-200 hover:border-primary/30 transition-colors cursor-pointer">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-bold text-primary">{practice.vocabulary}</CardTitle>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(practice.practicedAt)}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid grid-cols-4 gap-2 mb-4">
            {thumbnails.map((image, index) => (
              <div key={index} className="relative">
                <div className="w-12 h-12 bg-blue-50 border-2 border-blue-200 rounded-lg flex items-center justify-center relative overflow-hidden">
                  <span className="text-lg font-bold text-blue-600">{image.character}</span>
                  {index === 3 && remainingCount > 0 && (
                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                      <span className="text-xs text-white font-bold">+{remainingCount}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm" className="w-full">
                <Eye className="w-4 h-4 mr-2" />
                상세보기
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-xl">
                  "{practice.vocabulary}" 쓰기 연습 결과
                  <Badge variant="secondary" className="ml-2">
                    {formatDate(practice.practicedAt)}
                  </Badge>
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-6">
                {/* 음운 학습 카드 (정답지) */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                  <h4 className="font-bold text-center mb-4 text-blue-800">음운 분해 과정 (정답지)</h4>
                  <div className="flex items-center justify-center space-x-2 flex-wrap">
                    {practice.practiceImages
                      .filter(img => img.type === "phoneme")
                      .map((phoneme, index) => (
                        <div key={index} className="w-8 h-8 bg-white rounded border border-blue-300 flex items-center justify-center">
                          <span className="text-sm font-bold text-blue-600">{phoneme.character}</span>
                        </div>
                      ))}
                    <span className="mx-2 text-blue-600 font-bold">=</span>
                    <div className="px-3 py-1 bg-blue-600 text-white rounded font-bold">
                      {practice.vocabulary}
                    </div>
                  </div>
                </div>

                {/* 학생 쓰기 과정 */}
                <div className="space-y-4">
                  <h4 className="font-bold text-lg text-gray-800">학생 쓰기 과정</h4>
                  
                  {/* 각 음절별로 그룹화하여 표시 */}
                  {practice.vocabulary.split('').map((syllable, syllableIndex) => {
                    const syllableImages = practice.practiceImages.filter(img => 
                      img.character === syllable && img.type === "syllable"
                    );
                    const phonemeImages = practice.practiceImages.filter(img => 
                      img.type === "phoneme" && practice.vocabulary.includes(syllable)
                    );

                    return (
                      <div key={syllableIndex} className="border rounded-lg p-4 bg-gray-50">
                        <h5 className="font-semibold mb-3 text-gray-700">"{syllable}" 만들기</h5>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {/* 자음/모음 쓰기 */}
                          {phonemeImages.slice(syllableIndex * 2, (syllableIndex + 1) * 2).map((phoneme, index) => (
                            <div key={index} className="text-center">
                              <p className="text-sm text-gray-600 mb-2">{phoneme.character} 쓰기</p>
                              <div className="w-20 h-20 bg-white border-2 border-gray-300 rounded-lg flex items-center justify-center mx-auto">
                                <span className="text-xl font-bold">{phoneme.character}</span>
                              </div>
                            </div>
                          ))}
                          
                          {/* 합쳐서 음절 쓰기 */}
                          {syllableImages.map((syllableImg, index) => (
                            <div key={index} className="text-center md:col-span-2">
                              <p className="text-sm text-gray-600 mb-2">합쳐서 "{syllable}" 쓰기</p>
                              <div className="w-24 h-24 bg-blue-50 border-2 border-blue-300 rounded-lg flex items-center justify-center mx-auto">
                                <span className="text-2xl font-bold text-blue-600">{syllable}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}

                  {/* 완성된 단어 */}
                  <div className="border-2 border-green-300 rounded-lg p-4 bg-green-50">
                    <h5 className="font-semibold mb-3 text-green-800 text-center">"{practice.vocabulary}" 완성하기</h5>
                    <div className="flex justify-center">
                      <div className="w-32 h-32 bg-white border-2 border-green-400 rounded-lg flex items-center justify-center">
                        <span className="text-3xl font-bold text-green-600">{practice.vocabulary}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI 칭찬 메시지 생성 */}
                <div className="flex justify-center space-x-3 pt-4 border-t">
                  <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
                    <Sparkles className="w-4 h-4 mr-2" />
                    AI로 칭찬 메시지 만들기
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      <NavigationHeader userType="guardian" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={() => navigate(`/guardian/students/${studentId}/analytics`)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              학습 분석으로 돌아가기
            </Button>
            <div className="flex items-center space-x-3">
              <div className={`w-12 h-12 ${student.profileColor} rounded-full flex items-center justify-center`}>
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-800">{student.name} 쓰기 연습 결과</h2>
                <p className="text-gray-600">{student.age}세 • 상세 쓰기 연습 현황</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">쓰기 연습 결과</CardTitle>
            <CardDescription>학생이 어휘 학습 중 연습한 쓰기 결과를 확인하세요</CardDescription>
            <div className="flex justify-end">
              <Badge variant="outline">{practiceResults.length}개의 연습 기록</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {practiceResults.map((practice) => (
                <PracticeWordCard key={practice.id} practice={practice} />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default GuardianWritingPracticeResults;
