
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Book, ArrowLeft, User, Palette, Send, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const StudentBuddy = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawing, setDrawing] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDrawingComplete = () => {
    setDrawing("mock-drawing-data");
    toast({
      title: "그림이 완성되었어요! 🎨",
      description: "AI 친구에게 보내볼까요?",
    });
  };

  const handleSendToAI = async () => {
    setIsGenerating(true);
    
    // Mock AI response delay
    setTimeout(() => {
      setIsGenerating(false);
      toast({
        title: "AI 친구가 반응했어요! ✨",
        description: "그림 속 캐릭터가 살아 움직여요!",
      });
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/student/dashboard")}
                className="border-gray-300"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                책장으로
              </Button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-warm-500 rounded-full flex items-center justify-center">
                  <Palette className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-800">AI 학습 친구</h1>
                  <p className="text-sm text-gray-600">그림을 그려서 AI 친구와 대화해봐요</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-warm-400 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Message */}
        <Card className="border-warm-200/50 bg-gradient-to-r from-warm-50/50 to-warm-100/50 mb-8">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-warm-400 rounded-full flex items-center justify-center animate-gentle-bounce">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">안녕! 나는 AI 친구야! 🤖</h2>
                <p className="text-gray-600 leading-dyslexic tracking-dyslexic">
                  그림을 그려서 나에게 보내봐! 그림 속 캐릭터를 살아 움직이게 해줄게!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Drawing Area */}
          <Card className="border-gray-200 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Palette className="w-5 h-5 text-warm-500" />
                <span>그림 그리기</span>
              </CardTitle>
              <CardDescription className="leading-dyslexic tracking-dyslexic">
                좋아하는 캐릭터나 동물을 그려보세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Drawing Canvas Area */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg h-80 flex items-center justify-center bg-gray-50 relative">
                {!drawing ? (
                  <div className="text-center">
                    <Palette className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 leading-dyslexic">
                      여기에서 그림을 그려보세요
                    </p>
                    <Button 
                      onClick={() => {
                        setIsDrawing(true);
                        setTimeout(handleDrawingComplete, 2000);
                      }}
                      disabled={isDrawing}
                      className="mt-4 bg-warm-500 hover:bg-warm-600"
                    >
                      {isDrawing ? '그리는 중...' : '그림 그리기 시작'}
                    </Button>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="w-full h-60 bg-gradient-to-br from-yellow-100 to-orange-100 rounded-lg flex items-center justify-center mb-4">
                      <div className="text-6xl">🐱</div>
                    </div>
                    <p className="text-gray-600 mb-4">멋진 그림이 완성되었어요!</p>
                    <Button 
                      onClick={() => {
                        setDrawing(null);
                        setIsDrawing(false);
                      }}
                      variant="outline"
                      size="sm"
                    >
                      다시 그리기
                    </Button>
                  </div>
                )}
              </div>

              {/* Send to AI Button */}
              {drawing && (
                <Button 
                  onClick={handleSendToAI}
                  disabled={isGenerating}
                  className="w-full bg-primary hover:bg-primary/90 text-lg py-3"
                >
                  <Send className="w-5 h-5 mr-2" />
                  {isGenerating ? 'AI 친구가 생각 중...' : 'AI 친구에게 보내기'}
                </Button>
              )}
            </CardContent>
          </Card>

          {/* AI Response Area */}
          <Card className="border-gray-200 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-primary" />
                <span>AI 친구의 반응</span>
              </CardTitle>
              <CardDescription className="leading-dyslexic tracking-dyslexic">
                그림을 보내면 AI 친구가 반응해줄 거예요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* AI Response Area */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg h-80 flex items-center justify-center bg-gradient-to-br from-soft-50 to-primary/5">
                {!drawing ? (
                  <div className="text-center">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Sparkles className="w-8 h-8 text-primary" />
                    </div>
                    <p className="text-gray-500 leading-dyslexic">
                      그림을 그려서 AI 친구에게 보내보세요
                    </p>
                  </div>
                ) : isGenerating ? (
                  <div className="text-center">
                    <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 animate-soft-pulse">
                      <Sparkles className="w-8 h-8 text-white" />
                    </div>
                    <p className="text-primary font-medium">AI 친구가 그림을 분석하고 있어요...</p>
                    <p className="text-sm text-gray-600 mt-2">잠시만 기다려주세요 ✨</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="text-center mb-6">
                      <div className="text-8xl mb-4 animate-gentle-bounce">🐱</div>
                      <div className="bg-white rounded-lg p-4 shadow-sm border inline-block">
                        <p className="text-gray-800 font-medium">
                          "야옹! 안녕! 나는 고양이야! 🐾"
                        </p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-primary font-medium">AI 친구가 그림을 살아 움직이게 했어요!</p>
                      <p className="text-sm text-gray-600">고양이가 말을 걸고 있어요!</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Tips */}
              <div className="bg-warm-50 rounded-lg p-4 border border-warm-200">
                <h4 className="font-semibold text-warm-800 mb-2">💡 그림 그리기 팁</h4>
                <ul className="text-sm text-warm-700 space-y-1 leading-dyslexic">
                  <li>• 동물이나 사람을 그려보세요</li>
                  <li>• 간단한 그림도 괜찮아요</li>
                  <li>• AI 친구가 그림을 이해하고 반응해줄 거예요</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default StudentBuddy;
