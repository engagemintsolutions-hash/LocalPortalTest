// ================================================
// PROFESSIONAL PROPERTY REPORT JAVASCRIPT
// Simplified - no Chart.js, only map and table
// ================================================
//
// DATA SOURCES:
// - Market Intelligence: Land Registry House Price Index (HPI)
// - Comparables: Land Registry Price Paid Data
// - Property Details: EPC Register, Land Registry, Local Authority
// - All data sources are UK Government Open Data (free to use)
//
// ================================================

// Mock Data & Market Intelligence
const professionalReportData = {
  marketData: {
    doorstep_valuation: 202000,
    market_average_ytd: 187580,
    market_median_ytd: 185250,
    market_12month_avg: 183613,
    sample_size_ytd: 28,
    sample_size_12month: 42,
    area: "MK12",
    property_type: "flat",
    year: 2025,
    annual_change_pct: 49.6, // 2024 to 2025 YTD
    market_position_pct: 7.7 // Above market average
  },
  comparables: [
    {
      address: "Mccorquodale Road, Wolverton",
      distance: 0.04,
      date: "April 2018",
      price: 179000,
      pricePerSqft: 181,
      type: "2 bedroom flat/maisonette",
      size: "990 sqft",
      similarity: 92,
      lat: 52.0641,
      lng: -0.8101
    },
    {
      address: "Mccorquodale Road, Wolverton",
      distance: 0.05,
      date: "September 2013",
      price: 156000,
      pricePerSqft: 216,
      type: "2 bedroom flat/maisonette",
      size: "721 sqft",
      similarity: 95,
      lat: 52.0639,
      lng: -0.8098
    },
    {
      address: "Galaxy, 0.04 miles",
      distance: 0.04,
      date: "December 2009",
      price: 176000,
      pricePerSqft: 244,
      type: "2 bedroom flat/maisonette",
      size: "Approx 721 sqft",
      similarity: 88,
      lat: 52.0643,
      lng: -0.8105
    },
    {
      address: "Galaxy, 0.06 miles",
      distance: 0.06,
      date: "February 2018",
      price: 174000,
      pricePerSqft: 241,
      type: "2 bedroom flat/maisonette",
      size: "Approx 721 sqft",
      similarity: 87,
      lat: 52.0638,
      lng: -0.8109
    },
    {
      address: "Jersey Road, 0.1 miles",
      distance: 0.1,
      date: "April 2005",
      price: 157995,
      pricePerSqft: 174,
      type: "2 bedroom flat",
      size: "909 sqft",
      similarity: 84,
      lat: 52.0635,
      lng: -0.8095
    },
    {
      address: "Meadham Meadow, 0.34 miles",
      distance: 0.34,
      date: "September 2016",
      price: 158000,
      pricePerSqft: 178,
      type: "2 bedroom flat",
      size: "887 sqft",
      similarity: 82,
      lat: 52.0628,
      lng: -0.8088
    },
    {
      address: "Wolverton Road, 0.12 miles",
      distance: 0.12,
      date: "March 2019",
      price: 185000,
      pricePerSqft: 245,
      type: "2 bedroom flat",
      size: "755 sqft",
      similarity: 90,
      lat: 52.0645,
      lng: -0.8112
    },
    {
      address: "Station Street, 0.15 miles",
      distance: 0.15,
      date: "June 2020",
      price: 192000,
      pricePerSqft: 258,
      type: "2 bedroom flat",
      size: "744 sqft",
      similarity: 89,
      lat: 52.0633,
      lng: -0.8118
    },
    {
      address: "Church Street, 0.18 miles",
      distance: 0.18,
      date: "January 2021",
      price: 198000,
      pricePerSqft: 265,
      type: "2 bedroom flat",
      size: "747 sqft",
      similarity: 88,
      lat: 52.0629,
      lng: -0.8125
    },
    {
      address: "Stratford Road, 0.22 miles",
      distance: 0.22,
      date: "August 2021",
      price: 205000,
      pricePerSqft: 272,
      type: "2 bedroom flat",
      size: "753 sqft",
      similarity: 86,
      lat: 52.0625,
      lng: -0.8082
    },
    {
      address: "Green Lane, 0.25 miles",
      distance: 0.25,
      date: "November 2021",
      price: 210000,
      pricePerSqft: 278,
      type: "2 bedroom flat",
      size: "755 sqft",
      similarity: 85,
      lat: 52.0621,
      lng: -0.8075
    },
    {
      address: "Creed Street, 0.28 miles",
      distance: 0.28,
      date: "March 2022",
      price: 215000,
      pricePerSqft: 285,
      type: "2 bedroom flat",
      size: "754 sqft",
      similarity: 84,
      lat: 52.0617,
      lng: -0.8069
    },
    {
      address: "Aylesbury Street, 0.30 miles",
      distance: 0.30,
      date: "July 2022",
      price: 208000,
      pricePerSqft: 276,
      type: "2 bedroom flat",
      size: "753 sqft",
      similarity: 83,
      lat: 52.0613,
      lng: -0.8062
    },
    {
      address: "Buckingham Road, 0.32 miles",
      distance: 0.32,
      date: "October 2022",
      price: 203000,
      pricePerSqft: 269,
      type: "2 bedroom flat",
      size: "754 sqft",
      similarity: 82,
      lat: 52.0609,
      lng: -0.8055
    },
    {
      address: "Radcliffe Street, 0.35 miles",
      distance: 0.35,
      date: "February 2023",
      price: 198000,
      pricePerSqft: 263,
      type: "2 bedroom flat",
      size: "752 sqft",
      similarity: 81,
      lat: 52.0605,
      lng: -0.8048
    }
  ]
};

// ================================================
// INITIALIZE REPORT
// ================================================

document.addEventListener('DOMContentLoaded', function() {
  // Check URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('professional') === 'true') {
    document.body.classList.add('has-professional');
  }
  if (urlParams.get('docs') === 'true') {
    document.body.classList.add('has-docs');
  }
  if (urlParams.get('export') === 'true') {
    document.body.classList.add('has-export');
  }

  // Set report date
  const today = new Date().toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
  document.getElementById('report-date').textContent = today;
  document.getElementById('footer-date').textContent = today;

  // Update comparables count
  const hasProUpgrade = document.body.classList.contains('has-professional');
  const comparablesCount = hasProUpgrade ? '50+' : '15';
  document.getElementById('comparables-subtitle').textContent = `${comparablesCount} comparable properties identified`;

  // Update planning subtitle
  const planningRadius = hasProUpgrade ? '500m' : '200m';
  const planningYears = hasProUpgrade ? '5 years' : '2 years';
  document.getElementById('planning-subtitle').textContent = `Planning search: ${planningRadius} radius, ${planningYears}`;

  // Initialize components
  initializeComparablesTable();
  initializeMarketIntelligence();

  // Initialize map after a brief delay
  setTimeout(() => {
    initializeComparablesMap();
  }, 500);

  console.log('Professional report loaded');
});

// ================================================
// MARKET INTELLIGENCE
// ================================================

function initializeMarketIntelligence() {
  const marketData = professionalReportData.marketData;

  // Calculate and display market insights
  console.log('Market Intelligence loaded:', {
    valuation: `£${marketData.doorstep_valuation.toLocaleString()}`,
    market_avg: `£${marketData.market_average_ytd.toLocaleString()}`,
    position: `+${marketData.market_position_pct}% above market`,
    sample_size: marketData.sample_size_ytd,
    annual_change: `+${marketData.annual_change_pct}%`
  });

  // This data is already displayed in the HTML, but could be dynamically updated
  // if we implement real-time HPI API integration in the future
}

// ================================================
// COMPARABLES TABLE
// ================================================

function initializeComparablesTable() {
  const tbody = document.getElementById('comparablesTableBody');
  if (!tbody) return;

  const hasProUpgrade = document.body.classList.contains('has-professional');
  const comparablesToShow = hasProUpgrade ? professionalReportData.comparables : professionalReportData.comparables.slice(0, 6);

  comparablesToShow.forEach(comp => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${comp.address}</td>
      <td>${comp.distance.toFixed(2)} mi</td>
      <td>${comp.date}</td>
      <td>£${comp.price.toLocaleString()}</td>
      <td>£${comp.pricePerSqft}</td>
      <td>${comp.type}</td>
      <td>${comp.size}</td>
      <td>${comp.similarity}%</td>
    `;
    tbody.appendChild(row);
  });
}

// ================================================
// COMPARABLES MAP
// ================================================

function initializeComparablesMap() {
  const mapElement = document.getElementById('comparablesMap');
  if (!mapElement || !window.L) return;

  const subjectLat = 52.0640;
  const subjectLng = -0.8100;

  const map = L.map('comparablesMap', {
    scrollWheelZoom: false,
    dragging: true,
    zoomControl: true
  }).setView([subjectLat, subjectLng], 14);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 18
  }).addTo(map);

  // Subject property marker
  const subjectIcon = L.divIcon({
    html: '<div style="background: #DC2626; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></div>',
    className: '',
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });

  L.marker([subjectLat, subjectLng], { icon: subjectIcon })
    .addTo(map)
    .bindPopup('<strong>Subject Property</strong><br>8 Mccorquodale Road');

  // Comparables markers
  const hasProUpgrade = document.body.classList.contains('has-professional');
  const comparablesToShow = hasProUpgrade ? professionalReportData.comparables : professionalReportData.comparables.slice(0, 6);

  const compIcon = L.divIcon({
    html: '<div style="background: #0D9488; width: 10px; height: 10px; border-radius: 50%; border: 2px solid white;"></div>',
    className: '',
    iconSize: [14, 14],
    iconAnchor: [7, 7]
  });

  comparablesToShow.forEach(comp => {
    if (comp.lat && comp.lng) {
      L.marker([comp.lat, comp.lng], { icon: compIcon })
        .addTo(map)
        .bindPopup(`<strong>${comp.address}</strong><br>${comp.date}<br>£${comp.price.toLocaleString()}<br>Similarity: ${comp.similarity}%`);
    }
  });
}

// ================================================
// DATA EXPORT FUNCTIONS
// ================================================

function exportComparablesCSV() {
  const hasProUpgrade = document.body.classList.contains('has-professional');
  const comparables = hasProUpgrade ? professionalReportData.comparables : professionalReportData.comparables.slice(0, 6);

  let csv = 'Address,Distance,Date,Price,PricePerSqft,Type,Size,Similarity\n';
  comparables.forEach(comp => {
    csv += `"${comp.address}",${comp.distance},"${comp.date}",${comp.price},${comp.pricePerSqft},"${comp.type}","${comp.size}",${comp.similarity}\n`;
  });

  downloadCSV(csv, 'comparables.csv');
}

function exportPriceTrendsCSV() {
  let csv = 'Year,PropertyValue,AreaAverage\n';
  const years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"];
  const propValues = [145000, 152000, 168000, 175000, 189000, 195000, 202000, 218000, 210000, 198000, 202000];
  const areaValues = [138000, 145000, 158000, 168000, 182000, 188000, 195000, 210000, 203000, 192000, 196000];

  years.forEach((year, i) => {
    csv += `${year},${propValues[i]},${areaValues[i]}\n`;
  });
  downloadCSV(csv, 'price-trends.csv');
}

function exportFullDataCSV() {
  const marketData = professionalReportData.marketData;

  let csv = 'Type,Key,Value\n';
  csv += 'Property,Address,"8 Mccorquodale Road, Wolverton, Milton Keynes, MK12 5GP"\n';
  csv += 'Property,Type,Purpose Built Flat\n';
  csv += 'Property,Bedrooms,2\n';
  csv += 'Valuation,Estimate,202000\n';
  csv += 'Valuation,Confidence,78\n';
  csv += 'Valuation,Lower,182000\n';
  csv += 'Valuation,Upper,222000\n';
  csv += `Market,DoorstepValuation,${marketData.doorstep_valuation}\n`;
  csv += `Market,MK12_MarketAverage_YTD,${marketData.market_average_ytd}\n`;
  csv += `Market,MK12_Median_YTD,${marketData.market_median_ytd}\n`;
  csv += `Market,MK12_12MonthAverage,${marketData.market_12month_avg}\n`;
  csv += `Market,SampleSize_YTD,${marketData.sample_size_ytd}\n`;
  csv += `Market,SampleSize_12Month,${marketData.sample_size_12month}\n`;
  csv += `Market,PostcodeArea,"${marketData.area}"\n`;
  csv += `Market,AnnualChange_PCT,${marketData.annual_change_pct}\n`;
  csv += `Market,PositionVsMarket_PCT,${marketData.market_position_pct}\n`;
  downloadCSV(csv, 'full-report-data.csv');
}

function downloadCSV(csv, filename) {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

console.log('Professional Report loaded');
