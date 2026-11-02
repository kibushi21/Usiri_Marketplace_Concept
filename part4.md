---

# 12. Payments, trust and legal foundations

> **This section is a map of issues, not legal advice.** Tanzania's rules change, and their application depends on facts the group has not yet established. A qualified Tanzanian lawyer, accountant and, where relevant, the regulator must review the structure before launch. The group should budget for this review in Phase 4.

## 12.1 The payment flow we intend to use

The simplest compliant design is:

1. **Customer pays** through a licensed payment service provider (PSP) using mobile money, a card or a bank transfer. The PSP hosts the payment page or an in-app payment sheet.
2. **The PSP settles** the collected funds to the platform's merchant account, net of its fees, on an agreed cycle.
3. **The platform records** the order, the payment reference and the fee.
4. **The supplier is paid** after delivery is confirmed and the return window has passed, on a published schedule (for example T+3 or weekly), less commission and any adjustments.
5. **Refunds** are processed through the same PSP, with a clear reason code and a service-level target.
6. **Reconciliation** matches order, payment, settlement, refund and payout records daily.

The platform should use the PSP's **split-payment or marketplace settlement** feature if available, so that supplier funds are segregated or paid out under the provider's licence. If no such feature is available, the platform must confirm with counsel whether holding supplier funds creates a payment-service, deposit-taking or trust-account obligation.

**Do not call the arrangement "escrow" unless a licensed party is legally acting as escrow agent under a proper agreement.** An ordinary platform wallet that holds money for a few days is not escrow. Using the word loosely creates legal and reputational risk.

## 12.2 Payment methods

| Method | Customer appeal | Platform considerations | Status |
|---|---|---|---|
| Mobile money (M-Pesa, Mixx by Yas, Airtel Money, HaloPesa, T-Pesa, Azam Pesa) | High; familiar; low friction | Multiple integrations; fees; settlement times; phone-number verification | Likely core |
| Cards (Visa/Mastercard) | Useful for some customers and expatriates | Chargebacks; 3-D Secure; higher fees; fraud risk | Secondary |
| Bank transfer | Useful for larger orders and suppliers | Manual reconciliation; delayed confirmation | Limited |
| Cash on delivery | Trust for first-time buyers | Cash handling, refusal, theft, reconciliation; may require a courier licence or partner | Optional, restricted |
| TIPS / TANQR | Interbank and QR payments | Requires PSP support; customer familiarity varies | Explore |
| Wallet/credits | Repeat customers | Licensing and safeguarding issues; float risk | Avoid initially |

The exact list depends on what the chosen PSP supports. The platform should not integrate directly with every telco at launch; a licensed aggregator reduces complexity, even if the fee is slightly higher.

## 12.3 Reconciliation and payouts

Reconciliation is the least glamorous and most important finance process. A marketplace can appear to grow while losing money through unrecorded refunds, duplicate payouts, uncollected fees and carrier overbilling.

**Daily controls:**

- Match every order to a payment reference and a settlement line.
- Identify payments without orders and orders without payments.
- Record PSP fees per transaction, not as a monthly total.
- Match refunds to the original payment.
- Match carrier invoices to the manifest and rate card.
- Flag duplicates and anomalies.

**Payout controls:**

- Hold supplier payouts until delivery is confirmed and the return window closes.
- Deduct commission, refunds, penalties and any chargebacks with a clear statement.
- Require dual approval above a threshold.
- Keep a reserve (for example 5–10% of payouts) for a defined period to cover disputes.
- Publish the payout calendar and keep to it.
- Never pay a supplier to a different account without verified change control.

**Monthly close:**

- Reconcile the PSP balance, bank account, supplier payable ledger and order ledger.
- Review refunds, chargebacks, write-offs and exceptions.
- Compare budget to actual and explain variances.
- Sign off by finance and CEO.

## 12.4 Refunds, returns and chargebacks

The published policy should answer, in plain language:

- What can be returned, within how many days, and in what condition.
- What cannot be returned (for example, opened personal-care items, customised goods).
- Who pays return delivery, and when.
- How long a refund takes and to which method.
- What happens if the item is damaged, wrong or missing.
- How a dispute is escalated and decided.
- What the customer's statutory rights are, where they override the policy.

A common failure is to promise "easy returns" in marketing and then make the process difficult. The policy must match the operating capability. If the platform cannot inspect a returned item within 48 hours, it should not promise a 48-hour refund.

Chargebacks are different from ordinary refunds: the card issuer decides, often on documentary evidence. The platform needs a chargeback playbook, evidence templates and a fraud review before the first card payment is accepted.

## 12.5 Fraud and abuse controls

| Fraud type | How it appears | Control |
|---|---|---|
| Stolen payment instrument | Card or mobile money used without authorisation | PSP risk checks; 3-D Secure; device and phone verification; velocity limits |
| Fake payment screenshot | Customer claims payment but no settlement | Only fulfil on confirmed PSP settlement, never on a screenshot |
| Refund abuse | Repeated "not received" or "damaged" claims | Evidence requirements; pattern detection; account review |
| COD refusal | Customer refuses a parcel at the door | Phone confirmation; deposit for high-value orders; restrict COD |
| Supplier non-delivery | Supplier takes order but does not ship | Staged payouts; scorecard; delisting; reserve |
| Counterfeit goods | Product is not genuine | KYC; sample checks; brand authorisation; buyer reports; delisting |
| Account takeover | Attacker changes payout or address | MFA; change cooling period; notification; manual review |
| Internal fraud | Staff issue refunds to accomplices | Segregation of duties; audit logs; threshold approvals |

Fraud controls should be proportionate. Treating every customer as a criminal destroys conversion; treating none as a risk destroys the business. Start with simple rules, measure false positives and adjust.

## 12.6 Seller verification (KYC)

A verified seller is the platform's most important trust asset. The minimum check is:

- Legal identity: business registration or sole-trader ID, TIN, physical address.
- Ownership: who owns the business, and who is authorised to sign.
- Bank/mobile money account in the business name; verification of the account.
- Physical inspection: visit the shop, photograph the premises, check stock.
- Product legitimacy: invoices, brand authorisation where relevant, sample inspection.
- References: landlord, wholesaler or other marketplace.
- Sanctions/adverse media check where proportionate.
- Signed supplier agreement, including warranties, returns and data terms.
- Periodic re-verification (annual or on trigger).

High-risk categories (electronics, beauty, baby, health) require additional checks. A seller that fails verification should be rejected with a written reason and a route to appeal.

## 12.7 Consumer protection and standard-form contracts

Tanzania's Fair Competition Commission administers rules on standard-form consumer contracts. The Standard Form (Consumer Contracts) Regulations 2014 require certain standard-form contracts to be registered with the FCC, with an application and review process [S16]. The platform's customer terms, supplier terms and returns policy may fall within scope.

Practical steps:

- Draft terms in plain Swahili and English, with a readable summary.
- Avoid unfair terms: one-sided refund exclusions, unlimited liability disclaimers, unilateral price changes.
- Show the total price, delivery fee, taxes and return rights before payment.
- Register the standard-form contract as advised; keep the acknowledgement.
- Maintain a complaints log and respond within published times.
- Train support staff to apply the policy consistently.
- Review terms when the model changes.

The FCC process is not a one-off formality. A contract that is registered but not followed is still a consumer-protection problem.

## 12.8 Data protection (PDPA 2022)

The Personal Data Protection Act 2022 establishes the Personal Data Protection Commission and a set of obligations for organisations that collect personal data [S14]. Law-firm commentary reports a registration deadline of 8 April 2026, with enforcement from 9 April 2026 and a requirement for a Data Protection Officer [S15]. That date has passed; the group must confirm the current registration status, procedure and any transitional arrangements directly with the PDPC or counsel.

The platform will collect names, phone numbers, addresses, order histories, payment references, supplier KYC documents and possibly location data. The compliance baseline is:

- **Lawful basis:** identify the basis for each processing purpose (contract, consent, legal obligation, legitimate interest).
- **Notice:** tell people what is collected, why, for how long and who receives it.
- **Minimisation:** collect only what is needed. Do not collect ID numbers "just in case".
- **Consent:** where consent is the basis, make it specific, informed and easy to withdraw. Do not bundle consent into terms.
- **Data subject rights:** access, correction, deletion where applicable, objection, portability where relevant.
- **Retention:** a schedule by data type; delete or anonymise when no longer needed.
- **Security:** encryption, access control, logging, vendor management.
- **Breach response:** detect, contain, assess, notify the PDPC and affected individuals as required, and document.
- **Cross-border transfer:** confirm safeguards before using a cloud provider that stores data outside Tanzania.
- **Processor agreements:** contracts with PSPs, carriers, SMS providers and cloud hosts.
- **DPO:** appoint a competent person and give them access to the board.
- **Records:** maintain a data inventory and processing register.

Penalties reported by law firms can be severe, including substantial fines and imprisonment for serious breaches [S14]. The point is not the maximum penalty; it is that a data breach destroys customer trust faster than a delivery failure.

## 12.9 Electronic transactions and records

The Electronic Transactions Act 2015 (Cap. 442 R.E. 2022) recognises electronic transactions, signatures and records [S19]. This supports online contracting, electronic invoices and digital records, subject to the Act's requirements. The platform should:

- Keep reliable records of order confirmation, terms acceptance and payment.
- Use an audit trail for electronic signatures on supplier agreements.
- Ensure invoices and receipts meet tax requirements.
- Retain records for the period required by tax and commercial law.

## 12.10 Tax

The main taxes to confirm with an accountant are:

| Tax | Current reported position | What it means for the platform |
|---|---|---|
| VAT | Standard rate 18%; registration threshold TZS 200m turnover (or TZS 100m in six months) [S11] | Monitor threshold; VAT on commission and fees; input VAT on eligible costs; invoices |
| Corporate income tax | 30% for resident companies [S12] | Tax on profit, not GMV; losses may carry forward subject to rules |
| Withholding tax | Applies to certain payments; 15% reported on non-resident royalties [S13] | Brand licence or franchise fees may attract withholding; confirm |
| Payroll taxes | PAYE, social security and other contributions | Register as an employer; payroll compliance |
| Customs and import duty | Applies to imported goods | Supplier responsibility, but the platform should not facilitate under-declaration |
| Digital services / e-commerce rules | May change | Confirm current treatment with counsel and TRA |

The platform should issue proper invoices for commission and fees, keep VAT records, and not treat pass-through delivery charges as its own revenue without advice. Tax treatment of marketplace facilitator models can be complex; assume nothing.

## 12.11 Brand, trademark and franchise law

Tanzania has no stand-alone franchise statute. Franchise and brand-licence relationships are governed mainly by the Law of Contract Act (Cap. 345) and the Trade and Service Marks Act (Cap. 326), with competition and consumer rules also relevant [S13].

Key points:

- Register the platform's own trademark and secure the domain and social handles.
- Conduct a trademark search before adopting a name.
- A brand licence must be in writing, with scope, quality control, fees, term and termination.
- Franchise-like arrangements may attract withholding tax on royalties; confirm.
- Do not use another company's mark, packaging or photography without permission.
- Have a takedown process for counterfeit or infringing listings.
- Protect customer and supplier data; do not let a brand owner access it without a lawful basis.

## 12.12 Transport, liability and insurance

When a parcel is lost or damaged, the customer will look to the platform, even if the carrier caused the loss. The platform's terms should explain the remedy, and its carrier contract should allocate the cost.

Questions to resolve:

- What is the carrier's liability limit per parcel? Is it based on weight, declared value or a fixed cap?
- Are goods in transit insured? By whom? What are the exclusions?
- What evidence is required for a claim, and within what time?
- Who bears the cost of a failed delivery or return?
- Does the platform need its own goods-in-transit or public liability cover?
- Does the platform need a courier licence, or is it a customer of licensed carriers? TCRA licenses postal and courier operators, with application and licence fees [S17]. The answer depends on whether the platform takes possession of parcels or merely arranges carriage.

The group should obtain written confirmation from TCRA or counsel on the licensing question before handling parcels itself. Using licensed carriers reduces the risk but does not eliminate the platform's obligations to customers.

## 12.13 Address quality

Tanzania has a national postcode and addressing programme [S18], but many deliveries still rely on landmarks, phone calls and local knowledge. The platform should:

- Capture a landmark, ward and phone number, not only a street address.
- Allow a pin location where the customer can share one.
- Confirm the address by phone or SMS before dispatch.
- Maintain a delivery-zone table with expected transit times.
- Record failed-delivery reasons to improve the address database.

## 12.14 Compliance calendar (first year)

| Month | Item | Owner |
|---|---|---|
| 1 | Company registration, TIN, business licence, bank account | Finance |
| 1 | Trademark search and application | Finance/legal |
| 1–2 | Supplier agreement, customer terms, privacy notice | Legal adviser |
| 2 | PDPC registration and DPO appointment (confirm current rules) | Finance/compliance |
| 2 | FCC standard-form contract filing (confirm scope) | Legal adviser |
| 2 | PSP merchant application and KYC | Finance |
| 3 | Insurance review (goods in transit, public liability, cyber) | Finance |
| 3 | Employment contracts and payroll registration | Finance |
| 3 | VAT registration assessment | Accountant |
| 4 | Carrier agreements and SLA | CEO/COO |
| 4 | Security review and pen test | CTO |
| 6 | First compliance audit | Finance/compliance |
| 9 | Contract and policy review | Legal adviser |
| 12 | Annual tax and data-protection review | Finance/compliance |

## 12.15 Questions for lawyers, accountants and regulators

**Corporate and commercial**

1. What is the appropriate company structure for a group of founders with unequal time commitments?
2. How should founder equity, vesting and IP assignment be documented?
3. What disclosures and approvals are needed for a brand licence or franchise?
4. Can the platform enforce a supplier agreement that includes indemnities and chargebacks?
5. What consumer terms are required for distance selling, and which are unfair?

**Payments**

6. Does the proposed flow require a payment-service licence, or is the PSP's licence sufficient?
7. Can the platform hold supplier funds, and for how long, without a trust or payment licence?
8. What are the PSP's settlement, refund, chargeback and reserve terms?
9. How should the platform handle failed payments, duplicate payments and partial refunds?
10. What are the AML/KYC obligations for suppliers and high-risk customers?

**Data protection**

11. What is the current PDPC registration procedure and status?
12. Who should be the DPO, and what qualifications are required?
13. What lawful basis applies to marketing, analytics and fraud prevention?
14. Can customer data be stored on cloud servers outside Tanzania, and with what safeguards?
15. What is the breach notification timeline and format?

**Consumer and competition**

16. Which standard-form contracts must be filed with the FCC, and what is the process?
17. What refund and return rights cannot be excluded?
18. Do exclusivity or most-favoured-customer terms raise competition concerns?
19. How should complaints and disputes be recorded and escalated?

**Tax and transport**

20. How should commission, subscriptions, delivery fees and pass-through charges be treated for VAT?
21. Does the platform have withholding obligations on supplier payments or brand royalties?
22. Does the platform need a courier licence, or can it operate as a customer of licensed carriers?
23. What insurance is required or prudent for parcels, liability and cyber risk?
24. What records must be kept, and for how long?

These questions should be answered in writing and stored with the project's legal file. The answers will change the model; that is the point of asking before launch.

---

# 13. Market research and competitor analysis

## 13.1 Method and limits

This section is based on desk research conducted in October 2026: company websites, official statistics, government guidance and news reports. It is **not** a substitute for primary research. The group has not yet interviewed customers, suppliers or carriers, and has not run a pricing test. Market shares are not published in a reliable form, and this document does not invent them.

The desk research had three purposes: understand the customer's alternatives, identify what has and has not worked in Tanzania, and frame the questions that primary research must answer.

## 13.2 The competitive set

The platform would compete with several different kinds of alternative, not one competitor.

| Alternative | Model | Strengths | Weaknesses / gaps | What it means for the project |
|---|---|---|---|---|
| **Jiji** | Classifieds; sellers and buyers connect; no fulfilment [S21] | Large selection; familiar brand; free listing; strong SEO | No payment protection, delivery or consistent seller verification; buyer must negotiate | The platform must offer a materially safer, more convenient transaction, not just listings |
| **Kupatana** | Classifieds; broad categories [S22] | Established classifieds brand; broad inventory | Same structural gaps as classifieds; quality varies | Do not compete on number of listings; compete on completed orders |
| **KiKuu** | Cross-border e-commerce; ships into multiple countries [S23] | Low prices; wide assortment; established logistics for cross-border | Long delivery times; returns difficult; customs; limited local after-sales | Local stock and fast, accountable delivery are the differentiator |
| **Dar Shopping** | Local e-marketplace; delivery and pickup; cash on delivery and online payment [S24] | Local presence; delivery options; broad categories | Scale and seller quality unknown; trust and consistency are hard | A direct comparator; differentiate on curation, verification and service |
| **Jumia** | Pan-African marketplace; exited Tanzania in 2019 [S9]; reportedly considering a return in 2025 [S10] | Capital, systems, brand recognition if it returns | Past exit shows the difficulty; no confirmed launch | A returning Jumia would validate the market and intensify competition; do not plan on its absence |
| **Social commerce** (Instagram, Facebook, WhatsApp, TikTok) | Sellers market and negotiate directly; payment by mobile money; delivery informal | Low cost; personal; huge reach; impulse buying | No buyer protection; inconsistent delivery; no catalogue; trust depends on reputation | Partner with good social sellers rather than only competing with them |
| **Kariakoo and local shops** | Physical retail; negotiate in person; cash or mobile money | Immediate possession; see the product; relationships | Time cost; traffic; no delivery; limited comparison | The benchmark for price and trust; online must beat the total experience, not just the price |
| **Brand stores and supermarkets** | Brand.com or retail chain e-commerce | Authenticity; warranty; trusted returns | Narrow assortment; limited delivery coverage; higher prices | Potential suppliers or partners; not direct competitors in the chosen category |
| **Informal resellers** | Individual buyers who resell via social media | Flexible; cheap; personal service | No accountability; counterfeit risk; no scale | Some are potential suppliers; others are competition on price |

## 13.3 What the competitive picture tells us

**First, the market is not won by listings.** Jiji and Kupatana already aggregate enormous choice. A new site with fewer listings cannot win by being a smaller classifieds site. It must win by completing orders and standing behind them.

**Second, cross-border price competition is real.** KiKuu and similar platforms can undercut local prices on many goods. The local platform should not try to be the cheapest on every item. It should compete on delivery time, returns, local warranty and the ability to speak to someone.

**Third, a returning Jumia is a serious possibility.** If Jumia re-enters, it will bring capital, systems and brand awareness. The project's defence is not to outspend it but to be more trusted and more locally embedded in a narrow segment. A small marketplace can coexist with a large one if it serves a specific customer better.

**Fourth, social commerce is both competitor and supply channel.** Many good sellers already have Instagram and WhatsApp audiences. The platform can offer them fulfilment, payments and a storefront, rather than asking them to abandon their audience. This is a realistic supplier acquisition strategy.

## 13.4 Differentiation hypothesis

The proposed differentiation is a combination, not a single feature:

1. **Verified local sellers.** Physical verification, not just a phone number.
2. **Coordinated delivery.** One place to track, one party accountable.
3. **Buyer protection.** Clear returns and refunds, with a real remedy.
4. **Curation.** A focused assortment in home and kitchen, not an endless bazaar.
5. **Local support.** Swahili-speaking support within business hours, reachable by phone or WhatsApp.
6. **Supplier tools.** A simple portal, predictable payouts and fair rules.

Each feature is copyable. The combination, executed consistently, is the moat. Trust is built slowly and lost quickly; that is why operations matter more than the website.

## 13.5 Positioning statement

> For Dar es Salaam households who want home and kitchen goods without the risk of paying a stranger online, **Usiri Marketplace** (working name) is a curated marketplace that verifies every seller, coordinates delivery and resolves problems within 48 hours. Unlike classifieds and social sellers, it stands behind the order; unlike cross-border platforms, it delivers from local stock with local after-sales support.

The name is a working label only. It cannot be used publicly without a licence from Usiri. If no licence is agreed, the project must adopt an independent name.

## 13.6 Research gaps

The desk research cannot answer the questions that determine viability. The Phase 2 research must cover:

| Question | Method | Sample | Evidence standard |
|---|---|---|---|
| What do customers buy online today, and why? | Interviews | 30 | Recorded themes, not anecdotes |
| What delivery fee will they pay? | Survey with price options | 150+ | Stated preference; validate with a real test |
| What stops them buying from a new marketplace? | Interviews and survey | 30 + 150 | Ranked barriers |
| Which categories have the highest repeat potential? | Interviews and purchase diary | 30 | Actual or recent purchases |
| What commission will suppliers accept? | Supplier interviews | 15 | Specific percentage and rationale |
| What are the real carrier rates? | Quote requests | 3 carriers | Written rate card |
| What do returns cost? | Supplier and carrier interviews | 10 | Cost per return |
| Who are the credible suppliers? | Field visits | 40 | Verification checklist |
| What are competitors' delivery and return promises? | Mystery shopping | 8 | Screenshots and timestamps |
| Is a brand licence available and at what cost? | Partner meeting | 1–2 | Written indication |

## 13.7 Competitor monitoring

After launch, the group should track competitors monthly on a simple scorecard:

- Assortment breadth in the target category.
- Prices on a basket of 20 comparable SKUs.
- Delivery fee and promised time.
- Return policy and actual ease of return.
- Seller acquisition activity.
- Marketing channels and offers.
- Customer complaints on social media.

The purpose is not to copy. It is to notice when a competitor changes the rules, and to avoid being surprised.

---

# 14. Feasibility assessment

## 14.1 Overall judgement

The project is **technically feasible, operationally demanding, legally manageable and financially fragile at pilot scale**. It is not a bad idea; it is a hard business with a narrow margin for error. The group should proceed only if it is willing to run a disciplined, evidence-led research phase and to stop if the evidence does not support the model.

| Dimension | Rating | Rationale |
|---|---|---|
| Market | **Conditional** | Large population and growing digital payments, but unproven willingness to pay for a new marketplace; strong alternatives |
| Operational | **Challenging** | Multi-supplier fulfilment, address quality, carrier reliability and returns are hard; a small team can manage only a narrow scope |
| Technical | **Feasible** | Standard web stack, licensed payments and manual logistics are enough for a pilot; no exotic technology required |
| Financial | **Weak at pilot** | Contribution per order is thin; fixed costs consume it below about 1,200 orders/month in the moderate case |
| Legal / regulatory | **Manageable but non-trivial** | Registration, PDPA, FCC, tax, payments and transport liability all require professional advice and ongoing compliance |

## 14.2 SWOT

| Strengths | Weaknesses |
|---|---|
| Asset-light model; low capital relative to inventory retail | Thin unit economics; dependent on volume |
| Clear trust proposition in a low-trust market | No proprietary supply, brand or logistics asset |
| Local knowledge and language | Small team with limited operating experience |
| Narrow initial category reduces complexity | No proven demand; no customer base |
| Technology can be built or bought incrementally | Dependence on carriers and payment providers |
| Ability to learn quickly and pivot | Founder time and funding constraints |

| Opportunities | Threats |
|---|---|
| Social commerce sellers need fulfilment and trust | Jumia or another funded marketplace re-enters |
| Mobile money penetration and merchant growth | Carrier failure or price increase |
| Jumia's absence leaves a gap | Regulatory change or enforcement |
| Suppliers want digital reach without losing control | Fraud, counterfeits and reputational damage |
| Brand partnership with a trusted local name | Usiri declines or demands uneconomic terms |
| Expansion to B2B or adjacent cities after proof | Economic pressure reduces discretionary spending |

## 14.3 Risk register

Scores use likelihood 1–5 and impact 1–5; the score is the product. The full register, with editable scores, is in the workbook. The table below summarises the highest-priority risks. **These are assessments, not measured probabilities.**

| ID | Risk | Category | L | I | Score | Mitigation | Owner |
|---|---|---|---:|---:|---:|---|---|
| R01 | Usiri declines or negotiations stall | Strategic/partner | 4 | 5 | 20 | Independent-brand track; two alternative carriers; decision deadline before brand spend | Founder lead |
| R02 | Supplier fraud, counterfeit or misrepresentation | Commercial/trust | 3 | 5 | 15 | KYC, shop visits, samples, category limits, warranties, reserve, delisting | COO |
| R03 | Delivery failures, late or damaged parcels | Operational | 4 | 4 | 16 | Written SLA, two attempts, collection points, photos, insurance, exception desk | Ops lead |
| R04 | Low demand or high acquisition cost | Commercial | 4 | 4 | 16 | Narrow segment, waiting list, supplier-led demand, referrals, stop-loss budget | CEO |
| R05 | Thin margins make the model unviable | Financial | 4 | 4 | 16 | Test 8–12% commission, subscriptions, delivery fee; keep fixed costs lean | Finance lead |
| R06 | Payment fraud, chargebacks or reconciliation gaps | Financial/technology | 3 | 4 | 12 | Licensed PSP, device checks, velocity limits, daily reconciliation, payout holds | CTO |
| R07 | Data breach or PDPA non-compliance | Legal/technology | 3 | 5 | 15 | PDPC registration, data map, least privilege, encryption, breach playbook, insurance | CTO/DPO |
| R08 | Consumer-contract or returns policy challenged | Legal/reputation | 3 | 3 | 9 | Plain-language terms, FCC filing, clear returns, complaints log, legal review | Legal adviser |
| R09 | Jumia or another funded marketplace enters | Competitive | 3 | 5 | 15 | Differentiate on verification, delivery and support; avoid subsidy war; supplier switching costs | CEO |
| R10 | Over-dependence on one logistics partner | Operational/strategic | 4 | 3 | 12 | Qualify a second carrier; adapter layer; standard SLAs and parcel IDs | Ops lead |
| R11 | Key-person dependency and unclear founder roles | Organisational | 4 | 3 | 12 | Written roles, equity and vesting, documented processes, cross-training, IP assignment | Founders |
| R12 | Technology outage or security incident | Technology | 3 | 4 | 12 | Managed hosting, backups tested, monitoring, status page, incident runbook, WAF | CTO |
| R13 | Regulatory change or new tax rules | Regulatory | 3 | 3 | 9 | Quarterly review, accountant on retainer, flexible contracts, compliance calendar | Legal adviser |
| R14 | Currency or inflation pressure | Financial | 3 | 3 | 9 | TZS pricing, periodic repricing, cost buffers, avoid USD-linked commitments | Finance lead |
| R15 | Brand or reputational damage from an incident | Reputation | 2 | 5 | 10 | Brand-use guidelines, rapid response, compensation policy, transparency, escalation | CEO |

**Reading the register:** R01 and R03/R04/R05 are the risks that should shape the plan. R01 is addressed by the fallback track. R03–R05 are addressed by starting narrow, keeping fixed costs low and setting stop-loss triggers. The register should be reviewed monthly; a risk that is not reviewed is a decoration.

## 14.4 Scenario analysis

The model has three cost structures. The table shows the monthly operating result at different order volumes, with ancillary revenue ramping as in the cash plan. It illustrates operating leverage: small changes in volume produce large changes in profit or loss.

| Monthly orders | Lean (fixed TZS 2.2m) | Moderate (fixed TZS 5.6m) | Ambitious (fixed TZS 12m) |
|---:|---:|---:|---:|
| 300 | (681,000) | (4,081,000) | (10,481,000) |
| 900 | 1,957,000 | (1,443,000) | (7,843,000) |
| 1,200 | 3,376,000 | (24,000) | (6,424,000) |
| 1,500 | 4,495,000 | 1,095,000 | (5,305,000) |
| 3,000 | 10,090,000 | 6,690,000 | 290,000 |

Assumptions: contribution TZS 3,730/order; ancillary TZS 400,000 at 300 orders, TZS 800,000 at 900, and TZS 1.1m at 1,200 or more, for all scenarios. Figures are rounded to the nearest thousand and are planning illustrations, not forecasts.

The table shows why the lean structure is the right starting point. It can survive at 900 orders; the moderate structure cannot. The ambitious structure needs thousands of orders before it is viable, which is why it should not be attempted without serious capital and a proven playbook.

## 14.5 Kill criteria

The group should agree in advance what would cause it to stop. Proposed criteria:

- After Phase 2, fewer than 30% of surveyed customers say they would pay a delivery fee, or fewer than 15 suppliers meet the verification standard.
- No carrier can offer a written rate and service level within 20% of the model assumption.
- The best achievable commission is below 6% and suppliers refuse subscriptions.
- A pilot cannot reach 300 orders/month within six months despite a reasonable marketing spend.
- Contribution per order is below TZS 2,000 after three months of operation.
- A legal or regulatory issue cannot be resolved within the budget.
- The founders cannot commit the time required for 12 months.

Stopping is a legitimate outcome. It preserves capital and reputation for the next idea.

---

# 15. Startup costs and financial planning

## 15.1 Basis of the numbers

All figures are in Tanzanian shillings and are **planning assumptions**, not quotations. They are rounded and inclusive of VAT where VAT would apply, unless stated. The model uses an exchange rate of TZS 2,645 per USD for any conversion; the rate moves, so USD-denominated costs should be rechecked.

Three scenarios are presented:

- **Lean:** founder-led, unpaid founder time, minimal office, one contractor, manual operations. Suitable for a student group with limited capital.
- **Moderate:** small paid team, part-time technical support, modest office, professional advice. Requires external funding or significant savings.
- **Ambitious:** experienced team, larger build, marketing budget, multi-city preparation. Included for comparison; not recommended before proof.

## 15.2 One-time startup costs

| Item | Lean (TZS) | Moderate (TZS) | Ambitious (TZS) | Notes |
|---|---:|---:|---:|---|
| Company formation, TIN, licence, basic legal | 1,500,000 | 2,500,000 | 4,000,000 | BRELA, tax, basic contracts |
| Partner/franchise negotiation and due diligence | 1,500,000 | 5,000,000 | 10,000,000 | Legal and travel; not a fee |
| Illustrative brand licence/franchise fee (placeholder) | 0 | 15,000,000 | 50,000,000 | **Not a quote**; may be zero or unaffordable |
| Brand identity and UI/UX | 800,000 | 2,500,000 | 6,000,000 | Logo, design system, content |
| MVP development | 6,000,000 | 18,000,000 | 40,000,000 | Founder time plus contractors |
| Payment gateway integration and testing | 400,000 | 1,200,000 | 3,000,000 | Integration, certification, test transactions |
| Devices, office and equipment | 800,000 | 2,500,000 | 7,000,000 | Laptops, phones, furniture |
| Supplier onboarding and catalogue | 800,000 | 2,500,000 | 6,000,000 | Field visits, photography, training |
| Launch marketing | 2,000,000 | 6,000,000 | 15,000,000 | Digital, field, referral |
| Legal documents: T&Cs, privacy, consumer filing | 800,000 | 2,500,000 | 5,000,000 | Drafting and review |
| **Subtotal** | **14,600,000** | **57,700,000** | **146,000,000** | |
| Contingency (15%) | 2,190,000 | 8,655,000 | 21,900,000 | Scope and cost overruns |
| **Total one-time** | **16,790,000** | **66,355,000** | **167,900,000** | |

The placeholder franchise fee is the largest single variable. If a brand licence costs TZS 15m or TZS 50m upfront, it changes the funding requirement dramatically. The group should not accept a fee before it has evidence that the brand is worth more than an independent name. It may also be possible to structure a licence as a royalty on sales rather than an upfront fee, which shifts risk; that must be negotiated and taxed correctly.

## 15.3 Monthly operating costs

| Item | Lean (TZS/month) | Moderate (TZS/month) | Ambitious (TZS/month) | Notes |
|---|---:|---:|---:|---|
| Founder/management salaries | 0 | 1,200,000 | 3,900,000 | Lean assumes unpaid founders |
| Customer support and operations staff | 650,000 | 1,200,000 | 1,400,000 | One to three people |
| Development/maintenance contractor | 0 | 600,000 | 1,400,000 | Retainer or part-time |
| Cloud hosting, database, CDN | 150,000 | 300,000 | 500,000 | Usage-based |
| Domain, email, security, backup | 50,000 | 100,000 | 250,000 | Tools |
| SMS/WhatsApp notifications | 80,000 | 150,000 | 250,000 | Volume-dependent |
| Payment reconciliation and finance tools | 50,000 | 80,000 | 120,000 | Accounting and reconciliation |
| Marketing and acquisition | 500,000 | 800,000 | 2,000,000 | Can be paused |
| Field transport and supplier visits | 250,000 | 300,000 | 400,000 | Fuel, fares |
| Refund and claims reserve | 200,000 | 250,000 | 400,000 | Provision, not a cash cost until used |
| Accounting, payroll, legal retainer | 200,000 | 300,000 | 600,000 | Professional support |
| Office or co-working | 0 | 200,000 | 600,000 | Lean works remotely |
| Miscellaneous | 70,000 | 120,000 | 180,000 | Contingency |
| **Total** | **2,200,000** | **5,600,000** | **12,000,000** | |

The lean budget is deliberately austere. It assumes founders work without salary, use their own laptops and phones, and operate from home. That is a real constraint, not a permanent model. It also means the lean scenario is not a fair comparison of the true cost of the business; it is a comparison of the cash cost to the founders.

## 15.4 Twelve-month funding requirement

The funding requirement is the **peak cumulative cash need**, not the sum of all costs. Revenue during the pilot reduces the peak.

| Item | Lean (TZS) | Moderate (TZS) | Ambitious (TZS) |
|---|---:|---:|---:|
| One-time startup costs | 16,790,000 | 66,355,000 | 167,900,000 |
| Pre-launch operating costs (6 months) | 13,200,000 | 33,600,000 | 72,000,000 |
| Pilot net cash flow (6 months) | +1,649,500 | (18,000,500) | (55,450,500) |
| **Peak funding before buffer** | **28,340,500** | **117,955,500** | **295,350,500** |
| Buffer (10%) | 2,834,050 | 11,795,550 | 29,535,050 |
| **Total funding requirement** | **31,174,550** | **129,751,050** | **324,885,550** |

The lean pilot generates positive cash in months 4–6, so it does not need the full sum at once. The peak is reached in month 3. The moderate and ambitious pilots remain cash-negative through month 6, so the funding must cover the cumulative deficit.

## 15.5 Lean cash plan

| Pilot month | Orders | Contribution + ancillary (TZS) | Fixed costs (TZS) | Net (TZS) | Cumulative (TZS) |
|---:|---:|---:|---:|---:|---:|
| 1 | 100 | 573,000 | 2,200,000 | (1,627,000) | (31,617,000) |
| 2 | 250 | 1,232,500 | 2,200,000 | (967,500) | (32,584,500) |
| 3 | 450 | 2,128,500 | 2,200,000 | (71,500) | (32,656,000) |
| 4 | 650 | 3,024,500 | 2,200,000 | 824,500 | (31,831,500) |
| 5 | 800 | 3,734,000 | 2,200,000 | 1,534,000 | (30,297,500) |
| 6 | 900 | 4,157,000 | 2,200,000 | 1,957,000 | (28,340,500) |

The cumulative starts at the one-time cost plus six months of pre-launch operating costs: TZS 16,790,000 + TZS 13,200,000 = TZS 29,990,000. The pilot's net cash flow reduces the peak to TZS 28,340,500 by month 6. This is the most optimistic of the three scenarios because it assumes unpaid founders and no major incident.

## 15.6 Moderate cash plan

| Pilot month | Orders | Contribution + ancillary (TZS) | Fixed costs (TZS) | Net (TZS) | Cumulative (TZS) |
|---:|---:|---:|---:|---:|---:|
| 1 | 100 | 573,000 | 5,600,000 | (5,027,000) | (104,982,000) |
| 2 | 250 | 1,232,500 | 5,600,000 | (4,367,500) | (109,349,500) |
| 3 | 450 | 2,178,500 | 5,600,000 | (3,421,500) | (112,771,000) |
| 4 | 650 | 3,174,500 | 5,600,000 | (2,425,500) | (115,196,500) |
| 5 | 800 | 3,984,000 | 5,600,000 | (1,616,000) | (116,812,500) |
| 6 | 900 | 4,457,000 | 5,600,000 | (1,143,000) | (117,955,500) |

The moderate plan needs about TZS 118m before buffer, and it is still losing money at month 6. It only becomes viable above about 1,200 orders/month with full ancillary revenue. This is why external funding should not be raised on the promise of quick profitability.

## 15.7 Break-even and sensitivity

Section 9 sets out the full table. The headline figures are:

- **Lean:** about 295 orders/month (10/day) at TZS 1.1m ancillary revenue; about 375 at TZS 800,000.
- **Moderate:** about 1,206 orders/month (40/day); about 1,287 at TZS 800,000.
- **Ambitious:** about 2,922 orders/month (97/day); about 3,003 at TZS 800,000.

A 2% change in commission has a larger effect on break-even than a 10% change in fixed costs, because commission applies to every order. The group should test commission sensitivity first.

## 15.8 What the budget excludes

- Founder opportunity cost and unpaid salaries in the lean case.
- Full commercial rent in the lean case.
- A warehouse or inventory.
- Vehicles or drivers.
- A large brand campaign.
- Legal costs of a dispute or regulatory investigation.
- The cost of a full-time engineer in the lean case.
- Corporate tax (because the pilot is not profitable).
- Debt service (because no debt is assumed).

A budget that excludes these is not wrong, but it must be read with them in mind. The true economic cost of the lean scenario is higher than the cash cost.

## 15.9 Funding options

| Option | Fit | Advantages | Risks |
|---|---|---|---|
| Founders' savings and contributions | High for lean | No dilution; fast | Limited amount; personal risk |
| Family and friends | High for lean | Flexible; patient | Relationship risk; unclear terms |
| Grants and incubators | Medium | Non-dilutive; mentoring | Application time; reporting; eligibility |
| Supplier prepayment or subscription | Medium | Aligns supply; cash upfront | Suppliers may refuse; obligations |
| Angel investment | Medium | Capital and advice | Dilution; pressure to grow faster than evidence |
| Bank loan | Low at pilot | Keeps ownership | Personal guarantees; repayment before profit |
| Revenue-based financing | Low at pilot | Flexible repayment | Requires revenue; cost |
| Strategic partner (including Usiri) | Unknown | Distribution, brand, logistics | Loss of control; dependence; unclear terms |

The recommendation is to fund the research phase from founders' contributions and small grants, not to raise a large round. Raising money before the model is proven transfers control without reducing uncertainty.

## 15.10 Financial controls from day one

- A separate company bank account; no personal spending.
- A bookkeeping system from the first transaction.
- Monthly budget versus actual, with explanations.
- A 13-week cash-flow forecast.
- Dual approval for payments above a threshold.
- A supplier payable ledger and a customer refund ledger.
- A fixed asset register (laptops, phones).
- A documented expense policy.
- An annual audit or independent review when revenue justifies it.

These controls are not bureaucracy. They are how the group knows whether it is succeeding.

## 15.11 What would change the numbers most

1. **Commission rate.** Moving from 8% to 10% raises contribution per order by about TZS 1,440 and lowers moderate break-even from 1,206 to 870.
2. **Average order value.** Moving from TZS 75,000 to TZS 50,000 at 8% lowers contribution to TZS 2,420 and raises break-even to 1,860.
3. **Return rate.** A 10% return rate instead of 4% cuts commission and adds reverse logistics, reducing contribution materially.
4. **Carrier cost.** A TZS 1,000 increase per parcel wipes out the delivery coordination margin and more.
5. **Fixed costs.** Hiring one additional person at TZS 1m/month raises moderate break-even by about 268 orders.
6. **Ancillary revenue.** If suppliers refuse subscriptions and advertising, break-even rises by about 295 orders in the moderate case (TZS 1.1m / TZS 3,730).

The model should be re-run with real data after Phase 2. The workbook is built for that: change the assumptions and the outputs recalculate.
