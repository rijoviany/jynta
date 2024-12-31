import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, date
import time
import os
from werkzeug.utils import secure_filename
import pandas as pd
from collections import defaultdict



app = Flask(__name__)

# Path to the JSON file
DATA_FILE = 'prayer_counts.json'
UPLOAD_FOLDER = 'static/gallery/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
INTENTIONS_FILE = 'data/intentions.json'
TSHIRT_ORDERS_FILE = 'data/tshirt_orders.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle image upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If no file is selected, reload the page
        if file.filename == '':
            return redirect(request.url)
        # If the file is allowed, save it to the gallery folder
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('home'))  # Redirect to the homepage to see the uploaded image
    return render_template('upload.html')  # Show upload form


# Helper function to load data from JSON
def load_prayer_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    else:
        return {
            'soul': 0,
            'creed': 0,
            'hail': 0,
            'woc': 0,
            'blessed': 0,
            'rosary': 0,
            'stgertrude': 0  # Add this line
        }

# Helper function to save data to JSON
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

# Function to get the current count for a prayer type
def get_count(prayer_type):
    data = load_prayer_data()
    return data.get(prayer_type, 0)

# Function to increment the count for a prayer type
def increment_count(prayer_type):
    data = load_prayer_data()
    if prayer_type in data:
        if prayer_type == 'stgertrude':
            data[prayer_type] += 1000
        else:
            data[prayer_type] += 1
    else:
        if prayer_type == 'stgertrude':
            data[prayer_type] = 1000
        else:
            data[prayer_type] = 1
    save_data(data)
    return data[prayer_type]

# Function to calculate the days until the conference
def calculate_days_until_conference():
    conference_start_date = datetime(2024, 12, 26).date()
    today = date.today()
    days_until = (conference_start_date - today).days
    return max(0, days_until)  # Ensure we don't show negative days

def load_posts():
    try:
        with open('posts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save posts to a JSON file
def save_posts(posts):
    with open('posts.json', 'w') as f:
        json.dump(posts, f)


MINISTRY_ICONS = {
    'Zonal Council': 'fas fa-users',
    'Intercession': 'fas fa-pray',
    'Neyyattinkara Sub Zone': 'fas fa-map-marker-alt',
    'Kattakada Sub Zone': 'fas fa-map-marker-alt',
    'Nedumangad SubZone': 'fas fa-map-marker-alt',
    'Family Stream': 'fas fa-home',
    'Teens': 'fas fa-users',
    'Prolife': 'fas fa-heart',
    'Music': 'fas fa-music',
    'Formation': 'fas fa-graduation-cap'
}

def get_ministry_data():
    # Read the CSV file
    df = pd.read_csv('data/profiles.csv')
    
    # Group the data by ministry
    ministry_groups = defaultdict(list)
    for _, row in df.iterrows():
        ministry_groups[row['ministry_name']].append(row.to_dict())
    
    return ministry_groups



@app.route('/')
def home():
    days_until_conference = calculate_days_until_conference()
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    ministry_groups = get_ministry_data()
    # Sort the images by last modified time
    images.sort(key=lambda f: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f)), reverse=True)
    return render_template('home.html', days_until_conference=days_until_conference, images=images, ministry_groups=ministry_groups, ministry_icons=MINISTRY_ICONS)

@app.route('/pray-for-ahava')
def pray_for_ahava():
    counts = {
        'soul': get_count('soul'),
        'creed': get_count('creed'),
        'hail': get_count('hail'),
        'rosary': get_count('rosary'),
        'woc': get_count('woc'),
        'blessed': get_count('blessed'),
        'stgertrude': get_count('stgertrude')  # Add this line
    }
    return render_template('pray_for_ahava.html', counts=counts)

@app.route('/pray/<prayer_type>', methods=['POST'])
def pray(prayer_type):
    if prayer_type in ['soul', 'creed', 'hail', 'rosary', 'woc', 'blessed', 'stgertrude']:  
        count = increment_count(prayer_type)
        return jsonify({'success': True, 'count': count})
    else:
        return jsonify({'success': False, 'error': 'Invalid prayer type'}), 400

@app.route('/get_count/<prayer_type>')
def get_count_route(prayer_type):
    if prayer_type in ['soul', 'creed', 'hail', 'rosary','woc','blessed']:
        count = get_count(prayer_type)
        return jsonify({'count': count})
    else:
        return jsonify({'error': 'Invalid prayer type'}), 400


@app.route('/wog-for-ahava')
def wog():
    posts = load_posts()
    sorted_posts = sorted(posts, key=lambda x: sum(x['reactions'].values()), reverse=True)
    return render_template('wog_for_ahava.html', posts=sorted_posts[:2] + sorted_posts[2:])

@app.route('/post', methods=['POST'])
def post():
    content = request.form['content']
    new_post = {
        'id': len(load_posts()) + 1,
        'content': content,
        'timestamp': datetime.now().isoformat(),
        'reactions': {'❤️': 0}
    }
    posts = load_posts()
    posts.append(new_post)
    save_posts(posts)
    return jsonify(success=True)

@app.route('/react', methods=['POST'])
def react():
    post_id = int(request.form['post_id'])
    emoji = request.form['emoji']
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            post['reactions'][emoji] += 1
            break
    save_posts(posts)
    return jsonify(success=True)


#-----------------------------------

# Load the mysteries and data
with open('data/prayer_data.json', 'r') as file:
    prayer_data = json.load(file)

mysteries = {
    "Joyful Mysteries": [
        "1. The Annunciation",
        "2. The Visitation",
        "3. The Nativity",
        "4. The Presentation",
        "5. The Finding of Jesus in the Temple"
    ],
    "Sorrowful Mysteries": [
        "1. The Agony in the Garden",
        "2. The Scourging at the Pillar",
        "3. The Crowning with Thorns",
        "4. The Carrying of the Cross",
        "5. The Crucifixion"
    ],
    "Glorious Mysteries": [
        "1. The Resurrection",
        "2. The Ascension",
        "3. The Descent of the Holy Spirit",
        "4. The Assumption of Mary",
        "5. The Coronation of the Blessed Virgin Mary"
    ],
    "Luminous Mysteries": [
        "1. The Baptism of Jesus in the Jordan",
        "2. The Wedding at Cana",
        "3. The Proclamation of the Kingdom",
        "4. The Transfiguration",
        "5. The Institution of the Eucharist"
    ]
}

mystery_order = list(mysteries.keys())


@app.route('/uat')
def test():
    return render_template('test.html')

@app.route('/rosary-for-ahava')
def rosary_for_ahava():
    with open('data/prayer_data.json', 'r') as file:
        prayer_data = json.load(file)
    intentions = load_intentions()
        
    return render_template('rosary_for_ahava.html', data=prayer_data, intentions=intentions)


def load_intentions():
    try:
        with open(INTENTIONS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_intentions(intentions):
    with open(INTENTIONS_FILE, 'w') as file:
        json.dump(intentions, file, indent=2)


@app.route('/post_intention', methods=['POST'])
def post_intention():
    data = request.json
    intention_text = data.get('intention')
    if intention_text:
        new_intention = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'text': intention_text
        }
        intentions = load_intentions()
        intentions.insert(0, new_intention)  # Add new intention at the beginning
        save_intentions(intentions)
        return jsonify({
            'success': True,
            'date': new_intention['date'],
            'intention': new_intention['text']
        })
    else:
        return jsonify({'success': False, 'message': 'No intention provided'}), 400




@app.route('/pray_rosary', methods=['POST'])
def pray_rosary():
    prayer_data['currentHailMaryCount'] += 1

    if prayer_data['currentHailMaryCount'] > 10:
        prayer_data['currentDecade'] += 1
        prayer_data['currentHailMaryCount'] = 0

        if prayer_data['currentDecade'] > 5:
            prayer_data['currentDecade'] = 1
            prayer_data['currentMysteryIndex'] += 1
            prayer_data['totalRosariesPrayed'] += 1

            if prayer_data['currentMysteryIndex'] >= len(mystery_order):
                prayer_data['currentMysteryIndex'] = 0

    current_mystery_type = mystery_order[prayer_data['currentMysteryIndex']]
    prayer_data['mysteryType'] = current_mystery_type
    prayer_data['mysteryName'] = mysteries[current_mystery_type][prayer_data['currentDecade'] - 1]

    with open('data/prayer_data.json', 'w') as file:
        json.dump(prayer_data, file)

    return jsonify(prayer_data)

@app.route('/get_current_rosary_state', methods=['GET'])
def get_current_rosary_state():
    with open('data/prayer_data.json', 'r') as file:
        prayer_data = json.load(file)
    
    current_mystery_type = mystery_order[prayer_data['currentMysteryIndex']]
    prayer_data['mysteryType'] = current_mystery_type
    prayer_data['mysteryName'] = mysteries[current_mystery_type][prayer_data['currentDecade'] - 1]
    
    return jsonify(prayer_data)


@app.route('/reset', methods=['POST'])
def reset():
    prayer_data.update({
        "totalRosariesPrayed": 0,
        "currentMysteryIndex": 0,
        "currentDecade": 1,
        "currentHailMaryCount": 0
    })

    with open('data/prayer_data.json', 'w') as file:
        json.dump(prayer_data, file)

@app.route('/stream')
def stream():
    def event_stream():
        last_state = None
        while True:
            current_state = get_current_state()
            if current_state != last_state:
                last_state = current_state
                yield f"data: {json.dumps(current_state)}\n\n"
            time.sleep(1)  # Check for updates every second

    return Response(event_stream(), content_type='text/event-stream')

#-----------------------------------

# Helper function to load T-shirt orders
def load_tshirt_orders():
    try:
        with open(TSHIRT_ORDERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Helper function to save T-shirt orders
def save_tshirt_orders(orders):
    with open(TSHIRT_ORDERS_FILE, 'w') as file:
        json.dump(orders, file)

# Route for T-shirt booking page
@app.route('/book-tshirt')
def tshirt_booking():
    return redirect('https://docs.google.com/forms/d/e/1FAIpQLScOezSpsAiicsuJWqxlYBxYmXSVueXAYpZG99zEOa3t99uCbg/viewform')

# API endpoint for T-shirt booking
@app.route('/api/book-tshirt', methods=['POST'])
def book_tshirt():
    data = request.json
    required_fields = ['name', 'mobile', 'model', 'color', 'size']
    
    # Validate required fields
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Load existing orders
    orders = load_tshirt_orders()
    
    # Generate order ID (timestamp + count)
    order_id = f"TSH{int(time.time())}{len(orders) + 1}"
    
    # Create new order
    new_order = {
        'order_id': order_id,
        'name': data['name'],
        'mobile': data['mobile'],
        'model': data['model'],
        'color': data['color'],
        'size': data['size'],
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to orders list
    orders.append(new_order)
    save_tshirt_orders(orders)
    
    return jsonify({
        'message': 'T-shirt booked successfully',
        'order_id': order_id
    })



if __name__ == '__main__':
    # Initialize the JSON file with default values if it doesn't exist
    if not os.path.exists(DATA_FILE):
        save_data({
            'soul': 0,
            'creed': 0,
            'hail': 0,
            'woc': 0,
            'blessed': 0,
            'rosary': 0
        })
    app.run(host='0.0.0.0', debug=False)
