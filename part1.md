# Usiri Marketplace

## A proposed multi-vendor e-commerce and coordinated-delivery platform for Tanzania

**Project concept document for internal discussion**

| Document control | |
|---|---|
| Version | 1.0 — for group discussion |
| Date | 29 October 2026 |
| Prepared for | The founding group |
| Prepared by | Project initiator |
| Status | **Concept under investigation.** Not an approved project. Not a Usiri project. No partnership, franchise, licence, funding or technical integration exists. |
| Decision sought | Whether to fund a defined research phase (Phase 2), revise the concept, or stop |

---

> **Important notice — please read before the rest of the document**
>
> This document explores a business idea. It is not a business plan, a legal opinion, a tax opinion, an offer, a prospectus, or a commitment by anyone.
>
> **No relationship with Usiri Group of Companies exists.** Usiri is named only as one possible logistics and brand partner that the group could approach for discussions. Nothing in this document has been approved, authorised, sponsored or reviewed by Usiri. No franchise fee, royalty, route rate, service level, API, data-sharing arrangement or brand licence has been agreed, quoted or confirmed.
>
> **All financial figures are planning assumptions**, expressed in Tanzanian shillings (TZS). They are not quotations, market prices or forecasts. Supplier commissions, payment fees, delivery charges, salaries and the hypothetical franchise fee must all be tested with real counterparties.
>
> **Market figures are directional.** Public estimates of Tanzania's e-commerce market disagree with each other. They are used here to describe scale and uncertainty, not to promise a revenue opportunity.
>
> **No regulatory approval has been obtained.** References to Tanzania's data protection, consumer protection, payment, tax and transport rules are a map of questions for professional advisers, not a compliance certificate.
>
> The names and marks of Usiri and other companies belong to their owners. This document does not grant any right to use them.
>
> Anyone committing money, signing an agreement or approaching a partner should verify the relevant facts independently.

---

## How to read this document

The document is written for a group of university students and early-career entrepreneurs. It assumes curiosity but not specialist knowledge. Technical, legal and financial terms are explained the first time they appear, and there is a glossary at the end.

Each factual statement is tagged so that readers can see how much weight it can bear:

| Tag | Meaning |
|---|---|
| **[Verified]** | Checked against an official or primary source that is listed in Appendix B. |
| **[Self-reported]** | A claim made by a company about itself. It may be true, but it has not been independently audited. |
| **[Estimate]** | A third-party estimate or model. Useful for direction, not precision. |
| **[Assumption]** | A number or belief the group is using for planning. It must be tested. |
| **[To verify]** | A question on which the group does not yet have enough evidence. |

Source codes such as [S5] refer to the source register in Appendix B. Where sources conflict, the conflict is shown rather than hidden. The document also states, in Appendix F, what evidence would prove it wrong. A concept document that cannot be falsified is marketing, not analysis.

The document follows the twenty sections requested by the group's brief. Sections 1–5 explain the idea and the proposed partner relationship. Sections 6–12 explain how it would work. Sections 13–18 test whether it is feasible. Sections 19–20 set out the decision the group must make. The appendices hold the assumptions, sources, research checklist and glossary.

---

## Glossary of key terms

**Asset-light.** A business that does not own most of the expensive physical assets it uses. A marketplace can own software and contracts while suppliers own stock and carriers own vehicles.

**Average order value (AOV).** Total value of goods sold divided by the number of orders. If ten orders are worth TZS 750,000 together, the AOV is TZS 75,000.

**Break-even.** The sales volume at which contribution equals fixed costs, so the business makes neither a profit nor a loss.

**Carrier / 3PL.** A transport company that moves parcels. "Third-party logistics" (3PL) means using an outside company rather than owning a fleet.

**Chargeback.** A card payment that a customer disputes through the bank and has reversed. The platform may have to repay the money even after the goods have gone.

**Commission (take rate).** The percentage of a sale that the marketplace keeps. If a TZS 100,000 sale carries a 8% commission, the platform earns TZS 8,000 before payment and delivery costs.

**Contribution.** Revenue from an order minus the costs that vary directly with that order (payment fees, support, refund handling, delivery cost). Contribution is the money available to pay fixed costs. It is not profit.

**Escrow.** A legal arrangement in which a neutral, licensed party holds a buyer's money until conditions are met. Calling an ordinary platform wallet "escrow" does not make it one.

**Franchise.** A licence to operate a business under another company's brand and system, usually for an initial fee plus continuing royalties. Tanzania has no stand-alone franchise statute; franchise relationships are governed mainly by contract and trademark law [S13].

**Gross merchandise value (GMV).** The total value of goods sold through the platform, including the supplier's share. GMV is not the platform's revenue.

**KYC (know your customer).** Checks on the identity and legitimacy of a supplier or customer before doing business.

**MVP (minimum viable product).** The smallest version of a product that can be used by real customers to complete a real job, built to test assumptions rather than to impress.

**PDPA.** Tanzania's Personal Data Protection Act, 2022. It sets rules for collecting and using personal data and creates the Personal Data Protection Commission (PDPC) [S14].

**PSP (payment service provider).** A licensed company that processes payments. In Tanzania, payment services are regulated by the Bank of Tanzania.

**Reconciliation.** The routine matching of what the platform's order records say, what the payment provider actually settled, and what was paid out to suppliers. Poor reconciliation is how marketplaces lose money quietly.

**RACI.** A responsibility chart: who is **R**esponsible for doing the work, who is **A**ccountable for the result, who must be **C**onsulted, and who is **I**nformed.

**SLA (service level agreement).** A written promise about performance, such as delivery within 48 hours or response to a complaint within one working day, with consequences if it is missed.

**Take rate.** See commission. It can be calculated on gross sales or on net sales after returns; this document is explicit about which one is used.

---

# 1. Executive summary

## 1.1 The idea

The group is exploring a curated, multi-vendor online marketplace for Tanzania, operating initially in Dar es Salaam. Independent verified shops would list their products; the platform would bring customers, collect payment, coordinate delivery through a licensed carrier, handle customer service and stand behind the transaction when something goes wrong.

The proposed launch assortment is **everyday home, kitchen and small electrical goods** in the TZS 30,000–250,000 price band, sold by 25–40 verified Dar es Salaam suppliers. This is narrower than "sell everything". The narrowness is deliberate: it keeps delivery manageable, reduces counterfeit and warranty risk, and lets a small team become genuinely good at one promise before expanding.

The business would be **asset-light**. It would not buy stock, own warehouses or run its own fleet at pilot stage. It would earn a commission on sales, a small supplier subscription, a delivery coordination fee and, later, sponsored placement. Suppliers would hold stock and pack orders. A licensed carrier would move parcels. A licensed payment provider would collect money.

Usiri Group of Companies is one possible partner for the delivery and brand layer. **It is not a partner today.** The group has not approached Usiri for this project, has no term sheet, and has no confirmation that Usiri offers an API, a franchise, a rate card or any willingness to support a marketplace. The pilot plan is designed so that it can proceed with an independent brand and at least two carriers if Usiri declines or negotiations stall.

## 1.2 Why the group thinks there is an opportunity

Three facts shape the opportunity, and one caution shapes the plan.

The first fact is connectivity. Tanzania had about **49.3 million internet subscriptions** and **35.29% smartphone penetration** by March 2025, with 4G coverage reaching about 91% of the population [S5]. People can reach an online shop far more easily than they could a decade ago.

The second is payment. The Bank of Tanzania reports about **75.78 million active mobile money users** and **2.79 million mobile money merchants** in 2025, with person-to-business mobile money transactions worth TZS 37.5 trillion [S6]. Paying a stranger remotely is now normal behaviour, not an exotic act.

The third is the gap left by the market. Jumia, the best-known pan-African marketplace, stopped its Tanzanian e-commerce operations in November 2019 [S9]. As of November 2025 it was reported to be *considering* a return, but no launch had been confirmed [S10]. In the meantime, much online buying happens through Instagram, WhatsApp and Facebook pages, where the seller and buyer negotiate manually and trust depends on screenshots and reputation. Classifieds sites list goods but do not fulfil orders.

The caution is that e-commerce in Tanzania has been difficult for well-funded companies, not only for startups. Low average order values, expensive last-mile delivery, weak addresses, returns, counterfeit goods and thin margins are structural. A new marketplace does not make those problems disappear. It has to be designed around them.

## 1.3 What the numbers say

The financial model in Section 15 and the accompanying workbook is deliberately conservative. It assumes an average order value of TZS 75,000, a commission of 8% on net sales after returns, payment fees of 2.5%, a 4% return rate, a support cost of TZS 700 per order and a delivery coordination margin of TZS 500 per order.

On those assumptions, each order contributes about **TZS 3,730** towards fixed costs. That single number drives the whole business.

| Scenario | Monthly fixed costs | Orders needed to break even | Orders per day | 12-month funding need (incl. 10% buffer) |
|---|---:|---:|---:|---:|
| Lean | TZS 2.2m | **295** | about 10 | **TZS 31.17m** |
| Moderate | TZS 5.6m | **1,206** | about 40 | **TZS 129.75m** |
| Ambitious | TZS 12.0m | **2,922** | about 97 | **TZS 324.89m** |

[Assumption-based model; see Section 15 and the workbook.]

The pilot target is 900 completed orders per month by month six. At 900 orders, the lean structure is profitable at the contribution level but the moderate structure is still losing money: a worked example at 1,000 orders shows revenue of TZS 7.86m, contribution of TZS 4.83m and fixed costs of TZS 5.6m, leaving a **net loss of about TZS 770,000 for the month**. That is the most important finding in this document. A marketplace at pilot scale is a small, fragile business. It becomes attractive only when order volume rises, fixed costs stay controlled, and ancillary revenue appears.

The lean scenario is the only one a student group could plausibly fund from savings and small contributions. It requires about 295 orders a month to break even, or roughly ten orders a day — achievable in principle, but not guaranteed. The moderate scenario requires outside capital and a much stronger operating team. The ambitious scenario is included to show what "doing this properly" would cost, not as a recommendation.

## 1.4 The proposed relationship with Usiri

Usiri Group of Companies describes itself as a Tanzanian transport and services group with more than six years of operation, 50+ routes, 100+ agents, cargo and parcel carriage, bus ticketing and car rental [S1][S2]. Those are **self-reported marketing claims**. During desk research the group could not find a published fleet size, an API, a rate card, standard terms on liability, or a working public tracking page; the tracking link returned HTTP 404 [S4].

The concept therefore treats Usiri as a **candidate counterparty for investigation**, not as a foundation. A future relationship could combine a preferred-carrier agreement, a narrow brand licence, co-marketing and collection-point access. Each element would need its own written terms. The group would contribute demand, technology, supplier relationships, customer service and reporting. Usiri might contribute transport capacity, branch reach, local trust and possibly warehousing. Nothing about equity, exclusivity, fees, data or brand use should be assumed.

Section 5 sets out a negotiation checklist and the fallback: launch under an independent brand with a multi-carrier setup, and revisit Usiri when there is volume and evidence.

## 1.5 Recommendation

The group should **not** approve a launch today. It should approve a **bounded research phase**: eight weeks, a budget cap of TZS 2–5 million, and a written go/no-go decision at the end. The research must answer the questions that this document cannot answer from a desk: whether customers will pay a delivery fee, which categories they will buy online, what suppliers will accept, what carriers actually charge, and whether a brand licence is affordable and non-exclusive.

The research phase should run in parallel with an independent-brand track, so that the project does not die if Usiri says no. No franchise fee, deposit or brand-specific investment should be paid before due diligence and legal review.

The decision requested from the group is set out in Section 19: approve the research phase, appoint owners, set the budget cap, and agree the evidence thresholds that would justify building an MVP.

---

# 2. Problem statement and market opportunity

## 2.1 The customer problem

A customer in Dar es Salaam who wants to buy a rice cooker, a set of storage containers or a small fan faces a set of ordinary but irritating problems.

**Discovery is unreliable.** The customer can walk through Kariakoo or a neighbourhood shopping street, but comparing prices and stock across shops takes hours. Online, the same goods appear on Instagram pages, Facebook groups, classifieds sites and scattered WhatsApp catalogues. There is no single place where the offer is complete, current and comparable.

**Trust is personal.** In social commerce the buyer often pays a deposit or the full amount to a phone number before receiving anything. If the seller disappears, the buyer's remedy is a phone call, a report to the platform (if any) and luck. Reputation travels through word of mouth, which does not help a first-time buyer.

**Delivery is negotiated, not designed.** A seller may deliver personally, use a bus parcel service, or ask the customer to collect. Delivery times are vague, packaging is improvised, and responsibility for damage is unclear. The customer bears the uncertainty.

**Returns are awkward.** If the item is wrong, damaged or not what was pictured, the customer must argue with the seller. Many sellers do not accept returns. The customer's fallback is to stop buying online.

**Payment is not the bottleneck any more.** Mobile money is widespread [S6]. The bottleneck is confidence that the goods will arrive as described, on time, with someone accountable if they do not.

## 2.2 The supplier problem

A small, legitimate shop has the opposite set of problems.

It has good products and local knowledge, but limited digital reach. It can post on Instagram, but cannot easily manage a catalogue, calculate delivery, reconcile payments or handle returns at scale. It does not want to hand over its customer relationships or its margins. It has heard stories of online sellers being defrauded by fake payment screenshots and of marketplaces paying suppliers late.

A credible marketplace must therefore solve the supplier's problems too: predictable payouts, clear rules, manageable order flow, and a credible promise that the platform will not compete with the supplier by selling the same goods at a lower price.

## 2.3 The market context, in numbers

Tanzania's digital and payment infrastructure has improved faster than its organised e-commerce sector. The table below separates what is measured from what is estimated.

| Indicator | Figure | Source and caution |
|---|---:|---|
| Population | 61.74 million | 2022 Population and Housing Census [S20]. |
| Dar es Salaam region population | about 5.38 million | 2022 census [S20]. The initial market is a subset of this. |
| Internet subscriptions | 49.3 million | TCRA, quarter ending March 2025 [S5]. Subscriptions are not unique users. |
| Smartphone penetration | 35.29% | TCRA, March 2025 [S5]. Feature phones remain important. |
| 4G population coverage | about 91% | TCRA, March 2025 [S5]. Coverage is not usage. |
| Active mobile money users | 75.78 million | Bank of Tanzania, 2025 [S6]. Includes multiple accounts per person; not unique adults. |
| Mobile money merchants | 2.79 million | Bank of Tanzania, 2025 [S6]. |
| Person-to-business mobile money value | TZS 37.5 trillion | Bank of Tanzania, 2025 [S6]. Flows, not retail sales. |
| E-commerce market size, 2025 | USD 693.11 million | Trade.gov, citing a third-party estimate, +7% [S7]. |
| Alternative e-commerce estimate, 2025 | USD 536 million | eCommerceDB, 15–20% growth [S8]. Conflicts with the figure above. |

The two market-size estimates differ by about 29%. They use different definitions, include different categories and are built with different methods. Neither is an audited measurement of Tanzanian retail e-commerce. The honest conclusion is that the addressable online market is **in the range of USD 0.5–0.7 billion**, growing, and small relative to total retail. The document uses the range, not a single number.

It is also important not to convert national statistics into a market forecast. Fifty million internet subscriptions do not mean fifty million online shoppers. A large share of mobile money activity is person-to-person transfers, airtime and bill payments, not shopping [S6]. The gap between "connected" and "willing to buy goods online" is exactly what the research phase must measure.

## 2.4 Why the opportunity exists anyway

The market is not empty. Jiji and Kupatana list goods; Kikuu sells cross-border products; Dar Shopping and various Facebook and Instagram sellers serve local demand; brand stores and supermarkets sell online in a limited way. The opportunity is not "no one is online". It is that **no locally dominant operator has combined curated supply, reliable delivery and buyer protection at scale** since Jumia's exit.

That combination is hard, which is why it is valuable if it can be executed. A marketplace that merely lists products competes with free classifieds. A marketplace that guarantees the transaction — verified seller, tracked delivery, clear returns, someone to call — offers something different.

The opportunity statement is therefore narrow and testable:

> For urban households in Dar es Salaam who are willing to buy home and kitchen goods online, the project can build a trusted marketplace that verifies sellers, coordinates delivery and resolves problems, and can earn a commission plus a delivery coordination fee for doing so.

If customers do not value that guarantee enough to pay for it, the idea fails. That is the central hypothesis, not a detail.

## 2.5 Why previous attempts struggled

A serious concept must explain why Jumia, with far more capital and experience, left Tanzania in 2019 [S9]. Public reporting and the structure of the market suggest several pressures, although the company's full internal reasons are not public:

- **Thin unit economics.** Low average order values and high delivery costs leave little room for commission, especially when customers expect free delivery.
- **Trust and counterfeits.** Marketplaces that host third-party sellers inherit the sellers' quality problems. Returns and disputes are expensive.
- **Fragmented logistics.** Address quality, traffic and the cost of failed deliveries make last-mile delivery difficult and costly.
- **Cash-on-delivery and payment risk.** Where customers pay on delivery, refusal rates are high and cash handling is expensive. Where they pay upfront, trust must be earned.
- **Capital intensity.** Building demand, supply and logistics at the same time requires years of investment before contribution covers fixed costs.

These pressures have not disappeared. The project's answer is not to ignore them but to start smaller: one city, one assortment, a limited number of verified suppliers, a manual logistics pilot, and a cost structure that a small group can actually fund.

## 2.6 What would make the opportunity real

The opportunity becomes investable only if four conditions hold. Each is a research question, not a conclusion:

1. **Customers will pay.** A meaningful number of customers will buy at least twice a year and will pay a delivery fee rather than abandon the order.
2. **Suppliers will supply.** At least 25 credible suppliers will list real stock, accept the commission, pack to a standard and accept returns.
3. **Delivery can be coordinated.** A carrier will move parcels reliably at a cost that leaves a margin after the customer's delivery fee.
4. **The economics work at reachable volume.** Contribution per order and fixed costs produce a break-even volume that the team can reach within 12–18 months.

If any of these fails, the model must change. Section 14 sets out the tests and Section 19 sets out the decision rules.

---

# 3. Vision, mission and twelve-month objectives

## 3.1 Vision

> **To make buying from trusted Tanzanian sellers as reliable as walking into a shop.**

The vision is about reliability, not technology. The platform succeeds when a customer can order from a shop they have never visited, pay remotely, and receive the right item on time — and when something goes wrong, they know who will fix it.

## 3.2 Mission

> **To operate a curated marketplace that verifies sellers, coordinates delivery and stands behind every order.**

Three words carry the strategy: **curated** (not everything, not every seller), **coordinated** (the platform owns the handoffs, even when a carrier moves the parcel), and **stands behind** (the platform does not disappear when there is a dispute).

## 3.3 Values and operating principles

| Value | What it means in practice |
|---|---|
| Trust before growth | Do not list a seller who cannot be verified, even if the seller would bring sales. |
| Frugality | Spend on things that directly improve delivery, trust or repeat purchase. Do not spend on logo polish or a large office. |
| Transparency | Publish commission, delivery, return and payout rules in plain language. |
| Local partnership | Work with Tanzanian shops and carriers rather than displacing them. |
| Data care | Collect the minimum customer data needed, protect it, and never sell it. |
| Honest measurement | Report returns, failures and losses, not only GMV. |

## 3.4 Twelve-month objectives

The following objectives are **hypotheses with numbers attached**, not commitments. They are set for the first twelve months from the start of the pilot, not from today. Baselines are unknown, so targets are expressed as absolute levels and will be revised after the research phase.

| # | Objective | Target | Why it matters | Owner |
|---|---|---|---|---|
| O1 | Complete customer and supplier research | 30 customer interviews, 15 supplier interviews, 150+ survey responses, 8 mystery shops | Replaces opinion with evidence before spending on build | CEO |
| O2 | Sign pilot suppliers | 40 verified suppliers by month 3; 60 by month 6 | Supply depth is the first constraint on assortment | COO |
| O3 | Build a usable catalogue | 600 active products by month 3; 1,200 by month 6 | Customers need choice; too much choice creates operational chaos | COO |
| O4 | Reach pilot demand | 900 completed orders in month 6 | Tests whether the unit economics can work at small scale | CEO |
| O5 | Protect delivery reliability | At least 90% on-time delivery; damage and loss below 2% | Delivery failure destroys trust faster than low prices build it | Ops lead |
| O6 | Keep returns manageable | Return rate below 5% (electronics may be higher) | Returns consume margin and support time | COO |
| O7 | Acquire customers affordably | Cost per first-time buyer at most TZS 8,000 | Paid acquisition must not exceed contribution | Growth lead |
| O8 | Earn repeat business | At least 20% of buyers order again within 90 days | A marketplace without repeat purchase is a continuous ad campaign | CEO |
| O9 | Reach contribution margin | At least 4% of gross order value by month 6 | The business must fund its own variable costs | Finance lead |
| O10 | Resolve complaints | 90% of complaints resolved within 48 hours | Trust is built in the exception, not the ordinary order | Support lead |
| O11 | Achieve legal baseline | PDPC registration, FCC standard-form filing, written supplier and carrier contracts | Operating without these creates existential risk | Finance & compliance |
| O12 | Produce an honest pilot report | Unit economics, cohort retention, exception log and a go/no-go recommendation | The group must be able to stop as well as start | CEO |

Two disciplines apply to all twelve. First, **no target is a promise to investors**; the group has no investors at the time of writing. Second, **a missed target is data**, not a failure of character. The monthly review should ask what the miss reveals about the model, not who to blame.

## 3.5 The twelve-month sequence in one paragraph

Months 1–2 are research and partner conversations. Months 3–4 are legal setup, supplier onboarding and MVP build. Months 5–6 are a controlled pilot in Dar es Salaam with a small assortment. Months 7–12 are iteration: fix the biggest operational failure, deepen the best-selling categories, and decide whether the unit economics justify expansion to a second city or a second customer segment. The detailed roadmap is in Section 16.
