# Futproject.V1 ⚽🤖

Futproject.V1 is an end-to-end Machine Learning and Web Scraping pipeline designed to predict the outcomes of Brazilian football championship (Brasileirão) matches. The project automatically scrapes historical match data, processes the features, and trains a predictive model.

## Features ✨

- **Web Scraping:** Automated extraction of match results and statistics from [FBref](https://fbref.com/) across multiple seasons (2024, 2025, 2026) using Selenium and BeautifulSoup.
- **Data Storage:** Uses SQLite to store the scraped matches history locally (`db/database.sqlite`), ensuring no duplicates.
- **Feature Engineering:** Prepares the data, cleaning and transforming the raw stats into trainable features for the ML model.
- **Machine Learning Model:** Trains a Random Forest Classifier (`random_forest_brasileirao.pkl`) to predict match outcomes using Scikit-Learn.
- **Automated Pipeline:** `main.py` runs the full process from extraction to model training in a single step.

## Project Structure 📁

```
Futproject.V1/
├── db/                   # Contains the SQLite database with match history
├── src/                  # Source code for the project
│   ├── scraper/          # Modules for web scraping (Selenium, parsers)
│   ├── features/         # Data cleaning and feature engineering
│   └── models/           # ML model training and prediction scripts
├── main.py               # Main entry point to run the pipeline
├── requirements.txt      # Python dependencies
└── .gitignore            # Git ignore file
```

## Setup & Installation ⚙️

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Futproject.V1.git
   cd Futproject.V1
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # OR
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r Futproject.V1/requirements.txt
   ```

4. **Webdriver:**
   Ensure you have the appropriate WebDriver installed (e.g., ChromeDriver) compatible with your installed browser version for Selenium to work.

## Usage 🚀

To run the complete pipeline (Scraping -> Feature Engineering -> Model Training), simply execute:

```bash
python Futproject.V1/main.py
```

This will output the progress of the scraping, save data to the local SQLite database, prepare the dataset, and output a trained machine learning model inside the `src/models/` directory.

## Technologies Used 🛠️

- **Python 3**
- **Pandas & NumPy:** Data manipulation and analysis.
- **Scikit-Learn:** Machine Learning model training.
- **Selenium & BeautifulSoup4:** Web scraping and parsing.
- **SQLite3:** Local database storage.
- **Joblib:** Model serialization.

## License 📄
This project is for educational and research purposes.
