import { FaCog, FaSignOutAlt } from "react-icons/fa";

export default function Sidebar() {
  return (
    <aside className="w-60 h-screen bg-gray-900 text-white flex flex-col justify-between p-6">
      <div>
        <h2 className="text-xl font-bold mb-6">Panel</h2>
        <ul>
          <li className="mb-4">
            <a href="#" className="hover:text-teal-400">Dashboard</a>
          </li>
        </ul>
      </div>
      <div className="flex justify-between text-lg">
        <FaCog className="cursor-pointer hover:text-teal-400" />
        <FaSignOutAlt className="cursor-pointer hover:text-red-400" />
      </div>
    </aside>
  );
}
