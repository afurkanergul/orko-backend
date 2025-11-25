import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const url = request.nextUrl.clone();
  const pathname = url.pathname;

  // Get auth cookie
  const orkoAuth = request.cookies.get("orko_auth");

  // 🌐 Detect Cypress test mode (env injected in .env.local)
  const isCypress =
    process.env.NEXT_PUBLIC_CYPRESS === "true" ||
    request.headers.get("x-cypress") === "true";

  // 🚀 1) CYPRESS BYPASS — NO REDIRECTS, NO LOGIN
  if (isCypress) {
    console.log("🧪 Cypress mode detected → skipping auth middleware");
    return NextResponse.next();
  }

  // 🚪 2) Redirect to /login if not authenticated
  if (!orkoAuth && pathname.startsWith("/dashboard")) {
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }

  // 🔁 3) Redirect authenticated users away from /login
  if (orkoAuth && pathname === "/login") {
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  // Default allow
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login"],
};
