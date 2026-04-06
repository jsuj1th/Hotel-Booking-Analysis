"""
Hotel Booking PPTX v3 — one visualization per slide.
Run: python3 build_pptx.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY      = RGBColor(0x0D, 0x1B, 0x2A)
CRIMSON   = RGBColor(0xE6, 0x39, 0x46)
TEAL      = RGBColor(0x2A, 0x9D, 0x8F)
GOLD      = RGBColor(0xE9, 0xC4, 0x6A)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
OFFWHITE  = RGBColor(0xF4, 0xF4, 0xF4)
LIGHTGRAY = RGBColor(0xCC, 0xCC, 0xCC)
DARK      = RGBColor(0x1A, 0x1A, 0x2A)
PANEL     = RGBColor(0x14, 0x2A, 0x40)

FIG = '/Users/sujithjulakanti/Desktop/R&Python/Project/figures/'
OUT = '/Users/sujithjulakanti/Desktop/R&Python/Project/Hotel_Booking_Presentation_v2.pptx'

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.50)
BLANK = prs.slide_layouts[6]


# ═══════════════════════════════════════════════════════════════
# PRIMITIVES
# ═══════════════════════════════════════════════════════════════

def rect(slide, l, t, w, h, fill=None, line=None, line_pt=0):
    s = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid() if fill else s.fill.background()
    if fill:
        s.fill.fore_color.rgb = fill
    s.line.fill.background()
    if line and line_pt:
        s.line.color.rgb = line
        s.line.width = Pt(line_pt)
    return s


def txt(slide, text, l, t, w, h,
        size=14, bold=False, italic=False,
        color=WHITE, align=PP_ALIGN.LEFT, wrap=True):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = wrap
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name      = 'Calibri'
    r.font.size      = Pt(size)
    r.font.bold      = bold
    r.font.italic    = italic
    r.font.color.rgb = color
    return tb


def img(slide, path, l, t, w, h=None):
    if not os.path.exists(path):
        return
    if h:
        return slide.shapes.add_picture(path, Inches(l), Inches(t),
                                        width=Inches(w), height=Inches(h))
    return slide.shapes.add_picture(path, Inches(l), Inches(t), width=Inches(w))


# ═══════════════════════════════════════════════════════════════
# TEMPLATE BUILDERS
# ═══════════════════════════════════════════════════════════════

def chrome(slide):
    """Navy header bar + crimson top line applied to any slide."""
    rect(slide, 0, 0, 13.33, 7.50, fill=WHITE)
    rect(slide, 0, 0,  0.30, 7.50, fill=NAVY)
    rect(slide, 0.30, 0, 13.03, 0.07, fill=CRIMSON)
    rect(slide, 0.30, 0.07, 13.03, 1.05, fill=NAVY)


def header(slide, title, subtitle=''):
    chrome(slide)
    txt(slide, title,
        l=0.50, t=0.13, w=11.5, h=0.62,
        size=26, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle,
            l=0.50, t=0.71, w=11.5, h=0.34,
            size=12, italic=True, color=LIGHTGRAY)


def section_div(num, title, sub=''):
    """Full-bleed dark section-break slide."""
    slide = prs.slides.add_slide(BLANK)
    rect(slide, 0, 0, 13.33, 7.50, fill=NAVY)
    rect(slide, 0, 0,    13.33, 0.10, fill=CRIMSON)
    rect(slide, 0, 7.40, 13.33, 0.10, fill=CRIMSON)
    txt(slide, num,
        l=0.8, t=1.6, w=2.0, h=3.8,
        size=120, bold=True, color=CRIMSON, align=PP_ALIGN.LEFT)
    rect(slide, 3.1, 2.0, 0.07, 3.2, fill=CRIMSON)
    txt(slide, title,
        l=3.5, t=2.5, w=9.0, h=1.2,
        size=40, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if sub:
        txt(slide, sub,
            l=3.5, t=3.85, w=9.0, h=0.8,
            size=17, italic=True, color=LIGHTGRAY, align=PP_ALIGN.LEFT)
    return slide


def insight_panel(slide, bullets, title='Key Insight',
                  l=10.55, t=1.20, w=2.65, h=5.9,
                  title_color=GOLD):
    """Narrow navy insight panel on the right."""
    rect(slide, l, t, w, h, fill=PANEL)
    rect(slide, l, t, w, 0.50, fill=NAVY)
    txt(slide, title,
        l=l+0.12, t=t+0.07, w=w-0.2, h=0.38,
        size=12, bold=True, color=title_color)
    for i, b in enumerate(bullets):
        txt(slide, f'▸  {b}',
            l=l+0.15, t=t+0.60+i*0.52, w=w-0.25, h=0.50,
            size=11, color=WHITE, wrap=True)


def viz_slide(title, subtitle, fig_path, bullets,
              insight_title='Key Insight',
              fig_w=9.8, fig_l=0.45, fig_t=1.22,
              insight_color=GOLD):
    """Standard one-viz slide: header + figure (left) + insight panel (right)."""
    slide = prs.slides.add_slide(BLANK)
    header(slide, title, subtitle)
    img(slide, fig_path, l=fig_l, t=fig_t, w=fig_w)
    insight_panel(slide, bullets,
                  title=insight_title,
                  title_color=insight_color)
    return slide


def stat_card(slide, value, label, l, t, w=2.5, h=1.35,
              val_color=GOLD, bg=NAVY):
    rect(slide, l, t, w, h, fill=bg, line=CRIMSON, line_pt=1.5)
    txt(slide, value,
        l=l+0.1, t=t+0.06, w=w-0.2, h=0.75,
        size=34, bold=True, color=val_color, align=PP_ALIGN.CENTER)
    txt(slide, label,
        l=l+0.1, t=t+0.82, w=w-0.2, h=0.4,
        size=11, color=LIGHTGRAY, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.50, fill=NAVY)
rect(slide, 8.7,  0, 4.63, 7.50, fill=PANEL)
rect(slide, 0,    0, 13.33, 0.08, fill=CRIMSON)
rect(slide, 0, 6.94, 13.33, 0.08, fill=CRIMSON)
rect(slide, 8.7, 0,  0.06,  7.50, fill=TEAL)

txt(slide, 'Hotel Booking',
    l=0.6, t=0.7, w=7.8, h=1.05, size=52, bold=True, color=WHITE)
txt(slide, 'Demand Analysis',
    l=0.6, t=1.65, w=7.8, h=1.05, size=52, bold=True, color=CRIMSON)
txt(slide, 'EDA  ·  Classification  ·  Regularization',
    l=0.6, t=2.75, w=7.8, h=0.5, size=16, italic=True, color=LIGHTGRAY)

rect(slide, 0.6, 3.65, 7.8, 1.05, fill=PANEL, line=TEAL, line_pt=1)
txt(slide, 'Sai Nithin Reddy Maddi  ·  Sujith Julakanti',
    l=0.75, t=3.77, w=7.5, h=0.4, size=16, bold=True, color=WHITE)
txt(slide, 'STAT-654  ·  Texas A&M University  ·  April 2026',
    l=0.75, t=4.15, w=7.5, h=0.35, size=13, color=LIGHTGRAY)

for val, lbl, ty, col in [
    ('119K', 'Reservations',     1.1,  GOLD),
    ('37%',  'Cancel Rate',      2.8,  CRIMSON),
    ('8',    'Models',           4.5,  TEAL),
]:
    txt(slide, val, l=9.0, t=ty,   w=4.0, h=1.0,
        size=52, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(slide, lbl, l=9.0, t=ty+0.9, w=4.0, h=0.4,
        size=14, color=LIGHTGRAY, align=PP_ALIGN.CENTER)

txt(slide, 'Dataset: Kaggle — Hotel Booking Demand (Jesse Mostipak)',
    l=0.6, t=7.08, w=8.5, h=0.3, size=10, italic=True, color=LIGHTGRAY)


# ═══════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.50, fill=OFFWHITE)
rect(slide, 0, 0, 13.33, 1.22, fill=NAVY)
rect(slide, 0, 0, 13.33, 0.08, fill=CRIMSON)
txt(slide, 'Agenda', l=0.5, t=0.24, w=12.0, h=0.75,
    size=32, bold=True, color=WHITE)

cards = [
    ('01', 'Dataset Overview',       'Size, features, hotel types'),
    ('02', 'Cancellation by Hotel',  'City vs Resort rates'),
    ('03', 'Monthly Trends',         'Seasonal patterns'),
    ('04', 'Lead Time',              'Booking window vs cancel'),
    ('05', 'Deposit Type',           'Payment policy effect'),
    ('06', 'ADR Analysis',           'Pricing patterns'),
    ('07', 'Booking Channel',        'OTA, Direct, Corporate'),
    ('08', 'Guest Behaviour',        'Prior cancels, requests'),
    ('09', 'Guest Profile',          'Repeat vs new guests'),
    ('10', 'Geographic Insights',    'Country-level patterns'),
    ('11', 'Correlation Analysis',   'Feature relationships'),
    ('12', 'EDA Findings',           '8 headline takeaways'),
    ('13', 'Models Overview',        '8 classifiers compared'),
    ('14', 'Regularization',         'L1 vs L2 shrinkage paths'),
    ('15', 'Performance Metrics',    'F1, AUC, Accuracy'),
    ('16', 'ROC Curves',             'Discrimination ability'),
    ('17', 'Confusion Matrices',     'Error breakdown'),
    ('18', 'Feature Importance',     'What drives prediction'),
    ('19', 'Conclusions',            'Summary & implications'),
]

cols = 5
cw, ch = 2.52, 1.18
for i, (num, title, sub) in enumerate(cards):
    col = i % cols
    row = i // cols
    l = 0.28 + col * (cw + 0.05)
    t = 1.38 + row * (ch + 0.10)
    rect(slide, l, t, cw, ch, fill=WHITE, line=LIGHTGRAY, line_pt=0.5)
    rect(slide, l, t, cw, 0.44, fill=NAVY)
    txt(slide, num,   l=l+0.1,  t=t+0.05, w=0.5,      h=0.34,
        size=14, bold=True, color=CRIMSON)
    txt(slide, title, l=l+0.55, t=t+0.05, w=cw-0.6,   h=0.34,
        size=11, bold=True, color=WHITE)
    txt(slide, sub,   l=l+0.12, t=t+0.52, w=cw-0.2,   h=0.55,
        size=10, color=DARK)


# ═══════════════════════════════════════════════════════════════
# SECTION DIVIDER — EDA
# ═══════════════════════════════════════════════════════════════
section_div('01', 'Exploratory Data Analysis',
            'Understanding 119K hotel reservations before modelling')


# ═══════════════════════════════════════════════════════════════
# SLIDE — DATASET OVERVIEW
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
header(slide, 'Dataset Overview', 'Hotel Booking Demand — Kaggle (Jesse Mostipak)')

stat_card(slide, '119,390', 'Reservations', l=0.45, t=1.30)
stat_card(slide, '37%',     'Cancel Rate',  l=3.10, t=1.30, val_color=CRIMSON)
stat_card(slide, '2',       'Hotel Types',  l=5.75, t=1.30, val_color=TEAL)
stat_card(slide, '32',      'Raw Features', l=8.40, t=1.30, val_color=GOLD)
stat_card(slide, '3 yrs',   '2015 – 2017',  l=11.05, t=1.30)

img(slide, FIG+'eda_overview.png', l=0.45, t=2.90, w=12.3)
txt(slide, 'City Hotel: 66% of bookings, 42% cancel rate  ·  Resort Hotel: 28% cancel rate',
    l=0.45, t=6.88, w=12.3, h=0.38, size=11, italic=True, color=DARK)


# ═══════════════════════════════════════════════════════════════
# EDA SLIDES — one figure each
# ═══════════════════════════════════════════════════════════════

viz_slide(
    'Cancellation Rate by Hotel Type',
    'City Hotel cancels at ~42%; Resort Hotel at ~28%',
    FIG+'eda_hotel_type.png',
    bullets=[
        'City Hotel: 42% cancel',
        'Resort Hotel: 28% cancel',
        'City has 2× higher rate',
        'Class imbalance present',
        'Must stratify in\ntrain/test split',
    ],
    insight_title='Hotel Type',
    insight_color=CRIMSON,
)

viz_slide(
    'Monthly Booking & Cancellation Trends',
    'Seasonal demand shifts and their effect on cancellation rates',
    FIG+'eda_monthly_v2.png',
    bullets=[
        'Peak bookings: Jul–Aug',
        'Highest cancel: Jan–Feb',
        'Low-season bookings\ncancel proportionally more',
        'Volume & rate move\ninversely in shoulders',
    ],
    insight_title='Seasonality',
    insight_color=TEAL,
)

viz_slide(
    'Lead Time Distribution',
    'How far in advance bookings are made — and its link to cancellation',
    FIG+'eda_lead_time.png',
    bullets=[
        'Cancelled: 2× longer\nlead times on average',
        'City Hotel: wider spread',
        'Non-cancelled: mostly\n< 100 days ahead',
        '#1 numeric predictor\nacross all models',
    ],
    insight_title='Lead Time',
    insight_color=GOLD,
)

viz_slide(
    'Deposit Type vs Cancellation',
    'Payment policy has the most counter-intuitive signal in the dataset',
    FIG+'eda_deposit_type.png',
    bullets=[
        'Non-Refund: ~99% cancel',
        'No Deposit: ~28% cancel',
        'Refundable: ~22% cancel',
        'Paradox driven by\nOTA policy behaviour',
        'High predictive signal\ndespite odd direction',
    ],
    insight_title='Deposit Type',
    insight_color=CRIMSON,
)

viz_slide(
    'Average Daily Rate (ADR)',
    'Pricing patterns by hotel type, month, and cancellation status',
    FIG+'eda_adr.png',
    bullets=[
        'Resort ADR peaks Jul–Aug',
        'City ADR relatively flat',
        'Cancelled bookings:\nslightly higher ADR avg',
        'ADR tracks seasonal\ndemand closely',
    ],
    insight_title='Pricing',
    insight_color=TEAL,
)

viz_slide(
    'Length of Stay',
    'Booking duration patterns and cancellation risk',
    FIG+'eda_stay_duration.png',
    bullets=[
        '1–3 night stays dominate',
        'Very long stays (>7 nights)\nhave elevated cancel rates',
        'Sweet spot: 2–4 nights\n→ lowest cancel risk',
        '1-night bookings also\ncancel infrequently',
    ],
    insight_title='Stay Duration',
    insight_color=GOLD,
)

viz_slide(
    'Booking Channel & Market Segment',
    'Where guests book shapes their likelihood of cancelling',
    FIG+'eda_market_channel.png',
    bullets=[
        'Online TA: highest vol,\n36% cancel rate',
        'Direct: lower cancel rate',
        'Corporate / Groups:\nlowest cancel rates',
        'GDS: elevated cancel',
        'Channel reflects\nbooking commitment',
    ],
    insight_title='Channel',
    insight_color=CRIMSON,
)

viz_slide(
    'Guest Behaviour — Prior Cancels & Special Requests',
    'Engagement signals are among the strongest behavioural predictors',
    FIG+'eda_customer_behavior.png',
    bullets=[
        '1+ prior cancel → 80%+\nfuture cancel rate',
        '0 requests: ~40% cancel',
        '3+ requests: ~10% cancel',
        'Engaged guests\nrarely cancel',
        'Behavioural history\nis highly predictive',
    ],
    insight_title='Behaviour',
    insight_color=TEAL,
)

viz_slide(
    'Guest Profile — Repeat vs New Guests',
    'Loyalty dramatically reduces cancellation risk',
    FIG+'eda_guest_type.png',
    bullets=[
        'Repeat guests: 14%\ncancellation rate',
        'New guests: 38% cancel',
        'Transient type cancels\nmost (~39%)',
        'Group type: very low\ncancellation',
        'Loyalty = commitment',
    ],
    insight_title='Guest Type',
    insight_color=GOLD,
)

viz_slide(
    'Geographic Insights',
    'Country of origin and cancellation patterns by hotel type',
    FIG+'eda_country_heatmap.png',
    bullets=[
        'Portugal dominates\nbooking volume',
        'Wide variation by\ncountry of origin',
        'Some countries: near\n0% cancel rate',
        'City Hotel higher\nacross all countries',
        'Country is a moderate\npredictor',
    ],
    insight_title='Geography',
    insight_color=CRIMSON,
    fig_w=9.6,
)

viz_slide(
    'Correlation Analysis',
    'Numeric feature relationships — what correlates with cancellation',
    FIG+'eda_correlation_v2.png',
    bullets=[
        'lead_time: strongest\npositive corr.',
        'special_requests:\nnegative (protective)',
        'prev_cancellations:\npositive',
        'adr: slight positive',
        'adults / children:\nnear zero',
    ],
    insight_title='Correlations',
    insight_color=TEAL,
    fig_w=9.6,
)


# ═══════════════════════════════════════════════════════════════
# SLIDE — EDA KEY FINDINGS (dark card grid)
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.50, fill=NAVY)
rect(slide, 0, 0, 13.33, 0.09, fill=CRIMSON)
rect(slide, 0, 1.12, 13.33, 0.04, fill=PANEL)
txt(slide, 'EDA — 8 Key Findings',
    l=0.5, t=0.15, w=12.0, h=0.82, size=30, bold=True, color=WHITE)

findings = [
    (CRIMSON, 'Lead Time',         '2× longer lead time\nfor cancellations'),
    (TEAL,    'Deposit Type',      'Non-refundable → 99%\ncancellation paradox'),
    (GOLD,    'Prior Cancels',     'Strongest behavioural\npredictor overall'),
    (RGBColor(0x8E,0xCE,0xE4),
              'Special Requests',  '3+ requests → only\n10% cancel rate'),
    (CRIMSON, 'Hotel Type',        'City 42% vs Resort\n28% cancel rate'),
    (TEAL,    'Booking Channel',   'OTA dominates; Direct\nbookings commit more'),
    (GOLD,    'Repeat Guests',     '14% vs 38% for\nnew guests'),
    (RGBColor(0x8E,0xCE,0xE4),
              'Seasonality',       'Jan–Feb peak cancel\ndespite low volume'),
]

for i, (color, title, detail) in enumerate(findings):
    col = i % 4
    row = i // 4
    l = 0.30 + col * 3.24
    t = 1.28 + row * 2.95
    rect(slide, l, t, 3.02, 2.72, fill=PANEL, line=color, line_pt=2)
    rect(slide, l, t, 3.02, 0.54, fill=color)
    txt(slide, title, l=l+0.12, t=t+0.08, w=2.78, h=0.38,
        size=14, bold=True,
        color=NAVY if color == GOLD else WHITE)
    txt(slide, detail, l=l+0.15, t=t+0.68, w=2.72, h=1.85,
        size=13, color=WHITE, wrap=True)


# ═══════════════════════════════════════════════════════════════
# SECTION DIVIDER — MODELLING
# ═══════════════════════════════════════════════════════════════
section_div('02', 'Predictive Modelling',
            'Logistic · Probit · L1/L2 · PCA · Trees · Ensembles')


# ═══════════════════════════════════════════════════════════════
# SLIDE — MODELS OVERVIEW TABLE
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
header(slide, 'Models Compared',
       '8 classifiers — statistical baselines to ensemble methods')

rows = [
    ('Logistic Regression',          'sigmoid link, MLE',          'Ch. 3 — Baseline',         TEAL),
    ('Probit Regression',            'normal CDF link, MLE',       'Ch. 3 — GLM alternative',  TEAL),
    ('L1 Logistic (Lasso)',          'ℓ₁ penalty → sparse coefs', 'Ch. 5 — Regularization',   CRIMSON),
    ('L2 Logistic (Ridge)',          'ℓ₂ penalty → shrinkage',    'Ch. 5 — Regularization',   CRIMSON),
    ('PCA + Logistic Regression',    'dim. reduction → LR',        'Ch. 5 — Dimension Red.',   CRIMSON),
    ('Decision Tree',                'gini / entropy splits',      'Ch. 3 — Non-linear',       GOLD),
    ('Random Forest',                'bagged trees, sqrt feat.',   'Ensemble',                 GOLD),
    ('Gradient Boosting',            'sequential boosting',        'Ensemble',                 GOLD),
]

rect(slide, 0.45, 1.22, 12.3, 0.48, fill=NAVY)
for lbl, lx, ww in [('Model', 0.60, 3.8), ('Description', 4.55, 4.0),
                     ('Curriculum Link', 8.65, 3.0), ('Family', 11.75, 0.9)]:
    txt(slide, lbl, l=lx, t=1.27, w=ww, h=0.38, size=12, bold=True, color=WHITE)

for i, (model, desc, link, color) in enumerate(rows):
    t = 1.74 + i * 0.63
    bg = OFFWHITE if i % 2 == 0 else WHITE
    rect(slide, 0.45, t, 12.3, 0.60, fill=bg)
    rect(slide, 0.45, t, 0.08, 0.60, fill=color)
    txt(slide, model, l=0.65, t=t+0.10, w=3.75, h=0.42, size=12, bold=True, color=DARK)
    txt(slide, desc,  l=4.55, t=t+0.10, w=3.95, h=0.42, size=11, color=DARK)
    txt(slide, link,  l=8.65, t=t+0.10, w=2.95, h=0.42, size=11, italic=True, color=color)

for lbl, color, lx in [('Statistical (Ch.3)', TEAL, 0.5),
                        ('Regularization (Ch.5)', CRIMSON, 3.2),
                        ('Ensemble', GOLD, 6.2)]:
    rect(slide, lx, 6.93, 0.20, 0.20, fill=color)
    txt(slide, lbl, l=lx+0.26, t=6.90, w=2.5, h=0.28, size=10, color=DARK)


# ═══════════════════════════════════════════════════════════════
# MODELLING SLIDES — one figure each
# ═══════════════════════════════════════════════════════════════

shrink_path = FIG + ('shrinkage_paths.png'
                     if os.path.exists(FIG+'shrinkage_paths.png')
                     else 'eda_correlation.png')
viz_slide(
    'Regularization — L1 vs L2 Shrinkage Paths',
    'How each coefficient changes as λ increases  (STAT-654 Ch. 5)',
    shrink_path,
    bullets=[
        'L1 (Lasso): zeroes\nout irrelevant features',
        'L2 (Ridge): shrinks\nall — none hit zero',
        'Dashed line = λ\nchosen by CV',
        'Confirms Ch. 5 theory\non real hotel data',
        'Lasso removes several\nredundant features',
    ],
    insight_title='Regularization',
    insight_color=CRIMSON,
    fig_w=9.8,
)

viz_slide(
    'Model Performance — Test Set Metrics',
    'Accuracy · Precision · Recall · F1-Score · ROC-AUC across all 8 models',
    FIG+'metrics_comparison.png',
    bullets=[
        'Gradient Boosting:\nbest F1 & AUC',
        'Random Forest:\nclose second',
        'L1 Lasso: sparse\nmodel, solid F1',
        'Ridge ≈ standard LR',
        'Probit ≈ Logistic\n(theory confirmed)',
        'PCA-LR: slight drop',
    ],
    insight_title='Results',
    insight_color=GOLD,
    fig_w=9.8,
)

viz_slide(
    'ROC Curves — All 8 Models',
    'True Positive Rate vs False Positive Rate at varying thresholds',
    FIG+'roc_curves.png',
    bullets=[
        'Ensembles AUC > 0.92',
        'Logistic variants\n~0.80 – 0.85 AUC',
        'Ideal curve: top-left',
        'Random chance: 0.50',
        'AUC = probability model\nranks + case higher',
    ],
    insight_title='ROC / AUC',
    insight_color=TEAL,
    fig_w=7.5, fig_l=1.8,
)

viz_slide(
    'Confusion Matrices — All Models',
    'True/False Positive & Negative breakdown on the test set',
    FIG+'confusion_matrices.png',
    bullets=[
        'Ensembles minimize\nfalse negatives',
        'Logistic models miss\nmore cancellations',
        'High recall important:\ncost of missed cancel',
        'Precision–recall\ntrade-off visible',
    ],
    insight_title='Error Types',
    insight_color=CRIMSON,
    fig_w=9.6,
)

viz_slide(
    'Feature Importance — Ensemble Models',
    'Top predictors identified by Random Forest and Gradient Boosting',
    FIG+'fi_ensemble_comparison.png',
    bullets=[
        'lead_time: #1 across\nboth ensembles',
        'deposit_type: high\npredictive power',
        'adr: average daily rate',
        'special_requests:\nprotective signal',
        'prev_cancellations:\nbehavioural memory',
    ],
    insight_title='Top Features',
    insight_color=GOLD,
    fig_w=9.8,
)


# ═══════════════════════════════════════════════════════════════
# SLIDE — CONCLUSIONS (card grid)
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.50, fill=OFFWHITE)
rect(slide, 0, 0, 13.33, 1.22, fill=NAVY)
rect(slide, 0, 0, 13.33, 0.08, fill=CRIMSON)
txt(slide, 'Conclusions', l=0.5, t=0.22, w=12.0, h=0.78, size=32, bold=True, color=WHITE)

concs = [
    (CRIMSON, 'Gradient Boosting Wins',
     'Best F1 and AUC across all 8 models. Non-linear interactions matter.'),
    (TEAL,    'Lasso Selects Features',
     'L1 penalty zeros out redundant columns — sparse model, competitive accuracy.'),
    (GOLD,    'Probit ≈ Logistic',
     'Both GLMs give near-identical results, confirming theoretical similarity (Ch. 3).'),
    (RGBColor(0x8E,0xCE,0xE4),
              'PCA Costs Little',
     '15–20 components explain 90%+ variance with only slight F1 drop.'),
    (CRIMSON, 'Lead Time is #1',
     'Strongest predictor across all models — long booking window = higher risk.'),
    (TEAL,    'Business Implication',
     'Target interventions at long-lead, no-deposit, OTA bookings. Repeat guests and special requests are protective.'),
]

for i, (color, title, body) in enumerate(concs):
    col = i % 3
    row = i // 3
    l = 0.30 + col * 4.32
    t = 1.38 + row * 2.85
    rect(slide, l, t, 4.10, 2.65, fill=WHITE, line=color, line_pt=2)
    rect(slide, l, t, 4.10, 0.54, fill=color)
    txt(slide, title, l=l+0.12, t=t+0.08, w=3.85, h=0.38,
        size=13, bold=True, color=NAVY if color == GOLD else WHITE)
    txt(slide, body,  l=l+0.15, t=t+0.65, w=3.80, h=1.85,
        size=11, color=DARK, wrap=True)


# ═══════════════════════════════════════════════════════════════
# SLIDE — THANK YOU
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.33, 7.50, fill=NAVY)
rect(slide, 0, 0,    13.33, 0.08, fill=CRIMSON)
rect(slide, 0, 7.42, 13.33, 0.08, fill=CRIMSON)
rect(slide, 0, 0, 4.5, 7.50, fill=PANEL)
rect(slide, 4.5, 0, 0.06, 7.50, fill=TEAL)

txt(slide, 'Thank\nYou',
    l=0.4, t=1.8, w=3.8, h=3.5,
    size=54, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

txt(slide, 'Questions & Discussion',
    l=5.0, t=1.55, w=8.0, h=0.9, size=34, bold=True, color=WHITE)
txt(slide, 'Sai Nithin Reddy Maddi',
    l=5.0, t=2.62, w=8.0, h=0.45, size=16, color=LIGHTGRAY)
txt(slide, 'Sujith Julakanti',
    l=5.0, t=3.06, w=8.0, h=0.45, size=16, color=LIGHTGRAY)
rect(slide, 5.0, 3.7, 7.8, 0.04, fill=PANEL)
txt(slide, 'STAT-654  ·  Texas A&M University  ·  April 2026',
    l=5.0, t=3.90, w=7.8, h=0.4, size=13, italic=True, color=LIGHTGRAY)
txt(slide, 'Dataset: Kaggle — Hotel Booking Demand (Jesse Mostipak)',
    l=5.0, t=4.36, w=7.8, h=0.4, size=12, italic=True,
    color=RGBColor(0x77,0x88,0x99))

for val, lbl, lx in [('8','Models',5.2), ('119K','Bookings',7.3),
                      ('37%','Cancel Rate',9.4), ('0.93+','Best AUC',11.4)]:
    txt(slide, val, l=lx, t=5.55, w=1.8, h=0.85,
        size=30, bold=True,
        color=GOLD if lbl in ('Models','Bookings') else CRIMSON,
        align=PP_ALIGN.CENTER)
    txt(slide, lbl, l=lx, t=6.30, w=1.8, h=0.5,
        size=11, color=LIGHTGRAY, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════
prs.save(OUT)
print(f'Saved  → {OUT}')
print(f'Slides : {len(prs.slides)}')
