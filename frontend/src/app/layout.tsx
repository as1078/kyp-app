import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import React from 'react';
import { StoreProvider } from "./store/StoreProvider";
import PersistWrapper from './store/PersistWrapper';


const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <StoreProvider>
        <html lang="en">
          <body className={inter.className}>
            <PersistWrapper>{children}</PersistWrapper>
            </body>
        </html>
    </StoreProvider>
  );
}
