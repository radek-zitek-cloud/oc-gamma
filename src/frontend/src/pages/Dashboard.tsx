import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/store/authStore";

export function Dashboard() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="space-y-6" data-testid="dashboard-container">
      <h1 className="text-3xl font-bold" data-testid="dashboard-welcome-message">
        Welcome back, {user?.full_name || user?.username || "User"}!
      </h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Profile Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Username: {user?.username}
            </p>
            <p className="text-sm text-muted-foreground">
              Email: {user?.email}
            </p>
            <p className="text-sm text-muted-foreground">
              Role: {user?.role}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Dashboard content will be added here.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              No recent activity to display.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
