
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import SignupRoleSelect from "./pages/SignupRoleSelect";
import SignupGuardian from "./pages/SignupGuardian";
import SignupStudent from "./pages/SignupStudent";
import GuardianDashboard from "./pages/GuardianDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import StudentReader from "./pages/StudentReader";
import StudentBuddy from "./pages/StudentBuddy";
import NotFound from "./pages/NotFound";
import GuardianStudents from "./pages/GuardianStudents";
import GuardianDocuments from "./pages/GuardianDocuments";
import GuardianDocumentPreview from "./pages/GuardianDocumentPreview";
import GuardianProfile from "./pages/GuardianProfile";
import GuardianStudentAnalytics from "./pages/GuardianStudentAnalytics";
import GuardianWritingPracticeResults from "./pages/GuardianWritingPracticeResults";
import GuardianStore from "./pages/GuardianStore";
import GuardianStoreDetail from "./pages/GuardianStoreDetail";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup/select-role" element={<SignupRoleSelect />} />
          <Route path="/signup/guardian" element={<SignupGuardian />} />
          <Route path="/signup/student" element={<SignupStudent />} />
          <Route path="/guardian/dashboard" element={<GuardianDashboard />} />
          <Route path="/guardian/store" element={<GuardianStore />} />
          <Route path="/guardian/store/:documentId" element={<GuardianStoreDetail />} />
          <Route path="/guardian/students" element={<GuardianStudents />} />
          <Route path="/guardian/students/:studentId/analytics" element={<GuardianStudentAnalytics />} />
          <Route path="/guardian/students/:studentId/writing-practice" element={<GuardianWritingPracticeResults />} />
          <Route path="/guardian/documents" element={<GuardianDocuments />} />
          <Route path="/guardian/documents/:documentId/preview" element={<GuardianDocumentPreview />} />
          <Route path="/guardian/profile" element={<GuardianProfile />} />
          <Route path="/student/dashboard" element={<StudentDashboard />} />
          <Route path="/student/reader/:documentId/:pageNumber" element={<StudentReader />} />
          <Route path="/student/buddy" element={<StudentBuddy />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
