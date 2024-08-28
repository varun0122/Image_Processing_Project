from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import aiohttp
import asyncio
from PIL import Image
from io import BytesIO
import csv
import uuid
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, ProductImage, ProcessingRequest

app = Flask(__name__)

# Flask setup
engine = create_engine('mysql+mysqlconnector://username:password@localhost:3306/mydatabase')
# Note that username, password, mydatabase(database name) should be replaced according to one's credentials
Session = sessionmaker(bind=engine)
session = Session()

# Define paths
UPLOAD_FOLDER = 'uploads'  # Relative path for uploads
OUTPUT_FOLDER = 'output/csv'  # Relative path for output CSV
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# CSV validation function
def validate_csv(df):
    required_columns = ['Serial Number', 'Product Name', 'Input Image Urls']
    if not all(column in df.columns for column in required_columns):
        raise ValueError("CSV does not contain required columns")
    if df['Serial Number'].is_unique is False:
        raise ValueError("Serial Numbers are not unique")
    if df['Product Name'].isnull().any():
        raise ValueError("Product Name contains empty values")

# Image processing function
async def process_image(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            image_data = await response.read()
            image = Image.open(BytesIO(image_data))
            image = image.convert("RGB")
            output = BytesIO()
            image.save(output, format="JPEG", quality=50)
            return output.getvalue()
        else:
            raise Exception(f"Failed to download image from {url}")

# Function to handle file submission and start processing
@app.route('/submit_file', methods=['POST'])
def handle_file_submission():
    csv_file = request.files['file']
    request_id = str(uuid.uuid4())

    # Save the CSV file locally
    csv_file_path = os.path.join(UPLOAD_FOLDER, csv_file.filename)
    csv_file.save(csv_file_path)

    # Store initial request data in the database
    processing_request = ProcessingRequest(
        request_id=request_id,
        status='Pending',
        csv_file_path=csv_file_path
    )
    session.add(processing_request)
    session.commit()

    # Start asynchronous processing
    asyncio.run(process_csv(request_id, csv_file_path))

    # Return the request ID to the user
    return jsonify({"request_id": request_id})

# Asynchronous function to process the CSV file
async def process_csv(request_id, csv_file_path):
    request = session.query(ProcessingRequest).filter_by(request_id=request_id).first()

    # Read and validate the CSV
    df = pd.read_csv(csv_file_path)
    try:
        validate_csv(df)
    except ValueError as e:
        request.status = 'Failed'
        session.commit()
        raise e

    # Update status to 'In Progress'
    request.status = 'In Progress'
    session.commit()

    try:
        async with aiohttp.ClientSession() as http_session:
            for _, row in df.iterrows():
                input_image_urls = row['Input Image Urls'].split(',')
                output_image_urls = []
                
                for url in input_image_urls:
                    processed_image_data = await process_image(http_session, url)
                    file_path = os.path.join(OUTPUT_FOLDER, f"{row['Product Name']}_{uuid.uuid4().hex}.jpg")
                    with open(file_path, 'wb') as f:
                        f.write(processed_image_data)
                    
                    output_image_urls.append(file_path)

                # Save data to the database
                product_image = ProductImage(
                    serial_number=row['Serial Number'],
                    product_name=row['Product Name'],
                    original_url=','.join(input_image_urls),
                    processed_image_path=','.join(output_image_urls),
                    output_url=','.join(output_image_urls),
                    request_id=request_id  # Added request_id field
                )
                session.add(product_image)
                session.commit()

        # Update status to 'Completed'
        request.status = 'Completed'
    except Exception as e:
        request.status = 'Failed'
    finally:
        session.commit()

# API to check processing status
@app.route('/check_status', methods=['GET'])
def check_status():
    request_id = request.args.get('request_id')
    processing_request = session.query(ProcessingRequest).filter_by(request_id=request_id).first()
    
    if not processing_request:
        return jsonify({"error": "Invalid Request ID"}), 404
    
    return jsonify({"request_id": request_id, "status": processing_request.status})

# API to generate output CSV
@app.route('/generate_output_csv', methods=['GET'])
def generate_output_csv():
    request_id = request.args.get('request_id')
    product_images = session.query(ProductImage).filter_by(request_id=request_id).all()

    if not product_images:
        return jsonify({"error": "No processed images found"}), 404

    output_csv_path = os.path.join(OUTPUT_FOLDER, f"output_{request_id}.csv")
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Serial Number', 'Product Name', 'Input Image Urls', 'Output Image Urls']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for image in product_images:
            writer.writerow({
                'Serial Number': image.serial_number,
                'Product Name': image.product_name,
                'Input Image Urls': image.original_url,
                'Output Image Urls': image.output_url
            })

    return jsonify({"output_csv_path": f"/files/{os.path.basename(output_csv_path)}"})

# Serve files from output directory
@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/')
def index():
    return render_template('index.html')

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)