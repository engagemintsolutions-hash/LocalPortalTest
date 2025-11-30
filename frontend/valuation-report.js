// ================================================
// VALUATION REPORT JAVASCRIPT
// Mock data - ready for API integration
// ================================================

// Mock Data - Replace with API calls when backend is ready
const mockReportData = {
  property: {
    address: "8 Mccorquodale Road, Wolverton, Milton Keynes, MK12 5GP",
    type: "Purpose Built Flat",
    bedrooms: 2,
    bathrooms: 2,
    receptions: 1,
    size: 775,
    yearBuilt: 2007,
    tenure: "Leasehold"
  },
  valuation: {
    estimate: 202000,
    lower: 182000,
    upper: 222000,
    confidence: 78,
    confidenceLevel: "High Confidence"
  },
  history: {
    lastSalePrice: 167950,
    lastSaleDate: "September 2007",
    priceChange: 34050,
    priceChangePercent: 20.3
  },
  rental: {
    monthlyRent: 865,
    annualRent: 10380,
    yield: 5.1
  },
  comparables: [
    {
      address: "Mccorquodale Road, Wolverton",
      distance: "0.04 miles",
      price: 179000,
      date: "April 2018",
      type: "2 bedroom flat/maisonette",
      size: "990 sqft",
      status: "SSTC"
    },
    {
      address: "Mccorquodale Road, Wolverton",
      distance: "0.05 miles",
      price: 156000,
      date: "September 2013",
      type: "2 bedroom flat/maisonette",
      size: "721 sqft",
      status: "Sold"
    },
    {
      address: "Galaxy, 0.04 miles",
      distance: "0.04 miles",
      price: 176000,
      date: "December 2009",
      type: "2 bedroom flat/maisonette",
      size: "Approx 721 sqft",
      status: "Sold"
    },
    {
      address: "Galaxy, 0.06 miles",
      distance: "0.06 miles",
      price: 174000,
      date: "February 2018",
      type: "2 bedroom flat/maisonette",
      size: "Approx 721 sqft",
      status: "Sold"
    },
    {
      address: "Jersey Road, 0.1 miles",
      distance: "0.1 miles",
      price: 157995,
      date: "April 2005",
      type: "2 bedroom flat",
      size: "909 sqft",
      status: "Sold"
    },
    {
      address: "Meadham Meadow, 0.34 miles",
      distance: "0.34 miles",
      price: 158000,
      date: "September 2016",
      type: "2 bedroom flat",
      size: "887 sqft",
      status: "Sold"
    }
  ],
  market: {
    askingPriceAchieved: 97,
    averageTimeOnMarket: 10,
    searchVolume: 3006,
    searchPeriod: "28 days"
  },
  priceTrends: {
    labels: ["Sep-13", "Sep-14", "Sep-15", "Sep-16", "Sep-17", "Sep-18"],
    thisProperty: [145000, 152000, 168000, 175000, 189000, 202000],
    areaAverage: [138000, 145000, 158000, 168000, 182000, 195000]
  },
  schools: [
    {
      name: "Wyvern Primary School",
      rating: "Outstanding",
      distance: "0.3 miles",
      type: "Primary",
      ageRange: "4-11"
    },
    {
      name: "Radcliffe School",
      rating: "Good",
      distance: "0.8 miles",
      type: "Secondary",
      ageRange: "11-18"
    },
    {
      name: "St. Mary's CE Primary",
      rating: "Outstanding",
      distance: "1.1 miles",
      type: "Primary",
      ageRange: "4-11"
    }
  ],
  transport: [
    {
      type: "train",
      name: "Wolverton Station",
      distance: "0.6 miles",
      walkTime: "12 min",
      service: "Direct to London Euston (50 mins)"
    },
    {
      type: "bus",
      name: "Bus Stop",
      distance: "0.1 miles",
      walkTime: "2 min",
      service: "Routes 4, 5, 7 to MK Centre"
    }
  ],
  demographics: {
    labels: ["0-17", "18-29", "30-44", "45-64", "65+"],
    values: [18, 22, 28, 20, 12]
  },
  crime: {
    labels: ["Burglary", "Vehicle", "Violence", "Anti-Social", "Other"],
    values: [12, 18, 25, 30, 15],
    comparisonToNational: -23
  },
  environmental: {
    floodRisk: "Very Low",
    airQuality: "Good",
    greenSpace: "0.3 miles"
  },
  confidenceFactors: [
    {
      name: "Data Quality",
      score: 95,
      level: "high",
      description: "Excellent data coverage: EPC records, Land Registry history, 12 recent comparables"
    },
    {
      name: "Market Activity",
      score: 72,
      level: "medium",
      description: "Moderate sales volume in the area, active market with good comparable evidence"
    },
    {
      name: "Property Uniqueness",
      score: 85,
      level: "high",
      description: "Standard property type with many similar comparables in the local market"
    },
    {
      name: "Area Stability",
      score: 68,
      level: "medium",
      description: "Steady price growth, moderate volatility in recent years"
    }
  ]
};

// ================================================
// INITIALIZE REPORT
// ================================================

document.addEventListener('DOMContentLoaded', function() {
  // Set report date
  document.getElementById('report-date').textContent = new Date().toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  // Initialize all components
  initializeConfidenceGauge();
  initializePriceTrendChart();
  initializeComparables();
  initializeDemographicsChart();
  initializeCrimeChart();

  console.log('Valuation report initialized successfully');
});

// ================================================
// CONFIDENCE GAUGE
// ================================================

function initializeConfidenceGauge() {
  const canvas = document.getElementById('confidenceGauge');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const confidence = mockReportData.valuation.confidence;

  // Premium color scheme
  let mainColor, gradientColor;
  if (confidence >= 80) {
    mainColor = '#0D9488';
    gradientColor = '#0F766E';
  } else if (confidence >= 60) {
    mainColor = '#F59E0B';
    gradientColor = '#D97706';
  } else {
    mainColor = '#D1675E';
    gradientColor = '#B85C54';
  }

  // Create gradient
  const gradient = ctx.createLinearGradient(0, 0, 0, 180);
  gradient.addColorStop(0, mainColor);
  gradient.addColorStop(1, gradientColor);

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [confidence, 100 - confidence],
        backgroundColor: [gradient, '#F1F5F9'],
        borderWidth: 0,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '78%',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: false
        }
      },
      animation: {
        animateRotate: true,
        animateScale: false,
        duration: 1200,
        easing: 'easeInOutQuart'
      }
    }
  });
}

// ================================================
// PRICE TREND CHART
// ================================================

function initializePriceTrendChart() {
  const canvas = document.getElementById('priceTrendChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const data = mockReportData.priceTrends;

  // Create gradients for premium look
  const gradient1 = ctx.createLinearGradient(0, 0, 0, 400);
  gradient1.addColorStop(0, 'rgba(15, 82, 87, 0.12)');
  gradient1.addColorStop(1, 'rgba(15, 82, 87, 0.01)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [
        {
          label: '2-Bed Flats in MK12',
          data: data.thisProperty,
          borderColor: '#0F5257',
          backgroundColor: gradient1,
          borderWidth: 2.5,
          fill: true,
          tension: 0.35,
          pointRadius: 0,
          pointHoverRadius: 6,
          pointHoverBackgroundColor: '#0F5257',
          pointHoverBorderColor: '#fff',
          pointHoverBorderWidth: 3
        },
        {
          label: 'Milton Keynes Average',
          data: data.areaAverage,
          borderColor: '#94A3B8',
          backgroundColor: 'transparent',
          borderWidth: 2,
          fill: false,
          tension: 0.35,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: '#94A3B8',
          pointHoverBorderColor: '#fff',
          pointHoverBorderWidth: 2,
          borderDash: [6, 4]
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#0F172A',
          padding: 14,
          cornerRadius: 8,
          titleFont: {
            size: 13,
            weight: '600',
            family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
          },
          bodyFont: {
            size: 14,
            weight: '500',
            family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
          },
          titleMarginBottom: 8,
          bodySpacing: 6,
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': £' + context.parsed.y.toLocaleString();
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: function(value) {
              return '£' + (value / 1000) + 'k';
            },
            font: {
              size: 12,
              weight: '500'
            },
            color: '#64748B',
            padding: 8
          },
          border: {
            display: false
          },
          grid: {
            color: '#F1F5F9',
            drawBorder: false,
            lineWidth: 1
          }
        },
        x: {
          ticks: {
            font: {
              size: 12,
              weight: '500'
            },
            color: '#64748B',
            padding: 8
          },
          border: {
            display: false
          },
          grid: {
            display: false
          }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeInOutQuart'
      }
    }
  });
}

// ================================================
// COMPARABLES
// ================================================

function initializeComparables() {
  const container = document.getElementById('comparables-grid');
  if (!container) return;

  const comparables = mockReportData.comparables;

  container.innerHTML = comparables.map((comp, index) => `
    <div class="comparable-card">
      <div class="comparable-image" style="background: linear-gradient(135deg, #E5E7EB 0%, #F3F4F6 100%); display: flex; align-items: center; justify-content: center;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
      </div>
      <div class="comparable-info">
        <div class="comparable-address">${comp.address}</div>
        <div class="comparable-details">
          <div><strong>Type:</strong> ${comp.type}</div>
          <div><strong>Size:</strong> ${comp.size}</div>
          <div><strong>Distance:</strong> ${comp.distance}</div>
          <div><strong>Status:</strong> ${comp.status}</div>
        </div>
        <div class="comparable-price">£${comp.price.toLocaleString()}</div>
        <div class="comparable-date">Sold ${comp.date}</div>
      </div>
    </div>
  `).join('');
}

// ================================================
// DEMOGRAPHICS CHART
// ================================================

function initializeDemographicsChart() {
  const canvas = document.getElementById('demographicsChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const data = mockReportData.demographics;

  // Create sophisticated gradient
  const gradient = ctx.createLinearGradient(0, 0, 400, 0);
  gradient.addColorStop(0, 'rgba(15, 82, 87, 0.95)');
  gradient.addColorStop(1, 'rgba(13, 148, 136, 0.85)');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Population',
        data: data.values,
        backgroundColor: gradient,
        borderWidth: 0,
        borderRadius: 6,
        barPercentage: 0.65
      }]
    },
    options: {
      indexAxis: 'y', // Horizontal bars
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#0F172A',
          padding: 16,
          cornerRadius: 8,
          titleFont: {
            size: 13,
            weight: '600',
            family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
          },
          bodyFont: {
            size: 14,
            weight: '500',
            family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
          },
          displayColors: false,
          callbacks: {
            title: function(context) {
              return 'Age: ' + context[0].label;
            },
            label: function(context) {
              return context.parsed.x + '% of local population';
            }
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          max: 35,
          ticks: {
            callback: function(value) {
              return value + '%';
            },
            font: {
              size: 11,
              weight: '500',
              family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
            },
            color: '#64748B',
            padding: 8
          },
          border: {
            display: false
          },
          grid: {
            color: 'rgba(148, 163, 184, 0.12)',
            drawBorder: false,
            lineWidth: 1
          }
        },
        y: {
          ticks: {
            font: {
              size: 12,
              weight: '600',
              family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
            },
            color: '#0F172A',
            padding: 12,
            crossAlign: 'far'
          },
          border: {
            display: false
          },
          grid: {
            display: false
          }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeInOutQuart'
      }
    }
  });
}

// ================================================
// CRIME CHART
// ================================================

function initializeCrimeChart() {
  const canvas = document.getElementById('crimeChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const data = mockReportData.crime;

  // Sort data by value (highest to lowest) for better visualization
  const sortedData = data.labels
    .map((label, i) => ({ label, value: data.values[i] }))
    .sort((a, b) => b.value - a.value);

  const sortedLabels = sortedData.map(d => d.label);
  const sortedValues = sortedData.map(d => d.value);

  // Calculate percentages for display
  const total = sortedValues.reduce((a, b) => a + b, 0);
  const percentages = sortedValues.map(v => ((v / total) * 100).toFixed(1));

  // Create gradient for bars
  const createGradient = (index) => {
    const gradient = ctx.createLinearGradient(0, 0, 400, 0);
    // Strongest color for highest value, gradually lighter
    const intensity = 1 - (index * 0.15);
    gradient.addColorStop(0, `rgba(15, 82, 87, ${intensity * 0.9})`);
    gradient.addColorStop(1, `rgba(13, 148, 136, ${intensity * 0.75})`);
    return gradient;
  };

  const gradients = sortedValues.map((_, i) => createGradient(i));

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: sortedLabels,
      datasets: [{
        label: 'Incidents',
        data: sortedValues,
        backgroundColor: gradients,
        borderWidth: 0,
        borderRadius: 6,
        barPercentage: 0.7
      }]
    },
    options: {
      indexAxis: 'y', // Horizontal bars
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#0F172A',
          padding: 16,
          cornerRadius: 8,
          titleFont: {
            size: 13,
            weight: '600',
            family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
          },
          bodyFont: {
            size: 14,
            weight: '500',
            family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
          },
          displayColors: false,
          callbacks: {
            title: function(context) {
              const index = context[0].dataIndex;
              return sortedLabels[index];
            },
            label: function(context) {
              const index = context.dataIndex;
              return percentages[index] + '% of total incidents';
            }
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            display: false // Hide x-axis numbers for cleaner look
          },
          border: {
            display: false
          },
          grid: {
            display: false
          }
        },
        y: {
          ticks: {
            font: {
              size: 12,
              weight: '600',
              family: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif'
            },
            color: '#0F172A',
            padding: 12,
            crossAlign: 'far',
            callback: function(value, index) {
              // Add percentage to label
              return sortedLabels[index] + ' (' + percentages[index] + '%)';
            }
          },
          border: {
            display: false
          },
          grid: {
            display: false
          }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeInOutQuart'
      }
    }
  });
}

// ================================================
// API INTEGRATION PLACEHOLDER
// Replace mock data with real API calls
// ================================================

/*
async function fetchValuationReport(address) {
  try {
    const response = await fetch(`/api/valuation?address=${encodeURIComponent(address)}`);
    const data = await response.json();

    // Update all sections with real data
    updatePropertyDetails(data.property);
    updateValuation(data.valuation);
    updateComparables(data.comparables);
    // ... update other sections

    return data;
  } catch (error) {
    console.error('Error fetching valuation:', error);
    // Show error to user
  }
}
*/

// ================================================
// UTILITY FUNCTIONS
// ================================================

function formatCurrency(value) {
  return '£' + value.toLocaleString('en-GB');
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-GB', {
    month: 'long',
    year: 'numeric'
  });
}

function calculatePercentageChange(oldValue, newValue) {
  return (((newValue - oldValue) / oldValue) * 100).toFixed(1);
}

// ================================================
// PRINT FUNCTIONALITY
// ================================================

function printReport() {
  window.print();
}

// ================================================
// SHARE FUNCTIONALITY
// ================================================

function shareReport() {
  if (navigator.share) {
    navigator.share({
      title: 'Property Valuation Report',
      text: `Valuation report for ${mockReportData.property.address}`,
      url: window.location.href
    }).catch(err => console.log('Error sharing:', err));
  } else {
    // Fallback: Copy link to clipboard
    navigator.clipboard.writeText(window.location.href)
      .then(() => alert('Link copied to clipboard!'))
      .catch(err => console.log('Error copying:', err));
  }
}

console.log('Valuation Report JS loaded');
console.log('Mock data ready for:', mockReportData.property.address);
