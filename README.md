# GIS Projects Monorepo
Each project has its own directory under `projects/` with scripts to download data, transform it and display the results.  Each project's results will be available as a GitHub Page (eventually).

## Usage
```bash
# Install pipenv
## MacOS
brew install pipenv

## Ubuntu/Debian
sudo apt install -y pipenv

# Install dependencies
pipenv install

# Input API secrets for data downloads
cp .env.template .env
vim .env
```
## Project Structure
gis_projects/
├─ projects/
│  ├─ project1/
│  │  ├─ download.sh                # Download raw GIS data from local government sites
│  │  ├─ transform.py               # Transform data for analysis
│  │  ├─ analyze.py                 # Create the output data to be displayed
│  │  ├─ build_all.sh               # runs all the data scripts and generates result display site
│  │  ├─ README.md
├─ scripts/                         # Reusable scripts not specific to a single project
├─ site/                            # Display files
│  ├─ index.css
│  ├─ index.html
│  ├─ project1/                     # Site files to display results from project1
│  ├─ project2/                     # Site files to display results from project2 etc.
├─ specs/                           # Context files for spec-kit
