/**
 * SURAT EXPRESS - TRANSPORT & PARCEL MANAGEMENT SYSTEM
 * Vanilla JavaScript UI Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initParcelFormLookups();
  initDistributionFormLookups();
  initModalHandlers();
  initAlertAutoDismiss();
  initClientSideTableSearch();
  initCopyButtons();
  initSamplePillAutoFill();
  initInquiryWhatsAppAction();
});

/**
 * 1. Mobile Navigation & Sidebar Toggle
 */
function initMobileNav() {
  const toggleBtn = document.querySelector('.menu-toggle-btn');
  const sidebar = document.querySelector('.admin-sidebar');
  const navLinks = document.querySelector('.nav-links');

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      if (sidebar) {
        sidebar.classList.toggle('open');
      }
      if (navLinks) {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
      }
    });
  }

  // Close sidebar on click outside on mobile
  document.addEventListener('click', (e) => {
    if (sidebar && sidebar.classList.contains('open')) {
      if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    }
  });
}

/**
 * 2. Parcel Form Dynamic Party & Vehicle Lookups
 */
function initParcelFormLookups() {
  const partySelect = document.getElementById('id_party');
  const privateMarkInput = document.getElementById('id_private_mark');
  const vehicleSelect = document.getElementById('id_vehicle');
  const vehicleNumberInput = document.querySelector('input[name="vehicle_number_text"]');
  const driverNameInput = document.querySelector('input[name="driver_name_text"]');
  const driverContactInput = document.querySelector('input[name="driver_contact_text"]');

  // Lookup data embedded from Django context
  let partiesData = {};
  let vehiclesData = {};

  const partiesDataElem = document.getElementById('parties-json-data');
  if (partiesDataElem) {
    try {
      partiesData = JSON.parse(partiesDataElem.textContent);
    } catch (err) {
      console.warn("Could not parse parties data JSON", err);
    }
  }

  const vehiclesDataElem = document.getElementById('vehicles-json-data');
  if (vehiclesDataElem) {
    try {
      vehiclesData = JSON.parse(vehiclesDataElem.textContent);
    } catch (err) {
      console.warn("Could not parse vehicles data JSON", err);
    }
  }

  // When Party dropdown changes, auto-populate Private Mark
  if (partySelect && privateMarkInput) {
    partySelect.addEventListener('change', () => {
      const selectedId = partySelect.value;
      if (selectedId && partiesData[selectedId]) {
        const party = partiesData[selectedId];
        privateMarkInput.value = party.private_mark || '';
        
        // Also auto fill receiver/party name text if empty
        const partyNameInput = document.querySelector('input[name="party_name_text"]');
        if (partyNameInput && !partyNameInput.value) {
          partyNameInput.value = party.name || '';
        }
      }
    });
  }

  // When Vehicle dropdown changes, auto-populate driver info
  if (vehicleSelect) {
    vehicleSelect.addEventListener('change', () => {
      const selectedId = vehicleSelect.value;
      if (selectedId && vehiclesData[selectedId]) {
        const veh = vehiclesData[selectedId];
        if (vehicleNumberInput) vehicleNumberInput.value = veh.vehicle_number || '';
        if (driverNameInput) driverNameInput.value = veh.driver_name || '';
        if (driverContactInput) driverContactInput.value = veh.driver_contact || '';
      }
    });
  }
}

/**
 * 3. Local Distribution Tempo Lookups
 */
function initDistributionFormLookups() {
  const tempoSelect = document.getElementById('id_distribution_tempo');
  const driverNameInput = document.getElementById('id_tempo_driver');
  const driverContactInput = document.getElementById('id_tempo_driver_contact');

  let temposData = {};
  const temposDataElem = document.getElementById('tempos-json-data');
  if (temposDataElem) {
    try {
      temposData = JSON.parse(temposDataElem.textContent);
    } catch (err) {
      console.warn("Could not parse tempos data JSON", err);
    }
  }

  if (tempoSelect) {
    tempoSelect.addEventListener('change', () => {
      const selectedId = tempoSelect.value;
      if (selectedId && temposData[selectedId]) {
        const tempo = temposData[selectedId];
        if (driverNameInput) driverNameInput.value = tempo.driver_name || '';
        if (driverContactInput) driverContactInput.value = tempo.driver_contact || '';
      }
    });
  }
}

/**
 * 4. Modal Open/Close Controls
 */
function initModalHandlers() {
  // Modal triggers with data-modal-target
  const triggers = document.querySelectorAll('[data-modal-target]');
  triggers.forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = trigger.getAttribute('data-modal-target');
      const modal = document.getElementById(targetId);
      if (modal) {
        modal.classList.add('active');
      }
    });
  });

  // Close buttons
  const closeButtons = document.querySelectorAll('.modal-close, [data-modal-close]');
  closeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-backdrop');
      if (modal) {
        modal.classList.remove('active');
      }
    });
  });

  // Close on clicking backdrop outside modal box
  const backdrops = document.querySelectorAll('.modal-backdrop');
  backdrops.forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('active');
      }
    });
  });
}

/**
 * 5. Auto-dismiss Flash Alerts
 */
function initAlertAutoDismiss() {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 4500);
  });
}

/**
 * 6. Fast Client-side Table Search & Instant Filtering
 */
function initClientSideTableSearch() {
  const searchInput = document.getElementById('table-quick-search');
  if (!searchInput) return;

  const targetTable = document.querySelector('.data-table tbody');
  if (!targetTable) return;

  searchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase().trim();
    const rows = targetTable.querySelectorAll('tr');

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      if (text.includes(term)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  });
}

/**
 * 7. Copy Consignment Number to Clipboard
 */
function initCopyButtons() {
  const copyButtons = document.querySelectorAll('.btn-copy-lr');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const textToCopy = btn.getAttribute('data-copy') || btn.textContent.trim();
      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = '✓ Copied!';
        btn.style.color = '#10b981';
        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.style.color = '';
        }, 2000);
      });
    });
  });
}

/**
 * 8. Sample Tracking Pills Auto-Fill
 */
function initSamplePillAutoFill() {
  const pills = document.querySelectorAll('.sample-pill');
  const trackInputs = document.querySelectorAll('input[name="q"], #hero-track-input');

  pills.forEach(pill => {
    pill.addEventListener('click', (e) => {
      e.preventDefault();
      const lrCode = pill.getAttribute('data-track') || pill.textContent.trim();
      
      trackInputs.forEach(input => {
        input.value = lrCode;
        input.focus();
        input.dispatchEvent(new Event('input', { bubbles: true }));
      });

      // Visual click feedback
      const originalText = pill.textContent;
      pill.classList.add('active-pill');
      pill.textContent = `✓ ${lrCode}`;
      setTimeout(() => {
        pill.classList.remove('active-pill');
        pill.textContent = originalText;
      }, 1200);
    });
  });
}

/**
 * 9. Booking Inquiry Dynamic Quotation & WhatsApp Action
 */
function initInquiryWhatsAppAction() {
  const inquiryForm = document.getElementById('booking-inquiry-form');
  const packagesInput = document.getElementById('inquiry-packages');
  const quotationInput = document.getElementById('inquiry-quotation');
  const quotationDisplay = document.getElementById('quotation-display');

  // Dynamic estimate calculation
  function updateEstimate() {
    if (!packagesInput) return;
    const pkgs = parseInt(packagesInput.value, 10) || 1;
    // Standard Surat -> Ahmedabad average freight approx ₹250 to ₹350 per textile bale
    const minEst = pkgs * 250;
    const maxEst = pkgs * 350;
    const formattedQuote = `₹${minEst.toLocaleString('en-IN')} - ₹${maxEst.toLocaleString('en-IN')}`;

    if (quotationDisplay) {
      quotationDisplay.textContent = formattedQuote;
    }
    if (quotationInput && (!quotationInput.value || quotationInput.dataset.auto === 'true')) {
      quotationInput.value = formattedQuote;
      quotationInput.dataset.auto = 'true';
    }
  }

  if (packagesInput) {
    packagesInput.addEventListener('input', updateEstimate);
    packagesInput.addEventListener('change', updateEstimate);
    updateEstimate();
  }

  if (inquiryForm) {
    inquiryForm.addEventListener('submit', (e) => {
      const name = (inquiryForm.querySelector('input[name="name"]')?.value || '').trim();
      const phone = (inquiryForm.querySelector('input[name="phone"]')?.value || '').trim();
      const destination = (inquiryForm.querySelector('input[name="destination"]')?.value || 'Ahmedabad').trim();
      const message = (inquiryForm.querySelector('textarea[name="message"]')?.value || '').trim();
      const quotation = (quotationInput?.value || quotationDisplay?.textContent || '₹250 - ₹350 / Bale').trim();

      // Build formatted WhatsApp message for Veer Transport desk
      const whatsappMsg = 
        `*New Booking Inquiry - Veer Transport*\n` +
        `-----------------------------------------\n` +
        `🛣️ *Route:* Surat (Saroli) ➔ Ahmedabad\n` +
        `👤 *Party / Name:* ${name}\n` +
        `📞 *Phone:* ${phone}\n` +
        `📍 *Delivery Area:* ${destination}\n` +
        `📦 *Cargo Details:* ${message}\n` +
        `💰 *Estimated Quotation:* ${quotation}\n` +
        `-----------------------------------------\n` +
        `Hello Veer Transport team, please confirm booking availability and pickup schedule from Saroli godown.`;

      const whatsappUrl = `https://wa.me/919825012345?text=${encodeURIComponent(whatsappMsg)}`;

      // Open WhatsApp chat in a new window/tab
      window.open(whatsappUrl, '_blank');
    });
  }
}

