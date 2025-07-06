import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { MessageCircle, MapPin, Heart, Settings } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';

const BottomNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const isMobile = useIsMobile();

  // Don't show bottom nav if not mobile or user not authenticated
  if (!isMobile || !user) {
    return null;
  }

  const navigationItems = [
    {
      icon: MessageCircle,
      label: 'Chat',
      path: '/chat',
      isActive: location.pathname.startsWith('/chat')
    },
    {
      icon: MapPin,
      label: 'Trips',
      path: '/trips',
      isActive: location.pathname === '/trips'
    },
    {
      icon: Heart,
      label: 'Recommendations',
      path: '/recommendations',
      isActive: location.pathname === '/recommendations'
    },
    {
      icon: Settings,
      label: 'Settings',
      path: '/preferences',
      isActive: location.pathname === '/preferences'
    }
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 safe-area-inset-bottom">
      <div className="flex items-center justify-around py-2 px-4">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <Button
              key={item.path}
              variant="ghost"
              size="sm"
              className={cn(
                "flex-1 flex flex-col items-center gap-1 h-12 p-2 rounded-lg transition-colors",
                item.isActive 
                  ? "bg-primary/10 text-primary" 
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              )}
              onClick={() => navigate(item.path)}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{item.label}</span>
            </Button>
          );
        })}
      </div>
    </div>
  );
};

export default BottomNavigation; 