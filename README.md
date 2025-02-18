# Palettify

A Flask-based web application that connects to the Spotify API to analyze a user's top tracks and artists, to extract dominant colors from their album artwork and generate a unique color palette.

## Features  
- Fetches user's top tracks or artists.  
- Extracts the dominant color from album or artist images.  
- Allows users to generate a playlist from their top tracks.  
- Users can select time ranges and the number of items to fetch.  

## Installation  

### Prerequisites  
Ensure you have the following installed:  
- Python 3.x  
- pip (Python package manager)  

### Setup  

1. Clone the Repository  
     ```bash
     git clone https://github.com/your-username/palettify.git
     cd palettify

2. Create a Virtual Environment (Optional but Recommended)

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install Dependencies
   
    ```bash
    pip install -r requirements.txt

4. Create a .env file in the project directory and add the following:

    ```env
    SPOTIFY_CLIENT_ID=your-client-id
    SPOTIFY_CLIENT_SECRET=your-client-secret
    SPOTIFY_REDIRECT_URI=http://localhost:5000/callback

5. Run in terminal
    ```bash
    python app.py

6. Open your browser and go to:
   
    ```cpp
    http://127.0.0.1:5000/
