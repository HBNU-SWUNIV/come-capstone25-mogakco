
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, User } from "lucide-react";
import DocumentViewer from "@/components/DocumentViewer";
import NavigationHeader from "@/components/ui/navigation-header";

const GuardianDocumentPreview = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50">
      <NavigationHeader userType="guardian" />
      
      {/* Preview Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/guardian/documents")}
              className="border-gray-300"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              교안 보관함으로
            </Button>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">미리보기 모드</span>
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <DocumentViewer
        documentId={documentId || "1"}
        initialPage={1}
        isPreviewMode={true}
        showStudentFeatures={false}
        userType="guardian"
      />
    </div>
  );
};

export default GuardianDocumentPreview;
