
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useNavigate } from "react-router-dom";
import { Book, ArrowLeft } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const SignupGuardian = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "",
    organization: ""
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "회원가입 완료!",
      description: "보호자 대시보드로 이동합니다.",
    });
    navigate("/guardian/dashboard");
  };

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
            <h1 className="text-3xl font-bold text-gray-800">리딩브릿지</h1>
          </div>
          <p className="text-gray-600 leading-dyslexic tracking-dyslexic">
            보호자 계정을 만들어보세요
          </p>
        </div>

        <Card className="border-gray-200 shadow-lg">
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-2xl font-bold text-gray-800">보호자 회원가입</CardTitle>
            <CardDescription className="text-gray-600 leading-dyslexic tracking-dyslexic">
              아이의 학습을 지원하고 관리하세요
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name" className="text-gray-700 font-medium">이름</Label>
                <Input
                  id="name"
                  placeholder="이름을 입력하세요"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                  className="h-12 text-base border-gray-300 focus:border-primary"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-700 font-medium">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="이메일을 입력하세요"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                  className="h-12 text-base border-gray-300 focus:border-primary"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="role" className="text-gray-700 font-medium">역할</Label>
                <Select onValueChange={(value) => setFormData({...formData, role: value})}>
                  <SelectTrigger className="h-12 text-base border-gray-300 focus:border-primary">
                    <SelectValue placeholder="역할을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="parent">부모</SelectItem>
                    <SelectItem value="teacher">교사</SelectItem>
                    <SelectItem value="tutor">개인교사</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="organization" className="text-gray-700 font-medium">소속 (선택사항)</Label>
                <Input
                  id="organization"
                  placeholder="학교명 또는 기관명"
                  value={formData.organization}
                  onChange={(e) => setFormData({...formData, organization: e.target.value})}
                  className="h-12 text-base border-gray-300 focus:border-primary"
                />
              </div>
              
              <Button type="submit" className="w-full h-12 bg-primary hover:bg-primary/90 text-base">
                계정 만들기
              </Button>
            </form>
            
            <div className="text-center">
              <p className="text-gray-600 leading-dyslexic tracking-dyslexic text-sm">
                계정을 만들면{' '}
                <a href="#" className="text-primary hover:underline">이용약관</a>과{' '}
                <a href="#" className="text-primary hover:underline">개인정보처리방침</a>에 동의하는 것으로 간주됩니다.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SignupGuardian;
