# Questionnaire Wizard - Design Ultra Plan
## Make it Beautiful & Match Doorstep Homepage

## 🎨 Doorstep Brand Identity

### Color Palette
```css
Primary Coral: #EF6A68  (buttons, CTAs, accents)
Teal Dark:     #19727F  (headings, dark text)
Teal Light:    #BCD1D5  (subtle backgrounds)
Background:    #FAFAF9  (off-white)
Text Primary:  #1A1A1A  (main text)
Text Secondary: #4A5568  (subtitles)
```

### Typography
- **Font**: Inter (already loaded)
- **Headings**: 700-800 weight, tight letter-spacing (-0.025em)
- **Body**: 400 weight, 17px, line-height 1.7
- **Subtitles**: 18px, #4A5568 color

### Design System
- **Buttons**: Coral gradient with shadow
- **Border radius**: 6-8px (subtle, not too round)
- **Shadows**: Soft, subtle (0 4px 12px rgba)
- **Spacing**: Generous white space
- **Style**: Professional, clean, sophisticated (not playful)

---

## 🔄 Current Issues vs. Doorstep Style

### ❌ Current Wizard Problems:
1. **Purple gradient background** (should be #FAFAF9 off-white)
2. **Blue accent color** (#0066cc should be Coral #EF6A68)
3. **Too rounded** (16px should be 6-8px)
4. **Playful emoji** (🏫🚇🛡️ - Doorstep is more professional)
5. **Card shadows too strong** (should be subtle)
6. **Progress circles too large** (should be minimal)

### ✅ What to Keep:
- Multi-step flow (good UX)
- Progress bar concept
- Slider interactions
- Grid layouts

---

## 📐 Ultra Plan - Redesign Steps

### Phase 1: Color Scheme Transformation

**Replace**:
```css
/* OLD (Purple/Blue) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: #0066cc;
border-color: #0066cc;

/* NEW (Doorstep Coral/Teal) */
background: var(--color-background);  /* #FAFAF9 */
color: var(--color-coral);  /* #EF6A68 */
border-color: var(--color-teal-light);  /* #BCD1D5 */
```

### Phase 2: Typography & Headings

**Match Doorstep style**:
```css
h1 {
  font-size: 48px;  /* Larger, bolder */
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--color-teal-dark);  /* #19727F */
}

.subtitle {
  font-size: 18px;
  color: var(--color-text-secondary);  /* #4A5568 */
  font-weight: 400;
}
```

### Phase 3: Button Redesign

**Use Doorstep coral gradient**:
```css
.btn-primary {
  background: linear-gradient(135deg, #EF6A68 0%, #E84745 100%);
  color: white;
  padding: 14px 32px;
  border-radius: 6px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(239, 106, 104, 0.4);
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 106, 104, 0.5);
}
```

### Phase 4: Progress Bar Refinement

**Simpler, more professional**:
```css
.progress-fill {
  background: linear-gradient(90deg, #EF6A68, #19727F);  /* Coral to Teal */
}

.step-circle {
  width: 32px;  /* Smaller */
  height: 32px;
  background: #BCD1D5;  /* Teal light */
  color: #19727F;  /* Teal dark text */
}

.progress-step.active .step-circle {
  background: #EF6A68;  /* Coral */
  color: white;
}
```

### Phase 5: Card Design - Professional, Not Playful

**Remove emojis, use icons/text**:
```html
<!-- OLD -->
<div class="priority-icon">🏫</div>

<!-- NEW -->
<div class="priority-icon">
  <svg>...</svg>  <!-- Clean SVG icon -->
</div>
```

**Card styling**:
```css
.priority-card {
  background: white;
  border: 1px solid #BCD1D5;  /* Teal light */
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);  /* Subtle */
  padding: 24px;
}

.priority-card:hover {
  border-color: #EF6A68;  /* Coral on hover */
  box-shadow: 0 4px 12px rgba(239, 106, 104, 0.15);
}
```

### Phase 6: Property Type Cards

**More sophisticated**:
```css
.property-type-card {
  background: white;
  border: 2px solid #E5E7EB;  /* Neutral */
  border-radius: 8px;
  padding: 32px 20px;
  text-align: center;
  transition: all 0.2s;
}

.property-type-card.active {
  background: linear-gradient(135deg, rgba(239, 106, 104, 0.05), rgba(25, 114, 127, 0.05));
  border-color: #EF6A68;
  box-shadow: 0 4px 16px rgba(239, 106, 104, 0.2);
}

.property-type-card h3 {
  color: var(--color-teal-dark);
  font-size: 18px;
  font-weight: 600;
}
```

### Phase 7: Background & Layout

**Clean, spacious**:
```css
.wizard-page {
  background: linear-gradient(180deg, #FAFAF9 0%, #F3F4F6 100%);  /* Subtle gradient */
  min-height: 100vh;
  padding: 120px 0 80px;
}

.wizard-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px;
}

.wizard-step {
  background: white;
  border-radius: 8px;
  padding: 60px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);  /* Doorstep subtle shadow */
}
```

### Phase 8: Results Page Styling

**Match Doorstep property cards**:
```css
.result-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.result-card:hover {
  border-color: #EF6A68;
  box-shadow: 0 8px 24px rgba(239, 106, 104, 0.15);
  transform: translateY(-4px);
}

.result-price {
  color: var(--color-coral);  /* #EF6A68 */
  font-size: 28px;
  font-weight: 700;
}

.match-badge {
  background: var(--color-teal-dark);  /* #19727F */
  color: white;
  font-weight: 600;
}
```

### Phase 9: Form Elements

**Professional inputs**:
```css
input[type="text"],
input[type="number"],
select {
  border: 2px solid #E5E7EB;
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 16px;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #EF6A68;  /* Coral */
  outline: none;
  box-shadow: 0 0 0 3px rgba(239, 106, 104, 0.1);
}

/* Range sliders */
input[type="range"]::-webkit-slider-thumb {
  background: #EF6A68;  /* Coral */
}

input[type="range"] {
  background: #BCD1D5;  /* Teal light track */
}
```

### Phase 10: Responsive Polish

**Mobile optimization**:
```css
@media (max-width: 768px) {
  .wizard-step {
    padding: 32px 20px;
  }

  h1 {
    font-size: 32px;
  }

  .property-type-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

---

## 🎯 Implementation Priority

### Quick Wins (15 mins):
1. ✅ Replace purple gradient → off-white background
2. ✅ Change blue (#0066cc) → coral (#EF6A68)
3. ✅ Update button styles to coral gradient
4. ✅ Reduce border-radius from 16px → 8px
5. ✅ Lighten shadows

### Medium (30 mins):
6. ✅ Replace emoji with minimal icons or text
7. ✅ Refine priority cards to match Doorstep professionalism
8. ✅ Update progress bar colors (coral/teal)
9. ✅ Polish form inputs with Doorstep styling

### Polish (1 hour):
10. ✅ Add subtle animations (Doorstep has smooth transitions)
11. ✅ Perfect spacing/typography
12. ✅ Match results cards to Doorstep aesthetic
13. ✅ Add micro-interactions

---

## 📋 File Changes Needed

### 1. `questionnaire-wizard.css` (MAIN FILE)
- Replace all color values
- Update button styles
- Refine card designs
- Match Doorstep spacing

### 2. `questionnaire-wizard.html`
- Optionally replace emojis with text labels
- Adjust structure if needed

### 3. `questionnaire-wizard.js`
- No changes needed (functionality is fine)

---

## ✨ Result

**Before**: Purple/blue CompareTheMarket style (playful, consumer-focused)

**After**: Coral/teal Doorstep style (professional, sophisticated, trustworthy)

Matches the homepage perfectly - users feel they're in the same brand experience.

---

Ready to implement? I can update the CSS in one go to match Doorstep perfectly!
