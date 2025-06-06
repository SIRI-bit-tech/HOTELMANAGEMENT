--- /dev/null
+++ b/c:\Users\onovw\Desktop\PROJECT\hotelms\README.md
@@ -0,0 +1,159 @@
+# 🏨 HotelMS - Hotel Management System
+
+[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
+
+✨ A comprehensive, Django-powered Hotel Management System designed to streamline all aspects of hotel operations, from reservations and guest management to billing and housekeeping.
+
+---
+
+## 🌟 Core Features
+
+*   🔑 **User Management & Authentication:** Secure login and role-based access.
+*   🏨 **Room Management:** Define room types, manage room inventory, and track room statuses (available, occupied, dirty, maintenance).
+*   📅 **Reservations:** Create, view, update, and cancel bookings. Manage check-ins and check-outs.
+*   🧑‍🤝‍🧑 **Guest Management:** Maintain detailed guest profiles, preferences, stay history, and document management.
+*   💳 **Billing & Invoicing:** Generate invoices, track payments, manage refunds, and handle line items for services.
+*   🧹 **Housekeeping:** Manage housekeeping tasks, track room cleaning status, schedule staff, and manage supplies. Includes maintenance requests.
+*   🛎️ **Front Desk Operations:** Dashboard for arrivals, departures, room status, and quick check-in/check-out functionalities.
+*   📊 **Reporting & Analytics:** Generate various reports (occupancy, revenue, guest insights), with capabilities for scheduled reports.
+*   ⚙️ **Core System Settings:** Configure hotel details, tax rates, and other system-wide parameters. Includes an Audit Log for tracking important actions.
+*   📝 **Dynamic Forms & Views:** User-friendly interfaces for managing all modules.
+*   ⚡ **Task Queuing:** Utilizes Celery and Redis for background tasks (implied from `.env`).
+*   📱 **Responsive Design (Partial):** Uses HTMX for dynamic partial page updates in some modules.
+
+## 🛠️ Tech Stack
+
+*   **Backend:** Python, Django
+*   **Database:** PostgreSQL (recommended, based on commented `.env` settings) or SQLite (default for development, present in `.gitignore`)
+*   **Task Queue:** Celery
+*   **Message Broker/Result Backend:** Redis
+*   **Frontend:** Django Templates, HTML, CSS, JavaScript (with HTMX for some dynamic interactions)
+*   **Environment Management:** `.env` file for configuration.
+
+## 📋 Prerequisites
+
+Before you begin, ensure you have met the following requirements:
+
+*   Python 3.10 (as specified in `.idea/misc.xml`) or higher.
+*   `pip` (Python package installer).
+*   `git` (Version control).
+*   A running Redis server (for Celery).
+*   (Optional but Recommended for Production) A PostgreSQL database server.
+
+## 🚀 Getting Started
+
+### 1. Clone the Repository
+
+```bash
+git clone <your-repository-url>
+cd hotelms
+```
+
+### 2. Set Up a Virtual Environment
+
+It's highly recommended to use a virtual environment:
+
+```bash
+# On Windows
+python -m venv venv
+.\venv\Scripts\activate
+
+# On macOS/Linux
+python3 -m venv venv
+source venv/bin/activate
+```
+
+### 3. Install Dependencies
+
+Create a `requirements.txt` file if you don't have one by running:
+```bash
+pip freeze > requirements.txt
+```
+Then install the dependencies:
+```bash
+pip install -r requirements.txt
+```
+
+### 4. Configure Environment Variables
+
+Copy the example `.env` file (if you have one, or create one based on `c:\Users\onovw\Desktop\PROJECT\hotelms\.env`) and update it with your actual settings:
+
+```bash
+cp .env.example .env  # If you have an example file
+```
+
+Make sure to set at least the following in your `.env` file:
+
+```
+SECRET_KEY=your_strong_secret_key_here
+DEBUG=True
+
+# Database Settings (Example for PostgreSQL, adjust if using SQLite)
+# DB_NAME=hotelms
+# DB_USER=your_db_user
+# DB_PASSWORD=your_db_password
+# DB_HOST=localhost
+# DB_PORT=5432
+
+# Redis & Celery
+REDIS_URL=redis://localhost:6379/1
+CELERY_BROKER_URL=redis://localhost:6379/0
+CELERY_RESULT_BACKEND=redis://localhost:6379/0
+
+# Email (Example for console backend during development)
+EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
+```
+
+### 5. Apply Database Migrations
+
+```bash
+python manage.py migrate
+```
+
+### 6. Create a Superuser
+
+This will allow you to access the Django admin interface:
+
+```bash
+python manage.py createsuperuser
+```
+
+### 7. Run the Development Server
+
+```bash
+python manage.py runserver
+```
+
+The application will be accessible at `http://127.0.0.1:8000/`.
+
+### 8. Run Celery Worker (for background tasks)
+
+In a new terminal (with the virtual environment activated):
+```bash
+celery -A hotelms worker -l info
+```
+
+## 📂 Project Structure
+
+The project follows a modular Django app structure:
+
+```
+hotelms/
+├── apps/                   # Main application modules
+│   ├── billing/
+│   ├── core/
+│   ├── frontdesk/
+│   ├── guests/
+│   ├── housekeeping/
+│   ├── reports/
+│   ├── reservations/
+│   ├── rooms/
+│   └── users/
+├── hotelms/                # Project configuration (settings.py, urls.py)
+├── static/
+├── templates/
+├── manage.py
+├── requirements.txt
+└── .env
+```
+
+## 🤝 Contributing
+
+Contributions are welcome! If you'd like to contribute, please:
+
+1.  Fork the repository.
+2.  Create a new branch (`git checkout -b feature/your-feature-name`).
+3.  Make your changes.
+4.  Commit your changes (`git commit -m 'Add some amazing feature'`).
+5.  Push to the branch (`git push origin feature/your-feature-name`).
+6.  Open a Pull Request.
+
+Please ensure your code adheres to the project's coding standards and includes tests where applicable.
+
+## 📜 License
+
+This project is licensed under the MIT License. See the `LICENSE.txt` file for more information (if you add one).
+
+---
+
+Happy Hotel Managing! 🛎️🎉
+
+```
