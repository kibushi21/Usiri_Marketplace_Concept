const numberFormat = new Intl.NumberFormat("en-TZ", { maximumFractionDigits: 0 });

export function money(value: number | null | undefined): string {
  return `TSh ${numberFormat.format(Math.round(value ?? 0))}`;
}

export function shortMoney(value: number | null | undefined): string {
  const amount = Math.round(value ?? 0);
  if (Math.abs(amount) >= 1_000_000) return `TSh ${(amount / 1_000_000).toFixed(1)}m`;
  if (Math.abs(amount) >= 10_000) return `TSh ${Math.round(amount / 1000)}k`;
  return money(amount);
}

export function date(value: string | null | undefined): string {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "—";
  return parsed.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function day(value: string | null | undefined): string {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "—";
  return parsed.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

export function fromNow(value: string | null | undefined): string {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "—";
  const diff = parsed.getTime() - Date.now();
  const abs = Math.abs(diff);
  const minutes = Math.round(abs / 60_000);
  const hours = Math.round(abs / 3_600_000);
  const days = Math.round(abs / 86_400_000);
  const label = minutes < 60 ? `${minutes} min` : hours < 48 ? `${hours} hr` : `${days} days`;
  return diff >= 0 ? `in ${label}` : `${label} ago`;
}

export function percent(bp: number | null | undefined): string {
  return `${((bp ?? 0) / 100).toFixed(1)}%`;
}

export function titleCase(value: string | null | undefined): string {
  if (!value) return "";
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

const TONES: Record<string, string> = {
  green: "badge-green",
  amber: "badge-amber",
  red: "badge-red",
  blue: "badge-blue",
  neutral: "badge-neutral",
  brand: "badge-brand",
};

export function toneClass(tone: string): string {
  return TONES[tone] ?? "badge-neutral";
}

export function statusTone(status: string | null | undefined): string {
  switch (status) {
    case "paid":
    case "completed":
    case "delivered":
    case "succeeded":
    case "refunded":
    case "verified":
    case "active":
    case "approved":
    case "resolved":
      return "green";
    case "awaiting_payment":
    case "pending_payment":
    case "awaiting_acceptance":
    case "awaiting_supplier":
    case "pending":
    case "pending_approval":
    case "requested":
    case "open":
    case "in_progress":
    case "processing":
    case "pending_verification":
    case "booked":
    case "delayed":
    case "delivery_attempted":
      return "amber";
    case "cancelled":
    case "rejected":
    case "failed":
    case "suspended":
    case "succeeded_unmatched":
    case "urgent":
    case "returned_to_sender":
      return "red";
    case "in_transit":
    case "picked_up":
    case "out_for_delivery":
    case "preparing":
    case "accepted":
    case "ready":
    case "shipped":
    case "fulfilling":
    case "approved-hold":
      return "blue";
    case "partially_refunded":
      return "brand";
    default:
      return "neutral";
  }
}

/** Deterministic warm/earthy gradient per product so cards look intentional without photography. */
export function swatch(seed: string): string {
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) % 360;
  }
  const hue = 120 + (hash % 80);
  const hue2 = (hue + 38) % 360;
  return `linear-gradient(145deg, hsl(${hue} 34% 30%), hsl(${hue2} 42% 20%))`;
}

export function initials(value: string): string {
  return value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase() ?? "")
    .join("");
}

export function errorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return "Something went wrong. Please try again.";
}
