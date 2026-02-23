import { useBackendHealth } from "@/hooks/useSystem";
import { useAuthStore } from "@/store/authStore";
import { version as APP_VERSION } from "../../../package.json";

export function StatusBar() {
  const user = useAuthStore((state) => state.user);
  const { data: health, isError } = useBackendHealth();

  const backendVersion = health?.version || "unknown";
  const isConnected = !isError && health?.status === "ok";

  return (
    <footer className="fixed bottom-0 left-0 w-full h-8 z-50 border-t bg-secondary flex items-center px-4 text-xs font-mono">
      <div className="flex items-center gap-4 w-full">
        <span>Frontend: v{APP_VERSION}</span>
        <span className="flex items-center gap-1">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success' : 'bg-destructive'}`}></span>
          Backend: v{backendVersion}
        </span>
        {user && <span className="ml-auto">User: {user.username}</span>}
      </div>
    </footer>
  );
}
