import pytest
import requests
import logging
import csv
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

BASE_URL = "https://restcountries.com/v3.1/all?fields=name,capital,population,flags"


def get_country_data():
    """Fetches country data from the API."""
    try:
        start_time = time.time()
        response = requests.get(BASE_URL, timeout=5)
        end_time = time.time()

        response.raise_for_status()
        logger.info(f"Response time: {end_time - start_time:.3f} seconds")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        pytest.fail(f"API request failed: {e}")


@pytest.mark.parametrize("country_name, expected", [
    ("Switzerland", True),  # Positive case
    ("Mumbai", False),  # Negative case
    ("India", True)  # Additional case
])
def test_country_existence(country_name, expected):
    """Tests if a given country exists in the API response."""
    data = get_country_data()
    assert isinstance(data, list), "Response is not a list."

    country = next((i for i in data if i["name"].get("common") == country_name), None)
    assert (country is not None) == expected, f"Unexpected existence check for {country_name}"


@pytest.mark.parametrize("official_name, expected", [
    ("Swiss Confederation", True),  # Positive case
    ("Mumbai", False),  # Negative case
    ("Republic of India", True)  # Additional case
])
def test_official_name(official_name, expected):
    """Tests if a given official country name exists in the API response."""
    data = get_country_data()
    assert isinstance(data, list), "Response is not a list."

    country = next((i for i in data if i["name"].get("official") == official_name), None)
    assert (country is not None) == expected, f"Unexpected official name check for {official_name}"


def load_test_data_from_csv():
    """Loads test data from a CSV file."""
    test_data = []
    with open("test_data.csv", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            test_data.append((row[0], row[1] == "True"))
    return test_data


@pytest.mark.parametrize("country_name, expected", load_test_data_from_csv())
def test_data_driven_country_existence(country_name, expected):
    """Tests countries based on external CSV data."""
    data = get_country_data()
    country = next((i for i in data if i["name"].get("common") == country_name), None)
    assert (country is not None) == expected, f"Unexpected result for {country_name}"


def test_api_performance():
    """Measures API response time."""
    start_time = time.time()
    response = requests.get(BASE_URL, timeout=5)
    end_time = time.time()
    response.raise_for_status()
    response_time = end_time - start_time
    logger.info(f"API responded in {response_time:.3f} seconds")
    assert response_time < 3, "API response time exceeded 3 seconds"


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", "--maxfail=3", "--html=report.html"])
