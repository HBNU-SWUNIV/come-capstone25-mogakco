
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useNavigate } from "react-router-dom";
import { Book, ArrowLeft, Star, MessageCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const SignupStudent = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [step, setStep] = useState<'auth' | 'form'>('auth');
  const [formData, setFormData] = useState({
    name: "",
    grade: "",
    interests: [] as string[]
  });

  const interestOptions = [
    "동물", "우주", "과학", "음악", "미술", "운동", "요리", "게임", "만화", "영화"
  ];

  const handleKakaoAuth = () => {
    // Mock Kakao OAuth process
    toast({
      title: "카카오톡 인증 성공!",
      description: "학생 정보를 입력해주세요.",
    });
    setStep('form');
  };

  const toggleInterest = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "회원가입 완료!",
      description: "나의 책장으로 이동합니다.",
    });
    // Mock JWT login process - in real app, this would set the JWT token
    navigate("/student/dashboard");
  };

  if (step === 'auth') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <button 
              onClick={() => navigate("/signup/select-role")}
              className="inline-flex items-center space-x-2 text-gray-600 hover:text-primary mb-6 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>역할 선택으로 돌아가기</span>
            </button>
            
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                <Book className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-gray-800">ReadBuddy</h1>
            </div>
            <p className="text-gray-600 leading-dyslexic tracking-dyslexic">
              ReadBuddy와 함께 읽기 모험을 시작해요!
            </p>
          </div>

          <Card className="border-gray-200 shadow-lg">
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-2xl font-bold text-gray-800">학생 회원가입</CardTitle>
              <CardDescription className="text-gray-600 leading-dyslexic tracking-dyslexic">
                카카오톡으로 간편하게 인증해요
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              <div className="text-center space-y-4">
                <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <MessageCircle className="w-12 h-12 text-yellow-600 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">
                    카카오톡으로 인증할게요!
                  </h3>
                  <p className="text-gray-600 text-sm leading-dyslexic tracking-dyslexic">
                    카카오톡 앱이 열리면 본인 인증을 진행해주세요.
                    인증이 완료되면 다시 이 화면으로 돌아와요.
                  </p>
                </div>
                
                <Button 
                  onClick={handleKakaoAuth}
                  className="w-full h-12 bg-yellow-400 hover:bg-yellow-500 text-yellow-900 text-base font-medium"
                >
                  카카오톡 열어서 인증하기
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <button 
            onClick={() => setStep('auth')}
            className="inline-flex items-center space-x-2 text-gray-600 hover:text-primary mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>인증으로 돌아가기</span>
          </button>
          
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
              <Book className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800">ReadBuddy</h1>
          </div>
          <p className="text-gray-600 leading-dyslexic tracking-dyslexic">
            나에 대해 알려주세요!
          </p>
        </div>

        <Card className="border-gray-200 shadow-lg">
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-2xl font-bold text-gray-800">학생 정보 입력</CardTitle>
            <CardDescription className="text-gray-600 leading-dyslexic tracking-dyslexic">
              나만의 속도로 즐겁게 학습해요
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name" className="text-gray-700 font-medium">이름</Label>
                <Input
                  id="name"
                  placeholder="이름을 알려주세요"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                  className="h-12 text-base border-gray-300 focus:border-primary"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="grade" className="text-gray-700 font-medium">학년</Label>
                <Select onValueChange={(value) => setFormData({...formData, grade: value})}>
                  <SelectTrigger className="h-12 text-base border-gray-300 focus:border-primary">
                    <SelectValue placeholder="학년을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="elementary-1">초등학교 1학년</SelectItem>
                    <SelectItem value="elementary-2">초등학교 2학년</SelectItem>
                    <SelectItem value="elementary-3">초등학교 3학년</SelectItem>
                    <SelectItem value="elementary-4">초등학교 4학년</SelectItem>
                    <SelectItem value="elementary-5">초등학교 5학년</SelectItem>
                    <SelectItem value="elementary-6">초등학교 6학년</SelectItem>
                    <SelectItem value="middle-1">중학교 1학년</SelectItem>
                    <SelectItem value="middle-2">중학교 2학년</SelectItem>
                    <SelectItem value="middle-3">중학교 3학년</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-3">
                <Label className="text-gray-700 font-medium">좋아하는 것들 (3개까지 선택)</Label>
                <div className="grid grid-cols-2 gap-2">
                  {interestOptions.map((interest) => (
                    <button
                      key={interest}
                      type="button"
                      onClick={() => toggleInterest(interest)}
                      disabled={formData.interests.length >= 3 && !formData.interests.includes(interest)}
                      className={`p-3 rounded-lg border text-sm transition-all ${
                        formData.interests.includes(interest)
                          ? 'bg-primary text-white border-primary'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-primary/50'
                      } ${
                        formData.interests.length >= 3 && !formData.interests.includes(interest)
                          ? 'opacity-50 cursor-not-allowed'
                          : 'cursor-pointer'
                      }`}
                    >
                      <div className="flex items-center space-x-1">
                        {formData.interests.includes(interest) && <Star className="w-3 h-3" />}
                        <span>{interest}</span>
                      </div>
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500">
                  선택한 관심사: {formData.interests.length}/3
                </p>
              </div>
              
              <Button type="submit" className="w-full h-12 bg-primary hover:bg-primary/90 text-base">
                읽기 모험 시작하기! 🚀
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SignupStudent;
