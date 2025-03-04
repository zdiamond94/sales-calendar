from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev'

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

# Only create tables in development
if os.getenv('RAILWAY_ENVIRONMENT') != 'production':
    with app.app_context():
        db.drop_all()  # Only drop tables in development
        db.create_all()
else:
    # In production, just create tables if they don't exist
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(CATEGORIES)

@app.route('/api/events', methods=['GET'])
def get_events():
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
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'start_date': event.start_date.strftime('%Y-%m-%d'),
        'end_date': event.end_date.strftime('%Y-%m-%d'),
        'description': event.description,
        'link': event.link,
        'category': event.category
    } for event in events])

@app.route('/api/events', methods=['POST'])
def create_event():
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
    return jsonify({
        'id': event.id,
        'title': event.title,
        'start_date': event.start_date.strftime('%Y-%m-%d'),
        'end_date': event.end_date.strftime('%Y-%m-%d'),
        'description': event.description,
        'link': event.link,
        'category': event.category
    })

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.json
    event.title = data.get('title', event.title)
    event.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if 'start_date' in data else event.start_date
    event.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if 'end_date' in data else event.end_date
    event.description = data.get('description', event.description)
    event.link = data.get('link', event.link)
    event.category = data.get('category', event.category)
    db.session.commit()
    return jsonify({
        'id': event.id,
        'title': event.title,
        'start_date': event.start_date.strftime('%Y-%m-%d'),
        'end_date': event.end_date.strftime('%Y-%m-%d'),
        'description': event.description,
        'link': event.link,
        'category': event.category
    })

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('RAILWAY_ENVIRONMENT') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
