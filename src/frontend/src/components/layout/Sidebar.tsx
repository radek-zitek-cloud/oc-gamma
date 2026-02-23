import { Link } from "react-router-dom";

import { useAuthStore } from "@/store/authStore";

export function Sidebar() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <aside className="fixed left-0 top-14 bottom-8 w-64 z-40 border-r bg-background hidden md:block">
      <nav className="p-4 space-y-2">
        <Link
          to="/"
          className="block px-4 py-2 rounded-md hover:bg-accent hover:text-accent-foreground"
        >
          Dashboard
        </Link>
      </nav>
    </aside>
  );
}
