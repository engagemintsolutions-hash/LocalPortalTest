/**
 * Listing Detail Page - JavaScript
 * Fetches and displays detailed property information
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Current listing ID
let currentListingId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Get listing ID from URL
  const urlParams = new URLSearchParams(window.location.search);
  currentListingId = urlParams.get('id');

  if (!currentListingId) {
    showError('No listing ID provided');
    return;
  }

  // Load listing details
  loadListingDetails(currentListingId);
});

/**
 * Load listing details from API
 */
async function loadListingDetails(listingId) {
  try {
    const response = await fetch(`${API_BASE_URL}/listing/${listingId}`);

    if (!response.ok) {
      throw new Error('Failed to load listing');
    }

    const listing = await response.json();
    displayListingDetails(listing);

  } catch (error) {
    console.error('Error loading listing:', error);
    showError(error.message);
  }
}

/**
 * Display listing details on the page
 */
function displayListingDetails(listing) {
  // Hide loading, show content
  document.getElementById('loading').style.display = 'none';
  document.getElementById('property-content').style.display = 'block';

  // Format price
  const price = new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    maximumFractionDigits: 0
  }).format(listing.price);

  // Update header
  document.getElementById('property-price').textContent = price;
  document.getElementById('property-title').textContent = listing.title;
  document.getElementById('property-address').textContent = `${listing.address}, ${listing.postcode}`;

  // Update status badge (could be dynamic based on listing status)
  const statusBadge = document.getElementById('property-status');
  statusBadge.textContent = 'For Sale';
  statusBadge.style.background = '#28a745';

  // Quick facts
  document.getElementById('bedrooms').textContent = listing.bedrooms;
  document.getElementById('bathrooms').textContent = listing.bathrooms || 'N/A';
  document.getElementById('property-type').textContent = listing.property_type || 'N/A';

  const epcRating = document.getElementById('epc-rating');
  epcRating.textContent = listing.epc_rating || 'N/A';
  if (listing.epc_rating) {
    epcRating.classList.add(`rating-${listing.epc_rating}`);
  }

  // Description
  document.getElementById('property-description').textContent = listing.description || 'No description available.';

  // Key Features
  document.getElementById('epc-score').textContent = listing.epc_score || 'N/A';
  document.getElementById('conservation-area').textContent = listing.in_conservation_area ? 'Yes' : 'No';
  document.getElementById('flood-risk').textContent = formatFloodRisk(listing.flood_risk);
  document.getElementById('imd-decile').textContent = listing.imd_decile || 'N/A';
  document.getElementById('crime-rate').textContent = listing.crime_rate_percentile
    ? `${listing.crime_rate_percentile} percentile`
    : 'N/A';
  document.getElementById('broadband-speed').textContent = listing.max_download_speed_mbps
    ? `${listing.max_download_speed_mbps} Mbps`
    : 'N/A';

  // Valuation
  if (listing.avm_estimate) {
    const avmEstimate = new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      maximumFractionDigits: 0
    }).format(listing.avm_estimate);
    document.getElementById('avm-estimate').textContent = avmEstimate;

    const confidence = listing.avm_confidence_score
      ? `${Math.round(listing.avm_confidence_score * 100)}%`
      : 'N/A';
    document.getElementById('avm-confidence').textContent = confidence;

    if (listing.avm_value_delta_pct !== null && listing.avm_value_delta_pct !== undefined) {
      const delta = listing.avm_value_delta_pct;
      const deltaElement = document.getElementById('avm-delta');
      const deltaText = delta > 0 ? `+${delta.toFixed(1)}%` : `${delta.toFixed(1)}%`;
      deltaElement.textContent = deltaText;
      deltaElement.classList.add(delta > 0 ? 'positive' : 'negative');

      // Show undervalued alert
      if (listing.is_undervalued) {
        document.getElementById('undervalued-alert').style.display = 'block';
      }
    }
  }

  // School Quality
  const schoolQuality = listing.school_quality_score
    ? `${Math.round(listing.school_quality_score * 100)}% quality score`
    : 'N/A';
  document.getElementById('school-quality').textContent = schoolQuality;

  const schoolDistances = [];
  if (listing.distance_to_nearest_primary_m) {
    schoolDistances.push(`Primary: ${(listing.distance_to_nearest_primary_m / 1000).toFixed(1)}km`);
  }
  if (listing.distance_to_nearest_secondary_m) {
    schoolDistances.push(`Secondary: ${(listing.distance_to_nearest_secondary_m / 1000).toFixed(1)}km`);
  }
  document.getElementById('school-distances').textContent = schoolDistances.join(' | ') || 'Distance data unavailable';

  // Transport
  const station = listing.distance_to_nearest_station_m
    ? `Station: ${(listing.distance_to_nearest_station_m / 1000).toFixed(1)}km`
    : 'Station distance unavailable';
  document.getElementById('transport-station').textContent = station;

  const airport = listing.nearest_airport_code
    ? `${listing.nearest_airport_code}: ${(listing.distance_to_nearest_airport_m / 1000).toFixed(1)}km`
    : 'Airport distance unavailable';
  document.getElementById('transport-airport').textContent = airport;

  // Planning
  const planningText = listing.recent_planning_apps
    ? `${listing.recent_planning_apps} recent applications`
    : 'No recent planning applications';
  document.getElementById('planning-apps').textContent = planningText;
}

/**
 * Format flood risk for display
 */
function formatFloodRisk(risk) {
  if (!risk) return 'Unknown';
  return risk.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Purchase detailed report
 */
async function purchaseReport() {
  if (!currentListingId) {
    alert('No listing ID available');
    return;
  }

  // In a real implementation, this would:
  // 1. Show a payment modal with Stripe
  // 2. Process the payment
  // 3. Generate and download the report

  // For prototype, just show confirmation
  const confirmed = confirm(
    `Purchase detailed report for £5.00?\n\n` +
    `This will include:\n` +
    `- Full planning history\n` +
    `- Restrictive covenants\n` +
    `- Comparable sales analysis\n` +
    `- Detailed area metrics`
  );

  if (!confirmed) return;

  try {
    // Mock payment - in production, integrate with Stripe
    const response = await fetch(`${API_BASE_URL}/listing/${currentListingId}/purchase-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        listing_id: parseInt(currentListingId),
        user_id: 'demo_user_123', // In production, use real user ID
        payment_method_id: 'pm_mock_visa' // Mock payment method
      })
    });

    if (!response.ok) {
      throw new Error('Payment failed');
    }

    const result = await response.json();

    if (result.report_url) {
      // Report is ready, download it
      window.open(result.report_url, '_blank');
      alert('Report purchased successfully! Opening in new tab...');
    } else {
      // Report is being generated
      alert('Report purchased! You will receive an email when it\'s ready (typically within 5 minutes).');
    }

  } catch (error) {
    console.error('Purchase error:', error);
    alert(`Failed to purchase report: ${error.message}`);
  }
}

/**
 * Show error state
 */
function showError(message) {
  document.getElementById('loading').style.display = 'none';
  const errorContainer = document.getElementById('error-message');
  errorContainer.style.display = 'block';
  errorContainer.querySelector('p').textContent = `Error: ${message}`;
}
