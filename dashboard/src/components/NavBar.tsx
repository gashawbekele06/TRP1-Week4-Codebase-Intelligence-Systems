"use client";
export function NavBar() {
  const links = [
    { href: "#fde", label: "FDE Answers" },
    { href: "#graph", label: "Module Graph" },
    { href: "#lineage", label: "Lineage" },
    { href: "#modules", label: "Modules" },
    { href: "#query", label: "Query" },
    { href: "#trace", label: "Trace" },
  ];

  return (
    <header className="sticky top-0 z-50 bg-gray-950/90 backdrop-blur border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl">🗺</span>
          <span className="font-semibold text-white text-sm">Brownfield Cartographer</span>
          <span className="text-xs text-gray-500 hidden sm:block">— Codebase Intelligence Dashboard</span>
        </div>
        <nav className="flex items-center gap-1">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-xs text-gray-400 hover:text-cyan-400 px-2 py-1 rounded transition-colors hidden md:block"
            >
              {l.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
