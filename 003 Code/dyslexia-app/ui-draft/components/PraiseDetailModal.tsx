
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Star, Calendar } from "lucide-react";

interface Praise {
  id: number;
  content: string;
  stickers: number;
  date: string;
  guardianName: string;
}

interface PraiseDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  praise: Praise | null;
}

const PraiseDetailModal = ({ isOpen, onClose, praise }: PraiseDetailModalProps) => {
  if (!praise) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center flex items-center justify-center space-x-2">
            <span>받은 칭찬</span>
            <div className="flex">
              {Array.from({length: praise.stickers}).map((_, i) => (
                <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
              ))}
            </div>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* 칭찬 내용 */}
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-4 rounded-lg border border-yellow-200">
            <p className="text-gray-800 leading-relaxed font-dyslexic tracking-dyslexic">
              "{praise.content}"
            </p>
          </div>

          {/* 칭찬한 사람과 날짜 */}
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <span>👩‍👧‍👦 {praise.guardianName}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Calendar className="w-4 h-4" />
              <span>{praise.date}</span>
            </div>
          </div>

          {/* 스티커 표시 */}
          <div className="text-center py-2">
            <div className="inline-flex items-center space-x-1 bg-yellow-100 px-4 py-2 rounded-full">
              <span className="text-yellow-700 font-medium">칭찬 스티커</span>
              <div className="flex">
                {Array.from({length: praise.stickers}).map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-yellow-400 fill-current animate-pulse" />
                ))}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PraiseDetailModal;
