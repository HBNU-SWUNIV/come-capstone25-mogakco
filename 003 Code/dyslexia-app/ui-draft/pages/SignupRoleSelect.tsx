
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Book, ArrowLeft, Users, User } from "lucide-react";

const SignupRoleSelect = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <button 
            onClick={() => navigate("/")}
            className="inline-flex items-center space-x-2 text-gray-600 hover:text-primary mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>홈으로 돌아가기</span>
          </button>
          
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
              <Book className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800">리딩브릿지</h1>
          </div>
          <p className="text-gray-600 leading-dyslexic tracking-dyslexic">
            리딩브릿지와 함께 읽기 자신감을 키워보세요
          </p>
        </div>

        <Card className="border-gray-200 shadow-lg">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-2xl font-bold text-gray-800">회원가입</CardTitle>
            <CardDescription className="text-gray-600 leading-dyslexic tracking-dyslexic">
              어떤 역할로 리딩브릿지를 시작하시나요?
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-4 pb-8">
            <div className="grid md:grid-cols-2 gap-4">
              {/* Guardian Card */}
              <Card 
                className="cursor-pointer transition-all duration-300 hover:shadow-md hover:border-primary/50 border-2 border-gray-200 group"
                onClick={() => navigate("/signup/guardian")}
              >
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-soft-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/10 transition-colors">
                    <Users className="w-8 h-8 text-soft-600 group-hover:text-primary transition-colors" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">보호자</h3>
                  <p className="text-gray-600 leading-dyslexic tracking-dyslexic text-sm mb-4">
                    부모님 또는 교사로서
                    <br />
                    아이의 학습을 관리하고 지원해요
                  </p>
                  <div className="space-y-2 text-sm text-gray-500 text-left">
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                      <span>PDF 교안 업로드 및 변환</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                      <span>학습 진도 및 분석 리포트</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                      <span>아동 초대 및 관리</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Student Card */}
              <Card 
                className="cursor-pointer transition-all duration-300 hover:shadow-md hover:border-primary/50 border-2 border-gray-200 group"
                onClick={() => navigate("/signup/student")}
              >
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/10 transition-colors">
                    <User className="w-8 h-8 text-warm-600 group-hover:text-primary transition-colors" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">아동(학생)</h3>
                  <p className="text-gray-600 leading-dyslexic tracking-dyslexic text-sm mb-4">
                    학습의 주인공으로서
                    <br />
                    나만의 속도로 즐겁게 공부해요
                  </p>
                  <div className="space-y-2 text-sm text-gray-500 text-left">
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                      <span>맞춤형 인터랙티브 리더</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                      <span>TTS 및 접근성 도구</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                      <span>AI 학습 친구와 상호작용</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div className="text-center pt-4">
              <p className="text-gray-600 leading-dyslexic tracking-dyslexic">
                이미 계정이 있으신가요?{' '}
                <button 
                  onClick={() => navigate("/login")}
                  className="text-primary hover:underline font-medium"
                >
                  로그인하기
                </button>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SignupRoleSelect;
