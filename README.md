
# Job Search Website - Automation

This Django-based project automates job posting, viewing, and user interaction tracking for a job search website. Developed for a Fiverr client, this system integrates middleware to handle user requests, IP throttling, and analytics to track user engagement. It provides functionalities such as posting job listings, viewing jobs, and preventing abuse through rate limiting.

## Features

- **Job Posting**: Automates the process of posting job listings to the platform.
- **Job Viewing**: Automates the process of viewing job listings to test the website's job search functionality.
- **IP Throttling**: Limits the number of requests an IP address can make within a given time frame to prevent abuse.
- **User Interaction Tracking**: Tracks user interactions with job listings, including time spent on each page and navigation history.
- **Fake Middleware**: Handles invalid requests, ensuring that users are redirected to a custom error page.
- **Session Tracking**: Keeps track of user sessions to record their interactions with various job listings.
- **Error Handling**: Renders custom error pages when a server error (500) occurs or if the domain is invalid.


### Middleware

1. **CheckerMiddleware**: A placeholder middleware that processes POST requests (currently not implemented).
2. **FakeMiddleware**: Handles invalid domains and renders a custom error page (`cloudflare.html`).
3. **RequestThrottleMiddleware**: Throttles requests based on the IP address to prevent excessive requests within a short time frame.
4. **AnalyticsMiddleware**: Tracks user interactions with job listings (e.g., time spent on pages) and updates the database accordingly.

### Models

- **Page**: Represents individual job listings and pages within the site.
- **UserInteraction**: Stores information about user activity, such as session ID, page URL, time spent, IP address, and browser details.

### Views

- **Job Postings**: Views for creating, posting, and managing job listings.
- **Job Viewing**: Views that allow users to view job listings, automating the process for testing or analytics.

## Requirements

- **Django 3.x+**
- **Python 3.x+**
- **Redis** (for caching request throttling and session data)
- **Browser Automation (if needed)**: For job viewing automation, tools like `Selenium` and `Chromedriver` can be configured.

To install dependencies, run:

```bash
pip install -r requirements.txt
```

## Installation


### Step 1: Install Dependencies

Install all required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Settings

1. **Database Settings**: Set up your database (e.g., PostgreSQL, SQLite).
2. **Request Throttling**: Configure `REQUESTS_PER_IP_LIMIT` and `REQUEST_THROTTLE_TIMEOUT` in `settings.py`.
3. **Domain Settings**: Make sure the `DOMAIN` setting is correctly configured for your website.

### Step 3: Run Migrations

Create the necessary database tables:

```bash
python manage.py migrate
```

### Step 4: Run the Development Server

To start the development server, run:

```bash
python manage.py runserver
```



## How It Works

1. **Job Posting**: The system automates job postings, making it easier for users to publish job listings.
2. **Job Viewing**: The automation process allows the bot to view jobs, ensuring the platform is working as expected.
3. **Analytics Middleware**: The middleware tracks user interactions, such as time spent on each job listing page. It also logs session and IP address data.
4. **Request Throttling**: Prevents abuse by limiting the number of requests a single IP address can make within a given time.
5. **Fake Middleware**: Redirects users to a custom error page if they access the site with an incorrect domain or if there is an invalid request.

## Custom Middleware Logic

1. **FakeMiddleware**: 
   - Checks if the incoming request's domain is valid.
   - If not, it renders a `cloudflare.html` page with custom error details.
   
2. **RequestThrottleMiddleware**:
   - Tracks the number of requests made by each IP address.
   - Limits requests within a specific time window (default: 60 seconds).

3. **AnalyticsMiddleware**:
   - Tracks user interactions with job listings.
   - Stores interaction details like the time spent on a job listing and user’s browser details.
   
4. **CheckerMiddleware**:
   - Placeholder for processing POST requests (currently unused).

## Example Usage

- **Viewing Job Listings**: Users can view job listings, and the system will automatically track their interactions.
- **Posting Jobs**: Users can submit job listings through the platform, and the system will automatically post them.
- **Interaction Tracking**: The system logs user interactions with job pages, such as the time spent on each job listing page.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
