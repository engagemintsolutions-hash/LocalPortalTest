/**
 * Property Search Portal - JavaScript
 * Handles questionnaire form, API integration, and results display
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  initializeForm();
  setupPreferenceSliders();
  setupFormSubmission();
});

/**
 * Initialize form with default values and validation
 */
function initializeForm() {
  // Set default values if needed
  const form = document.getElementById('search-form');

  // Add input validation
  const budgetMax = document.getElementById('budget-max');
  budgetMax.addEventListener('input', validateBudget);
}

/**
 * Setup preference sliders with real-time updates
 */
function setupPreferenceSliders() {
  const sliders = [
    'pref-schools',
    'pref-commute',
    'pref-safety',
    'pref-energy',
    'pref-value',
    'pref-conservation'
  ];

  sliders.forEach(sliderId => {
    const slider = document.getElementById(sliderId);
    const valueDisplay = document.getElementById(`${sliderId}-value`);

    slider.addEventListener('input', function() {
      // Update display
      valueDisplay.textContent = `${this.value}%`;

      // Calculate total
      updateTotalWeight();
    });
  });
}

/**
 * Update total weight and warn if over 100%
 */
function updateTotalWeight() {
  const total =
    parseInt(document.getElementById('pref-schools').value) +
    parseInt(document.getElementById('pref-commute').value) +
    parseInt(document.getElementById('pref-safety').value) +
    parseInt(document.getElementById('pref-energy').value) +
    parseInt(document.getElementById('pref-value').value) +
    parseInt(document.getElementById('pref-conservation').value);

  const totalDisplay = document.getElementById('total-weight');
  totalDisplay.textContent = `${total}%`;

  if (total > 100) {
    totalDisplay.classList.add('over-limit');
  } else {
    totalDisplay.classList.remove('over-limit');
  }

  return total;
}

/**
 * Validate budget inputs
 */
function validateBudget() {
  const budgetMin = document.getElementById('budget-min');
  const budgetMax = document.getElementById('budget-max');

  if (budgetMin.value && budgetMax.value) {
    if (parseInt(budgetMin.value) > parseInt(budgetMax.value)) {
      budgetMax.setCustomValidity('Maximum budget must be greater than minimum');
    } else {
      budgetMax.setCustomValidity('');
    }
  }
}

/**
 * Setup form submission handler
 */
function setupFormSubmission() {
  const form = document.getElementById('search-form');

  form.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Validate total weight
    const totalWeight = updateTotalWeight();
    if (totalWeight > 100) {
      alert('Total preference weights cannot exceed 100%. Please adjust your preferences.');
      return;
    }

    // Collect form data
    const questionnaire = buildQuestionnaireJSON();

    // Show loading state
    showLoadingState();

    try {
      // Call API
      const results = await searchProperties(questionnaire);

      // Display results
      displayResults(results);

    } catch (error) {
      console.error('Search error:', error);
      showErrorState(error.message);
    }
  });
}

/**
 * Build questionnaire JSON from form
 */
function buildQuestionnaireJSON() {
  const form = document.getElementById('search-form');
  const formData = new FormData(form);

  // Get property types (checkboxes)
  const propertyTypes = Array.from(form.querySelectorAll('input[name="property_types"]:checked'))
    .map(cb => cb.value);

  // Get postcode areas (comma-separated string to array)
  const postcodeAreas = formData.get('postcode_areas')
    ? formData.get('postcode_areas').split(',').map(s => s.trim().toUpperCase())
    : null;

  // Get target airports
  const targetAirports = formData.get('target_airports')
    ? formData.get('target_airports').split(',').map(s => s.trim().toUpperCase())
    : null;

  // Get flood risk exclusions
  const excludeFloodRisk = Array.from(form.querySelectorAll('input[name="exclude_flood_risk"]:checked'))
    .map(cb => cb.value);

  // Build questionnaire object
  const questionnaire = {
    budget_min: formData.get('budget_min') ? parseFloat(formData.get('budget_min')) : null,
    budget_max: parseFloat(formData.get('budget_max')),
    bedrooms_min: parseInt(formData.get('bedrooms_min')),
    bedrooms_max: formData.get('bedrooms_max') ? parseInt(formData.get('bedrooms_max')) : null,
    property_types: propertyTypes.length > 0 ? propertyTypes : null,

    location: {
      postcode_areas: postcodeAreas,
      radius_km: formData.get('radius_km') ? parseFloat(formData.get('radius_km')) : null,
      target_airports: targetAirports,
      max_distance_to_airport_km: formData.get('max_distance_to_airport_km')
        ? parseFloat(formData.get('max_distance_to_airport_km'))
        : null
    },

    preferences: {
      schools: parseInt(formData.get('weight_schools')) / 100,
      commute: parseInt(formData.get('weight_commute')) / 100,
      safety: parseInt(formData.get('weight_safety')) / 100,
      energy: parseInt(formData.get('weight_energy')) / 100,
      value: parseInt(formData.get('weight_value')) / 100,
      conservation: parseInt(formData.get('weight_conservation')) / 100
    },

    min_epc_rating: formData.get('min_epc_rating') || null,
    must_be_in_conservation_area: formData.get('must_be_in_conservation_area') === 'on',
    exclude_flood_risk: excludeFloodRisk.length > 0 ? excludeFloodRisk : null
  };

  console.log('Questionnaire:', questionnaire);
  return questionnaire;
}

/**
 * Call search API
 */
async function searchProperties(questionnaire) {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(questionnaire)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Search failed');
  }

  return await response.json();
}

/**
 * Display search results
 */
function displayResults(data) {
  const resultsSection = document.getElementById('results-section');
  const resultsGrid = document.getElementById('results-grid');
  const resultCountNumber = document.getElementById('result-count-number');
  const loadingSpinner = document.getElementById('loading-spinner');
  const noResults = document.getElementById('no-results');

  // Hide loading
  loadingSpinner.style.display = 'none';

  // Show results section
  resultsSection.style.display = 'block';

  // Update count
  resultCountNumber.textContent = data.total_results;

  // Clear previous results
  resultsGrid.innerHTML = '';

  if (data.results.length === 0) {
    // Show no results message
    noResults.style.display = 'block';
    return;
  }

  // Hide no results message
  noResults.style.display = 'none';

  // Render property cards
  data.results.forEach(listing => {
    const card = createPropertyCard(listing);
    resultsGrid.appendChild(card);
  });

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Create a property card element
 */
function createPropertyCard(listing) {
  const card = document.createElement('div');
  card.className = 'property-card';
  card.onclick = () => viewListingDetail(listing.listing_id);

  // Format price
  const price = new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    maximumFractionDigits: 0
  }).format(listing.price);

  // Match score percentage
  const matchScorePercent = Math.round(listing.match_score * 100);

  // Build HTML
  card.innerHTML = `
    <div class="property-image" style="background: linear-gradient(135deg, #667eea ${matchScorePercent}%, #764ba2 100%);">
      <!-- Placeholder: In production, load actual property images -->
    </div>
    <div class="property-content">
      <div class="property-price">${price}</div>
      <div class="property-title">${listing.title}</div>
      <div class="property-address">${listing.address}, ${listing.postcode}</div>

      <div class="property-features">
        <span class="feature-tag">${listing.bedrooms} bed</span>
        ${listing.bathrooms ? `<span class="feature-tag">${listing.bathrooms} bath</span>` : ''}
        ${listing.property_type ? `<span class="feature-tag">${listing.property_type}</span>` : ''}
        ${listing.epc_rating ? `<span class="feature-tag">EPC ${listing.epc_rating}</span>` : ''}
        ${listing.is_undervalued ? '<span class="feature-tag" style="background: #d4edda; color: #155724;">Undervalued</span>' : ''}
      </div>

      <div class="property-score">
        <span class="match-score">Match</span>
        <div class="score-bar">
          <div class="score-fill" style="width: ${matchScorePercent}%"></div>
        </div>
        <span class="match-score">${matchScorePercent}%</span>
      </div>
    </div>
  `;

  return card;
}

/**
 * View listing detail page
 */
function viewListingDetail(listingId) {
  window.location.href = `listing-detail.html?id=${listingId}`;
}

/**
 * Show loading state
 */
function showLoadingState() {
  const resultsSection = document.getElementById('results-section');
  const loadingSpinner = document.getElementById('loading-spinner');
  const resultsGrid = document.getElementById('results-grid');
  const noResults = document.getElementById('no-results');

  resultsSection.style.display = 'block';
  loadingSpinner.style.display = 'block';
  noResults.style.display = 'none';
  resultsGrid.innerHTML = '';

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Show error state
 */
function showErrorState(message) {
  const loadingSpinner = document.getElementById('loading-spinner');
  const noResults = document.getElementById('no-results');

  loadingSpinner.style.display = 'none';
  noResults.style.display = 'block';
  noResults.innerHTML = `<p>Error: ${message}</p><p>Please try again or adjust your search criteria.</p>`;
}

/**
 * Mobile menu toggle (from main Doorstep site)
 */
function toggleMobileMenu() {
  const nav = document.getElementById('main-nav');
  nav.classList.toggle('active');
}
