
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useNavigate, useParams } from "react-router-dom";
import { Book, ArrowLeft, Star, Download, Clock, Users, Calendar, Eye, Heart, Share2, CheckCircle } from "lucide-react";
import NavigationHeader from "@/components/ui/navigation-header";
import { useToast } from "@/hooks/use-toast";

const GuardianStoreDetail = () => {
  const navigate = useNavigate();
  const { documentId } = useParams();
  const { toast } = useToast();

  // Mock data - in real app, fetch by documentId
  const [document] = useState({
    id: 1,
    title: "우리 동네 동물들",
    description: "아이들이 좋아하는 동네 동물들의 이야기를 통해 읽기 능력을 키워보세요. 난독증 학생들을 위해 특별히 설계된 폰트와 레이아웃으로 읽기 부담을 줄이고, 즐거운 학습 경험을 제공합니다.",
    coverImage: "bg-gradient-to-br from-green-400 to-blue-500",
    grade: "1-2학년",
    subject: "국어",
    price: 0,
    type: "free",
    downloads: 1234,
    rating: 4.8,
    reviewCount: 156,
    pages: 20,
    author: "리딩브릿지 팀",
    createdAt: "2024-01-15",
    lastUpdated: "2024-01-20",
    isPopular: true,
    isNew: false,
    tags: ["동물", "읽기", "난독증", "기초"],
    learningObjectives: [
      "동물의 특징과 서식지 이해",
      "기초 어휘력 향상",
      "읽기 자신감 증진",
      "환경 보호 의식 함양"
    ],
    tableOfContents: [
      { page: 1, title: "우리 동네에는 누가 살까요?" },
      { page: 3, title: "공원의 다람쥐 가족" },
      { page: 6, title: "연못의 오리들" },
      { page: 9, title: "나무 위의 새들" },
      { page: 12, title: "땅 속의 작은 친구들" },
      { page: 15, title: "밤에 나오는 동물들" },
      { page: 18, title: "동물들과 함께 살아가기" }
    ],
    features: [
      "난독증 친화적 폰트 사용",
      "TTS(음성 읽기) 지원",
      "단어별 하이라이트 기능",
      "AI 생성 보조 이미지",
      "학습 진도 추적",
      "어휘 설명 팝업"
    ],
    previewPages: [1, 2, 3] // Which pages are available for preview
  });

  const [selectedTab, setSelectedTab] = useState("overview");

  const handleAddToLibrary = () => {
    if (document.type === "free") {
      toast({
        title: "교안 추가 완료!",
        description: `${document.title}이(가) 내 보관함에 추가되었습니다.`,
      });
      navigate("/guardian/documents");
    } else if (document.type === "purchase") {
      toast({
        title: "구매 완료!",
        description: `${document.title}을(를) 구매했습니다. 내 보관함에서 확인하세요.`,
      });
      navigate("/guardian/documents");
    } else if (document.type === "rental") {
      toast({
        title: "대여 완료!",
        description: `${document.title}을(를) 7일간 대여했습니다.`,
      });
      navigate("/guardian/documents");
    }
  };

  const handlePreview = () => {
    navigate(`/guardian/documents/1/preview`);
  };

  const getPriceText = () => {
    if (document.type === "free") return "무료";
    if (document.type === "purchase") return `₩${document.price.toLocaleString()}`;
    if (document.type === "rental") return `₩${document.price.toLocaleString()}/7일`;
    return "";
  };

  const getPriceButtonText = () => {
    if (document.type === "free") return "내 보관함에 무료 추가";
    if (document.type === "purchase") return "구매하기";
    if (document.type === "rental") return "대여하기";
    return "";
  };

  const TabButton = ({ id, label, isActive, onClick }: { id: string, label: string, isActive: boolean, onClick: () => void }) => (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        isActive 
          ? "bg-primary text-white" 
          : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      <NavigationHeader userType="guardian" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate("/guardian/store")}
          className="mb-6 text-gray-600 hover:text-gray-800"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          스토어로 돌아가기
        </Button>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Document Info */}
          <div className="lg:col-span-2 space-y-8">
            {/* Main Info Card */}
            <Card className="border-gray-200 shadow-sm">
              <CardContent className="p-8">
                <div className="flex items-start space-x-6">
                  {/* Cover Image */}
                  <div className={`${document.coverImage} w-48 h-64 rounded-lg flex items-center justify-center shadow-lg flex-shrink-0`}>
                    <div className="text-center text-white p-4">
                      <Book className="w-12 h-12 mx-auto mb-4 opacity-80" />
                      <h4 className="font-bold text-lg leading-tight">{document.title}</h4>
                    </div>
                  </div>

                  {/* Document Details */}
                  <div className="flex-1 space-y-4">
                    <div>
                      <div className="flex items-center space-x-3 mb-2">
                        <h1 className="text-3xl font-bold text-gray-800">{document.title}</h1>
                        {document.isNew && (
                          <Badge className="bg-red-500 text-white">NEW</Badge>
                        )}
                        {document.isPopular && (
                          <Badge className="bg-yellow-500 text-white">인기</Badge>
                        )}
                      </div>
                      <p className="text-gray-600 leading-relaxed">{document.description}</p>
                    </div>

                    {/* Rating and Stats */}
                    <div className="flex items-center space-x-6">
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1">
                          <Star className="w-5 h-5 text-yellow-400 fill-current" />
                          <span className="font-semibold text-gray-800">{document.rating}</span>
                        </div>
                        <span className="text-sm text-gray-500">({document.reviewCount}개 리뷰)</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Download className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{document.downloads.toLocaleString()}회 다운로드</span>
                      </div>
                    </div>

                    {/* Meta Information */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">대상 학년:</span>
                          <span className="font-medium">{document.grade}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">과목:</span>
                          <span className="font-medium">{document.subject}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">페이지 수:</span>
                          <span className="font-medium">{document.pages}페이지</span>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">제작자:</span>
                          <span className="font-medium">{document.author}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">출시일:</span>
                          <span className="font-medium">{document.createdAt}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">업데이트:</span>
                          <span className="font-medium">{document.lastUpdated}</span>
                        </div>
                      </div>
                    </div>

                    {/* Tags */}
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">태그:</span>
                      <div className="flex flex-wrap gap-2">
                        {document.tags.map((tag, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tabbed Content */}
            <Card className="border-gray-200 shadow-sm">
              <CardHeader>
                <div className="flex space-x-2">
                  <TabButton 
                    id="overview" 
                    label="개요" 
                    isActive={selectedTab === "overview"} 
                    onClick={() => setSelectedTab("overview")} 
                  />
                  <TabButton 
                    id="contents" 
                    label="목차" 
                    isActive={selectedTab === "contents"} 
                    onClick={() => setSelectedTab("contents")} 
                  />
                  <TabButton 
                    id="features" 
                    label="특징" 
                    isActive={selectedTab === "features"} 
                    onClick={() => setSelectedTab("features")} 
                  />
                </div>
              </CardHeader>
              <CardContent>
                {selectedTab === "overview" && (
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3">학습 목표</h4>
                      <ul className="space-y-2">
                        {document.learningObjectives.map((objective, index) => (
                          <li key={index} className="flex items-center space-x-3">
                            <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                            <span className="text-gray-700">{objective}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {selectedTab === "contents" && (
                  <div className="space-y-3">
                    <h4 className="font-semibold text-gray-800 mb-4">목차</h4>
                    {document.tableOfContents.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                        <div className="flex items-center space-x-3">
                          <span className="w-8 h-8 bg-primary/10 text-primary rounded-full flex items-center justify-center text-sm font-medium">
                            {item.page}
                          </span>
                          <span className="font-medium text-gray-800">{item.title}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {selectedTab === "features" && (
                  <div className="space-y-4">
                    <h4 className="font-semibold text-gray-800 mb-4">특별 기능</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      {document.features.map((feature, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                          <span className="text-gray-700">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar - Purchase Info */}
          <div className="space-y-6">
            {/* Price and Action Card */}
            <Card className="border-primary/20 shadow-lg sticky top-4">
              <CardContent className="p-6">
                <div className="text-center space-y-4">
                  <div>
                    <span className="text-3xl font-bold text-primary">{getPriceText()}</span>
                    {document.type !== "free" && (
                      <div className="text-sm text-gray-500 mt-1">부가세 포함</div>
                    )}
                  </div>

                  <div className="space-y-3">
                    <Button onClick={handleAddToLibrary} className="w-full" size="lg">
                      {getPriceButtonText()}
                    </Button>
                    
                    <Button 
                      onClick={handlePreview}
                      variant="outline" 
                      className="w-full"
                      size="lg"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      미리보기
                    </Button>
                  </div>

                  <div className="flex justify-center space-x-4 pt-4 border-t border-gray-200">
                    <Button variant="ghost" size="sm">
                      <Heart className="w-4 h-4 mr-2" />
                      찜하기
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Share2 className="w-4 h-4 mr-2" />
                      공유하기
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Info Card */}
            <Card className="border-gray-200">
              <CardHeader>
                <CardTitle className="text-lg">한눈에 보기</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">난이도</span>
                  <span className="font-medium">초급</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">예상 소요시간</span>
                  <span className="font-medium">40-60분</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">추천 연령</span>
                  <span className="font-medium">6-8세</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">파일 형식</span>
                  <span className="font-medium">디지털 교안</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GuardianStoreDetail;
