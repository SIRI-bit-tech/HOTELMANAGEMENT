// Main JavaScript functionality for HotelPMS
document.addEventListener("DOMContentLoaded", () => {
    // Initialize tooltips
    initializeTooltips()

    // Initialize modals
    initializeModals()

    // Initialize date pickers
    initializeDatePickers()

    // Initialize search functionality
    initializeSearch()
})

// Toast notification system
function showToast(message, type = "info", duration = 5000) {
    const toast = document.createElement("div")
    toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full opacity-0 ${getToastClasses(type)}`

    toast.innerHTML = `
          <div class="flex items-center">
              <div class="flex-shrink-0">
                  ${getToastIcon(type)}
              </div>
              <div class="ml-3">
                  <p class="text-sm font-medium">${message}</p>
              </div>
              <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-gray-400 hover:text-gray-600">
                  <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                  </svg>
              </button>
          </div>
      `

    document.body.appendChild(toast)

    // Animate in
    setTimeout(() => {
        toast.classList.remove("translate-x-full", "opacity-0")
    }, 100)

    // Auto remove
    setTimeout(() => {
        toast.classList.add("translate-x-full", "opacity-0")
        setTimeout(() => toast.remove(), 300)
    }, duration)
}

function getToastClasses(type) {
    const classes = {
        success: "bg-green-50 border-l-4 border-green-400 text-green-700",
        error: "bg-red-50 border-l-4 border-red-400 text-red-700",
        warning: "bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700",
        info: "bg-blue-50 border-l-4 border-blue-400 text-blue-700",
    }
    return classes[type] || classes.info
}

function getToastIcon(type) {
    const icons = {
        success:
            '<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
        error:
            '<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
        warning:
            '<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
        info: '<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>',
    }
    return icons[type] || icons.info
}

// Modal functionality
function initializeModals() {
    const modalTriggers = document.querySelectorAll("[data-modal-target]")
    modalTriggers.forEach((trigger) => {
        trigger.addEventListener("click", function () {
            const modalId = this.getAttribute("data-modal-target")
            const modal = document.getElementById(modalId)
            if (modal) {
                showModal(modal)
            }
        })
    })

    const modalCloses = document.querySelectorAll("[data-modal-close]")
    modalCloses.forEach((close) => {
        close.addEventListener("click", function () {
            const modal = this.closest(".modal")
            if (modal) {
                hideModal(modal)
            }
        })
    })
}

function showModal(modal) {
    modal.classList.remove("hidden")
    modal.classList.add("flex")
    document.body.style.overflow = "hidden"
}

function hideModal(modal) {
    modal.classList.add("hidden")
    modal.classList.remove("flex")
    document.body.style.overflow = "auto"
}

// Date picker initialization
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]')
    dateInputs.forEach((input) => {
        // Set min date to today for check-in dates
        if (input.name.includes("check_in") || input.name.includes("date")) {
            input.min = new Date().toISOString().split("T")[0]
        }
    })
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll("[data-search]")
    searchInputs.forEach((input) => {
        let timeout
        input.addEventListener("input", function () {
            clearTimeout(timeout)
            timeout = setTimeout(() => {
                performSearch(this)
            }, 300)
        })
    })
}

function performSearch(input) {
    const searchTerm = input.value.toLowerCase()
    const targetSelector = input.getAttribute("data-search")
    const targets = document.querySelectorAll(targetSelector)

    targets.forEach((target) => {
        const text = target.textContent.toLowerCase()
        if (text.includes(searchTerm)) {
            target.style.display = ""
        } else {
            target.style.display = "none"
        }
    })
}

// Tooltip initialization
function initializeTooltips() {
    const tooltipTriggers = document.querySelectorAll("[data-tooltip]")
    tooltipTriggers.forEach((trigger) => {
        trigger.addEventListener("mouseenter", showTooltip)
        trigger.addEventListener("mouseleave", hideTooltip)
    })
}

function showTooltip(event) {
    const text = event.target.getAttribute("data-tooltip")
    const tooltip = document.createElement("div")
    tooltip.className = "absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded shadow-lg"
    tooltip.textContent = text
    tooltip.id = "tooltip"

    document.body.appendChild(tooltip)

    const rect = event.target.getBoundingClientRect()
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + "px"
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + "px"
}

function hideTooltip() {
    const tooltip = document.getElementById("tooltip")
    if (tooltip) {
        tooltip.remove()
    }
}

// Print functionality
function printElement(elementId) {
    const element = document.getElementById(elementId)
    if (!element) return

    const printWindow = window.open("", "_blank")
    printWindow.document.write(`
          <html>
              <head>
                  <title>Print</title>
                  <link href="https://cdn.tailwindcss.com" rel="stylesheet">
                  <style>
                      @media print {
                          body { margin: 0; }
                          .no-print { display: none !important; }
                      }
                  </style>
              </head>
              <body>
                  ${element.innerHTML}
              </body>
          </html>
      `)
    printWindow.document.close()
    printWindow.print()
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback()
    }
}

// Auto-save functionality
function autoSave(formId, interval = 30000) {
    const form = document.getElementById(formId)
    if (!form) return

    setInterval(() => {
        const formData = new FormData(form)
        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        }).then((response) => {
            if (response.ok) {
                showToast("Draft saved", "success", 2000)
            }
        })
    }, interval)
}
