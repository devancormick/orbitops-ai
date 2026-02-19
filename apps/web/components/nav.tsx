import Link from "next/link";

const items = [
  { href: "/", label: "Overview" },
  { href: "/workflows", label: "Templates" },
  { href: "/runs", label: "Documents" },
  { href: "/review", label: "Review" },
  { href: "/submit", label: "New Intake" },
  { href: "/admin", label: "Admin" },
  { href: "/auth", label: "Login" }
];

export function Navigation() {
  return (
    <header className="topbar">
      <Link href="/" className="brand">
        OrbitOps AI
      </Link>
      <nav className="nav">
        {items.map((item) => (
          <Link key={item.href} href={item.href} className="nav-link">
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
