import { Outlet } from "react-router-dom";
import { Header } from "@/components/Header";
import { CookieNotice } from "@/components/CookieNotice";
import { Footer } from "@/components/Footer";

// frob:doc docs/index.md#routing-and-page-shell
/** Page shell: header and footer wrap whichever route matched (or nothing, outside a router). */
export function App() {
  return (
    <div className="flex min-h-screen flex-col bg-paper font-base text-ink">
      <Header />
      {/* frob:ticket 01M2H5T11GEGRR23QSDXER9PXR */}
      <CookieNotice />
      <div className="flex flex-1 flex-col">
        <Outlet />
      </div>
      <Footer />
    </div>
  );
}
