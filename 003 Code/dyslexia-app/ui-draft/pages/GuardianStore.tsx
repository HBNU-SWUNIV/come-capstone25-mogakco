
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useNavigate } from "react-router-dom";
import { Book, Search, Star, Download, Clock, Users, TrendingUp, Heart, Filter } from "lucide-react";
import NavigationHeader from "@/components/ui/navigation-header";
import { useToast } from "@/hooks/use-toast";

const GuardianStore = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGrade, setSelectedGrade] = useState("all");
  const [selectedSubject, setSelectedSubject] = useState("all");
  const [selectedPrice, setSelectedPrice] = useState("all");

  // Mock data for store documents
  const [storeDocuments] = useState([
    {
      id: 1,
      title: "우리 동네 동물들",
      description: "아이들이 좋아하는 동네 동물들의 이야기를 통해 읽기 능력을 키워보세요",
      coverImage: "bg-gradient-to-br from-green-400 to-blue-500",
      grade: "1-2학년",
      subject: "국어",
      price: 0,
      type: "free",
      downloads: 1234,
      rating: 4.8,
      pages: 20,
      author: "리딩브릿지 팀",
      isPopular: true,
      isNew: false
    },
    {
      id: 2,
      title: "우주 탐험 이야기",
      description: "신비로운 우주를 탐험하며 과학적 호기심과 읽기 실력을 동시에 기를 수 있어요",
      coverImage: "bg-gradient-to-br from-purple-500 to-pink-500",
      grade: "3-4학년",
      subject: "과학",
      price: 5000,
      type: "purchase",
      downloads: 892,
      rating: 4.9,
      pages: 25,
      author: "우주과학연구소",
      isPopular: true,
      isNew: true
    },
    {
      id: 3,
      title: "마법의 숲 모험",
      description: "환상적인 모험 이야기로 상상력과 창의력을 키우는 특별한 교안",
      coverImage: "bg-gradient-to-br from-emerald-400 to-teal-500",
      grade: "2-3학년",
      subject: "국어",
      price: 500,
      rentalDays: 7,
      type: "rental",
      downloads: 567,
      rating: 4.7,
      pages: 18,
      author: "창작동화연구회",
      isPopular: false,
      isNew: true
    },
    {
      id: 4,
      title: "재미있는 수학 여행",
      description: "놀이를 통해 자연스럽게 수학 개념을 익힐 수 있는 교안",
      coverImage: "bg-gradient-to-br from-orange-400 to-red-500",
      grade: "1-3학년",
      subject: "수학",
      price: 3000,
      type: "purchase",
      downloads: 423,
      rating: 4.6,
      pages: 22,
      author: "수학교육연구원",
      isPopular: false,
      isNew: false
    },
    {
      id: 5,
      title: "바다 속 친구들",
      description: "바다 생물들의 신기한 이야기로 환경 의식과 읽기 능력을 기르세요",
      coverImage: "bg-gradient-to-br from-blue-400 to-cyan-500",
      grade: "1-2학년",
      subject: "환경",
      price: 0,
      type: "free",
      downloads: 789,
      rating: 4.5,
      pages: 16,
      author: "해양환경보호단체",
      isPopular: false,
      isNew: false
    },
    {
      id: 6,
      title: "세계 여러 나라 이야기",
      description: "다양한 문화를 배우며 글로벌 마인드와 읽기 실력을 키우는 교안",
      coverImage: "bg-gradient-to-br from-yellow-400 to-orange-500",
      grade: "3-5학년",
      subject: "사회",
      price: 800,
      rentalDays: 14,
      type: "rental",
      downloads: 345,
      rating: 4.8,
      pages: 30,
      author: "세계문화연구소",
      isPopular: false,
      isNew: true
    }
  ]);

  const featuredDocuments = storeDocuments.filter(doc => doc.isPopular).slice(0, 3);
  const newDocuments = storeDocuments.filter(doc => doc.isNew).slice(0, 4);

  const filteredDocuments = storeDocuments.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGrade = selectedGrade === "all" || doc.grade.includes(selectedGrade);
    const matchesSubject = selectedSubject === "all" || doc.subject === selectedSubject;
    const matchesPrice = selectedPrice === "all" || 
                        (selectedPrice === "free" && doc.type === "free") ||
                        (selectedPrice === "paid" && doc.type !== "free");
    
    return matchesSearch && matchesGrade && matchesSubject && matchesPrice;
  });

  const handleDocumentClick = (documentId: number) => {
    navigate(`/guardian/store/${documentId}`);
  };

  const handleAddToLibrary = (document: any, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (document.type === "free") {
      toast({
        title: "교안 추가 완료!",
        description: `${document.title}이(가) 내 보관함에 추가되었습니다.`,
      });
    } else if (document.type === "purchase") {
      toast({
        title: "구매 완료!",
        description: `${document.title}을(를) 구매했습니다. 내 보관함에서 확인하세요.`,
      });
    } else if (document.type === "rental") {
      toast({
        title: "대여 완료!",
        description: `${document.title}을(를) ${document.rentalDays}일간 대여했습니다.`,
      });
    }
  };

  const getPriceText = (document: any) => {
    if (document.type === "free") return "무료";
    if (document.type === "purchase") return `₩${document.price.toLocaleString()}`;
    if (document.type === "rental") return `₩${document.price.toLocaleString()}/${document.rentalDays}일`;
    return "";
  };

  const getPriceButtonText = (document: any) => {
    if (document.type === "free") return "내 보관함에 추가";
    if (document.type === "purchase") return "구매하기";
    if (document.type === "rental") return "대여하기";
    return "";
  };

  const DocumentCard = ({ document, size = "normal" }: { document: any, size?: "normal" | "large" }) => (
    <Card 
      className="border-gray-200 hover:border-primary/30 hover:shadow-lg transition-all duration-300 cursor-pointer group"
      onClick={() => handleDocumentClick(document.id)}
    >
      <CardContent className={`p-0 ${size === "large" ? "pb-4" : ""}`}>
        {/* Cover Image */}
        <div className={`${document.coverImage} ${size === "large" ? "h-48" : "h-32"} rounded-t-lg mb-4 flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform duration-300 relative`}>
          <div className="text-center text-white p-4">
            <Book className={`${size === "large" ? "w-8 h-8" : "w-6 h-6"} mx-auto mb-2 opacity-80`} />
            <h4 className={`font-bold ${size === "large" ? "text-lg" : "text-sm"} leading-tight`}>{document.title}</h4>
          </div>
          
          {/* Badges */}
          <div className="absolute top-2 right-2 flex flex-col gap-1">
            {document.isNew && (
              <Badge className="bg-red-500 text-white text-xs">NEW</Badge>
            )}
            {document.isPopular && (
              <Badge className="bg-yellow-500 text-white text-xs">인기</Badge>
            )}
          </div>
        </div>

        <div className="px-4 space-y-3">
          {/* Title and Description */}
          <div>
            <h3 className={`font-semibold text-gray-800 ${size === "large" ? "text-lg" : "text-base"} mb-1 leading-tight`}>
              {document.title}
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed line-clamp-2">
              {document.description}
            </p>
          </div>

          {/* Meta Information */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{document.grade}</span>
            <span>{document.subject}</span>
            <span>{document.pages}페이지</span>
          </div>

          {/* Rating and Downloads */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <Star className="w-4 h-4 text-yellow-400 fill-current" />
                <span className="text-sm font-medium text-gray-700">{document.rating}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Download className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500">{document.downloads}</span>
              </div>
            </div>
            <span className="text-sm font-semibold text-primary">{getPriceText(document)}</span>
          </div>

          {/* Action Button */}
          <Button 
            onClick={(e) => handleAddToLibrary(document, e)}
            className="w-full mt-3"
            size="sm"
            variant={document.type === "free" ? "outline" : "default"}
          >
            {getPriceButtonText(document)}
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      <NavigationHeader userType="guardian" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">교안 스토어</h2>
          <p className="text-gray-600">전문가가 제작한 검증된 교안을 찾아보세요</p>
        </div>

        {/* Search and Filters */}
        <Card className="border-gray-200 mb-8">
          <CardContent className="p-6">
            <div className="grid md:grid-cols-5 gap-4">
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <Input
                    placeholder="교안 제목이나 내용으로 검색..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Select value={selectedGrade} onValueChange={setSelectedGrade}>
                <SelectTrigger>
                  <SelectValue placeholder="학년 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 학년</SelectItem>
                  <SelectItem value="1">1학년</SelectItem>
                  <SelectItem value="2">2학년</SelectItem>
                  <SelectItem value="3">3학년</SelectItem>
                  <SelectItem value="4">4학년</SelectItem>
                  <SelectItem value="5">5학년</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                <SelectTrigger>
                  <SelectValue placeholder="과목 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 과목</SelectItem>
                  <SelectItem value="국어">국어</SelectItem>
                  <SelectItem value="수학">수학</SelectItem>
                  <SelectItem value="과학">과학</SelectItem>
                  <SelectItem value="사회">사회</SelectItem>
                  <SelectItem value="환경">환경</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedPrice} onValueChange={setSelectedPrice}>
                <SelectTrigger>
                  <SelectValue placeholder="가격 필터" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체</SelectItem>
                  <SelectItem value="free">무료</SelectItem>
                  <SelectItem value="paid">유료</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Featured Section */}
        {searchQuery === "" && selectedGrade === "all" && selectedSubject === "all" && selectedPrice === "all" && (
          <>
            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-6">
                <TrendingUp className="w-6 h-6 text-primary" />
                <h3 className="text-2xl font-bold text-gray-800">인기 교안</h3>
              </div>
              <div className="grid lg:grid-cols-3 gap-6">
                {featuredDocuments.map((document) => (
                  <DocumentCard key={document.id} document={document} size="large" />
                ))}
              </div>
            </div>

            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-6">
                <Star className="w-6 h-6 text-yellow-500" />
                <h3 className="text-2xl font-bold text-gray-800">새로 출시된 교안</h3>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {newDocuments.map((document) => (
                  <DocumentCard key={document.id} document={document} />
                ))}
              </div>
            </div>
          </>
        )}

        {/* All Documents / Search Results */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Filter className="w-6 h-6 text-gray-600" />
              <h3 className="text-2xl font-bold text-gray-800">
                {searchQuery || selectedGrade !== "all" || selectedSubject !== "all" || selectedPrice !== "all" 
                  ? "검색 결과" 
                  : "전체 교안"}
              </h3>
              <Badge variant="outline" className="text-gray-600">
                {filteredDocuments.length}개
              </Badge>
            </div>
          </div>

          {filteredDocuments.length === 0 ? (
            <Card className="border-gray-200">
              <CardContent className="p-12 text-center">
                <Book className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-600 mb-2">검색 결과가 없습니다</h4>
                <p className="text-gray-500">다른 검색어나 필터를 시도해보세요.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredDocuments.map((document) => (
                <DocumentCard key={document.id} document={document} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GuardianStore;
