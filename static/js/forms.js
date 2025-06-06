// Form handling and validation
document.addEventListener("DOMContentLoaded", () => {
    initializeForms()
})

function initializeForms() {
    // Initialize form validation
    initializeFormValidation()

    // Initialize date pickers
    initializeDatePickers()

    // Initialize auto-complete
    initializeAutoComplete()

    // Initialize form submission
    initializeFormSubmission()

    // Initialize dynamic forms
    initializeDynamicForms()
}

function initializeFormValidation() {
    const forms = document.querySelectorAll("form[data-validate]")
    forms.forEach((form) => {
        form.addEventListener("submit", function (e) {
            if (!validateForm(this)) {
                e.preventDefault()
            }
        })

        // Real-time validation
        const inputs = form.querySelectorAll("input, select, textarea")
        inputs.forEach((input) => {
            input.addEventListener("blur", function () {
                validateField(this)
            })
        })
    })
}

function validateForm(form) {
    let isValid = true
    const inputs = form.querySelectorAll("input[required], select[required], textarea[required]")

    inputs.forEach((input) => {
        if (!validateField(input)) {
            isValid = false
        }
    })

    return isValid
}

function validateField(field) {
    const value = field.value.trim()
    const type = field.type
    let isValid = true
    let message = ""

    // Required field validation
    if (field.hasAttribute("required") && !value) {
        isValid = false
        message = "This field is required"
    }

    // Email validation
    else if (type === "email" && value && !isValidEmail(value)) {
        isValid = false
        message = "Please enter a valid email address"
    }

    // Phone validation
    else if (field.name.includes("phone") && value && !isValidPhone(value)) {
        isValid = false
        message = "Please enter a valid phone number"
    }

    // Date validation
    else if (type === "date" && value) {
        if (field.name.includes("check_in") && new Date(value) < new Date()) {
            isValid = false
            message = "Check-in date cannot be in the past"
        } else if (field.name.includes("check_out")) {
            const checkInField = field.form.querySelector('input[name*="check_in"]')
            if (checkInField && new Date(value) <= new Date(checkInField.value)) {
                isValid = false
                message = "Check-out date must be after check-in date"
            }
        }
    }

    // Number validation
    else if (type === "number" && value) {
        const min = field.getAttribute("min")
        const max = field.getAttribute("max")

        if (min && Number.parseFloat(value) < Number.parseFloat(min)) {
            isValid = false
            message = `Value must be at least ${min}`
        } else if (max && Number.parseFloat(value) > Number.parseFloat(max)) {
            isValid = false
            message = `Value must be at most ${max}`
        }
    }

    // Display validation result
    showFieldValidation(field, isValid, message)
    return isValid
}

function showFieldValidation(field, isValid, message) {
    // Remove existing validation
    const existingError = field.parentNode.querySelector(".field-error")
    if (existingError) {
        existingError.remove()
    }

    // Update field styling
    field.classList.remove("border-red-500", "border-green-500")

    if (!isValid) {
        field.classList.add("border-red-500")

        // Add error message
        const errorDiv = document.createElement("div")
        errorDiv.className = "field-error text-red-500 text-sm mt-1"
        errorDiv.textContent = message
        field.parentNode.appendChild(errorDiv)
    } else if (field.value.trim()) {
        field.classList.add("border-green-500")
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
}

function isValidPhone(phone) {
    const phoneRegex = /^[+]?[1-9][\d]{0,15}$/
    return phoneRegex.test(phone.replace(/[\s\-$$$$]/g, ""))
}

function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]')
    dateInputs.forEach((input) => {
        // Set min date to today for future dates
        if (input.name.includes("check_in") || input.name.includes("arrival")) {
            input.min = new Date().toISOString().split("T")[0]
        }

        // Auto-update dependent date fields
        input.addEventListener("change", function () {
            updateDependentDates(this)
        })
    })
}

function updateDependentDates(dateInput) {
    const form = dateInput.form

    if (dateInput.name.includes("check_in")) {
        const checkOutInput = form.querySelector('input[name*="check_out"]')
        if (checkOutInput) {
            const checkInDate = new Date(dateInput.value)
            checkInDate.setDate(checkInDate.getDate() + 1)
            checkOutInput.min = checkInDate.toISOString().split("T")[0]

            // Clear check-out if it's before new check-in
            if (checkOutInput.value && new Date(checkOutInput.value) <= new Date(dateInput.value)) {
                checkOutInput.value = ""
            }
        }
    }
}

function initializeAutoComplete() {
    const autoCompleteInputs = document.querySelectorAll("[data-autocomplete]")
    autoCompleteInputs.forEach((input) => {
        let timeout
        input.addEventListener("input", function () {
            clearTimeout(timeout)
            timeout = setTimeout(() => {
                performAutoComplete(this)
            }, 300)
        })
    })
}

function performAutoComplete(input) {
    const query = input.value.trim()
    if (query.length < 2) return

    const endpoint = input.getAttribute("data-autocomplete")

    fetch(`${endpoint}?q=${encodeURIComponent(query)}`, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            showAutoCompleteResults(input, data)
        })
        .catch((error) => {
            console.error("Autocomplete failed:", error)
        })
}

function showAutoCompleteResults(input, results) {
    // Remove existing results
    const existingResults = document.getElementById("autocomplete-results")
    if (existingResults) {
        existingResults.remove()
    }

    if (results.length === 0) return

    // Create results container
    const resultsDiv = document.createElement("div")
    resultsDiv.id = "autocomplete-results"
    resultsDiv.className =
        "absolute z-50 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"

    results.forEach((result) => {
        const resultItem = document.createElement("div")
        resultItem.className = "px-4 py-2 hover:bg-gray-100 cursor-pointer"
        resultItem.textContent = result.label
        resultItem.addEventListener("click", () => {
            input.value = result.value
            input.setAttribute("data-selected-id", result.id)
            resultsDiv.remove()
        })
        resultsDiv.appendChild(resultItem)
    })

    // Position results
    input.parentNode.style.position = "relative"
    input.parentNode.appendChild(resultsDiv)

    // Close results when clicking outside
    document.addEventListener(
        "click",
        (e) => {
            if (!input.contains(e.target) && !resultsDiv.contains(e.target)) {
                resultsDiv.remove()
            }
        },
        { once: true },
    )
}

function initializeFormSubmission() {
    const ajaxForms = document.querySelectorAll("form[data-ajax]")
    ajaxForms.forEach((form) => {
        form.addEventListener("submit", function (e) {
            e.preventDefault()
            submitFormAjax(this)
        })
    })
}

function submitFormAjax(form) {
    const formData = new FormData(form)
    const submitButton = form.querySelector('button[type="submit"]')
    const originalText = submitButton.textContent

    // Show loading state
    submitButton.disabled = true
    submitButton.textContent = "Submitting..."

    fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then((response) => {
            if (response.ok) {
                return response.json()
            }
            throw new Error("Form submission failed")
        })
        .then((data) => {
            if (data.success) {
                showToast(data.message || "Form submitted successfully", "success")
                if (data.redirect) {
                    window.location.href = data.redirect
                } else {
                    form.reset()
                }
            } else {
                showFormErrors(form, data.errors)
            }
        })
        .catch((error) => {
            console.error("Form submission error:", error)
            showToast("An error occurred while submitting the form", "error")
        })
        .finally(() => {
            // Restore button state
            submitButton.disabled = false
            submitButton.textContent = originalText
        })
}

function showFormErrors(form, errors) {
    // Clear existing errors
    form.querySelectorAll(".field-error").forEach((error) => error.remove())

    // Show new errors
    Object.keys(errors).forEach((fieldName) => {
        const field = form.querySelector(`[name="${fieldName}"]`)
        if (field) {
            showFieldValidation(field, false, errors[fieldName][0])
        }
    })
}

function initializeDynamicForms() {
    // Add/remove form sections
    const addButtons = document.querySelectorAll("[data-add-form]")
    addButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const targetId = this.getAttribute("data-add-form")
            addFormSection(targetId)
        })
    })

    // Remove form sections
    document.addEventListener("click", (e) => {
        if (e.target.matches("[data-remove-form]")) {
            e.target.closest(".form-section").remove()
        }
    })
}

function addFormSection(templateId) {
    const template = document.getElementById(templateId)
    if (!template) return

    const container = template.parentNode
    const newSection = template.cloneNode(true)

    // Update field names and IDs
    const fields = newSection.querySelectorAll("input, select, textarea")
    const index = container.children.length

    fields.forEach((field) => {
        if (field.name) {
            field.name = field.name.replace(/\d+/, index)
        }
        if (field.id) {
            field.id = field.id.replace(/\d+/, index)
        }
        field.value = ""
    })

    container.appendChild(newSection)
}
