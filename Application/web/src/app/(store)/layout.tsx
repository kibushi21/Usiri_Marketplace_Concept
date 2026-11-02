import { AssistantWidget } from "@/components/assistant-chat";
import { SiteFooter } from "@/components/footer";
import { SiteHeader } from "@/components/header";

export default function StoreLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SiteHeader />
      <main>{children}</main>
      <SiteFooter />
      <AssistantWidget />
    </>
  );
}
