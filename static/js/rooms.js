// Room management functionality
document.addEventListener("DOMContentLoaded", () => {
    initializeRoomManagement()
})

function initializeRoomManagement() {
    // Initialize room status updates
    initializeRoomStatusUpdates()

    // Initialize room filters
    initializeRoomFilters()

    // Initialize drag and drop for housekeeping
    initializeDragAndDrop()

    // Initialize room search
    initializeRoomSearch()
}

function initializeRoomStatusUpdates() {
    const statusButtons = document.querySelectorAll(".room-status-btn")
    statusButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const roomId = this.getAttribute("data-room-id")
            const newStatus = this.getAttribute("data-status")
            updateRoomStatus(roomId, newStatus)
        })
    })
}

function updateRoomStatus(roomId, status) {
    const formData = new FormData()
    formData.append("status", status)
    formData.append("csrfmiddlewaretoken", getCsrfToken())

    fetch(`/rooms/${roomId}/update-status/`, {
        method: "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then((response) => response.text())
        .then((html) => {
            const roomCard = document.querySelector(`[data-room-id="${roomId}"]`).closest(".room-card")
            roomCard.outerHTML = html
            showToast("Room status updated successfully", "success")

            // Re-initialize event listeners for the new card
            initializeRoomStatusUpdates()
        })
        .catch((error) => {
            console.error("Failed to update room status:", error)
            showToast("Failed to update room status", "error")
        })
}

function initializeRoomFilters() {
    const filterForm = document.getElementById("room-filter-form")
    if (!filterForm) return

    const filterInputs = filterForm.querySelectorAll("select, input")
    filterInputs.forEach((input) => {
        input.addEventListener("change", () => {
            filterRooms()
        })
    })
}

function filterRooms() {
    const formData = new FormData(document.getElementById("room-filter-form"))
    const params = new URLSearchParams(formData)

    fetch(`/rooms/?${params.toString()}`, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then((response) => response.text())
        .then((html) => {
            document.getElementById("room-grid").innerHTML = html
            initializeRoomStatusUpdates()
        })
        .catch((error) => {
            console.error("Failed to filter rooms:", error)
        })
}

function initializeDragAndDrop() {
    const roomCards = document.querySelectorAll(".room-card")
    const housekeepingTasks = document.querySelectorAll(".housekeeping-task")

    // Make room cards droppable
    roomCards.forEach((card) => {
        card.addEventListener("dragover", function (e) {
            e.preventDefault()
            this.classList.add("drag-over")
        })

        card.addEventListener("dragleave", function () {
            this.classList.remove("drag-over")
        })

        card.addEventListener("drop", function (e) {
            e.preventDefault()
            this.classList.remove("drag-over")

            const taskId = e.dataTransfer.getData("text/plain")
            const roomId = this.getAttribute("data-room-id")
            assignTaskToRoom(taskId, roomId)
        })
    })

    // Make housekeeping tasks draggable
    housekeepingTasks.forEach((task) => {
        task.setAttribute("draggable", "true")
        task.addEventListener("dragstart", function (e) {
            e.dataTransfer.setData("text/plain", this.getAttribute("data-task-id"))
            this.classList.add("dragging")
        })

        task.addEventListener("dragend", function () {
            this.classList.remove("dragging")
        })
    })
}

function assignTaskToRoom(taskId, roomId) {
    const formData = new FormData()
    formData.append("room_id", roomId)
    formData.append("csrfmiddlewaretoken", getCsrfToken())

    fetch(`/housekeeping/tasks/${taskId}/assign/`, {
        method: "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                showToast("Task assigned successfully", "success")
                // Refresh the task list
                location.reload()
            } else {
                showToast("Failed to assign task", "error")
            }
        })
        .catch((error) => {
            console.error("Failed to assign task:", error)
            showToast("Failed to assign task", "error")
        })
}

function initializeRoomSearch() {
    const searchInput = document.getElementById("room-search")
    if (!searchInput) return

    let timeout
    searchInput.addEventListener("input", function () {
        clearTimeout(timeout)
        timeout = setTimeout(() => {
            searchRooms(this.value)
        }, 300)
    })
}

function searchRooms(query) {
    const params = new URLSearchParams({ search: query })

    fetch(`/rooms/?${params.toString()}`, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then((response) => response.text())
        .then((html) => {
            document.getElementById("room-grid").innerHTML = html
            initializeRoomStatusUpdates()
        })
        .catch((error) => {
            console.error("Failed to search rooms:", error)
        })
}

// Room availability checker
function checkRoomAvailability(checkIn, checkOut, roomType = null) {
    const params = new URLSearchParams({
        check_in: checkIn,
        check_out: checkOut,
    })

    if (roomType) {
        params.append("room_type", roomType)
    }

    return fetch(`/rooms/availability/?${params.toString()}`, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            return data.available_rooms
        })
        .catch((error) => {
            console.error("Failed to check availability:", error)
            return []
        })
}

// Utility function to get CSRF token
function getCsrfToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value
}
