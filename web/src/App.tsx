import { Outlet } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

// frob:doc docs/index.md#routing-and-page-shell
/** Page shell: header and footer wrap whichever route matched (or nothing, outside a router). */
export function App() {
  return (
    <>
      <Header />
      {/* frob:todo 01M2H5T11GEGRR23QSDXER9PXR render <CookieNotice /> here, above the Outlet, until dismissed */}
      <Outlet />
      <Footer />
    </>
  );
}
