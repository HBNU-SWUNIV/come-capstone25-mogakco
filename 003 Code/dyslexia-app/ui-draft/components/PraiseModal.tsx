
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Star } from "lucide-react";
import { useState } from "react";

interface PraiseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSavePraise: (praise: string, stickers: number) => void;
  studentName?: string;
}

const PraiseModal = ({ isOpen, onClose, onSavePraise, studentName = "학생" }: PraiseModalProps) => {
  const [praise, setPraise] = useState("");
  const [selectedStickers, setSelectedStickers] = useState(1);

  const handleSave = () => {
    if (praise.trim()) {
      onSavePraise(praise, selectedStickers);
      setPraise("");
      setSelectedStickers(1);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center">
            {studentName}에게 칭찬하기 ⭐
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* 스티커 개수 선택 */}
          <div>
            <label className="block text-sm font-medium mb-2">칭찬 스티커 개수</label>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((count) => (
                <button
                  key={count}
                  onClick={() => setSelectedStickers(count)}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-lg border transition-colors ${
                    selectedStickers === count
                      ? "bg-yellow-100 border-yellow-300 text-yellow-700"
                      : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <span>{count}</span>
                  <Star className="w-4 h-4" />
                </button>
              ))}
            </div>
          </div>

          {/* 칭찬 내용 */}
          <div>
            <label className="block text-sm font-medium mb-2">칭찬 내용</label>
            <Textarea
              value={praise}
              onChange={(e) => setPraise(e.target.value)}
              placeholder="오늘 정말 열심히 책을 읽었네요! 훌륭해요!"
              className="min-h-[100px]"
            />
          </div>

          {/* 버튼들 */}
          <div className="flex space-x-2 pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1">
              취소
            </Button>
            <Button 
              onClick={handleSave} 
              disabled={!praise.trim()}
              className="flex-1 bg-yellow-500 hover:bg-yellow-600"
            >
              칭찬하기
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PraiseModal;
