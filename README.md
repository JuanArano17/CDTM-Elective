# 🏃‍♂️💪 Rep&Run - Hybrid Athlete Training Platform

A comprehensive training application for hybrid athletes that combines running and strength training with nutrition tracking, heart rate monitoring, route discovery, and music recommendations.

## 🚀 Features

### 🏃‍♂️ Running Session Management
- **Session Types**: Fartlek, Intervals, Long Run, Recovery Run, Easy Run, Tempo Run
- **Metrics Tracking**: Duration, distance, pace (avg/max), heart rate (avg/max)
- **GPS Integration**: Interactive route maps with Folium
- **Training Journal**: Personal notes and perceived effort logging
- **Session History**: View, edit, and delete previous sessions

### 💪 Strength Training Management
- **Exercise Database**: Comprehensive library of compound, isolation, and functional exercises
- **Workout Tracking**: Sets, reps, weight, rest time, RPE
- **Muscle Group Targeting**: Track which muscle groups are being worked
- **Progress Visualization**: Charts showing strength progression over time
- **Routine Management**: Save and reuse workout routines

### 🥗 Nutrition & AI Meal Suggestions
- **AI-Powered Recommendations**: Meal suggestions based on fitness goals
- **Dietary Preferences**: Support for vegan, vegetarian, gluten-free, etc.
- **Macro Tracking**: Protein, carbs, fat, and calorie monitoring
- **Food Logging**: Manual entry with comprehensive nutrition database
- **Daily Goals**: Visual progress tracking against nutrition targets

### ❤️ Heart Rate Zones
- **Zone Calculator**: Automatic calculation based on age (220-age formula)
- **5 Training Zones**: Recovery, Aerobic, Tempo, Threshold, Anaerobic
- **Zone Analysis**: Time spent in each zone from running sessions
- **Training Guide**: Detailed explanations of each zone's purpose

### 🗺️ Routes & Gyms Discovery
- **Running Routes**: Find popular routes by city with difficulty ratings
- **Gym Locator**: Discover nearby gyms with ratings and addresses
- **Interactive Maps**: Visual representation using Folium
- **Travel-Friendly**: Perfect for athletes on the go

### 🎵 Music Recommendations
- **Workout-Specific Playlists**: Curated for different training types
- **Spotify Integration**: Ready for music platform connections
- **Training Tips**: BPM recommendations for different workout intensities
- **Motivation Boost**: High-energy tracks for maximum performance

### 📊 Progress Reports & Analytics
- **Dashboard Overview**: Key metrics and recent activity
- **Progress Charts**: Visual tracking of running pace and strength volume
- **Weekly/Monthly Reports**: Comprehensive training analysis
- **Trend Analysis**: Performance improvements over time

## 🛠️ Technology Stack

### Core Framework
- **Streamlit**: Main web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

### Visualization & Maps
- **Plotly**: Interactive charts and graphs
- **Folium**: Interactive maps and GPS visualization
- **Matplotlib**: Additional plotting capabilities
- **Seaborn**: Statistical data visualization

### AI & External Integrations
- **OpenAI**: AI-powered meal suggestions
- **Spotipy**: Spotify music integration
- **Geopy**: Geocoding and location services

### Machine Learning
- **Scikit-learn**: Data analysis and modeling
- **Linear Regression**: Progress trend analysis

### Utilities
- **Requests**: HTTP library for API calls
- **Python-dotenv**: Environment variable management
- **JSON**: Data serialization

## 📦 Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd CDTM-Elective
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional):
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

4. **Run the application**:
```bash
streamlit run project.py
```

## 🎯 Usage Guide

### Getting Started
1. **Profile Setup**: Navigate to "👤 Profile & Settings" to configure your personal information
2. **Dashboard**: View your training overview and recent activity
3. **Start Training**: Begin logging running and strength training sessions

### Running Sessions
1. Go to "🏃‍♂️ Running Sessions"
2. Select "➕ Add Session" tab
3. Choose session type and enter metrics
4. Add notes and perceived effort
5. Save your session

### Strength Training
1. Navigate to "💪 Strength Training"
2. Create new session with exercise details
3. Track sets, reps, weight, and RPE
4. View progress in the analytics tab

### Nutrition Tracking
1. Visit "🥗 Nutrition & AI Meals"
2. Get AI-powered meal suggestions
3. Log your daily food intake
4. Monitor macro progress

### Heart Rate Training
1. Go to "❤️ Heart Rate Zones"
2. View your calculated zones
3. Analyze zone distribution from running sessions
4. Follow zone training guidelines

## 📱 Features in Detail

### Running Session Management
- **6 Session Types**: Comprehensive training variety
- **GPS Route Visualization**: Interactive maps with start/end markers
- **Heart Rate Integration**: Zone-based training analysis
- **Performance Metrics**: Pace tracking and improvement monitoring

### Strength Training Features
- **Exercise Database**: 18+ exercises across 3 categories
- **Muscle Group Tracking**: Targeted training analysis
- **Volume Calculation**: Automatic total weight lifted computation
- **RPE Integration**: Rate of Perceived Exertion tracking

### AI Nutrition System
- **Goal-Based Suggestions**: Tailored to muscle gain, fat loss, or maintenance
- **Dietary Accommodation**: Vegan, vegetarian, gluten-free support
- **Macro Optimization**: Balanced nutrition recommendations
- **Meal Variety**: Different suggestions for each meal type

### Heart Rate Zone Training
- **Scientific Calculation**: 220-age formula implementation
- **5 Training Zones**: Complete zone spectrum coverage
- **Session Analysis**: Automatic zone time calculation
- **Training Guidance**: Purpose and benefits of each zone

### Location Services
- **Route Discovery**: Popular running routes by city
- **Gym Finder**: Local fitness facilities with ratings
- **Interactive Maps**: Visual location representation
- **Travel Support**: Perfect for mobile athletes

### Music Integration
- **Workout-Specific Playlists**: 4 training categories
- **Spotify Ready**: API integration prepared
- **BPM Guidelines**: Tempo recommendations
- **Motivation Focus**: High-energy track suggestions

## 🔧 Customization

### Adding New Exercises
Edit the `EXERCISE_DATABASE` in the code:
```python
EXERCISE_DATABASE = {
    'Your Category': {
        'Exercise Name': ['Muscle Group 1', 'Muscle Group 2']
    }
}
```

### Customizing Music Playlists
Modify the `MUSIC_PLAYLISTS` dictionary:
```python
MUSIC_PLAYLISTS = {
    'Your Workout Type': [
        'Playlist 1',
        'Playlist 2'
    ]
}
```

### Adding New Cities
Extend the route and gym databases:
```python
def find_running_routes(city):
    routes = {
        'Your City': [
            {'name': 'Route Name', 'distance': '5.0 km', 'surface': 'Paved', 'difficulty': 'Easy'}
        ]
    }
```

## 🚀 Future Enhancements

### Planned Features
- **Strava Integration**: Automatic workout sync
- **Garmin/Polar Sync**: Device data import
- **Social Features**: Training with friends
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: Native iOS/Android versions

### API Integrations
- **Google Maps API**: Enhanced route discovery
- **Yelp API**: Real gym reviews and ratings
- **OpenFoodFacts**: Comprehensive food database
- **Weather API**: Training condition recommendations

## 📊 Data Management

### Session Storage
- **Running Sessions**: Date, type, metrics, notes
- **Strength Sessions**: Exercise details, volume, RPE
- **Nutrition Log**: Food entries, macros, goals
- **User Profile**: Personal metrics and preferences

### Data Persistence
- **Session State**: Streamlit's built-in state management
- **Local Storage**: Browser-based data persistence
- **Export Options**: CSV/JSON data export (planned)

## 🎨 User Interface

### Design Principles
- **Clean & Modern**: Minimalistic interface design
- **Dark Mode**: Default dark theme for better UX
- **Responsive Layout**: Works on desktop and mobile
- **Intuitive Navigation**: Easy-to-use sidebar menu

### Visual Elements
- **Interactive Charts**: Plotly-powered visualizations
- **Progress Indicators**: Real-time goal tracking
- **Color-Coded Zones**: Heart rate zone visualization
- **Map Integration**: Folium-based location services

## 🔒 Security & Privacy

### Data Protection
- **Local Storage**: No external data transmission
- **Session-Based**: Temporary data storage
- **No Personal Data**: No sensitive information collection
- **GDPR Compliant**: Privacy-focused design

### Future Security
- **User Authentication**: OAuth2 implementation
- **Data Encryption**: Sensitive data protection
- **Cloud Storage**: Secure data backup
- **API Security**: Secure external integrations

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- **Python PEP 8**: Code style compliance
- **Docstrings**: Function documentation
- **Type Hints**: Parameter type annotations
- **Error Handling**: Robust exception management

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit Team**: For the amazing web app framework
- **Plotly**: Interactive visualization library
- **Folium**: Python mapping library
- **OpenAI**: AI-powered features
- **Spotify**: Music integration capabilities

## 📞 Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

---

**🏃‍♂️💪 Rep&Run** - Empowering hybrid athletes to achieve their training goals with comprehensive tracking, AI-powered nutrition, and intelligent training insights.
