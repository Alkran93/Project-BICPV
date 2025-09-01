export default function Header() {
  return (
    <header className="flex justify-between items-center p-4 bg-white border-b shadow-sm">
      <span className="text-gray-600 text-sm">📅 Miércoles 6, 2025 - ⏰ 16:44:31</span>
      <div className="flex items-center gap-2 text-sm">
        <span>Temperatura</span>
        <span className="w-3 h-3 rounded-full bg-green-500"></span>
        <span>Status</span>
      </div>
    </header>
  );
}
