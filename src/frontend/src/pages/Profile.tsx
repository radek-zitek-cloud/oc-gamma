import { useState } from "react";
import { Link } from "react-router-dom";
import { Key, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCurrentUser, useUpdateProfile } from "@/hooks/useAuth";
import { useAuthStore } from "@/store/authStore";

export function Profile() {
  const user = useAuthStore((state) => state.user);
  const { isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();

  const [profileData, setProfileData] = useState({
    email: user?.email || "",
    full_name: user?.full_name || "",
  });

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateProfile.mutateAsync(profileData);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold" data-testid="profile-heading">Profile</h1>
      </div>

      <Card data-testid="profile-form">
        <CardHeader>
          <CardTitle>Edit Profile</CardTitle>
          <CardDescription>
            Update your email address and display name.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={profileData.email}
                onChange={(e) =>
                  setProfileData({ ...profileData, email: e.target.value })
                }
                data-testid="profile-email-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input
                id="full_name"
                type="text"
                value={profileData.full_name}
                onChange={(e) =>
                  setProfileData({ ...profileData, full_name: e.target.value })
                }
                data-testid="profile-fullname-input"
              />
            </div>
            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                asChild
                data-testid="profile-cancel-button"
              >
                <Link to="/">Cancel</Link>
              </Button>
              <Button
                type="submit"
                disabled={updateProfile.isPending}
                data-testid="profile-save-button"
              >
                {updateProfile.isPending ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>
            Manage your password and account security.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            to="/password"
            className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-muted"
            data-testid="profile-change-password-link"
          >
            <div className="flex items-center gap-3">
              <Key className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Change Password</p>
                <p className="text-sm text-muted-foreground">
                  Update your password to keep your account secure
                </p>
              </div>
            </div>
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
