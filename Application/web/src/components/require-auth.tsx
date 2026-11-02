"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { useAuth } from "@/lib/auth";
import type { Role } from "@/lib/types";

import { Alert, Loading } from "./ui";

function allows(role: Role, roles: Role[]): boolean {
  if (role === "superadmin") return true;
  return roles.includes(role);
}

export function RequireAuth({
  roles,
  children,
}: {
  roles?: Role[];
  children: ReactNode;
}) {
  const { user, ready } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (ready && !user) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [ready, user, pathname, router]);

  if (!ready) return <Loading label="Checking your session…" />;
  if (!user) return <Loading label="Redirecting to sign in…" />;

  if (roles && !allows(user.role, roles)) {
    return (
      <div className="container section">
        <Alert kind="error">
          This area is for {roles.map((role) => role.replace(/_/g, " ")).join(" / ")} accounts. You are
          signed in as {user.role.replace(/_/g, " ")}.
        </Alert>
        <p style={{ marginTop: 16 }}>
          <Link href="/" className="btn btn-secondary">
            Back to the marketplace
          </Link>
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
