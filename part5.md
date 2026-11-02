---

# 16. Implementation roadmap

## 16.1 Principles

The roadmap is sequential at the gates and parallel where possible. It is designed so that **no phase depends on Usiri saying yes**. The partner track runs alongside the independent track, and the project can proceed without a brand licence or a carrier agreement.

Each phase has a deliverable, a budget range, a dependency and a **go/no-go test**. A phase is not complete because time has passed; it is complete because the deliverable exists and the test is met.

## 16.2 The seven phases

| Phase | Duration | Key deliverables | Budget (TZS) | Dependencies | Go/no-go test | Owner |
|---|---|---|---:|---|---|---|
| **1. Internal concept review** | 2–4 weeks | This document; meeting decision; written go/revise/stop; budget cap | 0–500,000 | Founder availability | Group agrees to fund Phase 2 and appoints owners | CEO |
| **2. Customer, supplier and competitor research** | 6–8 weeks | 30 customer interviews; 15 supplier interviews; 8 mystery shops; 150+ survey responses; competitor price check; segment recommendation | 2–5m | Access to suppliers and customers | Evidence supports a specific segment, price band and delivery fee | CEO + COO |
| **3. Partner and franchise feasibility** | 4–6 weeks | Carrier capability assessment; indicative rates; draft term sheet; franchise/legal briefing; Usiri meeting notes | 1–3m | Willingness of carriers to meet | A carrier confirms interest and rates are within 20% of the model | CEO |
| **4. Commercial negotiation and legal review** | 6–10 weeks | Heads of terms; brand licence/franchise draft (if any); carrier SLA; data-processing agreement; legal opinion; PDPC/FCC filings | 3–8m | Partner interest; legal counsel | Terms are affordable, non-exclusive and risk allocation is acceptable | CEO + Finance |
| **5. MVP build and operational preparation** | 8–12 weeks | Working MVP; supplier handbook; support scripts; finance controls; pilot plan; 20 suppliers ready | 10–30m | Phase 2–4 findings; team capacity | MVP passes acceptance tests; 20 suppliers onboarded | CTO + COO |
| **6. Controlled pilot** | 12 weeks | Live orders in Dar es Salaam; weekly dashboard; incident log; cohort data | 8–20m | MVP, suppliers, carrier, PSP | KPIs meet agreed thresholds or a clear fix path exists | COO |
| **7. Evaluation and expansion decision** | 4 weeks | Pilot report; unit economics; decision memo; next-phase budget | 1–2m | Pilot data | Group decides to scale, pivot or stop | CEO |

## 16.3 Timeline

If the phases run sequentially, the elapsed time is about 42–56 weeks. With Phase 3 running in parallel with Phase 2, and Phase 4 starting as soon as a partner indicates interest, the realistic elapsed time to pilot launch is **9–11 months**. The pilot itself runs for 12 weeks.

| Month | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Phase 1 | █ | | | | | | | | | | | |
| Phase 2 | | █ | █ | | | | | | | | | |
| Phase 3 | | █ | █ | | | | | | | | | |
| Phase 4 | | | | █ | █ | | | | | | | |
| Phase 5 | | | | | █ | █ | █ | | | | | |
| Phase 6 | | | | | | | | █ | █ | █ | | |
| Phase 7 | | | | | | | | | | | █ | |

The chart is indicative. Legal review and carrier negotiation are the most likely sources of delay.

## 16.4 Critical path

The critical path is:

**Research findings → segment and price decision → carrier rates and SLA → MVP requirements → build → supplier onboarding → pilot.**

The brand licence is **not** on the critical path. If Usiri takes longer than expected, the independent track continues. This is deliberate.

The payment integration is on the critical path because no pilot can run without it. The PSP sandbox should be opened in Phase 4, not Phase 5, so that certification does not delay launch.

## 16.5 Parallel tracks

| Track | Runs during | Purpose | Owner |
|---|---|---|---|
| Customer research | Phase 2 | Understand demand, price sensitivity, barriers | CEO |
| Supplier research and recruitment | Phase 2–5 | Build a pipeline of verified suppliers | COO |
| Carrier and Usiri discussions | Phase 3–4 | Obtain rates, SLA, terms; assess brand licence | CEO |
| Legal and compliance | Phase 4–5 | Company, contracts, PDPA, FCC, tax, insurance | Finance |
| Technology | Phase 5 | Build and test the MVP | CTO |
| Finance and controls | Phase 4–5 | Bank account, reconciliation, payout process, budget | Finance |
| Marketing preparation | Phase 5 | Brand, content, waiting list, launch plan | Growth |

## 16.6 Stage gates

A stage gate is a formal review with a written decision. The group should not proceed on momentum.

**Gate 1 — after Phase 1:** Is the concept worth researching? Is there a budget and an owner?

**Gate 2 — after Phase 2:** Is there a specific segment with evidence of willingness to pay? Are there at least 15 suppliers who meet the standard? Is the delivery fee acceptable?

**Gate 3 — after Phase 3:** Is there a carrier with written rates and a service level within the model? Is a brand licence available on acceptable terms, or is the independent track viable?

**Gate 4 — after Phase 4:** Are the legal terms acceptable? Is the total funding requirement within the group's capacity? Are the regulatory questions answered?

**Gate 5 — after Phase 5:** Does the MVP pass acceptance tests? Are 20 suppliers ready? Is the support process staffed?

**Gate 6 — after Phase 6:** Do the pilot KPIs meet the thresholds? Is there a credible path to break-even?

**Gate 7 — after Phase 7:** Scale, pivot or stop.

## 16.7 Budget note

The phase budgets above are a **cash-timing view**, not an additional budget on top of Section 15. Phase 5 overlaps with the one-time MVP cost, and Phase 6 overlaps with the pilot operating costs. The group should map each phase to the budget lines in the workbook to avoid double counting.

## 16.8 What could delay the roadmap

- Legal review takes longer than expected.
- A carrier cannot provide written rates.
- The PSP's merchant onboarding requires documents the company does not yet have.
- Supplier recruitment is slower than planned.
- The MVP scope grows.
- A founder becomes unavailable.

The plan should include a two-week buffer before the pilot and a rule that the launch date can slip once without a scope change. A second slip requires a formal review.

---

# 17. Minimum viable product

## 17.1 Definition

The MVP is the smallest product that lets a real customer in Dar es Salaam buy a real product from a real supplier, pay by mobile money, receive a tracked delivery and get a refund if something goes wrong — while the platform's small team can operate it without chaos.

It is not a demo. It is not a beautiful prototype. It is a working, secure, supportable system with a narrow scope.

## 17.2 Must-have capabilities

### Customer-facing

- Browse categories and search products.
- Product page with price, description, dimensions, stock status, delivery estimate, return policy and seller information.
- Cart supporting multiple suppliers.
- Guest checkout with phone number and address; optional account creation.
- Delivery fee and total price shown before payment.
- Payment by at least two mobile money providers and one card option through a licensed PSP.
- Order confirmation by SMS and on-screen.
- Order status page with tracking reference.
- Cancel or request a return within the published window.
- Contact support by phone or WhatsApp.
- Swahili and English interface.

### Supplier-facing

- Supplier application and document upload.
- Product upload by form and CSV; image upload.
- Stock and price update.
- Order alert; accept, pack and mark ready for handover.
- Packing slip and label download.
- Payout statement with commission, refunds and adjustments.
- Performance scorecard.

### Admin-facing

- Supplier verification queue and document records.
- Catalogue moderation and category management.
- Order management with sub-orders and statuses.
- Refund and return processing.
- Payment reconciliation view.
- Payout approval with dual control.
- Carrier booking and manifest.
- Support ticket queue with order context.
- Basic reports: orders, GMV, revenue, contribution, returns, delivery performance.
- Role-based access and audit log.

### Trust and legal

- Terms of service, privacy notice and returns policy in plain language.
- Seller verification badge and explanation.
- Secure checkout and data protection notice.
- Complaints and dispute process.
- PDPA registration and FCC filing (as advised).

## 17.3 Should-have capabilities (after launch)

- Verified buyer reviews with photos.
- Supplier-funded vouchers and campaigns.
- Sponsored placement.
- Saved addresses and wish lists.
- Referral programme.
- Delivery notifications via WhatsApp.
- Partial refund automation.
- Supplier scorecard automation.
- Cohort and retention dashboards.
- Address book with landmarks and pin location.

## 17.4 Deferred capabilities

| Capability | Why deferred |
|---|---|
| Native iOS/Android apps | Web/PWA is enough to test demand; apps add cost and review cycles |
| Real-time GPS tracking | Carrier capability uncertain; status updates are sufficient |
| AI recommendations | No data; adds complexity |
| Chat between buyer and seller | Creates disintermediation and moderation burden |
| Customer wallet or credit | Licensing, fraud and float risk |
| Same-day delivery | Operationally unrealistic at pilot |
| Multi-city zones | One city first |
| Warehouse management | No warehouse |
| International shipping | Customs, tax and delivery complexity |
| Loyalty programme | No repeat base yet |
| Marketplace advertising auction | No traffic yet |
| Microservices | Unnecessary complexity |
| Multi-currency | Not needed |
| Automated supplier payouts | Manual approval is safer at pilot |

## 17.5 Acceptance criteria

The MVP is ready for pilot only when all of the following are true:

1. A test customer can complete a purchase end-to-end on a mid-range Android phone in under five minutes.
2. Payment succeeds and fails gracefully, with a clear message and no duplicate charge.
3. An order creates the correct supplier sub-orders, commission and payout entries.
4. A supplier can accept, pack and mark an order ready, and print a label.
5. An admin can book a carrier, record a tracking number and mark delivery.
6. A customer can request a return and receive a refund through the PSP.
7. Reconciliation matches 100% of test transactions.
8. Access controls prevent a supplier from seeing another supplier's orders or customer data.
9. Backups restore successfully in a test.
10. The privacy notice, terms and returns policy are published and linked at checkout.
11. Support has a written script and can find any order in under 30 seconds.
12. The system survives a simulated 100 concurrent users without error.

## 17.6 Build sequence

| Sprint | Focus | Output |
|---|---|---|
| 1 | Foundations | Repository, environments, auth, database schema, design system |
| 2 | Catalogue and search | Supplier product upload, categories, product pages, search |
| 3 | Cart and checkout | Multi-supplier cart, address, delivery estimate, fees |
| 4 | Payments and orders | PSP integration, order creation, sub-orders, confirmation |
| 5 | Supplier and admin | Supplier portal, order management, labels, carrier booking |
| 6 | Returns, support and reporting | Returns, refunds, tickets, dashboards, reconciliation |
| 7 | Hardening | Security review, performance, backups, acceptance tests |

Seven two-week sprints equal fourteen weeks; with overlap and a smaller scope, 8–12 weeks is achievable. The estimate assumes a dedicated technical lead and one developer.

## 17.7 What not to build

Do not build a feature because a competitor has it. Do not build a feature because it is technically interesting. Build only what is required for the pilot's promise. Every additional feature adds maintenance, security surface and training cost.

The most common MVP failure is not a missing feature; it is a system that cannot be operated reliably by the team that built it.

---

# 18. Key performance indicators

## 18.1 Measurement principles

- **Targets are hypotheses**, set before the pilot and revised with evidence.
- **One north-star metric**, supported by guardrails. The north star is **successful delivered orders per month** — orders that arrive on time and are not returned for a platform-caused reason. It combines demand, fulfilment and trust.
- **Every metric has an owner, a source and a review frequency.** A metric without an owner is a number, not a control.
- **Report bad numbers early.** A late report is worse than a bad one.

## 18.2 The KPI table

| # | KPI | Definition | Target (month 6) | Source | Frequency | Owner |
|---|---|---|---|---|---|---|
| 1 | Verified suppliers | Suppliers that passed KYC and have at least one live listing | 40 by month 3; 60 by month 6 | Supplier register | Weekly | COO |
| 2 | Active products | Listings visible, in stock and not suppressed | 600 by month 3; 1,200 by month 6 | Catalogue | Weekly | COO |
| 3 | Monthly visitors | Unique visitors to web/PWA | 45,000 | Analytics | Weekly | Growth |
| 4 | Conversion rate | Completed orders / unique visitors | 2.0% | Analytics + orders | Weekly | Growth |
| 5 | Completed orders | Delivered or collected and confirmed | 900/month | Order system | Daily | COO |
| 6 | Average order value | Net GMV / completed orders | TZS 75,000 (range 50,000–100,000) | Order system | Weekly | Finance |
| 7 | Cancellation rate | Cancelled orders / placed orders | Below 4% | Order system | Weekly | COO |
| 8 | Return rate | Returned units / delivered units | Below 5% | Returns log | Weekly | COO |
| 9 | On-time delivery | Delivered within promised window | At least 90% | Carrier manifest + POD | Weekly | Ops |
| 10 | Cost per acquired customer | Marketing spend / first-time buyers | At most TZS 8,000 | Marketing + orders | Monthly | Growth |
| 11 | Repeat purchase rate | Buyers with 2+ orders in 90 days | At least 20% | Order system | Monthly | CEO |
| 12 | Contribution margin | Contribution / gross order value | At least 4% | Finance | Monthly | Finance |
| 13 | Complaints resolved | Resolved within 48 hours | At least 90% | Support system | Weekly | Support |
| 14 | Supplier retention | Suppliers active after 90 days | At least 80% | Supplier register | Quarterly | COO |
| 15 | Platform uptime | Availability of checkout and order APIs | At least 99.5% monthly | Monitoring | Monthly | CTO |

## 18.3 Leading indicators

Lagging metrics tell the group what happened. Leading indicators tell it what is about to happen.

| Leading indicator | Why it matters | Watch threshold |
|---|---|---|
| Supplier application-to-verification time | Slow verification kills supply momentum | Above 7 days |
| Time to first listing | A supplier that does not list within a week may never list | Above 7 days |
| Checkout completion rate | Payment or address friction | Below 60% |
| Delivery exception rate | Precursor to complaints and returns | Above 10% |
| First-attempt delivery success | Cost and customer experience | Below 75% |
| Support response time | Trust during exceptions | Above 4 hours |
| Refund processing time | Cash and trust | Above 7 days |
| Repeat order within 30 days | Early signal of retention | Below 10% |
| Supplier cancellation rate | Supply reliability | Above 5% |
| Marketing cost per add-to-cart | Efficiency of acquisition | Rising for 3 weeks |

## 18.4 Dashboard and review rhythm

- **Daily:** orders, payments, delivery exceptions, support queue, cash balance.
- **Weekly:** suppliers, catalogue, traffic, conversion, on-time delivery, returns, complaints.
- **Monthly:** cohort retention, contribution margin, CAC, supplier retention, budget versus actual, risk register.
- **Quarterly:** unit economics, market changes, strategy, phase gate.

The dashboard should be visible to the whole team. Hiding bad numbers from the team is how small problems become crises.

## 18.5 Stop-loss triggers

The group should agree in advance that certain results trigger a pause or pivot:

- Contribution per order below TZS 2,000 for three consecutive months.
- Return rate above 8% for two consecutive months.
- On-time delivery below 80% for two consecutive months.
- CAC above TZS 12,000 for two consecutive months.
- Supplier churn above 30% in a quarter.
- A data breach or regulatory enforcement action.
- Cash below two months of fixed costs.

A trigger does not automatically mean stop. It means a formal review within two weeks, with a written decision.

---

# 19. Group discussion and decision framework

## 19.1 Purpose of the meeting

The meeting is not a launch approval. It is a decision about **whether to fund a research phase** and under what conditions. The group should leave with a written decision, a budget cap and named owners.

## 19.2 Pre-reading

Participants should read:

1. This concept document, especially Sections 1, 9, 14, 15 and 19.
2. The one-page executive summary.
3. The startup budget and decision workbook (Assumptions, Startup Budget, Break-even, Cash Plan, Risk Register).
4. The four diagrams.

Reading time: about 60–75 minutes. The meeting should not be used to read the document aloud.

## 19.3 Agenda (90 minutes)

| Time | Item | Lead | Output |
|---:|---|---|---|
| 0–5 | Welcome, purpose, decision sought | Chair | Alignment |
| 5–20 | The idea and the customer problem | Project initiator | Shared understanding |
| 20–35 | Business model and unit economics | Finance lead | Clarity on contribution and break-even |
| 35–50 | Usiri relationship: what is known and not known | Project initiator | Realistic expectations |
| 50–65 | Risks, feasibility and what would kill the idea | COO | Agreed top risks |
| 65–80 | Decision matrix and options | Chair | Scores and preferred option |
| 80–90 | Budget, owners, dates, next meeting | Chair | Written decision |

## 19.4 Questions for the group

**About the customer**

1. Which specific customer are we serving, and what do they buy today?
2. Would we use this service ourselves? Why or why not?
3. What would make a first-time buyer trust us with TZS 75,000?
4. Is the delivery fee acceptable, or does it need to be absorbed into the price?

**About the supplier**

5. Which five shops would we approach first, and why would they say yes?
6. What commission would make them refuse?
7. Can they pack to a standard, and who trains them?
8. What happens when a supplier cancels or sends the wrong item?

**About the partner**

9. What exactly do we want from Usiri: carriage, brand, branches, or all three?
10. What are we willing to give in return?
11. What is our walk-away condition?
12. If Usiri says no, do we still proceed?

**About the money**

13. How much can the group afford to lose?
14. Who funds the research phase, and on what terms?
15. What evidence would justify the next tranche?
16. What is the stop-loss trigger?

**About the team**

17. Who is accountable for each phase?
18. Who has the technical skill to build or manage the MVP?
19. What happens if a founder leaves?
20. How will we make decisions when we disagree?

## 19.5 Options

| Option | Description | When to choose |
|---|---|---|
| **A. Fund research (recommended)** | Approve Phase 2 with a cap of TZS 2–5m, 8 weeks, named owners, and a written go/no-go | The group believes the problem is worth testing and can afford the research |
| **B. Revise and return** | Send the concept back for a narrower scope, a different segment or a lower budget | The group sees potential but is not convinced by the current scope |
| **C. Pause** | Take no further action for now; keep the document | The group lacks time, money or conviction |
| **D. Stop** | Record the decision and close the project | The risks or costs are unacceptable |

## 19.6 Decision matrix

Score each criterion from 1 (very poor) to 5 (very strong). Multiply by the weight. The weighted total is out of 5. The scores are **judgements**, not measurements; the purpose is to structure the discussion, not to replace it.

| Criterion | Weight | Question | Score (1–5) | Weighted |
|---|---:|---|---:|---:|
| Commercial attractiveness | 25% | Is the customer problem large and urgent? Will they pay? | | |
| Feasibility | 20% | Can this team build and operate the MVP? | | |
| Cost and funding | 15% | Is it affordable, with a credible path to break-even? | | |
| Risk | 20% | Is the downside acceptable, including partner dependence? | | |
| Strategic fit | 10% | Does it fit our skills, network and ambitions? | | |
| Evidence quality | 10% | Do we have enough evidence to proceed? | | |
| **Total** | **100%** | | | **/5** |

**Suggested interpretation** (to be agreed before scoring):

- **4.0–5.0:** proceed to Phase 2 with confidence.
- **3.0–3.9:** proceed, but fix the weakest criterion first.
- **2.0–2.9:** revise the concept and reassess.
- **Below 2.0:** stop or pivot.

Do not score "evidence quality" highly on the basis of this document alone. It is desk research, not primary evidence.

## 19.7 Ownership and funding questions the group must not skip

The document does not assume that ownership, equity, salaries or funding are agreed. The meeting should address, at least at a principle level:

- Who is a founder, and who is an early employee or adviser?
- What is each person contributing: time, money, skills, network?
- How is equity divided, and does it vest over time?
- Who funds the research phase, and is it a loan, a gift or equity?
- What happens if the group needs more money and one founder cannot contribute?
- Who owns the intellectual property?
- How are disagreements resolved, and what is the deadlock rule?
- What is the exit or wind-down process?

These questions do not need final answers at the first meeting. They need an owner and a date.

## 19.8 Decision record template

| Item | Record |
|---|---|
| Date and attendees | |
| Decision | Fund Phase 2 / revise / pause / stop |
| Budget cap | TZS |
| Scope | |
| Owners | |
| Deadline | |
| Conditions | |
| Dissenting views | |
| Next review date | |

The record should be circulated within 48 hours and stored with the project files.

## 19.9 What not to decide today

- Do not approve a launch.
- Do not sign or authorise a franchise fee.
- Do not promise Usiri anything.
- Do not allocate equity without a written agreement.
- Do not commit to a launch date before the research and legal work.
- Do not treat a verbal expression of interest as a partnership.

---

# 20. Conclusion and next steps

## 20.1 What we know

- Tanzania has widespread mobile connectivity and mobile money, with 49.3 million internet subscriptions and 75.78 million active mobile money users reported in 2025 [S5][S6].
- The organised e-commerce market is small relative to the population, with public estimates ranging from about USD 536m to USD 693m for 2025 [S7][S8].
- Jumia exited Tanzania in 2019 and had not confirmed a return as of November 2025 [S9][S10].
- Classifieds and social commerce dominate; they offer selection but not reliable fulfilment or buyer protection [S21][S22].
- Usiri describes a substantial transport network but publishes no API, rate card, liability terms or working tracking page [S1][S2][S4].
- The unit economics are thin: at the model's assumptions, each order contributes about TZS 3,730 before fixed costs.

## 20.2 What we believe but have not proven

- Urban households will pay a delivery-related charge of TZS 5,000–7,000 for a reliable, tracked delivery.
- At least 25–40 credible home and kitchen suppliers will accept an 8% commission and a service standard.
- A licensed carrier can deliver within 2–4 days at a cost that leaves a small coordination margin.
- A curated, verified marketplace can earn repeat business in a market where trust is scarce.
- A brand licence with Usiri would help, but is not essential to launch.

Each belief is a research question. None should be presented to a partner or investor as a fact.

## 20.3 What we do not know

- The actual return rate by category.
- The actual carrier rates and service levels.
- The commission suppliers will accept.
- The delivery fee customers will pay.
- The cost of acquiring a customer in Dar es Salaam.
- Whether Usiri is interested in a partnership, and on what terms.
- Whether a returning Jumia would change the market.
- The final legal and tax treatment of the marketplace model.
- Whether the founders can commit the time and capital required.

## 20.4 Recommendation

**Proceed to a bounded research phase, not to launch.**

The research phase should:

- Last eight weeks.
- Cost no more than TZS 2–5 million.
- Be led by a named owner, with support from at least two other members.
- Produce a written report with evidence, not opinions.
- End in a go/no-go decision using the criteria in Section 19.

In parallel, the group should:

- Approach at least two carriers, including Usiri, for written rates and service levels.
- Speak to a lawyer about company structure, PDPA, FCC, payments and transport liability.
- Speak to an accountant about VAT, corporate tax and withholding.
- Start an independent brand track so the project is not dependent on a licence.
- Recruit a pipeline of 20–40 suppliers for interviews, without asking for commitments.

## 20.5 The next 30, 60 and 90 days

**First 30 days**

- Hold the group decision meeting; record the decision and budget.
- Appoint the research lead and phase owners.
- Draft the interview guides and survey.
- List 60 target suppliers and 10 target carriers.
- Open initial legal and accounting conversations.
- Set up a project folder, budget tracker and weekly meeting.

**Days 31–60**

- Complete 15 customer interviews and 8 supplier interviews.
- Run the survey; aim for 150 responses.
- Mystery-shop 8 competitors.
- Request written rates from 3 carriers.
- Meet Usiri for an information discussion; send a written summary.
- Produce an interim findings memo.

**Days 61–90**

- Complete all interviews and analysis.
- Build the segment, price and delivery recommendation.
- Obtain a legal briefing note and an accounting note.
- Re-run the financial model with real data.
- Hold the Phase 2 gate review.
- Decide: proceed to partner negotiation and MVP, revise, or stop.

## 20.6 Conditions for proceeding to build

The group should not authorise the MVP until:

1. The research shows a specific segment with willingness to pay.
2. At least 15 suppliers meet the verification standard and are willing to sign.
3. A carrier provides written rates and a service level within 20% of the model.
4. The legal questions on payments, data, consumer contracts and transport are answered.
5. The funding for Phase 5 is committed or plausibly available.
6. The founders have signed a roles, equity and IP agreement.
7. The group has agreed the stop-loss triggers.

If these conditions are not met, the correct decision is to revise or stop, not to build and hope.

## 20.7 Closing statement

This document describes a real opportunity and a difficult business. The opportunity is not that Tanzania has many phones or that e-commerce is growing. It is that a customer in Dar es Salaam still cannot easily buy a good product from a trusted local seller, pay safely, receive it on time and get a fair remedy if something goes wrong. Someone will solve that. The question is whether this group can solve it with the resources, discipline and patience it requires.

The answer is not in this document. It is in the next eight weeks of conversations, quotes and evidence. The group should spend a small amount of money to find out, rather than a large amount to assume.

---

# Appendix A. Assumptions register

Every financial figure in this document depends on an assumption. The register makes them explicit so that they can be tested, challenged and replaced.

| ID | Assumption | Value | Basis | Sensitivity | How to verify |
|---|---|---|---:|---|---|
| A01 | Average order value | TZS 75,000 | Planning judgement based on target category | High; at TZS 50,000 break-even rises to 1,860 | Supplier price lists; competitor basket |
| A02 | Commission | 8% of net GMV | Comparable marketplace range; not a quote | High; 10% lowers moderate break-even to 870 | Supplier interviews; willingness-to-pay test |
| A03 | Payment fee | 2.5% of net GMV | Planning assumption | Medium; each 0.5% costs TZS 360/order | PSP quotation |
| A04 | Return rate | 4% of gross | Planning assumption; category-dependent | High; 8% cuts contribution materially | Supplier and competitor data; pilot |
| A05 | Refund handling | 1% of returned value | Planning assumption | Low | Pilot measurement |
| A06 | Support cost | TZS 700/order | Planning assumption | Medium | Time study; staffing model |
| A07 | Customer delivery charge | TZS 5,000/order average | Planning assumption; pass-through | High; affects conversion | Customer survey; price test |
| A08 | Carrier cost | TZS 5,000/order average | Planning assumption; no quote | Very high | Written carrier rate card |
| A09 | Coordination fee / cost | TZS 1,000 / TZS 500 | Planning assumption | Medium | Customer test; time study |
| A10 | Supplier subscriptions | TZS 600,000/month total | 30 suppliers × TZS 20,000 | Medium | Supplier interviews |
| A11 | Sponsored revenue | TZS 500,000/month | Planning assumption from month 6 | Medium | Supplier interviews; traffic data |
| A12 | Fixed opex | TZS 2.2m / 5.6m / 12m | Bottom-up budget in Section 15 | High | Quotes; hiring plan |
| A13 | Pre-launch period | 6 months | Roadmap estimate | Medium | Phase plan |
| A14 | Pilot period | 6 months | Roadmap estimate | Medium | Phase plan |
| A15 | Order ramp | 100 → 900/month | Planning assumption | High | Pilot data |
| A16 | Contingency | 15% of one-time costs | Standard planning allowance | Low–medium | Review at gate |
| A17 | Franchise fee (placeholder) | 0 / 15m / 50m | Illustrative only; **not a quote** | Very high | Written term sheet |
| A18 | FX rate | TZS 2,645/USD | Planning assumption | Medium for USD costs | Bank of Tanzania rate on the day |
| A19 | Ancillary ramp | TZS 200k → 1.1m/month | Planning assumption | Medium | Pilot data |
| A20 | CAC target | TZS 8,000 | Planning assumption | High | Campaign measurement |
| A21 | Conversion target | 2.0% | Planning assumption | Medium | Analytics |
| A22 | Monthly visitors | 45,000 by month 6 | Planning assumption | Medium | Analytics |
| A23 | Repeat purchase | 20% in 90 days | Planning assumption | High | Cohort analysis |
| A24 | Supplier count | 60 by month 6 | Planning assumption | Medium | Recruitment pipeline |
| A25 | Active SKUs | 1,200 by month 6 | Planning assumption | Medium | Catalogue |
| A26 | Delivery success | 90% on time; 80% first attempt | Operational target | High | Carrier data |

---

# Appendix B. Source register

All sources were accessed on 29 October 2026 unless otherwise stated. The register records what each source was used for and its limitations. A source's presence here does not mean the group has independently audited it.

| ID | Publisher | Title / page | URL | Used for | Limitations |
|---|---|---|---|---|---|
| S1 | Usiri Group of Companies | About | https://www.usirigroup.co.tz/about | Self-reported years, routes, agents, trips, customers | Company marketing; figures not audited; inconsistent across pages |
| S2 | Usiri Group of Companies | Transportation | https://www.usirigroup.co.tz/services/transportation | Service scope and routes | No rates, API, liability terms or fleet size |
| S3 | Usiri Group of Companies | Locations | https://www.usirigroup.co.tz/locations | Branch list | Self-reported; addresses not verified |
| S4 | Usiri Group of Companies | Tracking | https://www.usirigroup.co.tz/track | Tested public tracking | Returned HTTP 404 at review; no public tracking interface |
| S5 | TCRA | Communications Statistics Report, quarter ending March 2025 | https://www.tcra.go.tz/tcra-tovuti/2025/mamlaka-website/documents/quarterly-statistics/Communication_Statistics_report_for_end_of_March_2025_1744814447_4329fbf17d.pdf | Internet subscriptions, smartphone penetration, 4G coverage | Official; Q1 2025; subscriptions not unique users |
| S6 | Bank of Tanzania | National Payment Systems Annual Report 2025 | https://www.bot.go.tz/Publications/Regular/Annual%20Report/en/2026060211494565.pdf | Mobile money users, merchants, P2B value, licensed providers | Official; 2025 data; definitions differ from TCRA |
| S7 | International Trade Administration (USA) | Tanzania Country Commercial Guide — eCommerce | https://www.trade.gov/country-commercial-guides/tanzania-ecommerce | Market estimate, social commerce dominance | Government guide citing third-party estimate; differs from S8 |
| S8 | eCommerceDB | E-Commerce Industry in Tanzania | https://ecdb.com/resources/sample-data/market/tz/all | Alternative market estimate and growth | Model-based estimate; conflicts with S7 |
| S9 | Reuters / Africanews | How Jumia closed two portfolios in 10 days | https://www.africanews.com/2019/12/03/how-jumia-closed-two-portfolios-in-10-days-from-cameroon-to-tanzania/ | Jumia exit, 27 November 2019 | Historical news report |
| S10 | TechCabal | Jumia considers Tanzania and Angola expansion | https://techcabal.com/2025/11/18/jumia-considers-tanzania-angola-expansion/ | Possible Jumia return | News report; no confirmed launch or date |
| S11 | TRA | Value Added Tax | https://www.tra.go.tz/page/value-added-tax-vat | VAT rate and threshold | Official guidance; confirm current application |
| S12 | PwC | Tanzania — Corporate — Taxes on corporate income | https://taxsummaries.pwc.com/tanzania/corporate/taxes-on-corporate-income | Corporate income tax rate | Professional summary; confirm Finance Act |
| S13 | ZATRA | Franchising Tanzania: Law, Tax and Royalty Guide | https://www.zatra.co/post/franchising-tanzania | Franchise law, contract/trademark statutes, withholding | Law-firm commentary; not legal advice |
| S14 | DLA Piper | Data protection laws in Tanzania | https://www.dlapiperdataprotection.com/?c=TZ&t=l | PDPA 2022 obligations, PDPC, penalties | Professional summary; verify against the Act |
| S15 | Rex Attorneys | PDPC registration deadline | https://rexattorneys.co.tz/portfolio/reminder-to-clients-final-deadline-for-registration-with-the-personal-data-protection-commission-pdpc/ | Registration deadline, DPO requirement | Law-firm update; confirm with PDPC |
| S16 | Fair Competition Commission | Standard Form (Consumer Contracts) Regulations 2014 | https://www.fcc.go.tz/attachments/attachment-1719186970334-2762257834.%20Standard%20Form%20CONSUMER%20CONTRACTS%20Regulations%202014.pdf | Consumer contract registration | Regulation; confirm filing practice and scope |
| S17 | TCRA | Postal services and licensing | https://www.tcra.go.tz/resources/postal-services | Courier licence categories and fees | Official; applicability to marketplace model to confirm |
| S18 | TCRA | National Addressing and Postcode | https://www.tcra.go.tz/services/featured/national-adressing-and-postcode | Postcode and addressing programme | Official; practical address quality remains a constraint |
| S19 | Ministry of Finance | Electronic Transactions Act 2015 (Cap. 442 R.E. 2022) | https://www.mof.go.tz/uploads/documents/en-1676545044-THE%20ELECTRONIC%20TRANSACTIONS%20ACT,%20CAP%20442%20R.E.%202022.pdf | Electronic transactions, signatures, records | Primary legislation; interpretation requires counsel |
| S20 | National Bureau of Statistics | 2022 Population and Housing Census — population size | https://sensa.nbs.go.tz/dissemination/results | Population 61,741,120; Dar es Salaam | Official census; regional figure used as approximate |
| S21 | Jiji Tanzania | Website | https://www.jiji.co.tz/ | Classifieds model | Site reviewed; no audited market share |
| S22 | Kupatana | Website | https://kupatana.com/ | Classifieds model | Site reviewed; "#1" claim is self-reported |
| S23 | KiKuu | Website | https://www.kikuu.co.tz/ | Cross-border e-commerce model | Site reviewed; delivery times vary |
| S24 | Dar Shopping | Website | https://darshopping.co.tz/ | Local marketplace, delivery and payment options | Site reviewed; scale and seller quality not verified |

**A note on source conflicts.** S7 and S8 give materially different market sizes. S5 and S6 use different definitions of mobile money and internet users. S1 and S2 give different route and agent counts. The document reports the conflict rather than choosing the most flattering number. Where a decision depends on the number, the group must obtain a primary measurement.

---

# Appendix C. Research questions and evidence checklist before approaching Usiri

## C.1 Customer evidence

1. What did you buy online in the last 12 months, from whom, and how did you pay?
2. What was the last online purchase that went wrong? What happened?
3. How much did you pay for delivery? Would you pay TZS 5,000? TZS 7,000?
4. What would make you trust a new marketplace with a TZS 75,000 order?
5. Which categories would you buy online, and which would you never buy online?
6. How important is same-day or next-day delivery?
7. Would you return an item if the process were easy? What would make it easy?
8. Which platforms and shops do you use today, and why?
9. What is your monthly household budget for home and kitchen goods?
10. Would you recommend a good experience to a friend? What would you say?

**Evidence standard:** 30 interviews, recorded themes, at least 150 survey responses, 8 mystery shops with screenshots and timestamps.

## C.2 Supplier evidence

11. What do you sell, and what is your monthly sales volume?
12. Have you sold online before? What happened?
13. What commission would you accept? What would make you refuse?
14. Would you pay a monthly subscription? How much?
15. Who packs and dispatches orders today?
16. What is your return policy, and what does a return cost you?
17. How do you verify payment today? Have you been defrauded?
18. What would you need from a marketplace to trust it?
19. Which products are your best sellers, and which are your most returned?
20. Would you give a marketplace exclusivity? For how long?

**Evidence standard:** 15 interviews, 5 site visits, product and price lists, written indication of commission acceptance.

## C.3 Carrier evidence

21. What routes do you cover, and what are the transit times?
22. What is your rate per kilogram, and how do you calculate volumetric weight?
23. What are your surcharges and minimum charges?
24. What is your liability limit for loss and damage?
25. Do you have goods-in-transit insurance? What does it cover?
26. How do you provide tracking and proof of delivery?
27. Do you have an API, or only a portal/manual process?
28. What is your capacity during peak season?
29. What are your payment and reconciliation terms?
30. Are you willing to sign an SLA with penalties?

**Evidence standard:** three written rate cards, one draft SLA, one API or portal demonstration.

## C.4 Partner evidence

31. Is Usiri interested in a carrier agreement, a brand licence, a franchise, or none?
32. Who has authority to negotiate and sign?
33. What are the brand licence terms and fees, if any?
34. What data can be shared, and under what roles?
35. What is the termination and wind-down process?

**Evidence standard:** written expression of interest, named contact, indicative terms, legal review.

## C.5 Legal and regulatory evidence

36. What company structure and registrations are required?
37. What PDPC registration and DPO arrangements apply?
38. Which consumer contracts must be filed with the FCC?
39. Does the payment flow require a licence or a licensed partner?
40. What tax registrations and treatments apply?
41. Does the platform need a courier licence?
42. What insurance is required or prudent?

**Evidence standard:** written advice from a Tanzanian lawyer and accountant; confirmation from the relevant regulator where possible.

## C.6 What not to do before the evidence exists

- Do not pay a franchise or brand fee.
- Do not sign an exclusive carrier agreement.
- Do not promise suppliers a commission rate or payout date.
- Do not announce a launch date.
- Do not describe the project as an Usiri project.
- Do not raise money on projections that the research has not tested.

---

# Appendix D. Financial model formulas

The workbook implements the following logic. The formulas are shown so that any reader can reproduce or challenge the numbers.

**Unit economics**

- Net GMV per order = AOV × (1 − return rate)
- Commission = Net GMV × commission rate
- Payment fee = Net GMV × payment fee rate
- Refund handling = AOV × return rate × refund handling rate
- Logistics net = coordination fee − coordination cost
- **Contribution per order = commission + logistics net − payment fee − refund handling − support cost**

**Worked example (1,000 orders)**

- Gross GMV = 1,000 × AOV
- Net GMV = Gross GMV × (1 − return rate)
- Revenue = commission + subscriptions + coordination revenue + sponsored revenue
- Variable costs = payment fees + refund handling + support + coordination cost
- **Contribution = Revenue − Variable costs**
- **Net result = Contribution − Fixed opex**
- Take rate = Revenue ÷ Gross GMV
- Contribution margin = Contribution ÷ Gross GMV
- Net margin = Net result ÷ Gross GMV

**Break-even**

- **Break-even orders = (Fixed opex − Ancillary revenue) ÷ Contribution per order**

**Cash plan**

- Starting cash = −(One-time costs + Pre-launch opex)
- Monthly net = (Orders × Contribution per order) + Ancillary revenue − Fixed opex
- Cumulative cash = Starting cash + Σ Monthly net
- **Funding requirement = One-time costs + Pre-launch opex − Σ Pilot net cash flow**
- Funding with buffer = Funding requirement × 1.10

**Rounding.** Figures in the document are rounded for readability. The workbook retains the underlying values. Small differences between a hand calculation and the workbook are due to rounding, not to a different model.

---

# Appendix E. Diagram index

| Diagram | File | What it shows | Use |
|---|---|---|---|
| Business model | `diagrams/business_model.svg` | Five actors (Usiri as potential partner, suppliers, operator, customers, carrier), the regulatory perimeter and the money flow | Explain the model in one page |
| Workflow | `diagrams/workflow.svg` | Customer, marketplace, supplier, carrier and payment provider across eight stages | Train the team; identify handoffs |
| Organisation | `diagrams/organisation.svg` | Founders/board, CEO, CTO, COO, finance, growth and their teams | Discuss roles and hiring |
| Technology architecture | `diagrams/tech_architecture.svg` | Clients, edge, application, data and integrations | Brief a developer; scope the MVP |

The diagrams are communication tools. They are not contracts, org charts with legal effect, or technical specifications.

---

# Appendix F. Limitations and falsification tests

## F.1 Limitations of this document

1. **Desk research only.** No customer, supplier or carrier interviews have been conducted. The market section is a literature review, not primary evidence.
2. **No quotations.** Every cost, fee and rate is a planning assumption. No carrier, PSP, supplier, lawyer or landlord has quoted the group.
3. **No legal or tax advice.** The legal section identifies issues; it does not resolve them.
4. **Self-reported partner information.** Usiri's claims are from its own website and have not been audited. There is no confirmation of interest.
5. **Conflicting market data.** The two market-size estimates differ by about 29%; neither is definitive.
6. **Thin unit economics.** The model shows a loss at pilot volume in the moderate scenario. This is a finding, not a formatting error.
7. **Optimistic operational assumptions.** The model assumes 90% on-time delivery and a 4% return rate before any operating history exists.
8. **Unpriced risks.** Fraud, regulatory fines, brand damage and key-person loss are not fully priced.
9. **Time sensitivity.** Regulations, fees, market conditions and competitor behaviour will change.
10. **No commitment.** Nothing in this document creates an obligation on the group, Usiri or any third party.

## F.2 What would prove this concept wrong

The concept should be revised or abandoned if:

- Fewer than 30% of surveyed customers say they would pay a delivery fee of TZS 5,000 or more.
- Fewer than 15 suppliers meet the verification standard and accept an 8% commission.
- No carrier can offer a written rate and service level within 20% of the model.
- The realistic return rate is above 8% in the chosen category.
- Customer acquisition cost exceeds TZS 12,000 for two consecutive months.
- Contribution per order falls below TZS 2,000 after three months of operation.
- The pilot cannot reach 300 orders/month within six months despite a reasonable marketing spend.
- A legal or regulatory requirement cannot be met within the budget.
- A brand licence is only available on exclusive, expensive or unacceptable terms, and the independent brand cannot attract customers.
- The founders cannot commit the time and capital required for 12 months.

## F.3 What would strengthen the concept

- A signed, non-exclusive carrier agreement with a written rate card and SLA.
- 15+ suppliers with signed agreements and live stock.
- 30+ customer interviews showing a consistent willingness to pay.
- A priced MVP from a credible developer.
- Written legal and tax advice.
- A pilot with real orders, real returns and real contribution data.
- A second carrier qualified and benchmarked.
- A brand licence term sheet that is affordable and terminable.

---

# Appendix G. Document history and next review

| Version | Date | Author | Change | Status |
|---|---|---|---|---|
| 0.1 | 29 Oct 2026 | Project initiator | Initial research notes and model | Internal |
| 1.0 | 29 Oct 2026 | Project initiator | Full concept document, diagrams, workbook, meeting pack | For group discussion |
| 1.1 | After Phase 2 | Research lead | Replace assumptions with evidence; re-run model | Planned |

**Next review:** at the Phase 2 gate, or earlier if a material fact changes (for example, Usiri confirms or declines interest, a carrier publishes rates, or a competitor announces a launch).

**Owner of this document:** the project initiator, until the group appoints a CEO or research lead.

---

*End of concept document.*
