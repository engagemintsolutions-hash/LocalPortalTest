// Dashboard content states
const dashboardStates = {
  main: `
    <div class="dash-header">
      <span class="dash-title">Portfolio Dashboard</span>
      <div class="dash-stats">
        <div><small>Properties</small><strong>1,247</strong></div>
        <div><small>Completed</small><strong>1,189</strong></div>
      </div>
    </div>
    <div class="dash-content">
      <div class="dash-property">
        <div>
          <h4>42 Kensington Gardens, London W2 4RA</h4>
          <p>3 bed • 2 bath • Victorian Terrace</p>
        </div>
        <span class="dash-badge">High Confidence</span>
      </div>
      <div class="dash-valuation">
        <small>RECOMMENDED VALUATION</small>
        <h3>£875,000</h3>
        <p>Range: £850,000 - £900,000</p>
      </div>
      <div class="dash-models">
        <div class="dash-model">
          <small>DETERMINISTIC</small>
          <strong>£872,500</strong>
        </div>
        <div class="dash-model">
          <small>ML MODEL</small>
          <strong>£877,300</strong>
          <span>+0.5% variance</span>
        </div>
      </div>
      <div class="dash-comparables">
        <small>MATCHED COMPARABLES (3)</small>
        <div class="dash-comp">
          <span>38 Kensington Gardens<br><em>0.1 mi • Sold Mar 2024</em></span>
          <strong>£865,000</strong>
        </div>
        <div class="dash-comp">
          <span>51 Queensway<br><em>0.3 mi • Sold Jan 2024</em></span>
          <strong>£890,000</strong>
        </div>
        <div class="dash-comp">
          <span>15 Leinster Square<br><em>0.4 mi • Sold Feb 2024</em></span>
          <strong>£858,000</strong>
        </div>
      </div>
      <div class="dash-footer">
        <div class="dash-risks">
          <span class="risk-good">✓ Complete</span>
          <span class="risk-good">✓ Strong comps</span>
          <span class="risk-warn">⚠ Volatility</span>
        </div>
        <span class="dash-status">Ready for review</span>
      </div>
    </div>
  `,

  pillars: `
    <div class="dash-header">
      <span class="dash-title">Dual-System Validation</span>
    </div>
    <div class="dash-content" style="justify-content: center;">
      <div class="dash-valuation">
        <small>DETERMINISTIC MODEL</small>
        <h3>£872,500</h3>
        <p>Based on 15+ property attributes</p>
      </div>
      <div style="text-align: center; padding: 1.5rem 0;">
        <div style="font-size: 32px; color: var(--color-teal-dark);">⇅</div>
        <p style="font-size: 14px; color: var(--color-teal-dark); font-weight: 600;">CROSS-VALIDATION</p>
      </div>
      <div class="dash-valuation" style="background: #F0FDF4; border-color: #10B981;">
        <small>ML MODEL</small>
        <h3 style="color: #10B981;">£877,300</h3>
        <p>+0.5% variance • High confidence</p>
      </div>
      <div style="background: #FAFAF9; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
        <p style="font-size: 14px; color: var(--color-text); text-align: center; margin: 0;">
          <strong>Both models agree</strong><br>
          <span style="font-size: 12px; color: var(--color-text-secondary);">Models within 0.5% indicate strong valuation confidence</span>
        </p>
      </div>
    </div>
  `,

  transparency: `
    <div class="dash-header">
      <span class="dash-title">Transparency Report</span>
    </div>
    <div class="dash-content">
      <div style="background: #F0F9FF; padding: 1.5rem; border-radius: 8px; border: 2px solid var(--color-teal-dark);">
        <h4 style="font-size: 14px; color: var(--color-teal-dark); margin-bottom: 1rem;">✓ What We Know</h4>
        <ul style="list-style: none; padding: 0; font-size: 13px; color: var(--color-text-secondary);">
          <li style="padding: 0.5rem 0;">• 3 matched comparables within 0.5 mi</li>
          <li style="padding: 0.5rem 0;">• Full transaction history (5 years)</li>
          <li style="padding: 0.5rem 0;">• Satellite + street imagery analyzed</li>
          <li style="padding: 0.5rem 0;">• IMD & location intelligence</li>
        </ul>
      </div>

      <div style="background: #FEF3C7; padding: 1.5rem; border-radius: 8px; border: 2px solid #F59E0B; margin-top: 1rem;">
        <h4 style="font-size: 14px; color: #92400E; margin-bottom: 1rem;">⚠ Assumptions Made</h4>
        <ul style="list-style: none; padding: 0; font-size: 13px; color: #78350F;">
          <li style="padding: 0.5rem 0;">• Internal condition assumed "good"</li>
          <li style="padding: 0.5rem 0;">• No recent refurbishment data</li>
        </ul>
      </div>

      <div style="background: #D1FAE5; padding: 1.5rem; border-radius: 8px; border: 2px solid #10B981; margin-top: 1rem;">
        <h4 style="font-size: 14px; color: #065F46; margin-bottom: 0.5rem;">Confidence Score</h4>
        <div style="font-size: 32px; font-weight: 700; color: #10B981;">87%</div>
        <p style="font-size: 12px; color: #065F46; margin: 0;">High confidence valuation</p>
      </div>
    </div>
  `,

  comparison: `
    <div class="dash-header" style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);">
      <span class="dash-title">❌ Generalist AI Tools</span>
    </div>
    <div class="dash-content" style="justify-content: center;">
      <div style="background: #FEE2E2; border: 2px solid #DC2626; border-radius: 8px; padding: 1.5rem;">
        <ul style="list-style: none; padding: 0; font-size: 14px; color: #991B1B;">
          <li style="padding: 0.75rem 0; border-bottom: 1px solid #FCA5A5;">❌ Black-box outputs</li>
          <li style="padding: 0.75rem 0; border-bottom: 1px solid #FCA5A5;">❌ Hallucination risk</li>
          <li style="padding: 0.75rem 0; border-bottom: 1px solid #FCA5A5;">❌ No human oversight</li>
          <li style="padding: 0.75rem 0;">❌ Unexplainable results</li>
        </ul>
      </div>

      <div style="text-align: center; padding: 1rem 0; font-size: 24px;">⇓</div>

      <div style="background: #D1FAE5; border: 2px solid #10B981; border-radius: 8px; padding: 1.5rem;">
        <h4 style="font-size: 16px; color: #065F46; margin-bottom: 1rem; text-align: center;">✓ Doorstep Approach</h4>
        <ul style="list-style: none; padding: 0; font-size: 14px; color: #065F46;">
          <li style="padding: 0.75rem 0; border-bottom: 1px solid #6EE7B7;">✓ Transparent reasoning</li>
          <li style="padding: 0.75rem 0; border-bottom: 1px solid #6EE7B7;">✓ Deterministic ground truth</li>
          <li style="padding: 0.75rem 0; border-bottom: 1px solid #6EE7B7;">✓ Manual review, always</li>
          <li style="padding: 0.75rem 0;">✓ Audit-ready clarity</li>
        </ul>
      </div>
    </div>
  `,

  visual: `
    <div class="dash-header">
      <span class="dash-title">Visual Intelligence</span>
    </div>
    <div class="dash-content">
      <div style="background: linear-gradient(135deg, #BCD1D5 0%, #19727F 100%); aspect-ratio: 16/10; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: 600; margin-bottom: 1rem;">
        Satellite View
      </div>
      <div style="background: #FAFAF9; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB; margin-bottom: 1rem;">
        <h4 style="font-size: 13px; color: var(--color-teal-dark); margin-bottom: 0.5rem;">✓ AI Detected Features</h4>
        <ul style="list-style: none; padding: 0; font-size: 12px; color: var(--color-text-secondary);">
          <li style="padding: 0.3rem 0;">• Garden: 85m² (rear)</li>
          <li style="padding: 0.3rem 0;">• Parking: 2 spaces (front)</li>
          <li style="padding: 0.3rem 0;">• Extension: Single-storey (rear)</li>
          <li style="padding: 0.3rem 0;">• Plot: 320m² total</li>
        </ul>
      </div>

      <div style="background: linear-gradient(135deg, #BCD1D5 0%, #19727F 100%); aspect-ratio: 16/10; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: 600; margin-bottom: 1rem;">
        Street View
      </div>
      <div style="background: #FAFAF9; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">
        <h4 style="font-size: 13px; color: var(--color-teal-dark); margin-bottom: 0.5rem;">✓ Condition Assessment</h4>
        <ul style="list-style: none; padding: 0; font-size: 12px; color: var(--color-text-secondary);">
          <li style="padding: 0.3rem 0;">• Roof: Good condition</li>
          <li style="padding: 0.3rem 0;">• Façade: Well maintained</li>
          <li style="padding: 0.3rem 0;">• Windows: Double glazed (UPVC)</li>
          <li style="padding: 0.3rem 0;">• Recent refurbishment signals</li>
        </ul>
      </div>
    </div>
  `
};

// Scroll handler
let currentState = 'main';

function updateDashboard() {
  const sections = document.querySelectorAll('.content-section');
  const dashboard = document.getElementById('dashboardContent');

  if (!dashboard) return;

  sections.forEach(section => {
    const rect = section.getBoundingClientRect();
    const isInView = rect.top < window.innerHeight / 2 && rect.bottom > window.innerHeight / 2;

    if (isInView) {
      const newState = section.dataset.dashboard;
      if (newState && newState !== currentState) {
        currentState = newState;
        dashboard.style.opacity = '0';
        setTimeout(() => {
          dashboard.innerHTML = dashboardStates[newState];
          dashboard.style.opacity = '1';
        }, 200);
      }
    }
  });
}

// Initialize
window.addEventListener('DOMContentLoaded', () => {
  const dashboard = document.getElementById('dashboardContent');
  if (dashboard) {
    dashboard.innerHTML = dashboardStates.main;
  }
});

// Listen for scroll
window.addEventListener('scroll', updateDashboard);
