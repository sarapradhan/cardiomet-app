'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const LINKS: [string, string][] = [
  ['/', 'Home'],
  ['/benchmark', 'Check labs'],
  ['/timeline', 'Timeline'],
];

export function NavBar() {
  const path = usePathname();
  return (
    <nav aria-label="Primary" style={{ display: 'flex', gap: 2 }}>
      {LINKS.map(([href, label]) => (
        <Link key={href} href={href} className="nav-link"
          data-active={href === '/' ? path === '/' : path.startsWith(href)}
          aria-current={(href === '/' ? path === '/' : path.startsWith(href)) ? 'page' : undefined}>
          {label}
        </Link>
      ))}
    </nav>
  );
}
