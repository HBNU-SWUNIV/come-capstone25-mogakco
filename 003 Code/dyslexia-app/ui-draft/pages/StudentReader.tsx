
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, User } from "lucide-react";
import DocumentViewer from "@/components/DocumentViewer";

const StudentReader = () => {
  const { documentId, pageNumber } = useParams();
  const navigate = useNavigate();

  const handlePageChange = (newPage: number) => {
    navigate(`/student/reader/${documentId}/${newPage}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50">
      {/* Student Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/student/dashboard")}
              className="border-gray-300"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              책장으로
            </Button>
            <div className="w-8 h-8 bg-warm-400 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
          </div>
        </div>
      </header>

      <DocumentViewer
        documentId={documentId || "1"}
        initialPage={parseInt(pageNumber || "1")}
        onPageChange={handlePageChange}
        showStudentFeatures={true}
        userType="student"
      />
    </div>
  );
};

export default StudentReader;
