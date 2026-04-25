import { useState } from 'react';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export default function Calendar() {
  const [currentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<number | null>(null);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDay = new Date(year, month, 1).getDay();

  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  const blanks = Array.from({ length: firstDay }, (_, i) => i);

  // Sample scheduled posts
  const scheduledPosts: Record<number, { type: string; title: string }[]> = {
    5: [{ type: 'instagram', title: 'ADHD morning routine' }],
    12: [{ type: 'youtube', title: 'Overstimulation explained' }],
    18: [{ type: 'tiktok', title: 'Mental health check-in' }, { type: 'instagram', title: 'Self-care tips' }],
    24: [{ type: 'youtube', title: 'Anxiety management' }],
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Content Calendar</h1>
        <button className="flex items-center px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
          <Plus className="w-4 h-4 mr-2" />
          Add Post
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">
            {currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
          </h2>
          <div className="flex gap-2">
            <button className="p-2 hover:bg-gray-100 rounded">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded">
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-7 gap-4">
          {DAYS.map((day) => (
            <div key={day} className="p-4 text-center font-medium text-gray-500 border-b">
              {day}
            </div>
          ))}
          {blanks.map((_, i) => (
            <div key={`blank-${i}`} className="p-4 min-h-[100px]" />
          ))}
          {days.map((day) => (
            <div
              key={day}
              onClick={() => setSelectedDate(day)}
              className={`p-4 min-h-[100px] border cursor-pointer hover:bg-gray-50 ${
                selectedDate === day ? 'bg-primary-50 border-primary-300' : ''
              }`}
            >
              <span className="text-sm font-medium">{day}</span>
              {scheduledPosts[day] && (
                <div className="mt-2 space-y-1">
                  {scheduledPosts[day].map((post, i) => (
                    <div
                      key={i}
                      className={`text-xs px-2 py-1 rounded ${
                        post.type === 'youtube'
                          ? 'bg-red-100 text-red-700'
                          : post.type === 'instagram'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {post.title}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 flex gap-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-200" />
          <span className="text-sm text-gray-600">YouTube</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-200" />
          <span className="text-sm text-gray-600">Instagram</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-200" />
          <span className="text-sm text-gray-600">TikTok</span>
        </div>
      </div>
    </div>
  );
}
