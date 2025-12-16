
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Upload, FileText, Users, Calendar, Eye, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import NavigationHeader from "@/components/ui/navigation-header";
import DocumentUploadModal from "@/components/DocumentUploadModal";
import DocumentAssignModal from "@/components/DocumentAssignModal";
import { useDocumentPolling } from "@/hooks/useDocumentPolling";

const GuardianDocuments = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<{id: number, title: string} | null>(null);

  // Mock data for documents with processing documents
  const [documents, setDocuments] = useState([
    {
      id: 1,
      title: "우리 동네 동물들",
      uploadDate: "2024-01-15",
      status: "변환 완료",
      assignedStudents: 2,
      totalPages: 20,
      grade: "초등 1-2학년",
      thumbnailColor: "bg-warm-400"
    },
    {
      id: 2,
      title: "우주 탐험 이야기",
      uploadDate: "2024-01-12", 
      status: "변환 중",
      assignedStudents: 1,
      totalPages: 25,
      grade: "초등 3-4학년",
      thumbnailColor: "bg-soft-400",
      progress: 65
    },
    {
      id: 3,
      title: "마법의 숲 모험",
      uploadDate: "2024-01-10",
      status: "변환 완료",
      assignedStudents: 0,
      totalPages: 18,
      grade: "초등 1-2학년",
      thumbnailColor: "bg-green-400"
    }
  ]);

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handlePreviewDocument = (documentId: number) => {
    navigate(`/guardian/documents/${documentId}/preview`);
  };

  const handleAssignDocument = (documentId: number, documentTitle: string) => {
    setSelectedDocument({id: documentId, title: documentTitle});
    setAssignModalOpen(true);
  };

  const handleUploadStart = (newDocument: any) => {
    setDocuments(prev => [newDocument, ...prev]);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "변환 완료":
        return "bg-green-100 text-green-700";
      case "변환 중":
        return "bg-yellow-100 text-yellow-700";
      case "변환 실패":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  // 진행 중인 문서들에 대한 폴링 훅 사용
  const processingDocs = documents.filter(doc => doc.status === "변환 중");

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
      <NavigationHeader userType="guardian" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-800">교안 보관함</h2>
            <p className="text-gray-600 mt-2">업로드한 교안을 관리하고 학생들에게 할당해보세요</p>
          </div>
          <Button 
            className="bg-primary hover:bg-primary/90"
            onClick={() => setUploadModalOpen(true)}
          >
            <Upload className="w-4 h-4 mr-2" />
            새 교안 업로드
          </Button>
        </div>

        {/* Search and Filter */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="교안 제목으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Documents Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDocuments.map((document) => (
            <DocumentCard 
              key={document.id}
              document={document}
              onPreview={handlePreviewDocument}
              onAssign={handleAssignDocument}
              getStatusColor={getStatusColor}
            />
          ))}
        </div>

        {/* Empty State */}
        {filteredDocuments.length === 0 && searchTerm === "" && (
          <Card className="border-dashed border-2 border-gray-300">
            <CardContent className="p-12 text-center">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">아직 업로드한 교안이 없습니다</h3>
              <p className="text-gray-500 mb-4">PDF 교안을 업로드하여 AI 변환을 시작해보세요</p>
              <Button 
                className="bg-primary hover:bg-primary/90"
                onClick={() => setUploadModalOpen(true)}
              >
                <Upload className="w-4 h-4 mr-2" />
                첫 교안 업로드하기
              </Button>
            </CardContent>
          </Card>
        )}

        {/* No Search Results */}
        {filteredDocuments.length === 0 && searchTerm !== "" && (
          <Card className="border-gray-200">
            <CardContent className="p-8 text-center">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-600 mb-2">검색 결과가 없습니다</h3>
              <p className="text-gray-500">"{searchTerm}"와 일치하는 교안을 찾을 수 없습니다</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Upload Modal */}
      <DocumentUploadModal
        open={uploadModalOpen}
        onOpenChange={setUploadModalOpen}
        onUploadStart={handleUploadStart}
      />

      {/* Assign Modal */}
      <DocumentAssignModal
        open={assignModalOpen}
        onOpenChange={setAssignModalOpen}
        documentTitle={selectedDocument?.title || ""}
      />
    </div>
  );
};

// 문서 카드 컴포넌트를 별도로 분리
const DocumentCard = ({ document, onPreview, onAssign, getStatusColor }: any) => {
  const { status: pollingStatus } = useDocumentPolling(
    document.id,
    document.status === "변환 중"
  );

  // 폴링된 상태가 있으면 사용, 없으면 기본 상태 사용
  const currentStatus = pollingStatus?.status || document.status;
  const currentProgress = pollingStatus?.progress || document.progress || 0;

  return (
    <Card className="border-gray-200 hover:border-primary/30 hover:shadow-lg transition-all duration-300">
      <CardHeader className="pb-4">
        {/* Document Thumbnail */}
        <div className={`${document.thumbnailColor} h-32 rounded-lg mb-4 flex items-center justify-center relative`}>
          <div className="text-center text-white">
            <FileText className="w-8 h-8 mx-auto mb-2 opacity-80" />
            <p className="text-sm font-medium">
              {document.totalPages || pollingStatus?.totalPages || '?'}페이지
            </p>
          </div>
          
          {/* 변환 중일 때 프로그레스 오버레이 */}
          {currentStatus === "변환 중" && (
            <div className="absolute inset-0 bg-black/50 rounded-lg flex flex-col items-center justify-center">
              <div className="text-white text-center w-full px-4">
                <p className="text-sm font-medium mb-2">변환 중...</p>
                <div className="w-full">
                  <Progress value={currentProgress} className="h-2 bg-white/20" />
                  <p className="text-xs mt-1">{Math.round(currentProgress)}%</p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg leading-tight">{document.title}</CardTitle>
            <CardDescription className="mt-1">{document.grade}</CardDescription>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(currentStatus)}`}>
            {currentStatus}
          </span>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Document Info */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1 text-gray-600">
              <Calendar className="w-3 h-3" />
              <span>업로드</span>
            </div>
            <span className="text-gray-800">{document.uploadDate}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1 text-gray-600">
              <Users className="w-3 h-3" />
              <span>할당된 학생</span>
            </div>
            <span className="text-gray-800">{document.assignedStudents}명</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <Button 
            onClick={() => onPreview(document.id)}
            variant="outline"
            className="flex-1"
            disabled={currentStatus !== "변환 완료"}
          >
            <Eye className="w-4 h-4 mr-1" />
            미리보기
          </Button>
          <Button 
            onClick={() => onAssign(document.id, document.title)}
            variant="outline"
            className="flex-1"
            disabled={currentStatus !== "변환 완료"}
          >
            <Users className="w-4 h-4 mr-1" />
            할당
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default GuardianDocuments;
