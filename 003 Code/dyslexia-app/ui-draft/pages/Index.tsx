
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Book, Heart, Star, Users, FileText, PlayCircle, Volume2, Type, Eye, Palette, Lightbulb, Image, ChevronLeft, ChevronRight, BookOpen, Headphones, Globe, Monitor, Zap } from "lucide-react";
import DocumentViewer from "@/components/DocumentViewer";

const Index = () => {
  const navigate = useNavigate();
  const [showDemo, setShowDemo] = useState(false);

  const features = [
    {
      icon: <FileText className="w-6 h-6 text-primary" />,
      title: "AI 맞춤 변환",
      description: "PDF를 난독증 친화적인 디지털 교안으로 자동 변환해요"
    },
    {
      icon: <Heart className="w-6 h-6 text-warm-500" />,
      title: "읽기 자신감",
      description: "TTS, 폰트 조절 등으로 아이만의 속도로 학습할 수 있어요"
    },
    {
      icon: <Star className="w-6 h-6 text-yellow-500" />,
      title: "AI 학습 친구",
      description: "그림을 그리면 AI 친구가 살아 움직이며 반응해요"
    },
    {
      icon: <Users className="w-6 h-6 text-soft-500" />,
      title: "학습 관리",
      description: "보호자에게 상세한 학습 분석 리포트를 제공해요"
    }
  ];

  const keyFeatures = [
    {
      icon: <Globe className="w-12 h-12 text-blue-500" />,
      title: "해외 자료의 한국형 재생성",
      description: "공개 저작권의 해외 교육 자료를 한국 난독증 학생들에게 맞게 AI로 재생성합니다",
      details: "원문의 핵심 내용을 유지하면서 한국어 특성과 난독증 학습자의 특성을 고려하여 최적화된 콘텐츠로 변환해요"
    },
    {
      icon: <Monitor className="w-12 h-12 text-green-500" />,
      title: "언제 어디서나 원격 지도",
      description: "보호자와 아동 간 실시간 모니터링으로 원격에서도 효과적인 학습 지도가 가능합니다",
      details: "학습 진도, 이해도, 집중도를 실시간으로 확인하고 필요한 순간에 즉시 도움을 제공할 수 있어요"
    },
    {
      icon: <Zap className="w-12 h-12 text-purple-500" />,
      title: "난독증 맞춤 솔루션",
      description: "난독 아동의 개별적인 학습 특성을 분석하여 맞춤형 학습 환경을 제공합니다",
      details: "읽기 속도, 이해도, 선호하는 학습 방식을 분석하여 각 아이에게 최적화된 학습 경험을 설계해요"
    }
  ];

  const testimonials = [
    {
      title: "난독·경계선 학생 10배 늘었는데...예산 '빈토막'",
      subtitle: "전지역 예산 30-50% 삭감, 난독협회등록 치료사 부족",
      period: "25년 국내기사"
    },
    {
      title: "난독증 학생 서울시만 3년 새 8배 늘어...\"예산 늘려 영유아기부터 치료해야\"",
      subtitle: "난독학생이 2020년부터 2023년까지 958명으로 약 8.5배 ↑",
      period: "23년 국내기사"
    },
    {
      title: "늘어나는 난독·경계선 지능학생...조기 발견해야 치료 수월",
      subtitle: "아이들이 어른들의 게이를 못 받는 시간 증가",
      period: "23년 국내기사"
    }
  ];

  return (
    <div className="min-h-screen bg-white font-dyslexic">
      {/* Header */}
      <header className="py-4 px-4 sm:px-8 border-b border-gray-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">리딩브릿지</h1>
          <div className="flex items-center space-x-3">
            <Button 
              variant="outline" 
              onClick={() => navigate("/login")} 
              className="border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg px-6"
            >
              로그인
            </Button>
            <Button 
              onClick={() => navigate("/signup/select-role")} 
              className="bg-primary hover:bg-primary/90 rounded-lg px-6"
            >
              회원가입
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section - White Background */}
      <section className="py-12 px-4 sm:px-8 bg-white">
        <div className="max-w-6xl mx-auto">
          {/* Text Content */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-primary mb-6 leading-tight">
              리딩브릿지
            </h1>
            <h2 className="text-2xl text-gray-700 mb-4 leading-relaxed">
              난독증 학생들을 위한 맞춤형 학습 경험
            </h2>
            <p className="text-lg text-gray-600 mb-8 leading-relaxed max-w-2xl mx-auto">
              보호자가 업로드한 PDF 교안을 AI로 변환하여 모든 학생이 쉽게 배울 수 있도록 지원합니다
            </p>
            
            <div className="flex justify-center space-x-4 mb-12">
              <Button 
                size="lg" 
                onClick={() => setShowDemo(true)}
                variant="outline"
                className="text-lg px-12 py-4 rounded-lg border-primary text-primary hover:bg-primary hover:text-white"
              >
                체험해보기
              </Button>
              <Button 
                size="lg" 
                onClick={() => navigate("/signup/select-role")}
                className="bg-primary hover:bg-primary/90 text-lg px-12 py-4 rounded-lg"
              >
                무료로 시작하기
              </Button>
            </div>
          </div>

          {/* Demo Section */}
          {showDemo ? (
            <div className="max-w-7xl mx-auto mb-12">
              <div className="bg-gray-50 rounded-2xl p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-800">리딩브릿지 체험하기</h3>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setShowDemo(false)}
                  >
                    닫기
                  </Button>
                </div>
                <p className="text-gray-600 mb-6">
                  실제 학생들이 사용하는 것과 동일한 환경에서 직접 체험해보세요. 
                  폰트 크기 조절, TTS 음성 읽기, 어휘 하이라이트 등 모든 기능을 사용할 수 있습니다.
                </p>
              </div>
              
              <DocumentViewer
                documentId="demo"
                initialPage={1}
                showStudentFeatures={true}
                userType="student"
              />
            </div>
          ) : (
            // Enhanced Tablet Mockup - Simplified Preview
            <div className="max-w-6xl mx-auto">
              <div className="relative bg-gray-800 rounded-3xl p-4 shadow-2xl">
                {/* iPad Frame */}
                <div className="bg-black rounded-2xl p-2">
                  <div className="bg-white rounded-xl overflow-hidden" style={{ aspectRatio: '4/3' }}>
                    {/* Simplified Interface Preview */}
                    <div className="h-full flex flex-col">
                      {/* Header Preview */}
                      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <BookOpen className="w-6 h-6 text-primary" />
                            <h3 className="text-xl font-bold text-gray-800">우리 동네 동물들</h3>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2 text-sm text-gray-500">
                              <span>1 / 20 페이지</span>
                            </div>
                            <Button size="sm" variant="outline" className="text-xs">
                              <Headphones className="w-3 h-3 mr-1" />
                              듣기
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Main Content Preview */}
                      <div className="flex-1 flex">
                        {/* Left Sidebar Preview */}
                        <div className="w-16 bg-gray-50 border-r border-gray-200 p-2 flex flex-col items-center space-y-3">
                          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                            <Volume2 className="w-5 h-5 text-white" />
                          </div>
                          <div className="w-10 h-10 bg-warm-500 rounded-lg flex items-center justify-center">
                            <Type className="w-5 h-5 text-white" />
                          </div>
                          <div className="w-10 h-10 bg-soft-500 rounded-lg flex items-center justify-center">
                            <Eye className="w-5 h-5 text-white" />
                          </div>
                        </div>

                        {/* Content Area Preview */}
                        <div className="flex-1 p-8 bg-gradient-to-b from-white to-gray-50">
                          <div className="max-w-4xl mx-auto">
                            <div className="grid md:grid-cols-2 gap-8">
                              <div className="space-y-4">
                                <p className="text-lg leading-relaxed tracking-wide text-gray-800 font-dyslexic">
                                  우리 동네에는 많은 <span className="bg-yellow-200 px-1 rounded">동물</span> 친구들이 살고 있어요.
                                </p>
                                <p className="text-lg leading-relaxed tracking-wide text-gray-800 font-dyslexic">
                                  공원에서는 귀여운 <span className="bg-yellow-200 px-1 rounded">다람쥐</span>들이 나무를 오르내리며 놀고 있어요.
                                </p>
                              </div>
                              <div className="space-y-4">
                                <p className="text-lg leading-relaxed tracking-wide text-gray-800 font-dyslexic">
                                  연못에서는 <span className="bg-yellow-200 px-1 rounded">오리</span> 가족이 평화롭게 헤엄치고 있어요.
                                </p>
                                <div className="w-32 h-20 bg-gradient-to-r from-green-100 to-blue-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300 mx-auto">
                                  <span className="text-gray-500 text-xs">AI 생성 이미지</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Bottom Navigation Preview */}
                      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
                        <div className="flex items-center justify-between">
                          <Button variant="outline" size="sm" disabled>
                            <ChevronLeft className="w-4 h-4 mr-2" />
                            이전 페이지
                          </Button>
                          
                          <div className="flex-1 mx-8">
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div className="bg-primary h-3 rounded-full" style={{ width: '5%' }}></div>
                            </div>
                          </div>
                          
                          <Button size="sm" className="bg-primary">
                            다음 페이지
                            <ChevronRight className="w-4 h-4 ml-2" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Feature highlights below tablet */}
              <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-2">
                    <Volume2 className="w-6 h-6 text-primary" />
                  </div>
                  <h4 className="font-semibold text-gray-800">TTS 음성 지원</h4>
                  <p className="text-sm text-gray-600">텍스트를 음성으로 읽어줘요</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-warm-500/10 rounded-full flex items-center justify-center mb-2">
                    <Type className="w-6 h-6 text-warm-500" />
                  </div>
                  <h4 className="font-semibold text-gray-800">폰트 조절</h4>
                  <p className="text-sm text-gray-600">읽기 편한 글씨체로 변경</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-yellow-500/10 rounded-full flex items-center justify-center mb-2">
                    <Lightbulb className="w-6 h-6 text-yellow-500" />
                  </div>
                  <h4 className="font-semibold text-gray-800">어휘 분석</h4>
                  <p className="text-sm text-gray-600">어려운 단어를 쉽게 설명</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-soft-500/10 rounded-full flex items-center justify-center mb-2">
                    <BookOpen className="w-6 h-6 text-soft-500" />
                  </div>
                  <h4 className="font-semibold text-gray-800">책처럼 읽기</h4>
                  <p className="text-sm text-gray-600">자연스러운 읽기 경험 제공</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Key Features Section */}
      <section className="py-16 px-4 sm:px-8 bg-gradient-to-b from-blue-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              리딩브릿지의 핵심 기능
            </h3>
            <p className="text-lg text-gray-600">
              난독증 학생들을 위한 혁신적인 학습 솔루션을 제공합니다
            </p>
          </div>
          
          <div className="space-y-16">
            {keyFeatures.map((feature, index) => (
              <div key={index} className={`flex flex-col ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center gap-12`}>
                <div className="flex-1">
                  <div className="flex items-center mb-6">
                    <div className="mr-4 p-3 bg-white rounded-xl shadow-lg">
                      {feature.icon}
                    </div>
                    <h4 className="text-2xl font-bold text-gray-900">{feature.title}</h4>
                  </div>
                  <p className="text-lg text-gray-700 mb-4 leading-relaxed">
                    {feature.description}
                  </p>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.details}
                  </p>
                </div>
                <div className="flex-1">
                  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
                    {index === 0 && (
                      <div className="space-y-6">
                        <div className="text-center">
                          <h5 className="font-semibold text-gray-800 mb-4">콘텐츠 변환 예시</h5>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <h6 className="text-sm font-medium text-gray-600 mb-2">원문 (영어)</h6>
                            <p className="text-sm text-gray-800">
                              "The quick brown fox jumps over the lazy dog."
                            </p>
                          </div>
                          <div className="bg-primary/5 p-4 rounded-lg">
                            <h6 className="text-sm font-medium text-primary mb-2">변환된 내용</h6>
                            <p className="text-sm text-gray-800 font-dyslexic leading-relaxed">
                              빠른 <span className="bg-yellow-200 px-1 rounded">갈색</span> 여우가 게으른 개 위로 뛰어넘어요.
                            </p>
                          </div>
                        </div>
                        <div className="flex justify-center">
                          <div className="w-24 h-16 bg-gradient-to-r from-orange-100 to-yellow-100 rounded-lg flex items-center justify-center border-2 border-dashed border-orange-300">
                            <span className="text-orange-600 text-xs">AI 생성</span>
                          </div>
                        </div>
                      </div>
                    )}
                    {index === 1 && (
                      <div className="space-y-6">
                        <div className="text-center">
                          <h5 className="font-semibold text-gray-800 mb-4">실시간 모니터링 대시보드</h5>
                        </div>
                        <div className="space-y-4">
                          <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-400">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium text-green-800">민지의 학습 상태</span>
                              <span className="text-xs text-green-600">활발히 학습 중</span>
                            </div>
                            <div className="mt-2 bg-green-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                            </div>
                          </div>
                          <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium text-yellow-800">준호의 학습 상태</span>
                              <span className="text-xs text-yellow-600">도움 필요</span>
                            </div>
                            <div className="mt-2 bg-yellow-200 rounded-full h-2">
                              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    {index === 2 && (
                      <div className="space-y-6">
                        <div className="text-center">
                          <h5 className="font-semibold text-gray-800 mb-4">개인 맞춤 학습 분석</h5>
                        </div>
                        <div className="space-y-4">
                          <div className="bg-blue-50 p-4 rounded-lg">
                            <h6 className="text-sm font-medium text-blue-800 mb-2">읽기 선호도</h6>
                            <div className="flex space-x-2">
                              <span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded">큰 글씨</span>
                              <span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded">음성 지원</span>
                            </div>
                          </div>
                          <div className="bg-purple-50 p-4 rounded-lg">
                            <h6 className="text-sm font-medium text-purple-800 mb-2">학습 패턴</h6>
                            <div className="flex space-x-2">
                              <span className="px-2 py-1 bg-purple-200 text-purple-800 text-xs rounded">시각적 학습</span>
                              <span className="px-2 py-1 bg-purple-200 text-purple-800 text-xs rounded">반복 학습</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 sm:px-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            모든 학생은 배울 권리가 있습니다.
          </h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-gray-200 hover:shadow-md transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="flex justify-center mb-4">
                    {feature.icon}
                  </div>
                  <h4 className="font-semibold text-gray-800 mb-2">{feature.title}</h4>
                  <p className="text-sm text-gray-600 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-16 px-4 sm:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-6">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-gray-200">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 mb-2 leading-relaxed">
                        {testimonial.title}
                      </h4>
                      <p className="text-primary text-sm mb-2 leading-relaxed">
                        {testimonial.subtitle}
                      </p>
                    </div>
                    <span className="text-sm text-gray-500 ml-4">
                      {testimonial.period}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-8 bg-primary text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-3xl font-bold mb-4 leading-relaxed">
            지금 시작해서 아이의 읽기 자신감을 키워보세요
          </h3>
          <p className="text-xl opacity-90 mb-8 leading-relaxed">
            첫 교안 업로드부터 AI 분석까지, 모든 기능을 무료로 체험하세요
          </p>
          <Button 
            size="lg" 
            variant="secondary"
            onClick={() => navigate("/signup/select-role")}
            className="bg-white text-primary hover:bg-gray-50 text-lg px-8 py-4 rounded-lg"
          >
            무료 체험 시작하기
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 sm:px-8 bg-gray-50">
        <div className="max-w-6xl mx-auto text-center text-gray-600">
          <p className="leading-relaxed">
            © 2024 리딩브릿지. 모든 아이의 읽기 자신감을 응원합니다.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
