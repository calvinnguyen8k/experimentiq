import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ExperimentIQ | Experiment intake",
  description: "Turn an experiment idea into traceable facts and clear questions.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
