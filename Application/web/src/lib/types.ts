export type Role =
  | "customer"
  | "supplier"
  | "ops_admin"
  | "ops_finance"
  | "ops_support"
  | "superadmin";

export interface User {
  id: string;
  email: string;
  phone: string | null;
  full_name: string;
  role: Role;
  locale: string;
  supplier_id: string | null;
  email_verified: boolean;
}

export interface Address {
  id: string;
  label: string;
  recipient_name: string;
  phone: string;
  region: string;
  district: string;
  ward: string | null;
  street: string;
  landmark: string | null;
  is_default: boolean;
}

export interface Session {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: User;
}

export interface Me {
  user: User;
  addresses: Address[];
}

export interface Category {
  id: string;
  slug: string;
  name: string;
  name_sw: string;
}

export interface Department {
  id: string;
  slug: string;
  name: string;
  name_sw: string;
  description: string | null;
  categories: Category[];
  product_count: number;
}

export interface ProductSummary {
  id: string;
  slug: string;
  name: string;
  brand: string | null;
  department: string;
  department_slug: string | null;
  department_name: string | null;
  supplier: string;
  supplier_id: string;
  price_from: number;
  price_to: number;
  variant_count: number;
  in_stock: boolean;
  origin: string | null;
}

export interface Variant {
  id: string;
  sku: string;
  name: string;
  price: number;
  available: number;
  weight_g: number;
}

export interface ProductDetail extends ProductSummary {
  description: string;
  attributes: Record<string, string> | null;
  variants: Variant[];
  supplier_region: string;
  supplier_rating: number;
}

export interface ProductPage {
  total: number;
  limit: number;
  offset: number;
  items: ProductSummary[];
}

export interface PhotoSearchResult {
  provider: string;
  tags: string[];
  note: string;
  total: number;
  items: ProductSummary[];
}

export interface CartLine {
  id: string;
  variant_id: string;
  qty: number;
  product_id: string;
  product_slug: string;
  product_name: string;
  variant_name: string;
  unit_price: number;
  line_total: number;
  available: number;
  supplier_id: string;
  supplier_name: string;
  warnings: string[];
}

export interface SupplierTotal {
  supplier_id: string;
  supplier_name: string;
  merchandise_total: number;
  delivery_fee: number;
}

export interface Cart {
  id: string;
  items: CartLine[];
  item_count: number;
  subtotal: number;
  delivery_total: number;
  total: number;
  supplier_groups: SupplierTotal[];
  free_delivery_threshold: number;
  has_warnings: boolean;
}

export interface CheckoutQuote extends Cart {
  can_checkout: boolean;
  issues: string[];
}

export interface OrderItem {
  id: string;
  supplier_order_id: string;
  variant_id: string;
  product_name: string;
  variant_name: string;
  sku: string;
  unit_price: number;
  qty: number;
  line_total: number;
  status: string;
  rejection_reason: string | null;
  refunded_qty: number;
  returnable: boolean;
}

export interface Shipment {
  id: string;
  supplier_order_id: string;
  carrier: string;
  mode: string;
  tracking_number: string | null;
  status: string;
  fee: number;
  booked_at: string | null;
  delivered_at: string | null;
  pod_ref: string | null;
  events: ShipmentEvent[];
}

export interface ShipmentEvent {
  id: string;
  status: string;
  note: string | null;
  actor: string;
  occurred_at: string;
}

export interface SupplierBrief {
  id: string;
  name: string;
  region: string;
  phone: string | null;
}

export interface OrderBrief {
  id: string;
  code: string;
  status: string;
  payment_status: string;
  placed_at: string;
  customer_name: string | null;
  delivery_address: ShipAddress;
}

export interface ShipAddress {
  recipient_name: string | null;
  phone: string | null;
  region: string | null;
  district: string | null;
  ward: string | null;
  street: string | null;
  landmark: string | null;
}

export interface SupplierOrder {
  id: string;
  code: string;
  order_id: string;
  supplier_id: string;
  status: string;
  merchandise_total: number;
  delivery_fee: number;
  commission_bp: number;
  commission_amount: number;
  supplier_payable: number;
  remaining_payable: number;
  refunded_merchandise: number;
  refunded_delivery: number;
  payout_status: string;
  accepted_at: string | null;
  delivered_at: string | null;
  eligible_at: string | null;
  rejection_reason: string | null;
  items: OrderItem[];
  shipments: Shipment[];
  supplier?: SupplierBrief;
  order?: OrderBrief;
}

export interface Order {
  id: string;
  code: string;
  customer_id: string;
  customer_name: string | null;
  status: string;
  stage: string;
  payment_status: string;
  currency: string;
  subtotal: number;
  delivery_total: number;
  total: number;
  refunded_total: number;
  placed_at: string;
  paid_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  notes: string | null;
  delivery_address: ShipAddress;
  supplier_orders: SupplierOrder[];
  item_count: number;
  items?: OrderItem[];
}

export interface Payment {
  id: string;
  order_id: string;
  provider: string;
  provider_ref: string | null;
  amount: number;
  currency: string;
  method: string;
  msisdn: string | null;
  status: string;
  initiated_at: string;
  completed_at: string | null;
  failure_reason: string | null;
  redirect_url?: string | null;
}

export interface Refund {
  id: string;
  order_id: string;
  supplier_order_id: string | null;
  amount: number;
  merchandise_amount: number;
  delivery_amount: number;
  commission_reversal: number;
  status: string;
  reason: string;
  created_at: string;
  completed_at: string | null;
}

export interface ReturnRecord {
  id: string;
  code: string;
  order_id: string;
  supplier_order_id: string;
  item_id: string;
  qty: number;
  reason: string;
  details: string | null;
  status: string;
  decision_note: string | null;
  refund_amount: number | null;
  requested_at: string;
  decided_at: string | null;
  received_at: string | null;
  refund_id: string | null;
  order_code?: string | null;
  item?: { product_name: string; variant_name: string; unit_price: number };
}

export interface Payout {
  id: string;
  supplier_id: string;
  amount: number;
  status: string;
  period_start: string;
  period_end: string;
  requested_by: string;
  approved_by: string | null;
  approved_at: string | null;
  paid_at: string | null;
  provider_ref: string | null;
  notes: string | null;
  rejection_reason: string | null;
  created_at: string;
  supplier_name?: string | null;
  supplier?: { id: string; trading_name: string; code: string; region: string } | null;
  orders?: { id: string; code: string; payable: number }[];
}

export interface TicketMessage {
  id: string;
  author_id: string;
  body: string;
  internal: boolean;
  created_at: string;
}

export interface Ticket {
  id: string;
  code: string;
  order_id: string | null;
  customer_id: string;
  subject: string;
  category: string;
  priority: string;
  status: string;
  assigned_to: string | null;
  created_at: string;
  closed_at: string | null;
  messages?: TicketMessage[];
  customer_name?: string | null;
  customer_email?: string | null;
  order_code?: string | null;
}

export interface PlatformSettings {
  values: Record<string, string | number | boolean>;
  labels: Record<string, string>;
  defaults: Record<string, string | number | boolean>;
}

export interface PayoutBalance {
  eligible: number;
  in_payout: number;
  settled: number;
  orders_awaiting_hold: number;
}

export interface SupplierDashboard {
  supplier: {
    id: string;
    code: string;
    legal_name: string;
    trading_name: string;
    status: string;
    region: string;
    city: string;
    rating: number;
    commission_bp: number | null;
    payout_method: string;
    payout_provider: string;
    contact_name: string | null;
    contact_email: string | null;
    contact_phone: string | null;
  };
  balance: PayoutBalance;
  summary: {
    by_status: Record<string, { orders: number; value: number }>;
    commission: number;
    products: number;
  };
  recent_orders: SupplierOrder[];
  config: { payout_hold_days: number; commission_bp: number };
}

export interface OpsSummary {
  orders_paid: number;
  gmv: number;
  refunds: number;
  net_gmv: number;
  commission_earned: number;
  delivery_earned: number;
  supplier_payable: number;
  cash_at_psp: number;
  orders_by_status: Record<string, number>;
  supplier_orders_by_status: Record<string, number>;
  awaiting_supplier_acceptance: number;
  pending_payouts: number;
  pending_payout_value: number;
  open_returns: number;
  low_stock: { product: string; sku: string; on_hand: number; reserved: number }[];
  top_products: { product: string; qty: number; value: number }[];
}

export interface OpsDashboard {
  summary: OpsSummary;
  recent_orders: Order[];
  awaiting_acceptance: {
    id: string;
    code: string;
    order_code: string | null;
    supplier: string | null;
    value: number;
    items: number;
    created_at: string;
  }[];
}

export interface SupplierVariantRow {
  id: string;
  sku: string;
  name: string;
  price: number;
  on_hand: number;
  reserved: number;
  available: number;
  active: boolean;
  weight_g: number;
}

export interface SupplierProduct extends Omit<ProductDetail, "variants"> {
  status: string;
  created_at: string;
  variants: SupplierVariantRow[];
}

export interface SupplierDirectoryEntry {
  id: string;
  code: string;
  name: string;
  legal_name: string;
  status: string;
  region: string;
  products: number;
  rating: number;
}

export interface SupplierProfile {
  id: string;
  code: string;
  legal_name: string;
  trading_name: string;
  status: string;
  region: string;
  city: string;
  rating: number;
  commission_bp: number | null;
  payout_method: string;
  payout_provider: string;
  contact_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  tin: string;
  brela_number: string;
  payout: { method: string; provider: string; account_name: string; account_number: string };
  documents: { id: string; type: string; status: string; file_ref: string | null; notes: string | null }[];
  balance: PayoutBalance;
  products: { id: string; name: string; status: string; variants: number; stock: number }[];
}

export interface LedgerBalance {
  code: string;
  name: string;
  kind: string;
  balance: number;
}

export interface LedgerView {
  balances: LedgerBalance[];
  balanced: boolean;
  transactions: {
    id: string;
    kind: string;
    reference: string;
    memo: string | null;
    created_at: string;
    entries: { account: string; debit: number; credit: number }[];
  }[];
}

export interface AuditEntry {
  id: string;
  actor: string;
  actor_role: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  created_at: string;
}

export interface OpsOrder extends Order {
  customer: User | null;
  payments: Payment[];
  refunds: Refund[];
  returns: ReturnRecord[];
  audit: { action: string; actor_role: string; entity_type: string; entity_id: string; created_at: string }[];
}

export interface Meta {
  platform: string;
  currency: string;
  delivery_fee_flat: number;
  free_delivery_threshold: number;
  return_window_days: number;
  reservation_ttl_minutes: number;
  support_email: string;
  support_phone: string;
  providers: { payments: string; carrier: string };
}

export interface Notification {
  id: string;
  channel: string;
  template: string;
  payload: Record<string, unknown> | null;
  status: string;
  created_at: string;
  read_at: string | null;
}

export interface PublicSupplier {
  id: string;
  name: string;
  region: string;
  city: string;
  rating: number;
  products: ProductSummary[];
}

export interface StockRow {
  id: string;
  sku: string;
  name: string;
  price: number;
  on_hand: number;
  reserved: number;
  available: number;
  active: boolean;
}

export interface AssistantChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AssistantChatResult {
  reply: string;
  provider: string;
  model: string | null;
  note: string;
  audience: "customer" | "ops";
  products: ProductSummary[];
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  author_id: string | null;
  author_name: string;
  author_party: "customer" | "supplier" | "logistics" | "system";
  body: string;
  kind: "text" | "system" | "handoff";
  created_at: string;
}

export interface ChatConversation {
  id: string;
  code: string;
  order_id: string;
  order_code: string | null;
  supplier_order_id: string;
  supplier_order_code: string | null;
  supplier_id: string;
  supplier_name: string;
  customer_id: string;
  customer_name: string;
  assigned_party: "supplier" | "logistics";
  assigned_name: string;
  handoff_at: string | null;
  handoff_note: string | null;
  last_message_at: string;
  created_at: string;
  shipment: {
    carrier: string;
    tracking_number: string | null;
    status: string;
  } | null;
  last_message: ChatMessage | null;
  can_reply: boolean;
  can_handoff: boolean;
  can_take_over: boolean;
  can_return: boolean;
  messages?: ChatMessage[];
}
