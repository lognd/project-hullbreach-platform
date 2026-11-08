import { useEffect, type ReactNode } from "react";
import { useSession } from "@/auth/session";
import { navigate } from "@/components/navigate";

// frob:ticket 01M2H5T12E0JWYSBMM6HZ09J6Q
/** Renders children for an admin session only; anyone else is redirected to the start page. */
export function AdminGate({ children }: { children: (token: string) => ReactNode }) {
  const session = useSession();
  const allowed = session !== null && session.role === "admin";
  useEffect(() => {
    if (!allowed) {
      navigate("/");
    }
  }, [allowed]);
  return allowed && session !== null ? <>{children(session.token)}</> : null;
}
