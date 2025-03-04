# Codeium Sales Calendar

A simple calendar web application for Codeium's Revenue Marketing team to manage and display upcoming sales events.

## Features
- Monthly calendar view
- Easy event addition
- Simple event display
- Clean, modern interface
- Color-coded event categories
- Search and filter capabilities
- Multi-day event support

## Local Development Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Visit `http://localhost:3001` in your browser

## Usage
- Click on any day to add an event
- View all events in the monthly calendar view
- Navigate between months using the arrows
- Use the search bar to find specific events
- Filter events by category using the dropdown
- Click on events to view details or edit them

## Deployment
This application is deployed on Railway. The deployment process is automated through GitHub integration.

### Environment Variables
The following environment variables are required in production:
- `SECRET_KEY`: For session security
- `RAILWAY_ENVIRONMENT`: Set to 'production'
- `DATABASE_URL`: Automatically provided by Railway

## Event Categories
- Conferences (Blue)
- Exec Dinners (Purple)
- Executive Travel (Yellow)
- Marketing Event (Green)
- Internal Event (Red)
