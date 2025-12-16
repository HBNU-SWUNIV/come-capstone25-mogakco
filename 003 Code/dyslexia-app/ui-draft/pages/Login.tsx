
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Book, ArrowLeft } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Login = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleKakaoLogin = () => {
    // Mock Kakao login logic - redirect based on some condition
    // In real implementation, this would call Kakao SDK
    toast({
      title: "카카오 로그인 성공!",
      description: "대시보드로 이동합니다.",
    });
    
    // Mock logic for role determination
    // In real app, this would come from the backend after Kakao auth
    const userRole = Math.random() > 0.5 ? 'guardian' : 'student';
    
    if (userRole === 'guardian') {
      navigate("/guardian/dashboard");
    } else {
      navigate("/student/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic flex items-center justify-center p-4">
      <div className="w-full max-w-md">
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
            다시 만나서 반가워요!
          </p>
        </div>

        <Card className="border-gray-200 shadow-lg">
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-2xl font-bold text-gray-800">로그인</CardTitle>
            <CardDescription className="text-gray-600 leading-dyslexic tracking-dyslexic">
              카카오 계정으로 간편하게 로그인하세요
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <Button 
              onClick={handleKakaoLogin}
              className="w-full h-12 bg-yellow-400 hover:bg-yellow-500 text-yellow-900 text-base font-medium"
            >
              카카오로 로그인
            </Button>
            
            <div className="text-center">
              <p className="text-gray-600 leading-dyslexic tracking-dyslexic">
                아직 계정이 없으신가요?{' '}
                <button 
                  onClick={() => navigate("/signup/select-role")}
                  className="text-primary hover:underline font-medium"
                >
                  회원가입하기
                </button>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
