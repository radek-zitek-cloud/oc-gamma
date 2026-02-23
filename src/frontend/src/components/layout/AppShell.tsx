import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { StatusBar } from "./StatusBar";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="h-screen w-screen overflow-hidden">
      <Header />
      <Sidebar />
      <main className="absolute top-14 bottom-8 right-0 left-0 md:left-64 overflow-y-auto bg-background p-6">
        {children}
      </main>
      <StatusBar />
    </div>
  );
}
