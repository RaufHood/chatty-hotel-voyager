import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Plus, MessageCircle, User, LogOut, Trash2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { getChatSessions } from '@/pages/Chat';

interface ChatSession {
  id: string;
  title: string;
  lastMessage?: string;
  createdAt: string;
  updatedAt: string;
}

interface ChatSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);

  // Load chat sessions from localStorage
  useEffect(() => {
    if (user) {
      loadChatSessions();
    }
  }, [user, isOpen]); // Reload when sidebar opens

  const loadChatSessions = () => {
    try {
      setLoading(true);
      const sessions = getChatSessions();
      setChatSessions(sessions);
    } catch (error) {
      console.error('Error loading chat sessions:', error);
      toast({
        title: 'Error',
        description: 'Failed to load chat history.',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    // Clear the current session to ensure a new chat is created
    localStorage.removeItem('currentChatSession');
    
    // Navigate to new chat (without sessionId)
    navigate('/chat');
    onClose();
  };

  const handleChatSelect = (sessionId: string) => {
    navigate(`/chat/${sessionId}`);
    onClose();
  };

  const handleDeleteChat = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent chat selection
    
    try {
      // Get current sessions
      const sessions = getChatSessions();
      
      // Remove the session
      const updatedSessions = sessions.filter(s => s.id !== sessionId);
      
      // Save back to localStorage
      localStorage.setItem('chatSessions', JSON.stringify(updatedSessions));
      
      // If we deleted the current session, navigate to new chat
      if (location.pathname === `/chat/${sessionId}`) {
        navigate('/chat');
      }
      
      // Reload sessions
      loadChatSessions();
      
      toast({
        title: 'Chat deleted',
        description: 'The chat has been removed from your history.'
      });
    } catch (error) {
      console.error('Error deleting chat:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete chat.',
        variant: 'destructive'
      });
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/');
      toast({
        title: 'Signed out',
        description: 'You have been signed out successfully.'
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to sign out.',
        variant: 'destructive'
      });
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
      
      if (diffInHours < 24) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } else if (diffInHours < 168) { // 7 days
        return date.toLocaleDateString([], { weekday: 'short' });
      } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      }
    } catch (error) {
      return '';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:relative lg:inset-auto">
      {/* Overlay for mobile */}
      <div 
        className="absolute inset-0 bg-black/50 lg:hidden" 
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="absolute left-0 top-0 h-full w-80 bg-white shadow-lg lg:relative lg:shadow-none border-r">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Chat History</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="lg:hidden"
              >
                ×
              </Button>
            </div>
            
            <Button
              onClick={handleNewChat}
              className="w-full justify-start"
              size="sm"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>
          </div>

          {/* Chat Sessions */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-2">
              {loading ? (
                <div className="space-y-2">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="h-12 bg-gray-100 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : chatSessions.length > 0 ? (
                chatSessions.map((session) => (
                  <div
                    key={session.id}
                    className={`group relative p-3 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer ${
                      location.pathname === `/chat/${session.id}` ? 'bg-blue-50 border border-blue-200' : ''
                    }`}
                    onClick={() => handleChatSelect(session.id)}
                  >
                    <div className="flex items-start gap-2">
                      <MessageCircle className="w-4 h-4 mt-1 text-gray-500 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm truncate">{session.title}</p>
                          <span className="text-xs text-gray-400 ml-2">
                            {formatDate(session.updatedAt)}
                          </span>
                        </div>
                        {session.lastMessage && (
                          <p className="text-xs text-gray-500 truncate mt-1">
                            {session.lastMessage}
                          </p>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => handleDeleteChat(session.id, e)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 h-6 w-6"
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <MessageCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p className="text-sm">No chats yet</p>
                  <p className="text-xs">Start a new conversation!</p>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* User Section */}
          <div className="p-4 border-t">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user?.email || 'User'}
                </p>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSignOut}
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
