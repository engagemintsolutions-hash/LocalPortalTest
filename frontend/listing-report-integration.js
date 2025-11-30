/**
 * Integration script for professional-report.html
 *
 * Add this script to professional-report.html to:
 * 1. Load real listing data from API
 * 2. Show £5 paywall before full report
 * 3. Populate report with actual property data
 *
 * Usage: professional-report.html?listing_id=123
 */

const API_BASE_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', function() {
    // Check if listing_id is provided
    const urlParams = new URLSearchParams(window.location.search);
    const listingId = urlParams.get('listing_id');

    if (listingId) {
        loadListingData(listingId);
    } else {
        // No listing ID - show demo data (existing behavior)
        console.log('No listing_id provided - using demo data');
    }
});

async function loadListingData(listingId) {
    try {
        const response = await fetch(`${API_BASE_URL}/listing/${listingId}`);

        if (!response.ok) {
            throw new Error('Failed to load listing');
        }

        const listing = await response.json();

        // Populate report with real data
        populateReport(listing);

        // Show paywall overlay
        showPaywallOverlay(listingId, listing);

    } catch (error) {
        console.error('Error loading listing:', error);
        alert('Could not load property data. Please try again.');
    }
}

function populateReport(listing) {
    // Update address
    const addressElements = document.querySelectorAll('[data-field="address"]');
    addressElements.forEach(el => {
        el.textContent = `${listing.address}, ${listing.postcode}`;
    });

    // Update price
    const price = new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'GBP',
        maximumFractionDigits: 0
    }).format(listing.price);

    const priceElements = document.querySelectorAll('[data-field="price"]');
    priceElements.forEach(el => {
        el.textContent = price;
    });

    // Update beds/baths
    document.querySelectorAll('[data-field="bedrooms"]').forEach(el => {
        el.textContent = listing.bedrooms;
    });

    document.querySelectorAll('[data-field="bathrooms"]').forEach(el => {
        el.textContent = listing.bathrooms || 'N/A';
    });

    // Update EPC
    document.querySelectorAll('[data-field="epc-rating"]').forEach(el => {
        el.textContent = listing.epc_rating || 'N/A';
    });

    // Update AVM
    if (listing.avm_estimate) {
        const avmPrice = new Intl.NumberFormat('en-GB', {
            style: 'currency',
            currency: 'GBP',
            maximumFractionDigits: 0
        }).format(listing.avm_estimate);

        document.querySelectorAll('[data-field="avm-estimate"]').forEach(el => {
            el.textContent = avmPrice;
        });
    }

    // Update description
    if (listing.description) {
        document.querySelectorAll('[data-field="description"]').forEach(el => {
            el.textContent = listing.description;
        });
    }

    console.log('Report populated with real listing data');
}

function showPaywallOverlay(listingId, listing) {
    // Create paywall overlay
    const overlay = document.createElement('div');
    overlay.id = 'paywall-overlay';
    overlay.innerHTML = `
        <div class="paywall-backdrop" onclick="closePaywall()"></div>
        <div class="paywall-modal">
            <button class="paywall-close" onclick="closePaywall()">&times;</button>

            <div class="paywall-content">
                <div class="paywall-icon">🔒</div>
                <h2>Unlock Full Property Report</h2>
                <p class="paywall-subtitle">Get comprehensive insights for this property</p>

                <div class="paywall-preview">
                    <h3>${listing.title}</h3>
                    <p>${listing.address}, ${listing.postcode}</p>
                    <div class="paywall-price">£${new Intl.NumberFormat('en-GB').format(listing.price)}</div>
                </div>

                <div class="paywall-features">
                    <h4>This report includes:</h4>
                    <ul>
                        <li>✓ Full planning application history</li>
                        <li>✓ Restrictive covenants & legal constraints</li>
                        <li>✓ Comparable sales analysis</li>
                        <li>✓ Detailed AVM breakdown with confidence intervals</li>
                        <li>✓ School catchment areas & Ofsted ratings</li>
                        <li>✓ Crime statistics & safety data</li>
                        <li>✓ Flood risk assessment</li>
                        <li>✓ Transport links & journey times</li>
                        <li>✓ Area quality metrics (IMD, broadband, etc.)</li>
                    </ul>
                </div>

                <div class="paywall-pricing">
                    <div class="price-tag">
                        <span class="price-amount">£5.00</span>
                        <span class="price-label">One-time payment</span>
                    </div>
                </div>

                <button class="btn btn-primary btn-large" onclick="purchaseReport(${listingId})">
                    <span>Purchase Full Report - £5.00</span>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path d="M9 11L12 14L22 4M21 12V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>

                <p class="paywall-note">Secure payment via Stripe • Instant PDF download</p>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        #paywall-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 10000; }
        .paywall-backdrop { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); }
        .paywall-modal { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 16px; max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .paywall-close { position: absolute; top: 20px; right: 20px; background: none; border: none; font-size: 2rem; cursor: pointer; color: #666; width: 40px; height: 40px; border-radius: 50%; transition: background 0.2s; }
        .paywall-close:hover { background: #f5f5f5; }
        .paywall-content { padding: 50px 40px; }
        .paywall-icon { font-size: 4rem; text-align: center; margin-bottom: 20px; }
        .paywall-content h2 { text-align: center; font-size: 2rem; margin-bottom: 10px; color: #1a1a1a; }
        .paywall-subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 1.125rem; }
        .paywall-preview { background: #f5f7fa; padding: 20px; border-radius: 12px; margin-bottom: 30px; text-align: center; }
        .paywall-preview h3 { margin: 0 0 8px 0; font-size: 1.25rem; }
        .paywall-preview p { margin: 0 0 12px 0; color: #666; }
        .paywall-price { font-size: 1.75rem; font-weight: 700; color: #667eea; }
        .paywall-features { margin-bottom: 30px; }
        .paywall-features h4 { margin-bottom: 15px; }
        .paywall-features ul { list-style: none; padding: 0; margin: 0; }
        .paywall-features li { padding: 8px 0; color: #333; }
        .paywall-pricing { text-align: center; margin-bottom: 25px; }
        .price-tag { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px 40px; border-radius: 12px; display: inline-block; }
        .price-amount { display: block; font-size: 3rem; font-weight: 700; margin-bottom: 5px; }
        .price-label { font-size: 0.875rem; opacity: 0.9; }
        .paywall-content .btn-large { width: 100%; }
        .paywall-note { text-align: center; color: #666; font-size: 0.875rem; margin-top: 15px; }
    `;
    document.head.appendChild(style);
}

function closePaywall() {
    const overlay = document.getElementById('paywall-overlay');
    if (overlay) {
        overlay.remove();
    }
}

async function purchaseReport(listingId) {
    // Demo: Show payment flow
    const confirmed = confirm(
        'DEMO: Purchase full property report for £5.00?\n\n' +
        'In production, this would:\n' +
        '1. Open Stripe payment modal\n' +
        '2. Process £5 payment\n' +
        '3. Generate comprehensive PDF report\n' +
        '4. Download automatically\n\n' +
        'For this demo, click OK to unlock the report.'
    );

    if (!confirmed) return;

    try {
        // Mock API call
        const response = await fetch(`${API_BASE_URL}/listing/${listingId}/purchase-report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                listing_id: listingId,
                user_id: 'demo_user',
                payment_method_id: 'pm_demo_card'
            })
        });

        if (response.ok) {
            // Payment succeeded - close paywall and show full report
            closePaywall();

            // Show success message
            showSuccessMessage();

            // Scroll to report
            window.scrollTo({ top: 0, behavior: 'smooth' });

        } else {
            throw new Error('Payment failed');
        }

    } catch (error) {
        console.error('Purchase error:', error);

        // For demo, just unlock anyway
        closePaywall();
        showSuccessMessage();
    }
}

function showSuccessMessage() {
    const message = document.createElement('div');
    message.className = 'success-banner';
    message.innerHTML = `
        <div class="success-content">
            <span class="success-icon">✓</span>
            <span>Report unlocked! Full property insights now available below.</span>
        </div>
    `;

    document.body.insertBefore(message, document.body.firstChild);

    // Add success banner styles
    const style = document.createElement('style');
    style.textContent = `
        .success-banner { position: fixed; top: 80px; left: 50%; transform: translateX(-50%); background: #28a745; color: white; padding: 16px 32px; border-radius: 8px; box-shadow: 0 4px 12px rgba(40,167,69,0.3); z-index: 9999; animation: slideDown 0.3s ease; }
        .success-content { display: flex; align-items: center; gap: 12px; font-weight: 600; }
        .success-icon { background: white; color: #28a745; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; }
        @keyframes slideDown { from { transform: translate(-50%, -100%); } to { transform: translate(-50%, 0); } }
    `;
    document.head.appendChild(style);

    // Remove after 5 seconds
    setTimeout(() => {
        message.style.animation = 'slideUp 0.3s ease';
        message.style.animationFillMode = 'forwards';
        setTimeout(() => message.remove(), 300);
    }, 5000);
}
