// Dashboard specific functionality
document.addEventListener("DOMContentLoaded", () => {
    initializeDashboard()
    startRealTimeUpdates()
})

function initializeDashboard() {
    // Initialize charts
    initializeOccupancyChart()
    initializeRevenueChart()

    // Initialize real-time counters
    animateCounters()

    // Initialize quick actions
    initializeQuickActions()
}

function initializeOccupancyChart() {
    const ctx = document.getElementById("occupancyChart")
    if (!ctx) return

    // Simple canvas-based chart
    const canvas = ctx.getContext("2d")
    const data = JSON.parse(ctx.dataset.chartData || "[]")

    drawPieChart(canvas, data)
}

function drawPieChart(ctx, data) {
    const centerX = ctx.canvas.width / 2
    const centerY = ctx.canvas.height / 2
    const radius = Math.min(centerX, centerY) - 10

    let currentAngle = 0
    const colors = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444"]

    data.forEach((item, index) => {
        const sliceAngle = (item.value / 100) * 2 * Math.PI

        ctx.beginPath()
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
        ctx.lineTo(centerX, centerY)
        ctx.fillStyle = colors[index % colors.length]
        ctx.fill()

        currentAngle += sliceAngle
    })
}

function animateCounters() {
    const counters = document.querySelectorAll("[data-counter]")
    counters.forEach((counter) => {
        const target = Number.parseInt(counter.getAttribute("data-counter"))
        const duration = 2000
        const increment = target / (duration / 16)
        let current = 0

        const timer = setInterval(() => {
            current += increment
            if (current >= target) {
                current = target
                clearInterval(timer)
            }
            counter.textContent = Math.floor(current)
        }, 16)
    })
}

function startRealTimeUpdates() {
    // Update dashboard every 30 seconds
    setInterval(() => {
        fetch("/dashboard/update/", {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                updateDashboardMetrics(data)
            })
            .catch((error) => {
                console.error("Dashboard update failed:", error)
            })
    }, 30000)
}

function updateDashboardMetrics(data) {
    // Update occupancy rate
    const occupancyElement = document.getElementById("occupancy-rate")
    if (occupancyElement) {
        occupancyElement.textContent = data.occupancy_rate + "%"
    }

    // Update revenue
    const revenueElement = document.getElementById("today-revenue")
    if (revenueElement) {
        revenueElement.textContent = "$" + data.today_revenue
    }

    // Update arrivals
    const arrivalsElement = document.getElementById("arrivals-today")
    if (arrivalsElement) {
        arrivalsElement.textContent = data.arrivals_today
    }

    // Update pending tasks
    const tasksElement = document.getElementById("pending-tasks")
    if (tasksElement) {
        tasksElement.textContent = data.pending_tasks
    }
}

function initializeQuickActions() {
    const quickActions = document.querySelectorAll(".quick-action")
    quickActions.forEach((action) => {
        action.addEventListener("click", function () {
            const actionType = this.getAttribute("data-action")
            handleQuickAction(actionType)
        })
    })
}

function handleQuickAction(actionType) {
    switch (actionType) {
        case "new-reservation":
            window.location.href = "/reservations/create/"
            break
        case "check-in":
            showCheckInModal()
            break
        case "check-out":
            showCheckOutModal()
            break
        case "maintenance":
            showMaintenanceModal()
            break
        default:
            console.log("Unknown action:", actionType)
    }
}

function showCheckInModal() {
    const modal = document.getElementById("check-in-modal")
    if (modal) {
        showModal(modal)
    }
}

function showCheckOutModal() {
    const modal = document.getElementById("check-out-modal")
    if (modal) {
        showModal(modal)
    }
}

function showMaintenanceModal() {
    const modal = document.getElementById("maintenance-modal")
    if (modal) {
        showModal(modal)
    }
}

function initializeRevenueChart() {
    // Placeholder for revenue chart initialization
    console.log("Revenue chart initialized")
}

function showModal(modal) {
    modal.style.display = "block"
}
  