/**
 * Expanded Questionnaire Wizard - 8 Steps
 */

const wizardState = {
  currentStep: 1,
  totalSteps: 8,  // Updated to 8 steps
  data: {
    budget_max: null,
    budget_min: null,
    bedrooms: 4,
    bathrooms: 2,
    propertyTypes: ['flat', 'semi_detached', 'detached'],
    postcodeAreas: 'London, SW1',
    radius: 20,
    tenure: 'any'
  }
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  setupBedroomSelector();
  setupBathroomSelector();
  setupPropertyTypeCards();
  setupRadiusSlider();
  updateProgress();
});

function nextStep() {
  if (wizardState.currentStep < wizardState.totalSteps) {
    if (!validateStep(wizardState.currentStep)) {
      return;
    }

    saveStepData(wizardState.currentStep);
    wizardState.currentStep++;
    showStep(wizardState.currentStep);
    updateProgress();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function prevStep() {
  if (wizardState.currentStep > 1) {
    wizardState.currentStep--;
    showStep(wizardState.currentStep);
    updateProgress();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function showStep(stepNumber) {
  document.querySelectorAll('.wizard-step').forEach(step => {
    step.classList.remove('active');
  });

  document.getElementById(`step-${stepNumber}`).classList.add('active');

  document.querySelectorAll('.progress-step').forEach((step, index) => {
    const stepNum = index + 1;
    step.classList.remove('active', 'completed');

    if (stepNum < stepNumber) {
      step.classList.add('completed');
    } else if (stepNum === stepNumber) {
      step.classList.add('active');
    }
  });
}

function updateProgress() {
  const percent = ((wizardState.currentStep - 1) / (wizardState.totalSteps - 1)) * 100;
  document.getElementById('progress-fill').style.width = `${percent}%`;
}

function validateStep(stepNumber) {
  if (stepNumber === 1) {
    const budgetMax = document.getElementById('budget-max').value;
    if (!budgetMax || parseFloat(budgetMax) <= 0) {
      alert('Please enter your maximum budget');
      return false;
    }
  }

  if (stepNumber === 3) {
    const postcodes = document.getElementById('postcode-areas').value;
    if (!postcodes || postcodes.trim() === '') {
      alert('Please enter at least one location');
      return false;
    }
  }

  return true;
}

function saveStepData(stepNumber) {
  if (stepNumber === 1) {
    wizardState.data.budget_max = parseFloat(document.getElementById('budget-max').value);
    wizardState.data.budget_min = parseFloat(document.getElementById('budget-min').value) || null;
  }

  if (stepNumber === 2) {
    wizardState.data.tenure = document.getElementById('tenure-pref').value;
  }

  if (stepNumber === 3) {
    wizardState.data.postcodeAreas = document.getElementById('postcode-areas').value;
    wizardState.data.radius = parseFloat(document.getElementById('radius-slider').value);
  }
}

function setupBedroomSelector() {
  document.querySelectorAll('.bedroom-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.bedroom-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      wizardState.data.bedrooms = parseInt(this.dataset.beds);
    });
  });
}

function setupBathroomSelector() {
  document.querySelectorAll('.bathroom-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.bathroom-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      wizardState.data.bathrooms = parseInt(this.dataset.baths);
    });
  });
}

function setupPropertyTypeCards() {
  document.querySelectorAll('.property-type-card').forEach(card => {
    card.addEventListener('click', function() {
      const type = this.dataset.type;

      if (this.classList.contains('active')) {
        this.classList.remove('active');
        wizardState.data.propertyTypes = wizardState.data.propertyTypes.filter(t => t !== type);
      } else {
        this.classList.add('active');
        wizardState.data.propertyTypes.push(type);
      }
    });
  });
}

function setupRadiusSlider() {
  const slider = document.getElementById('radius-slider');
  const valueDisplay = document.getElementById('radius-value');

  slider.addEventListener('input', function() {
    valueDisplay.textContent = this.value;
  });
}

function setBudget(amount) {
  document.getElementById('budget-max').value = amount;
}

// Results display helper
function addResultsCSS() {
  if (document.getElementById('results-css')) return;

  const style = document.createElement('style');
  style.id = 'results-css';
  style.textContent = `
    .results-header { margin-bottom: 40px; text-align: center; }
    .results-header h2 { font-size: 36px; font-weight: 800; color: var(--color-teal-dark); margin-bottom: 12px; }
    .results-header p { font-size: 18px; color: var(--color-text-secondary); }
    .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; margin-bottom: 48px; }
    .result-card { background: white; border: 1px solid #E5E7EB; border-radius: 8px; overflow: hidden; cursor: pointer; transition: all 0.2s; }
    .result-card:hover { border-color: var(--color-coral); transform: translateY(-4px); box-shadow: 0 8px 24px rgba(239, 106, 104, 0.15); }
    .result-image { height: 220px; position: relative; background-size: cover; background-position: center; }
    .match-badge { position: absolute; top: 16px; right: 16px; background: var(--color-teal-dark); color: white; padding: 8px 16px; border-radius: 6px; font-weight: 700; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
    .result-content { padding: 24px; }
    .result-price { font-size: 28px; font-weight: 700; color: var(--color-coral); margin-bottom: 12px; }
    .result-title { font-size: 18px; margin: 0 0 8px 0; font-weight: 600; color: var(--color-teal-dark); }
    .result-address { color: var(--color-text-secondary); margin: 0 0 16px 0; font-size: 15px; }
    .result-features { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
    .feature-badge { background: #F3F4F6; padding: 6px 12px; border-radius: 4px; font-size: 13px; font-weight: 600; color: var(--color-text); }
    .feature-badge.highlight { background: var(--color-teal); color: white; }
    .result-match-bar { height: 6px; background: #E5E7EB; border-radius: 3px; overflow: hidden; margin-bottom: 16px; }
    .match-bar-fill { height: 100%; background: linear-gradient(90deg, var(--color-coral), var(--color-teal)); transition: width 0.3s; }
    .btn-sm { padding: 12px 24px; font-size: 14px; width: 100%; }
    .results-actions { text-align: center; margin-top: 32px; }
  `;
  document.head.appendChild(style);
}

function displayResults(data) {
  document.getElementById('loading-state').style.display = 'none';
  const resultsContainer = document.getElementById('results-content');
  resultsContainer.style.display = 'block';

  if (!data.results || data.results.length === 0) {
    resultsContainer.innerHTML = `
      <div style="text-align: center; padding: 60px 20px;">
        <h2 style="color: var(--color-teal-dark); margin-bottom: 16px;">No properties found</h2>
        <p>Try adjusting your search criteria or importance weights</p>
        <button class="btn btn-primary" onclick="wizardState.currentStep = 1; showStep(1); updateProgress();">Start Over</button>
      </div>
    `;
    return;
  }

  let html = `
    <div class="results-header">
      <h2>We found ${data.total_results} perfect homes for you!</h2>
      <p>Sorted by best match based on your importance ratings</p>
    </div>
    <div class="results-grid">
  `;

  data.results.forEach(listing => {
    const matchPercent = Math.round(listing.match_score * 100);
    const price = new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      maximumFractionDigits: 0
    }).format(listing.price);

    const imageUrl = listing.image_url || listing.image_urls?.[0] || 'property-front.jpg';

    html += `
      <div class="result-card" onclick="window.location.href='professional-report.html?listing_id=${listing.listing_id}'">
        <div class="result-image" style="background-image: url('${imageUrl}'); background-size: cover; background-position: center;">
          <div class="match-badge">${matchPercent}% Match</div>
        </div>
        <div class="result-content">
          <div class="result-price">${price}</div>
          <h3 class="result-title">${listing.title || 'Property for sale'}</h3>
          <p class="result-address">${listing.address || listing.postcode || ''}</p>

          <div class="result-features">
            <span class="feature-badge">${listing.bedrooms} bed</span>
            ${listing.bathrooms ? `<span class="feature-badge">${listing.bathrooms} bath</span>` : ''}
            ${listing.property_type ? `<span class="feature-badge">${listing.property_type}</span>` : ''}
            ${listing.is_undervalued ? '<span class="feature-badge highlight">Great Value</span>' : ''}
          </div>

          <div class="result-match-bar">
            <div class="match-bar-fill" style="width: ${matchPercent}%"></div>
          </div>

          <button class="btn btn-primary btn-sm">
            View Property & Get £5 Report
          </button>
        </div>
      </div>
    `;
  });

  html += `
    </div>
    <div class="results-actions">
      <button class="btn btn-secondary" onclick="window.location.reload()">New Search</button>
    </div>
  `;

  resultsContainer.innerHTML = html;
  addResultsCSS();
}
