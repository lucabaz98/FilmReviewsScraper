
# Movie Data Scraping Project

## Overview

This project is designed to scrape movie data from various sources. The collected data includes movies and its ratings. The data is then stored in a MongoDB database for further analysis.

## Project Structure

The project is organized into several Python scripts, each responsible for a specific task:

- **scraper.py**: The main script to be executed for scraping data.
- **imdb.py**: Contains functions to scrape votes and ratings data from IMDb.
- **my_movies.py**: Contains functions to scrape data from MyMovies website.
- **coming_soon.py**: Contains functions to scrape data from ComingSoon website.

## Requirements

The project requires several Python libraries. These are listed in the `requirements.txt` file:

```
beautifulsoup4==4.12.3
pymongo==4.6.1
PyYAML==6.0.1
Requests==2.32.3
selenium==3.141.0
tqdm==4.66.4
```

## Installation

1. **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Setup MongoDB**:
    Ensure you have a MongoDB instance running and update the connection settings in `configs.yaml`.

4. **Setup IMDb API Key**:
    Create an account on [OMDb API](https://www.omdbapi.com/) and obtain an API key. Update the `configs.yaml` file to include your API key.

## Usage

### Running the Scraper

To run the scraper and collect data, execute the following command:

```sh
python scraper.py <country> <seasons>
```

- `<country>`: The country code for the box office data (e.g., "usa").
- `<seasons>`: One or more seasons to scrape data for (e.g., 2022).

For example, to scrape data for the USA for the year 2015 and 2022:

```sh
python scraper.py usa 2015 2022
```

### Configuration

**configs.yaml**: This file contains all the necessary configuration settings used in the project. Ensure this file is correctly set up with your specific details.

## Future Improvements

We are planning several future improvements to enhance the functionality and coverage of this project:

1. **Updating Film Ratings**: Implementing a feature to update existing film ratings with new ratings if they have changed.
2. **Italy Box Office Rankings**: Adding Italy as a source for box office data in addition to the USA.
3. **Optimized Data Storage**: Refactoring the database schema to better handle multiple data sources and improve data retrieval efficiency.
4. **Enhanced Error Handling**: Implementing more robust error handling and logging mechanisms to ensure the scraper can recover from common issues without manual intervention.
5. **Automated Schedules**: Setting up automated schedules for scraping tasks to ensure data is regularly updated without manual execution.
6. **Data Visualization**: Integrating data visualization tools to provide graphical insights into the collected data directly from the database.
