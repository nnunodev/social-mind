import { useLocation, Link } from 'react-router-dom';
import { LayoutDashboard, Zap, Calendar } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Hooks', href: '/hooks', icon: Zap },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
];

export default function Navigation() {
  const location = useLocation();

  return (
    <nav className="w-64 min-h-screen bg-white border-r border-gray-200 fixed left-0 top-0">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-primary-600">
          Social Mind
        </h1>
        <p className="text-sm text-gray-500 mt-1">Mind in Low Light Studio</p>
      </div>
      
      <ul className="px-3">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;
          
          return (
            <li key={item.name}>
              <Link
                to={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-900'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <Icon className={cn('w-5 h-5', isActive ? 'text-primary-600' : 'text-gray-400')} />
                {item.name}
              </Link>
            </li>
          );
        })}
      </ul>
      
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
            <span className="text-primary-600 font-medium text-sm">Mi</span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">Mind in Low Light</p>
            <p className="text-xs text-gray-500">Content Studio</p>
          </div>
        </div>
      </div>
    </nav>
  );
}
