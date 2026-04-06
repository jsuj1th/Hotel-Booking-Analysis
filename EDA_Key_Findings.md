# EDA Key Findings — Hotel Booking Cancellation Prediction

**Dataset:** Hotel Booking Demand (~119,390 records, 2015–2017)  
**Authors:** Sai Nithin Reddy Maddi · Sujith Julakanti  
**Course:** STAT-654 · March 2026

---

## 1. Overall Cancellation Rate

- **37% of all bookings were cancelled** — a significant class imbalance.
- City Hotel cancellation rate: **~42%**
- Resort Hotel cancellation rate: **~28%**
- City Hotel receives more bookings overall but suffers nearly **1.5× higher cancellation rate** than Resort Hotel.

---

## 2. Temporal Patterns

- **Peak booking months:** July and August (summer travel season).
- **Highest cancellation rates:** June (41.5%), April (40.8%), and May (39.7%).
- January and February have the **lowest** cancellation rates (~30–33%) despite being low season.
- Cancellation rate and booking volume tend to move **together** during peak summer months — high demand periods also see more cancellations in absolute terms.
- Resort Hotel ADR peaks sharply in Jul–Aug, while City Hotel ADR remains relatively flat year-round.

---

## 3. Lead Time

- **Cancelled bookings have significantly longer lead times** than non-cancelled ones.
- Most non-cancelled bookings are made **< 100 days** before arrival.
- Cancelled bookings show a much wider spread, often booked **6–12 months** in advance.
- City Hotel shows a wider lead time distribution than Resort Hotel.
- **Lead time is one of the strongest predictors of cancellation.**

---

## 4. Deposit Type (Counter-Intuitive Finding)

- **Non-Refundable deposits: ~99% cancellation rate** — a striking paradox.
- No Deposit: ~28% cancellation rate.
- Refundable: ~22% cancellation rate.
- The Non-Refund paradox is likely driven by **OTA (Online Travel Agency) policy behaviour** — agents book non-refundable rates and cancel when they cannot fill them, or guests cancel knowing they'll forfeit the deposit.
- Despite being counter-intuitive, deposit type is a **high-signal feature** for the model.

---

## 5. Length of Stay

- **1–3 night stays dominate** total booking volume.
- **1-night stays have the lowest cancel rate (~25%)** — likely last-minute, committed bookings.
- **2–3 night stays have the highest cancel rates (~44%)** among high-volume groups.
- Stays beyond 7 nights have very small sample sizes (< 1,200 bookings each), making cancel rate estimates unreliable for those groups.
- No consistent upward trend for long stays — the pattern is **non-linear**.

---

## 6. Customer Behaviour

### Prior Cancellations
- Guests with **1+ prior cancellation** have an ~80% chance of cancelling again.
- **Past cancellation behaviour is the strongest behavioural predictor** in the dataset.

### Special Requests
- `total_of_special_requests` counts the number of **additional preferences a guest submits at booking** — e.g., requesting a high floor, twin beds, early check-in, airport transfer, or a non-smoking room.
- Guests with **0 special requests: ~48% cancel rate**.
- Guests with **1–2 special requests: ~22% cancel rate**.
- Guests with **4+ special requests: ~10% cancel rate**.
- More special requests indicate a guest is actively planning their stay — a strong **negative (protective) predictor** of cancellation.

---

## 7. Booking Channel & Market Segment

**Market Segment (by cancellation rate):**

| Segment | Cancel Rate | Count |
|---|---|---|
| Groups | **61.1%** — highest | 19,811 |
| Online TA | 36.7% | 56,477 |
| Offline TA/TO | 34.3% | 24,219 |
| Aviation | 21.9% | 237 |
| Corporate | 18.7% | 5,295 |
| Direct | **15.3%** — lowest | 12,606 |
| Complementary | 13.1% | 743 |

**Distribution Channel (by cancellation rate):**

| Channel | Cancel Rate | Count |
|---|---|---|
| TA/TO | **41.0%** — highest | 97,870 |
| Corporate | 22.1% | 6,677 |
| GDS | 19.2% | 193 |
| Direct | **17.5%** — lowest | 14,645 |

- **Groups have the highest cancellation rate (~61%)** — likely because group blocks are reserved speculatively and released if attendance falls short.
- **Direct bookings have the lowest cancel rate** — guests who book directly are more intentional and committed.
- **TA/TO channel dominates volume** and also carries the highest cancellation burden.
- Channel choice reflects the **nature of booking intent and financial commitment**.

---

## 8. Guest Profile

| Guest Type | Cancellation Rate |
|---|---|
| New Guest | ~38% |
| Repeat Guest | ~14% |

- Repeat guests are **2.7× less likely** to cancel than new guests.
- **Transient customers** cancel most (~39%).
- **Group bookings** have the lowest cancellation rate.
- Loyalty and familiarity with the hotel are strong indicators of commitment.

---

## 9. Geographic Insights

- **Portugal (PRT)** dominates total bookings (domestic market).
- Significant variation in cancellation rate by country of origin.
- Some countries show near 0% cancellation rates.
- City Hotel generally shows higher cancellation rates **across all top countries**.
- Country of origin is a **moderate predictor** — useful but not dominant.

---

## 10. Correlation with Cancellation (`is_canceled`)

| Feature | Direction | Strength |
|---|---|---|
| `lead_time` | Positive | Strong |
| `previous_cancellations` | Positive | Strong |
| `total_of_special_requests` | **Negative** | Moderate |
| `adr` | Positive | Weak–Moderate |
| `total_nights` | Positive | Weak |
| `adults` / `children` | Near zero | Negligible |
| `is_repeated_guest` | **Negative** | Weak–Moderate |

---

## Summary: Top Predictors for Cancellation

1. **Lead Time** — longer window → higher risk
2. **Deposit Type** — Non-Refund is paradoxically the riskiest
3. **Prior Cancellations** — history repeats itself
4. **Special Requests** — protective signal (more = less likely to cancel)
5. **Booking Channel** — OTA vs Direct vs Corporate
6. **Repeated Guest** — loyalty significantly reduces cancellation risk
7. **Hotel Type** — City Hotel inherently higher risk
8. **Seasonality** — winter months show elevated cancellation rates

---

*These findings directly informed feature selection and model design in the modelling phase.*
