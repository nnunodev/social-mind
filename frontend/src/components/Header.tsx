export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="ml-64 px-8 py-4">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-500">Welcome back ✨</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="px-3 py-1 text-xs font-medium text-primary-700 bg-primary-100 rounded-full">
              v1.0
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
