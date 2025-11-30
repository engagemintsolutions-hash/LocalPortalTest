/**
 * Questionnaire Wizard - CompareTheMarket Style
 * Multi-step property search with visual interface
 */

// State
const wizardState = {
  currentStep: 1,
  totalSteps: 5,
  data: {
    budget_max: null,
    budget_min: null,
    bedrooms: 3,
    propertyTypes: [],
    postcodeAreas: '',
    radius: 5,
    targetAirport: null,
    maxAirportDist: null,
    priorities: {
      schools: 20,
      commute: 20,
      safety: 20,
      energy: 20,
      value: 20,
      conservation: 0
    }
  }
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  setupBedroomSelector();
  setupPropertyTypeCards();
  setupRadiusSlider();
  setupPrioritySliders();
  updateProgress();
});

/**
 * Navigate between steps
 */
function nextStep() {
  if (wizardState.currentStep < wizardState.totalSteps) {
    // Validate current step
    if (!validateStep(wizardState.currentStep)) {
      return;
    }

    // Save data from current step
    saveStepData(wizardState.currentStep);

    // Move to next step
    wizardState.currentStep++;
    showStep(wizardState.currentStep);
    updateProgress();

    // Scroll to top
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
  // Hide all steps
  document.querySelectorAll('.wizard-step').forEach(step => {
    step.classList.remove('active');
  });

  // Show current step
  document.getElementById(`step-${stepNumber}`).classList.add('active');

  // Update progress steps
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

/**
 * Validate current step
 */
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
      alert('Please enter at least one postcode area');
      return false;
    }
  }

  return true;
}

/**
 * Save data from each step
 */
function saveStepData(stepNumber) {
  if (stepNumber === 1) {
    wizardState.data.budget_max = parseFloat(document.getElementById('budget-max').value);
    wizardState.data.budget_min = parseFloat(document.getElementById('budget-min').value) || null;
  }

  if (stepNumber === 3) {
    wizardState.data.postcodeAreas = document.getElementById('postcode-areas').value;
    wizardState.data.radius = parseFloat(document.getElementById('radius-slider').value);
    wizardState.data.targetAirport = document.getElementById('target-airport').value || null;
    wizardState.data.maxAirportDist = parseFloat(document.getElementById('max-airport-dist').value) || null;
  }
}

/**
 * Setup interactive controls
 */
function setupBedroomSelector() {
  document.querySelectorAll('.bedroom-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.bedroom-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      wizardState.data.bedrooms = parseInt(this.dataset.beds);
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

function setupPrioritySliders() {
  const sliders = {
    'priority-schools': 'schools',
    'priority-commute': 'commute',
    'priority-safety': 'safety',
    'priority-energy': 'energy',
    'priority-value': 'value',
    'priority-conservation': 'conservation'
  };

  Object.keys(sliders).forEach(sliderId => {
    const slider = document.getElementById(sliderId);
    const key = sliders[sliderId];
    const valueDisplay = document.getElementById(`val-${key}`);

    slider.addEventListener('input', function() {
      const value = parseInt(this.value);
      wizardState.data.priorities[key] = value;
      valueDisplay.textContent = value;
      updateTotalPriority();
    });
  });
}

function updateTotalPriority() {
  const total = Object.values(wizardState.data.priorities).reduce((sum, val) => sum + val, 0);
  const totalDisplay = document.getElementById('total-priority');

  totalDisplay.textContent = `${total}%`;

  if (total > 100) {
    totalDisplay.classList.add('over-limit');
  } else {
    totalDisplay.classList.remove('over-limit');
  }
}

/**
 * Quick budget setter
 */
function setBudget(amount) {
  document.getElementById('budget-max').value = amount;
}

/**
 * Search properties (Step 4 -> Step 5)
 */
async function searchProperties() {
  // Validate priorities total
  const total = Object.values(wizardState.data.priorities).reduce((sum, val) => sum + val, 0);
  if (total > 100) {
    alert('Total priorities cannot exceed 100%. Please adjust your sliders.');
    return;
  }

  // Save final data
  saveStepData(3);  // Make sure location is saved
  saveStepData(4);  // Priorities (already saved via sliders but be safe)

  // Move to results step
  wizardState.currentStep = 5;
  showStep(5);
  updateProgress();

  // Show loading
  document.getElementById('loading-state').style.display = 'block';
  document.getElementById('results-content').style.display = 'none';

  try {
    // Build API request
    const questionnaire = buildQuestionnaire();

    // Call search API
    const response = await fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(questionnaire)
    });

    if (!response.ok) {
      throw new Error('Search failed');
    }

    const data = await response.json();

    // Display results
    displayResults(data);

  } catch (error) {
    console.error('Search error:', error);
    document.getElementById('loading-state').style.display = 'none';
    document.getElementById('results-content').innerHTML = `
      <div class="error-message">
        <h2>Oops! Something went wrong</h2>
        <p>We couldn't complete your search. Please try again or adjust your criteria.</p>
        <button class="btn btn-primary" onclick="prevStep()">Back to Preferences</button>
      </div>
    `;
    document.getElementById('results-content').style.display = 'block';
  }
}

function buildQuestionnaire() {
  const postcodes = wizardState.data.postcodeAreas
    .split(',')
    .map(p => p.trim().toUpperCase())
    .filter(p => p);

  return {
    budget_max: wizardState.data.budget_max,
    budget_min: wizardState.data.budget_min,
    bedrooms_min: wizardState.data.bedrooms,
    property_types: wizardState.data.propertyTypes.length > 0 ? wizardState.data.propertyTypes : null,

    location: {
      postcode_areas: postcodes,
      radius_km: wizardState.data.radius,
      target_airports: wizardState.data.targetAirport ? [wizardState.data.targetAirport] : null,
      max_distance_to_airport_km: wizardState.data.maxAirportDist
    },

    preferences: {
      schools: wizardState.data.priorities.schools / 100,
      commute: wizardState.data.priorities.commute / 100,
      safety: wizardState.data.priorities.safety / 100,
      energy: wizardState.data.priorities.energy / 100,
      value: wizardState.data.priorities.value / 100,
      conservation: wizardState.data.priorities.conservation / 100
    }
  };
}

function displayResults(data) {
  document.getElementById('loading-state').style.display = 'none';

  const resultsContainer = document.getElementById('results-content');
  resultsContainer.style.display = 'block';

  if (data.results.length === 0) {
    resultsContainer.innerHTML = `
      <div class="no-results">
        <h2>No properties found</h2>
        <p>Try adjusting your search criteria</p>
        <button class="btn btn-primary" onclick="wizardState.currentStep = 1; showStep(1);">Start Over</button>
      </div>
    `;
    return;
  }

  // Display results
  let html = `
    <div class="results-header">
      <h2>We found ${data.total_results} perfect homes for you!</h2>
      <p>Sorted by best match</p>
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

    // Get first image URL (from S3 or placeholder)
    const imageUrl = listing.image_url || 'property-front.jpg'; // Use existing Doorstep placeholder

    html += `
      <div class="result-card" onclick="viewListingWithReport(${listing.listing_id})">
        <div class="result-image" style="background-image: url('${imageUrl}'); background-size: cover; background-position: center;">
          <div class="match-badge">${matchPercent}% Match</div>
        </div>
        <div class="result-content">
          <div class="result-price">${price}</div>
          <h3 class="result-title">${listing.title}</h3>
          <p class="result-address">${listing.address}, ${listing.postcode}</p>

          <div class="result-features">
            <span class="feature-badge">${listing.bedrooms} bed</span>
            ${listing.bathrooms ? `<span class="feature-badge">${listing.bathrooms} bath</span>` : ''}
            ${listing.epc_rating ? `<span class="feature-badge">EPC ${listing.epc_rating}</span>` : ''}
            ${listing.is_undervalued ? '<span class="feature-badge highlight">Great Value</span>' : ''}
          </div>

          <div class="result-match-bar">
            <div class="match-bar-fill" style="width: ${matchPercent}%"></div>
          </div>

          <button class="btn btn-primary btn-sm">
            View Details & Get £5 Report
          </button>
        </div>
      </div>
    `;
  });

  html += `
    </div>
    <div class="results-actions">
      <button class="btn btn-secondary" onclick="wizardState.currentStep = 1; showStep(1);">New Search</button>
    </div>
  `;

  resultsContainer.innerHTML = html;

  // Add results CSS if not already there
  addResultsCSS();
}

function addResultsCSS() {
  if (document.getElementById('results-css')) return;

  const style = document.createElement('style');
  style.id = 'results-css';
  style.textContent = `
    .results-header { margin-bottom: 30px; text-align: center; }
    .results-header h2 { font-size: 2rem; margin-bottom: 10px; }
    .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; margin-bottom: 40px; }
    .result-card { background: #f5f7fa; border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform 0.2s; }
    .result-card:hover { transform: translateY(-4px); }
    .result-image { height: 200px; position: relative; }
    .match-badge { position: absolute; top: 12px; right: 12px; background: white; padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 0.875rem; color: #667eea; }
    .result-content { padding: 20px; }
    .result-price { font-size: 1.75rem; font-weight: 700; color: #667eea; margin-bottom: 8px; }
    .result-title { font-size: 1.125rem; margin: 0 0 5px 0; }
    .result-address { color: #666; margin: 0 0 15px 0; }
    .result-features { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
    .feature-badge { background: white; padding: 4px 10px; border-radius: 6px; font-size: 0.875rem; }
    .feature-badge.highlight { background: #28a745; color: white; }
    .result-match-bar { height: 6px; background: #e5e5e5; border-radius: 3px; margin-bottom: 15px; overflow: hidden; }
    .match-bar-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); }
    .results-actions { text-align: center; }
    .btn-sm { padding: 10px 20px; font-size: 0.875rem; width: 100%; }
  `;
  document.head.appendChild(style);
}

function viewListingWithReport(listingId) {
  // Navigate to professional report page (existing Doorstep page)
  // This links to the existing professional-report.html with the listing data
  window.location.href = `professional-report.html?listing_id=${listingId}`;
}
