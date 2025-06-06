// Calendar functionality for reservations and room availability
class HotelCalendar {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId)
        this.options = {
            view: "month",
            startDate: new Date(),
            ...options,
        }
        this.currentDate = new Date(this.options.startDate)
        this.events = []
        this.init()
    }

    init() {
        this.render()
        this.bindEvents()
        this.loadEvents()
    }

    render() {
        this.container.innerHTML = `
              <div class="calendar-header flex justify-between items-center mb-4">
                  <button id="prev-month" class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
                      Previous
                  </button>
                  <h2 id="current-month" class="text-xl font-bold">
                      ${this.formatMonth(this.currentDate)}
                  </h2>
                  <button id="next-month" class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
                      Next
                  </button>
              </div>
              <div class="calendar-grid grid grid-cols-7 gap-1">
                  ${this.renderCalendarGrid()}
              </div>
          `
    }

    renderCalendarGrid() {
        const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        let html = ""

        // Render day headers
        daysOfWeek.forEach((day) => {
            html += `<div class="calendar-day-header p-2 text-center font-semibold bg-gray-100">${day}</div>`
        })

        // Get first day of month and number of days
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1)
        const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0)
        const startDate = new Date(firstDay)
        startDate.setDate(startDate.getDate() - firstDay.getDay())

        // Render calendar days
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate)
            date.setDate(startDate.getDate() + i)

            const isCurrentMonth = date.getMonth() === this.currentDate.getMonth()
            const isToday = this.isToday(date)
            const events = this.getEventsForDate(date)

            html += `
                  <div class="calendar-day p-2 min-h-[80px] border ${isCurrentMonth ? "bg-white" : "bg-gray-50"} ${isToday ? "bg-blue-50 border-blue-200" : "border-gray-200"}" 
                       data-date="${date.toISOString().split("T")[0]}">
                      <div class="day-number text-sm ${isCurrentMonth ? "text-gray-900" : "text-gray-400"}">
                          ${date.getDate()}
                      </div>
                      <div class="events">
                          ${this.renderEvents(events)}
                      </div>
                  </div>
              `
        }

        return html
    }

    renderEvents(events) {
        return events
            .map(
                (event) => `
              <div class="event text-xs p-1 mb-1 rounded ${this.getEventClass(event.type)}" 
                   title="${event.title}">
                  ${event.title}
              </div>
          `,
            )
            .join("")
    }

    getEventClass(type) {
        const classes = {
            reservation: "bg-blue-100 text-blue-800",
            maintenance: "bg-red-100 text-red-800",
            cleaning: "bg-yellow-100 text-yellow-800",
            blocked: "bg-gray-100 text-gray-800",
        }
        return classes[type] || "bg-gray-100 text-gray-800"
    }

    bindEvents() {
        document.getElementById("prev-month").addEventListener("click", () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1)
            this.render()
            this.loadEvents()
        })

        document.getElementById("next-month").addEventListener("click", () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1)
            this.render()
            this.loadEvents()
        })

        // Add click handlers for calendar days
        this.container.addEventListener("click", (e) => {
            const dayElement = e.target.closest(".calendar-day")
            if (dayElement) {
                const date = dayElement.getAttribute("data-date")
                this.onDateClick(date)
            }
        })
    }

    loadEvents() {
        const startDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1)
        const endDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0)

        fetch(
            `/api/calendar/events/?start=${startDate.toISOString().split("T")[0]}&end=${endDate.toISOString().split("T")[0]}`,
        )
            .then((response) => response.json())
            .then((events) => {
                this.events = events
                this.render()
            })
            .catch((error) => {
                console.error("Failed to load calendar events:", error)
            })
    }

    getEventsForDate(date) {
        const dateStr = date.toISOString().split("T")[0]
        return this.events.filter((event) => {
            return event.start_date <= dateStr && event.end_date >= dateStr
        })
    }

    formatMonth(date) {
        return date.toLocaleDateString("en-US", { month: "long", year: "numeric" })
    }

    isToday(date) {
        const today = new Date()
        return date.toDateString() === today.toDateString()
    }

    onDateClick(date) {
        if (this.options.onDateClick) {
            this.options.onDateClick(date)
        }
    }

    addEvent(event) {
        this.events.push(event)
        this.render()
    }

    removeEvent(eventId) {
        this.events = this.events.filter((event) => event.id !== eventId)
        this.render()
    }
}

// Initialize calendar when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    const calendarContainer = document.getElementById("reservation-calendar")
    if (calendarContainer) {
        new HotelCalendar("reservation-calendar", {
            onDateClick: (date) => {
                showReservationModal(date)
            },
        })
    }
})

function showReservationModal(date) {
    const modal = document.getElementById("reservation-modal")
    if (modal) {
        const dateInput = modal.querySelector('input[name="check_in_date"]')
        if (dateInput) {
            dateInput.value = date
        }
        showModal(modal)
    }
}

function showModal(modal) {
    modal.classList.remove("hidden")
    modal.classList.add("flex")
}
