// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set minimum dates for date inputs
    setMinDates();
    
    // Initialize date dependency (return date must be after pickup date)
    setupDateDependency();
    
    // Add event listeners to search form inputs
    setupSearchFormListeners();
    
    // Setup location copy functionality
    setupLocationCopy();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

/**
 * Set minimum dates for date inputs to current date
 */
function setMinDates() {
    const today = new Date();
    const todayFormatted = today.toISOString().split('T')[0];
    
    // Format date for display (e.g., "Fri 04 Apr")
    const formatDateForDisplay = (date) => {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${days[date.getDay()]} ${String(date.getDate()).padStart(2, '0')} ${months[date.getMonth()]}`;
    };
    
    // Get all date inputs for pickup
    const pickupDateInputs = document.querySelectorAll('input[name="pickup_date"]');
    pickupDateInputs.forEach(input => {
        if (input.type === 'date') {
            input.min = todayFormatted;
            if (!input.value) {
                input.value = todayFormatted;
            }
        } else {
            // For text inputs (new design)
            if (!input.value) {
                input.value = formatDateForDisplay(today);
                // Store actual date value as data attribute for form submission
                input.dataset.actualDate = todayFormatted;
            }
        }
    });
    
    // Get all date inputs for return
    const returnDateInputs = document.querySelectorAll('input[name="return_date"]');
    
    // Set minimum return date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(today.getDate() + 1);
    const tomorrowFormatted = tomorrow.toISOString().split('T')[0];
    
    returnDateInputs.forEach(input => {
        if (input.type === 'date') {
            input.min = todayFormatted;
            if (!input.value) {
                input.value = tomorrowFormatted;
            }
        } else {
            // For text inputs (new design)
            if (!input.value) {
                input.value = formatDateForDisplay(tomorrow);
                // Store actual date value as data attribute for form submission
                input.dataset.actualDate = tomorrowFormatted;
            }
        }
    });
}

/**
 * Ensure return date is always after pickup date
 */
function setupDateDependency() {
    const pickupDateInputs = document.querySelectorAll('input[name="pickup_date"]');
    
    pickupDateInputs.forEach(pickupInput => {
        pickupInput.addEventListener('change', function() {
            const pickupForm = this.closest('form');
            if (!pickupForm) return;
            
            const returnInput = pickupForm.querySelector('input[name="return_date"]');
            if (!returnInput) return;
            
            const pickupDate = new Date(this.value);
            const returnDate = new Date(returnInput.value);
            
            // If return date is before or same as pickup date, set it to the next day
            if (returnDate <= pickupDate) {
                const nextDay = new Date(pickupDate);
                nextDay.setDate(pickupDate.getDate() + 1);
                returnInput.value = nextDay.toISOString().split('T')[0];
            }
            
            // Update the min attribute of the return date input
            returnInput.min = this.value;
        });
    });
}

/**
 * Add event listeners to the search form inputs
 */
function setupSearchFormListeners() {
    const searchForms = document.querySelectorAll('.search-form');
    
    searchForms.forEach(form => {
        // Add input validation
        const ageInput = form.querySelector('input[name="age"]');
        if (ageInput) {
            ageInput.addEventListener('input', function() {
                const value = parseInt(this.value);
                if (value < 18) {
                    this.setCustomValidity('Driver must be at least 18 years old');
                } else if (value > 99) {
                    this.setCustomValidity('Please enter a valid age');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
        
        // Handle form submission for new design
        form.addEventListener('submit', function(e) {
            // Handle text-based date inputs (convert from display format to YYYY-MM-DD)
            const pickupDateInput = form.querySelector('input[name="pickup_date"]');
            const returnDateInput = form.querySelector('input[name="return_date"]');
            
            // Only process if these are not date type inputs
            if (pickupDateInput && pickupDateInput.type !== 'date') {
                if (pickupDateInput.dataset.actualDate) {
                    // Create a hidden input with the actual date
                    const hiddenPickupDate = document.createElement('input');
                    hiddenPickupDate.type = 'hidden';
                    hiddenPickupDate.name = 'pickup_date_actual';
                    hiddenPickupDate.value = pickupDateInput.dataset.actualDate;
                    form.appendChild(hiddenPickupDate);
                }
            }
            
            if (returnDateInput && returnDateInput.type !== 'date') {
                if (returnDateInput.dataset.actualDate) {
                    // Create a hidden input with the actual date
                    const hiddenReturnDate = document.createElement('input');
                    hiddenReturnDate.type = 'hidden';
                    hiddenReturnDate.name = 'return_date_actual';
                    hiddenReturnDate.value = returnDateInput.dataset.actualDate;
                    form.appendChild(hiddenReturnDate);
                }
            }
            
            // Get time values
            const pickupTimeSelect = form.querySelector('select[name="pickup_time"]');
            const returnTimeSelect = form.querySelector('select[name="return_time"]');
            
            if (pickupTimeSelect) {
                const hiddenPickupTime = document.createElement('input');
                hiddenPickupTime.type = 'hidden';
                hiddenPickupTime.name = 'pickup_time';
                hiddenPickupTime.value = pickupTimeSelect.value;
                form.appendChild(hiddenPickupTime);
            }
            
            if (returnTimeSelect) {
                const hiddenReturnTime = document.createElement('input');
                hiddenReturnTime.type = 'hidden';
                hiddenReturnTime.name = 'return_time';
                hiddenReturnTime.value = returnTimeSelect.value;
                form.appendChild(hiddenReturnTime);
            }
        });
    });
}

/**
 * Copy pickup location to drop-off location if they're empty
 * Works with both input fields and select elements
 */
function setupLocationCopy() {
    // Handle input fields
    const pickupLocationInputs = document.querySelectorAll('input[name="pickup_location"]');
    pickupLocationInputs.forEach(pickupInput => {
        pickupInput.addEventListener('blur', function() {
            const form = this.closest('form');
            if (!form) return;
            
            const dropoffInput = form.querySelector('input[name="dropoff_location"]');
            if (!dropoffInput || dropoffInput.value.trim() !== '') return;
            
            // Copy pickup location to drop-off location if drop-off is empty
            dropoffInput.value = this.value;
        });
    });
    
    // Handle select elements (for new design)
    const pickupLocationSelects = document.querySelectorAll('select[name="pickup_location"]');
    pickupLocationSelects.forEach(pickupSelect => {
        pickupSelect.addEventListener('change', function() {
            const form = this.closest('form');
            if (!form) return;
            
            // In new design, we don't have a separate dropoff location selector
            // But we'll add a hidden input to store that the dropoff is same as pickup
            
            // Check if hidden input exists, if not create it
            let hiddenDropoff = form.querySelector('input[name="dropoff_location"]');
            if (!hiddenDropoff) {
                hiddenDropoff = document.createElement('input');
                hiddenDropoff.type = 'hidden';
                hiddenDropoff.name = 'dropoff_location';
                form.appendChild(hiddenDropoff);
            }
            
            // Set dropoff location same as pickup
            hiddenDropoff.value = this.value;
        });
    });
}

/**
 * Calculate rental duration and update price
 * @param {HTMLElement} pickupDateEl - The pickup date input element
 * @param {HTMLElement} returnDateEl - The return date input element
 * @param {number} dailyRate - The daily rate for the car
 */
function updateRentalPrice(pickupDateEl, returnDateEl, dailyRate) {
    if (!pickupDateEl || !returnDateEl || !dailyRate) return;
    
    const pickupDate = new Date(pickupDateEl.value);
    const returnDate = new Date(returnDateEl.value);
    
    if (isNaN(pickupDate.getTime()) || isNaN(returnDate.getTime())) return;
    
    // Calculate difference in days
    const timeDiff = returnDate.getTime() - pickupDate.getTime();
    const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
    
    // Ensure at least 1 day
    const rentalDays = Math.max(1, daysDiff);
    
    // Calculate total cost
    const totalCost = dailyRate * rentalDays;
    
    // Update the UI if price summary element exists
    const priceSummaryEl = document.querySelector('.price-summary');
    if (priceSummaryEl) {
        priceSummaryEl.innerHTML = `
            <div class="d-flex justify-content-between mb-2">
                <span>Base Rate ($${dailyRate.toFixed(2)} x ${rentalDays} days)</span>
                <span>$${totalCost.toFixed(2)}</span>
            </div>
            <div class="d-flex justify-content-between pt-2 border-top">
                <strong>Total</strong>
                <strong>$${totalCost.toFixed(2)}</strong>
            </div>
        `;
    }
    
    return totalCost;
}
