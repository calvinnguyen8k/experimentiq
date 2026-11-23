import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ExperimentIQ | Experiment planning",
  description: "Design an experiment, calculate its sample size, review risks, and export the plan.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
