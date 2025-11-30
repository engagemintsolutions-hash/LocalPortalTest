// PDF Report Generator for Doorstep Valuation Reports
// This module handles generation of RICS-style valuation reports as PDFs

/**
 * Generates a PDF valuation report based on property data
 * @param {Object} propertyData - Property valuation data
 * @returns {Promise<Blob>} PDF blob ready for download
 */
async function generateValuationPDF(propertyData) {
    // For production, integrate with jsPDF or similar library
    // This is the structure for the HTML-to-PDF conversion

    const reportHTML = generateReportHTML(propertyData);

    // Option 1: Client-side using jsPDF + html2canvas
    // Option 2: Server-side using puppeteer/headless chrome
    // Option 3: Use a PDF API service

    return reportHTML; // Return HTML for now, convert to PDF in production
}

/**
 * Generates the complete HTML report structure
 * @param {Object} data - Property and valuation data
 * @returns {string} Complete HTML report
 */
function generateReportHTML(data) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RICS Valuation Report - ${data.address}</title>
    ${getReportStyles()}
</head>
<body>
    <div class="container">
        ${generateLogoSection(data)}
        ${generateHeader(data)}
        ${generateExecutiveSummary(data)}
        ${generatePropertyDescription(data)}
        ${generateLocationContext(data)}
        ${generateComparableEvidence(data)}
        ${generateMethodology(data)}
        ${generateReconciliation(data)}
        ${generateRisks(data)}
        ${generateEnvironmental(data)}
        ${generateMarketConditions(data)}
        ${generateSources(data)}
        ${generateTerms(data)}
        ${generateAIDisclosure(data)}
        ${generateSignature(data)}
        ${generateFooter(data)}
    </div>
</body>
</html>`;
}

/**
 * Returns the complete CSS styles for the report
 */
function getReportStyles() {
    return `<style>
        @page {
            margin: 10mm;
            size: A4 portrait;
        }
        @media print {
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.5;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #FFFFFF;
        }
        .container {
            background-color: white;
            padding: 15px;
            margin: 0;
            width: 100%;
            box-sizing: border-box;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px 0;
            background: #FFFFFF;
            border-bottom: 3px solid #19727F;
        }
        .logo-container img {
            height: 120px;
            width: auto;
        }
        .header {
            text-align: center;
            border-bottom: 4px solid #19727F;
            padding-bottom: 20px;
            margin-bottom: 40px;
        }
        .header h1 {
            color: #19727F;
            font-size: 32px;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .header .subtitle {
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }
        .section {
            margin-bottom: 40px;
            page-break-inside: avoid;
        }
        .section-title {
            color: #19727F;
            font-size: 24px;
            border-bottom: 3px solid #EF6A68;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .subsection-title {
            color: #19727F;
            font-size: 18px;
            margin-top: 25px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .executive-summary {
            background-color: #F9F9F9;
            border-left: 5px solid #19727F;
            padding: 25px;
            margin-bottom: 30px;
        }
        .valuation-box {
            background: linear-gradient(135deg, #19727F 0%, #145A65 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 8px;
            margin: 30px 0;
            box-shadow: 0 5px 15px rgba(239, 106, 104, 0.3);
            border: 2px solid #EF6A68;
        }
        .valuation-box .amount {
            font-size: 48px;
            font-weight: bold;
            margin: 15px 0;
        }
        .valuation-box .label {
            font-size: 18px;
            opacity: 0.9;
        }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .info-card {
            background-color: #F9F9F9;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #19727F;
        }
        .info-card .label {
            font-weight: bold;
            color: #19727F;
            margin-bottom: 5px;
        }
        .info-card .value {
            font-size: 16px;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background-color: #19727F;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .badge-high {
            background-color: #70ad47;
            color: white;
        }
        ul {
            list-style-type: none;
            padding-left: 0;
        }
        ul li {
            padding: 8px 0 8px 30px;
            position: relative;
        }
        ul li:before {
            content: "▸";
            position: absolute;
            left: 10px;
            color: #19727F;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            padding-top: 30px;
            margin-top: 50px;
            border-top: 2px solid #EF6A68;
            color: #666;
            font-size: 14px;
        }
    </style>`;
}

/**
 * Generate logo section
 */
function generateLogoSection(data) {
    return `<div class="logo-container">
        <img src="doorstep-logo.png" alt="Doorstep">
    </div>`;
}

/**
 * Generate report header
 */
function generateHeader(data) {
    return `<div class="header">
        <h1>Property Valuation Report</h1>
        <div class="subtitle">Desktop Valuation - Instant Estimate</div>
    </div>`;
}

/**
 * Generate executive summary section
 */
function generateExecutiveSummary(data) {
    return `<div class="section executive-summary">
        <h2 class="section-title">Executive Summary</h2>

        <div class="info-grid">
            <div class="info-card">
                <div class="label">Property Address</div>
                <div class="value">${data.address}</div>
            </div>
            <div class="info-card">
                <div class="label">Valuation Date</div>
                <div class="value">${data.valuationDate || new Date().toLocaleDateString('en-GB')}</div>
            </div>
        </div>

        <div class="valuation-box">
            <div class="label">Estimated Market Value</div>
            <div class="amount">${formatCurrency(data.valuation)}</div>
            <div class="label">Range: ${formatCurrency(data.lowerRange)} - ${formatCurrency(data.upperRange)}</div>
        </div>

        <h3 class="subsection-title">Valuation Overview</h3>
        <p>This instant desktop valuation provides an estimated market value for the property at ${data.address}. The valuation is based on recent comparable sales in the local area, adjusted for property characteristics including type, size, and condition where known.</p>

        <p><strong>Important Notice:</strong> This is an automated desktop valuation generated instantly without physical inspection. For mortgage lending, legal transactions, or formal purposes, a full RICS Red Book valuation with physical inspection is required.</p>
    </div>`;
}

/**
 * Generate property description section
 */
function generatePropertyDescription(data) {
    return `<div class="section">
        <h2 class="section-title">Property Description</h2>

        <div class="info-grid">
            <div class="info-card">
                <div class="label">Address</div>
                <div class="value">${data.address}</div>
            </div>
            <div class="info-card">
                <div class="label">Property Type</div>
                <div class="value">${data.propertyType || 'House'}</div>
            </div>
            <div class="info-card">
                <div class="label">Estimated Bedrooms</div>
                <div class="value">${data.bedrooms || 'Not specified'}</div>
            </div>
            <div class="info-card">
                <div class="label">Tenure</div>
                <div class="value">Assumed Freehold (not verified)</div>
            </div>
        </div>

        <p><strong>Note:</strong> Property details are estimated based on available data sources. Physical characteristics have not been independently verified.</p>
    </div>`;
}

/**
 * Generate location context
 */
function generateLocationContext(data) {
    return `<div class="section">
        <h2 class="section-title">Location Context</h2>
        <p>The property is located in ${data.postcode || 'the specified postcode area'}. This instant valuation uses comparable sales from the surrounding area to estimate market value.</p>
    </div>`;
}

/**
 * Generate comparable evidence section
 */
function generateComparableEvidence(data) {
    return `<div class="section">
        <h2 class="section-title">Comparable Evidence</h2>
        <p>This valuation is based on analysis of recent property sales in the local area. Comparable properties were selected based on proximity, property type, size, and transaction recency.</p>

        <p><strong>Methodology:</strong> Distance-weighted comparable sales analysis with adjustments for property characteristics.</p>
    </div>`;
}

/**
 * Generate methodology section
 */
function generateMethodology(data) {
    return `<div class="section">
        <h2 class="section-title">Valuation Methodology</h2>

        <p><strong>Approach:</strong> Automated desktop valuation using comparative sales analysis</p>

        <h3 class="subsection-title">Data Sources</h3>
        <ul>
            <li>HM Land Registry Price Paid Data</li>
            <li>Energy Performance Certificate (EPC) Register</li>
            <li>Office for National Statistics demographic data</li>
            <li>Comparable sales within search radius</li>
        </ul>

        <h3 class="subsection-title">Limitations</h3>
        <ul>
            <li>No physical inspection undertaken</li>
            <li>Property condition not verified</li>
            <li>Desktop analysis only - not suitable for lending purposes</li>
            <li>Estimated property characteristics may differ from actual</li>
        </ul>
    </div>`;
}

/**
 * Generate reconciliation section
 */
function generateReconciliation(data) {
    return `<div class="section">
        <h2 class="section-title">Valuation Conclusion</h2>

        <div class="valuation-box">
            <div class="label">Final Estimated Value</div>
            <div class="amount">${formatCurrency(data.valuation)}</div>
            <div class="label">Confidence Range: ${formatCurrency(data.lowerRange)} - ${formatCurrency(data.upperRange)}</div>
        </div>

        <p>This estimated value is based on automated analysis of comparable sales data and should be used for indicative purposes only.</p>
    </div>`;
}

/**
 * Generate risks section
 */
function generateRisks(data) {
    return `<div class="section">
        <h2 class="section-title">Limitations & Risks</h2>

        <h3 class="subsection-title">Desktop Valuation Limitations</h3>
        <ul>
            <li>No physical inspection of the property has been undertaken</li>
            <li>Internal condition, fixtures, and fittings have not been assessed</li>
            <li>Structural defects, damp, or maintenance issues cannot be identified</li>
            <li>Property characteristics are estimated and not independently verified</li>
        </ul>

        <h3 class="subsection-title">Assumptions</h3>
        <ul>
            <li>Property is in reasonable condition for age and type</li>
            <li>No significant structural defects present</li>
            <li>All services are connected and functional</li>
            <li>Property has good marketable title</li>
        </ul>
    </div>`;
}

/**
 * Generate environmental section
 */
function generateEnvironmental(data) {
    return `<div class="section">
        <h2 class="section-title">Environmental Considerations</h2>
        <p>Environmental factors including energy efficiency, flood risk, and sustainability considerations may affect property value. A full environmental assessment has not been conducted for this instant valuation.</p>
    </div>`;
}

/**
 * Generate market conditions
 */
function generateMarketConditions(data) {
    return `<div class="section">
        <h2 class="section-title">Market Conditions</h2>
        <p>This valuation reflects current market conditions based on recent comparable sales. Market conditions can change rapidly and may affect the accuracy of this estimate.</p>
    </div>`;
}

/**
 * Generate sources section
 */
function generateSources(data) {
    return `<div class="section">
        <h2 class="section-title">Data Sources</h2>
        <ul>
            <li>HM Land Registry Price Paid Data</li>
            <li>Energy Performance Certificate Register</li>
            <li>Office for National Statistics</li>
            <li>Automated valuation algorithms</li>
        </ul>
    </div>`;
}

/**
 * Generate terms section
 */
function generateTerms(data) {
    return `<div class="section">
        <h2 class="section-title">Terms & Basis</h2>

        <div class="info-card">
            <div class="label">Valuation Purpose</div>
            <div class="value">Desktop estimate for general guidance only</div>
        </div>

        <div class="info-card" style="margin-top: 20px;">
            <div class="label">Basis of Value</div>
            <div class="value">Estimated Market Value based on comparable sales analysis</div>
        </div>

        <p style="margin-top: 20px;"><strong>Important:</strong> This instant valuation is not a formal RICS Red Book valuation and should not be relied upon for mortgage lending, legal transactions, or financial decisions.</p>
    </div>`;
}

/**
 * Generate AI disclosure
 */
function generateAIDisclosure(data) {
    return `<div class="section" style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 20px;">
        <h2 class="section-title">⚠️ Automated Valuation Disclosure</h2>

        <h3 class="subsection-title">Tool Description</h3>
        <p>This report was generated using Doorstep's automated valuation technology, combining machine learning models, comparable sales analysis, and geographic data to provide an instant property value estimate.</p>

        <h3 class="subsection-title">Limitations</h3>
        <ul>
            <li>No physical inspection undertaken</li>
            <li>Property characteristics estimated from available data</li>
            <li>Cannot assess condition, quality, or unique features</li>
            <li>Market conditions may change rapidly</li>
            <li>Not suitable for lending or legal purposes</li>
        </ul>

        <h3 class="subsection-title">Professional Oversight</h3>
        <p><strong>For formal valuations:</strong> Contact a RICS-qualified surveyor to conduct a full inspection and provide a Red Book compliant valuation report suitable for mortgage lending and legal transactions.</p>
    </div>`;
}

/**
 * Generate signature section
 */
function generateSignature(data) {
    return `<div class="section">
        <h2 class="section-title">Report Information</h2>
        <p><strong>Report Date:</strong> ${data.reportDate || new Date().toLocaleDateString('en-GB')}</p>
        <p><strong>Report Type:</strong> Automated Desktop Valuation</p>
        <p><strong>Generated by:</strong> Doorstep Automated Valuation System</p>
    </div>`;
}

/**
 * Generate footer
 */
function generateFooter(data) {
    return `<div class="footer">
        <p>Generated by Doorstep - AI-powered property valuations</p>
        <p>This is an automated estimate for guidance only</p>
        <p>© ${new Date().getFullYear()} Doorstep. All rights reserved.</p>
    </div>`;
}

/**
 * Format currency in GBP
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'GBP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateValuationPDF,
        generateReportHTML
    };
}
