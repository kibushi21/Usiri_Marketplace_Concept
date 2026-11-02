"use client";

import Link from "next/link";
import { useState } from "react";

import { OpsAuditPanel } from "@/components/ops/audit-panel";
import { ChatInbox } from "@/components/chat-inbox";
import { OpsLedgerPanel } from "@/components/ops/ledger-panel";
import { OpsOrdersPanel } from "@/components/ops/orders-panel";
import { OpsOverviewPanel } from "@/components/ops/overview-panel";
import { OpsPayoutsPanel } from "@/components/ops/payouts-panel";
import { OpsReturnsPanel } from "@/components/ops/returns-panel";
import { OpsSettingsPanel } from "@/components/ops/settings-panel";
import { OpsSuppliersPanel } from "@/components/ops/suppliers-panel";
import { OpsTicketsPanel } from "@/components/ops/tickets-panel";
import { RequireAuth } from "@/components/require-auth";
import { PageHead, Tabs } from "@/components/ui";
import { useAuth } from "@/lib/auth";

type TabId =
  | "overview"
  | "orders"
  | "suppliers"
  | "returns"
  | "tickets"
  | "chats"
  | "payouts"
  | "ledger"
  | "audit"
  | "settings";

const ROLE_LABEL: Record<string, string> = {
  ops_admin: "Operations administration",
  ops_finance: "Finance",
  ops_support: "Customer support",
  superadmin: "Super administrator",
};

export default function OpsPage() {
  return (
    <RequireAuth roles={["ops_admin", "ops_finance", "ops_support", "superadmin"]}>
      <OpsConsole />
    </RequireAuth>
  );
}

function OpsConsole() {
  const { user } = useAuth();
  const [tab, setTab] = useState<TabId>("overview");

  const canManage = user?.role === "ops_admin" || user?.role === "superadmin";
  const canFinance = user?.role === "ops_finance" || user?.role === "superadmin";
  const canDesk = user?.role !== "ops_finance";

  const tabs: { id: TabId; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "orders", label: "Orders" },
    { id: "suppliers", label: "Suppliers" },
    { id: "returns", label: "Returns" },
    { id: "tickets", label: "Support" },
    ...(canDesk ? [{ id: "chats" as TabId, label: "Logistics chat" }] : []),
    ...(canFinance ? [{ id: "payouts" as TabId, label: "Payouts" }] : []),
    ...(canFinance ? [{ id: "ledger" as TabId, label: "Ledger" }] : []),
    { id: "audit", label: "Audit" },
    ...(canManage ? [{ id: "settings" as TabId, label: "Settings" }] : []),
  ];

  return (
    <div className="container portal-body">
      <PageHead
        eyebrow="Operations console"
        title={ROLE_LABEL[user?.role ?? ""] ?? "Operations"}
        description={`Signed in as ${user?.full_name || user?.email}. Every action here is written to the audit trail.`}
        actions={
          <Link href="/shop" className="btn btn-secondary btn-sm">
            Open the storefront
          </Link>
        }
      />

      <div style={{ marginBottom: 22 }}>
        <Tabs items={tabs} active={tab} onChange={setTab} />
      </div>

      {tab === "overview" ? <OpsOverviewPanel onOpenOrders={() => setTab("orders")} /> : null}
      {tab === "orders" ? <OpsOrdersPanel /> : null}
      {tab === "suppliers" ? <OpsSuppliersPanel canManage={canManage} /> : null}
      {tab === "returns" ? <OpsReturnsPanel /> : null}
      {tab === "tickets" ? <OpsTicketsPanel /> : null}
      {tab === "chats" && canDesk ? <ChatInbox audience="ops" /> : null}
      {tab === "payouts" && canFinance ? <OpsPayoutsPanel /> : null}
      {tab === "ledger" && canFinance ? <OpsLedgerPanel /> : null}
      {tab === "audit" ? <OpsAuditPanel /> : null}
      {tab === "settings" && canManage ? <OpsSettingsPanel /> : null}
    </div>
  );
}
