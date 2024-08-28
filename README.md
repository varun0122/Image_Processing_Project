# Image_Processing_Project

# Image Processing System

## Overview

A web application that processes images from URLs provided in a CSV file, compresses them, and returns a downloadable CSV file with the processed image URLs.

## Features

- Upload CSV file with image URLs
- Compress images to 50% of original quality
- Check processing status with a unique request ID
- Download CSV file with processed image URLs

## Requirements

- Python 3.9+
- MySQL Server
- MySQL Workbench

## Setup

1. *Clone the Repository*
    
    git clone https://github.com/varun0122/Image_Processing_Project/
    cd Image_Processing_Project
    

2. *Install Dependencies*
    
    pip install -r requirements.txt
   

3. *Configure Database*
    - Update MySQL credentials in app.py and models.py.
    - Run python models.py to create database tables.

4. *Run the Application*
    
    python app.py
    

5. *Access the Application*
    - Open http://127.0.0.1:5000 in your browser.

## Usage

1. *Upload CSV:* Choose and submit your CSV file.
2. *Check Status:* Use the request ID to check processing status.
3. *Download CSV:* Once completed, download the processed CSV file.

## Folder Structure

- *uploads/*: CSV files uploaded by users
- *static/images/*: Processed images
- *output/*: Generated output CSV files
