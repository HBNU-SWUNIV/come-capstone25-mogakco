
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, Info } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DocumentUploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUploadStart: (documentData: any) => void;
}

const DocumentUploadModal = ({ open, onOpenChange, onUploadStart }: DocumentUploadModalProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { toast } = useToast();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        toast({
          title: "파일 형식 오류",
          description: "PDF 파일만 업로드할 수 있습니다.",
          variant: "destructive",
        });
        return;
      }
      setFile(selectedFile);
      setTitle(selectedFile.name.replace(".pdf", ""));
    }
  };

  const handleUpload = async () => {
    if (!file || !title.trim()) {
      toast({
        title: "입력 오류",
        description: "파일과 교안 이름을 모두 입력해주세요.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // 시뮬레이션: 실제로는 API 호출
      const formData = new FormData();
      formData.append("file", file);
      formData.append("title", title);

      // 업로드 진행률 시뮬레이션
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Mock API 호출 시뮬레이션
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      setUploadProgress(100);
      
      // 새 문서 데이터 생성 (실제로는 서버 응답)
      const newDocument = {
        id: Date.now(),
        title: title,
        uploadDate: new Date().toISOString().split('T')[0],
        status: "변환 중",
        assignedStudents: 0,
        totalPages: 0,
        grade: "미정",
        thumbnailColor: "bg-blue-400",
        progress: 0
      };

      onUploadStart(newDocument);
      
      toast({
        title: "업로드 시작",
        description: "교안 생성이 시작되었습니다. 진행률은 교안 보관함에서 확인하실 수 있습니다.",
      });

      // 상태 초기화
      setFile(null);
      setTitle("");
      setIsUploading(false);
      setUploadProgress(0);
      onOpenChange(false);

    } catch (error) {
      console.error("Upload error:", error);
      toast({
        title: "업로드 실패",
        description: "파일 업로드 중 오류가 발생했습니다.",
        variant: "destructive",
      });
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleClose = () => {
    if (!isUploading) {
      setFile(null);
      setTitle("");
      setUploadProgress(0);
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>새 교안 업로드</span>
          </DialogTitle>
        </DialogHeader>

        {!isUploading ? (
          <div className="space-y-6">
            {/* 파일 업로드 영역 */}
            <div className="space-y-2">
              <Label htmlFor="file-upload">PDF 파일 선택</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                <input
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">
                    {file ? file.name : "PDF 파일을 선택하세요"}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    클릭하여 파일 선택
                  </p>
                </label>
              </div>
            </div>

            {/* 교안 이름 입력 */}
            <div className="space-y-2">
              <Label htmlFor="title">교안 이름</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="교안 이름을 입력하세요"
              />
            </div>

            {/* 가이드 섹션 */}
            <div className="bg-blue-50 p-4 rounded-lg space-y-2">
              <div className="flex items-center space-x-2 text-blue-700">
                <Info className="w-4 h-4" />
                <span className="font-medium text-sm">업로드 가이드</span>
              </div>
              <div className="text-xs text-blue-600 space-y-1">
                <p>• 지원 파일 형식: PDF만 업로드 가능합니다</p>
                <p>• 자동 번역 지원: 모든 언어 자료는 한국어로 자동 번역됩니다</p>
                <p>• 변환 시간: 페이지 수에 따라 5-15분 소요됩니다</p>
              </div>
            </div>

            {/* 버튼 */}
            <div className="flex space-x-2">
              <Button variant="outline" onClick={handleClose} className="flex-1">
                취소
              </Button>
              <Button onClick={handleUpload} disabled={!file || !title.trim()} className="flex-1">
                <Upload className="w-4 h-4 mr-2" />
                생성하기
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-6 py-4">
            {/* 업로드 진행 중 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">교안을 생성하고 있어요!</h3>
              <p className="text-sm text-gray-600 mb-4">
                잠시만 기다려주세요. 변환이 완료되면 알려드릴게요.
              </p>
            </div>

            {/* 프로그레스 바 */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>업로드 진행률</span>
                <span>{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="h-2" />
            </div>

            <div className="bg-gray-50 p-3 rounded-lg text-center">
              <p className="text-sm text-gray-600">
                진행률은 대시보드 또는 교안 보관함에서 계속 확인하실 수 있어요!
              </p>
            </div>

            <Button onClick={handleClose} className="w-full">
              확인하고 닫기
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default DocumentUploadModal;
