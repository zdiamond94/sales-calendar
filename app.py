from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
if os.getenv('RENDER'):
    # Ensure we have a valid database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        database_url = 'sqlite:///calendar.db'  # Fallback to SQLite if no URL provided
        logger.warning('No DATABASE_URL found, falling back to SQLite')
    elif database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
        logger.info('Updated postgres:// to postgresql://')
    
    logger.info('Using database URL: %s...', database_url[:15])
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'prod-secret-key')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
    app.config['SECRET_KEY'] = 'dev'
    logger.info('Using development SQLite database')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

CATEGORIES = {
    'conference': {'name': 'Conferences', 'color': 'blue'},
    'exec_dinner': {'name': 'Exec Dinners', 'color': 'purple'},
    'exec_travel': {'name': 'Executive Travel', 'color': 'yellow'},
    'marketing': {'name': 'Marketing Event', 'color': 'green'},
    'internal': {'name': 'Internal Event', 'color': 'red'}
}

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
with app.app_context():
    try:
        logger.info('Creating database tables...')
        db.create_all()
        logger.info('Database tables created successfully')
    except Exception as e:
        logger.error('Error creating database tables: %s', str(e))
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(CATEGORIES)

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        search_query = request.args.get('search', '').lower()
        category_filter = request.args.get('category', '')
        
        query = Event.query
        
        if search_query:
            query = query.filter(
                (Event.title.ilike(f'%{search_query}%')) |
                (Event.description.ilike(f'%{search_query}%'))
            )
        
        if category_filter:
            query = query.filter(Event.category == category_filter)
        
        events = query.all()
        logger.info('Retrieved %d events from database', len(events))
        return jsonify([{
            'id': event.id,
            'title': event.title,
            'start_date': event.start_date.strftime('%Y-%m-%d'),
            'end_date': event.end_date.strftime('%Y-%m-%d'),
            'description': event.description,
            'link': event.link,
            'category': event.category
        } for event in events])
    except Exception as e:
        logger.error('Error retrieving events: %s', str(e))
        return jsonify({'error': 'Failed to retrieve events'}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    try:
        data = request.json
        event = Event(
            title=data['title'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            description=data.get('description'),
            link=data.get('link'),
            category=data['category']
        )
        db.session.add(event)
        db.session.commit()
        logger.info('Created new event: %s', event.title)
        return jsonify({
            'id': event.id,
            'title': event.title,
            'start_date': event.start_date.strftime('%Y-%m-%d'),
            'end_date': event.end_date.strftime('%Y-%m-%d'),
            'description': event.description,
            'link': event.link,
            'category': event.category
        })
    except Exception as e:
        logger.error('Error creating event: %s', str(e))
        return jsonify({'error': 'Failed to create event'}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        data = request.json
        event.title = data.get('title', event.title)
        event.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if 'start_date' in data else event.start_date
        event.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if 'end_date' in data else event.end_date
        event.description = data.get('description', event.description)
        event.link = data.get('link', event.link)
        event.category = data.get('category', event.category)
        db.session.commit()
        logger.info('Updated event: %s', event.title)
        return jsonify({
            'id': event.id,
            'title': event.title,
            'start_date': event.start_date.strftime('%Y-%m-%d'),
            'end_date': event.end_date.strftime('%Y-%m-%d'),
            'description': event.description,
            'link': event.link,
            'category': event.category
        })
    except Exception as e:
        logger.error('Error updating event: %s', str(e))
        return jsonify({'error': 'Failed to update event'}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        logger.info('Deleted event: %s', event.title)
        return '', 204
    except Exception as e:
        logger.error('Error deleting event: %s', str(e))
        return jsonify({'error': 'Failed to delete event'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    debug = not os.getenv('RENDER')
    app.run(debug=debug, host='0.0.0.0', port=port)
