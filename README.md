
# Satellite Imagery Interface

This project provides an API for accessing satellite imagery using Google Earth Engine (GEE) and displaying it on a web interface. The project is built using Flask and other necessary Python libraries.

## Table of Contents
- [Installation](#installation)
  - [Using Docker](#using-docker)
  - [Manual Installation](#manual-installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Files](#files)
- [Configuration](#configuration)
- [License](#license)

## Installation

### Using Docker

1. **Build the Docker image:**
    ```sh
    docker build -t satellite-imagery-interface .
    ```

2. **Run the Docker container:**
    ```sh
    docker run -p 5000:5000 -v $(pwd)/privatekey.json:/app/privatekey.json satellite-imagery-interface
    ```

This will start the Flask application in a Docker container, and it will be accessible at `http://127.0.0.1:5000`.

### Manual Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/satellite-imagery-interface.git
    cd satellite-imagery-interface
    ```

2. **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up your Google Earth Engine credentials:**
    - Replace the content of `privatekey.json` with your own service account key from Google Cloud Platform.

4. **Create and activate a virtual environment (optional but recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
    ```

## Usage

To start the Flask application, run:
```sh
flask run
```

By default, the app will run on `http://127.0.0.1:5000`.

You can access the web interface by navigating to this URL in your web browser.

## API Endpoints

### Get Imagery
- **URL:** `/v5000/earth/imagery/`
- **Method:** `GET`
- **Parameters:**
    - `lon` (float): Longitude of the location.
    - `lat` (float): Latitude of the location.
    - `date` (string): Year in `YYYY` format.
    - `dim` (float): Dimension in degrees for the search area (default: 0.1).

- **Example:**
    ```
    /v5000/earth/imagery/?lon=-95.21&lat=29.67&date=2018&dim=0.32
    ```

- **Response:**
    - `url` (string): URL to the generated thumbnail image.
    - `error` (string): Error message, if any.

## Files

- `app2.py`: Main Flask application file. Contains the API logic and Earth Engine initialization.
- `requirements.txt`: List of Python dependencies required for the project.
- `Dockerfile`: Configuration file for Docker containerization.
- `passenger_wsgi.py`: WSGI file for deployment on a Passenger server.
- `privatekey.json`: Contains the service account credentials for accessing Google Earth Engine.
- `template.html`: HTML template for the web interface.

## Configuration

### Google Earth Engine
This project uses Google Earth Engine (GEE) for satellite imagery. Ensure you have a GEE service account and the corresponding `privatekey.json` file set up properly.

### Environment Variables
You may need to set environment variables for configuration. Example:
```sh
export FLASK_APP=app2.py
export FLASK_ENV=development
```
