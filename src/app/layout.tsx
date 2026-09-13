import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ExactRef",
  description: "Refuse to write a spoken identifier as a verified fact.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app">
          <header className="top">
            <div className="brand">ExactRef</div>
            <div className="mode">Fixture replay · live create disabled</div>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
