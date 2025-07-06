import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, User, Bell, Globe, Shield, LogOut, Trash2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

const Preferences = () => {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  
  const [preferences, setPreferences] = useState({
    notifications: true,
    marketing: false,
    locationSharing: true,
    dataCollection: false,
  });

  const handleToggle = (key: keyof typeof preferences) => {
    setPreferences(prev => ({ ...prev, [key]: !prev[key] }));
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

  const handleDeleteAccount = () => {
    // TODO: Implement account deletion
    toast({
      title: 'Feature coming soon',
      description: 'Account deletion will be available in a future update.',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b px-4 py-4">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="h-8 w-8"
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <h1 className="text-xl font-semibold">Preferences</h1>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6">
        {/* User Profile */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Profile
            </CardTitle>
            <CardDescription>
              Manage your profile information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <p className="font-medium">{user?.email}</p>
                <p className="text-sm text-gray-600">Free Account</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notifications
            </CardTitle>
            <CardDescription>
              Control your notification preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="notifications">Push Notifications</Label>
                <p className="text-sm text-gray-600">
                  Receive notifications about your trips and bookings
                </p>
              </div>
              <Switch
                id="notifications"
                checked={preferences.notifications}
                onCheckedChange={() => handleToggle('notifications')}
              />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="marketing">Marketing Emails</Label>
                <p className="text-sm text-gray-600">
                  Receive emails about deals and offers
                </p>
              </div>
              <Switch
                id="marketing"
                checked={preferences.marketing}
                onCheckedChange={() => handleToggle('marketing')}
              />
            </div>
          </CardContent>
        </Card>

        {/* Privacy Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Privacy
            </CardTitle>
            <CardDescription>
              Manage your privacy settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="location">Location Sharing</Label>
                <p className="text-sm text-gray-600">
                  Allow app to use your location for better recommendations
                </p>
              </div>
              <Switch
                id="location"
                checked={preferences.locationSharing}
                onCheckedChange={() => handleToggle('locationSharing')}
              />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="data">Data Collection</Label>
                <p className="text-sm text-gray-600">
                  Allow anonymous usage analytics
                </p>
              </div>
              <Switch
                id="data"
                checked={preferences.dataCollection}
                onCheckedChange={() => handleToggle('dataCollection')}
              />
            </div>
          </CardContent>
        </Card>

        {/* App Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              App Settings
            </CardTitle>
            <CardDescription>
              General app preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Language</Label>
                <p className="text-sm text-gray-600">English (US)</p>
              </div>
              <Button variant="ghost" size="sm">
                Change
              </Button>
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Currency</Label>
                <p className="text-sm text-gray-600">USD ($)</p>
              </div>
              <Button variant="ghost" size="sm">
                Change
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Account Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Account Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={handleSignOut}
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
            <Button
              variant="destructive"
              className="w-full justify-start"
              onClick={handleDeleteAccount}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Account
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Preferences; 