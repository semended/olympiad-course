import Link from "next/link";
import { BookOpen, LayoutDashboard, Library, Send, UserRound } from "lucide-react";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/courses", label: "My Courses", icon: BookOpen },
  { href: "/courses", label: "Catalog", icon: Library },
  { href: "/dashboard/submissions", label: "Submissions", icon: Send },
  { href: "/dashboard/profile", label: "Profile", icon: UserRound }
];

export function Sidebar() {
  return (
    <aside className="hidden h-screen w-64 border-r bg-white p-6 lg:block">
      <div className="mb-8">
        <p className="text-xs uppercase text-slate-500">Olympiad</p>
        <h2 className="text-lg font-semibold">LMS Dashboard</h2>
      </div>
      <nav className="space-y-2">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-700 transition hover:bg-slate-100"
          >
            <link.icon className="h-4 w-4" />
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
