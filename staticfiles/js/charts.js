/**
 * SURAT EXPRESS - INTERACTIVE SVG CHARTS ENGINE
 * 100% Zero external dependencies / Pure Vanilla JavaScript + SVG
 */

document.addEventListener('DOMContentLoaded', () => {
  const chartDataElem = document.getElementById('chart-data-payload');
  if (!chartDataElem) return;

  try {
    const chartData = JSON.parse(chartDataElem.textContent);
    renderDailyTrendChart('chart-daily-parcels', chartData.daily);
    renderStatusDonutChart('chart-status-distribution', chartData.status);
    renderDestinationBarChart('chart-destinations', chartData.destinations);
  } catch (e) {
    console.error("Failed to render SVG charts:", e);
  }
});

/**
 * 1. Daily Trend Bar Chart (SVG)
 */
function renderDailyTrendChart(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container || !data || !data.counts) return;

  const width = 600;
  const height = 220;
  const padding = { top: 25, right: 20, bottom: 35, left: 35 };

  const labels = data.labels || [];
  const counts = data.counts || [];
  const maxVal = Math.max(...counts, 5);

  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;
  const barWidth = Math.min(36, (chartW / labels.length) * 0.55);
  const gap = chartW / labels.length;

  let svgContent = `
    <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: auto; max-height: 250px; font-family: system-ui, sans-serif;">
      <defs>
        <linearGradient id="barGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#3b82f6" />
          <stop offset="100%" stop-color="#1d4ed8" />
        </linearGradient>
        <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.15" />
        </filter>
      </defs>
  `;

  // Horizontal Grid Lines
  const gridCount = 4;
  for (let i = 0; i <= gridCount; i++) {
    const y = padding.top + (chartH / gridCount) * i;
    const val = Math.round(maxVal - (maxVal / gridCount) * i);
    svgContent += `
      <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="${i === gridCount ? 'none' : '3 3'}" />
      <text x="${padding.left - 8}" y="${y + 4}" font-size="10" fill="#94a3b8" text-anchor="end" font-weight="600">${val}</text>
    `;
  }

  // Draw Bars and X Labels
  counts.forEach((cnt, idx) => {
    const barHeight = (cnt / maxVal) * chartH;
    const x = padding.left + (idx * gap) + (gap - barWidth) / 2;
    const y = padding.top + chartH - barHeight;

    svgContent += `
      <g class="svg-bar-group" style="cursor: pointer;">
        <title>${labels[idx]}: ${cnt} Parcels</title>
        <rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" rx="4" fill="url(#barGrad)" filter="url(#shadow)">
          <animate attributeName="height" from="0" to="${barHeight}" dur="0.6s" fill="freeze" />
          <animate attributeName="y" from="${padding.top + chartH}" to="${y}" dur="0.6s" fill="freeze" />
        </rect>
        <text x="${x + barWidth / 2}" y="${y - 6}" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">${cnt}</text>
        <text x="${x + barWidth / 2}" y="${height - 12}" font-size="11" font-weight="600" fill="#64748b" text-anchor="middle">${labels[idx]}</text>
      </g>
    `;
  });

  svgContent += `</svg>`;
  container.innerHTML = svgContent;
}

/**
 * 2. Status Distribution Donut Chart (SVG)
 */
function renderStatusDonutChart(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container || !data || !data.counts) return;

  const labels = data.labels || [];
  const counts = data.counts || [];
  const colors = data.colors || ['#3b82f6', '#8b5cf6', '#06b6d4', '#f59e0b', '#10b981'];

  const total = counts.reduce((a, b) => a + b, 0);

  if (total === 0) {
    container.innerHTML = `<div style="text-align: center; color: #94a3b8; padding: 2rem;">No parcel activity recorded yet</div>`;
    return;
  }

  const size = 180;
  const cx = size / 2;
  const cy = size / 2;
  const r = 65;
  const strokeWidth = 24;
  const circumference = 2 * Math.PI * r;

  let cumulativeOffset = 0;
  let circlesSvg = '';
  let legendHtml = '<div style="display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; min-width: 140px;">';

  counts.forEach((cnt, idx) => {
    if (cnt === 0) return;
    const ratio = cnt / total;
    const dashArray = `${ratio * circumference} ${circumference}`;
    const dashOffset = -cumulativeOffset;
    cumulativeOffset += ratio * circumference;
    const color = colors[idx % colors.length];

    circlesSvg += `
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}" stroke-width="${strokeWidth}"
        stroke-dasharray="${dashArray}" stroke-dashoffset="${dashOffset}"
        transform="rotate(-90 ${cx} ${cy})" style="transition: stroke-width 0.2s ease; cursor: pointer;">
        <title>${labels[idx]}: ${cnt} (${Math.round(ratio * 100)}%)</title>
      </circle>
    `;

    legendHtml += `
      <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.82rem;">
        <span style="display: flex; align-items: center; gap: 0.4rem; color: #475569; font-weight: 500;">
          <span style="width: 10px; height: 10px; border-radius: 50%; background: ${color}; display: inline-block;"></span>
          ${labels[idx]}
        </span>
        <strong style="color: #0f172a; margin-left: 0.5rem;">${cnt}</strong>
      </div>
    `;
  });

  legendHtml += '</div>';

  const chartHtml = `
    <div style="display: flex; align-items: center; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
      <div style="position: relative; width: ${size}px; height: ${size}px;">
        <svg viewBox="0 0 ${size} ${size}" style="width: 100%; height: 100%;">
          <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#f1f5f9" stroke-width="${strokeWidth}" />
          ${circlesSvg}
        </svg>
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none;">
          <span style="font-size: 1.35rem; font-weight: 800; color: #0f172a; line-height: 1;">${total}</span>
          <span style="font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 600; margin-top: 2px;">Parcels</span>
        </div>
      </div>
      ${legendHtml}
    </div>
  `;

  container.innerHTML = chartHtml;
}

/**
 * 3. Top Destination Hubs (Horizontal Bar Chart)
 */
function renderDestinationBarChart(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container || !data || !data.labels) return;

  const labels = data.labels || [];
  const counts = data.counts || [];
  const maxVal = Math.max(...counts, 1);

  if (labels.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: #94a3b8; padding: 2rem;">No destination data available</div>`;
    return;
  }

  let html = `<div style="display: flex; flex-direction: column; gap: 0.85rem; width: 100%;">`;

  labels.forEach((dest, idx) => {
    const cnt = counts[idx];
    const pct = Math.max(8, Math.round((cnt / maxVal) * 100));

    html += `
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem;">
          <span style="color: #1e293b;">${dest}</span>
          <span style="color: #2563eb; font-weight: 700;">${cnt} consignments</span>
        </div>
        <div style="background: #f1f5f9; border-radius: 9999px; height: 10px; overflow: hidden; width: 100%;">
          <div style="background: linear-gradient(90deg, #3b82f6, #06b6d4); height: 100%; width: ${pct}%; border-radius: 9999px; transition: width 0.8s ease;"></div>
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
}
