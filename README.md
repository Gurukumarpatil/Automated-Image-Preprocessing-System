# Automated Image Preprocessing System Using AWS

A cloud-based web application that automates image preprocessing using AWS services. Users can upload images, process them automatically, store original and processed images securely, and view or download the results through a web dashboard.

## Overview

Manual image preprocessing is time-consuming and repetitive. This project automates the process using AWS cloud services, allowing uploaded images to be processed automatically without requiring manual intervention.

The system uses **Flask, Amazon S3, AWS Lambda, Amazon RDS (MySQL), and Amazon EC2** to build a complete cloud-based image preprocessing workflow.

## Features

- Image upload through a web interface
- Support for JPG, JPEG, PNG, and WebP images
- Secure storage of original images in Amazon S3
- Automatic image processing triggered by S3 events
- Image resizing and compression
- Processed image storage in a separate S3 folder
- Image metadata and processing status stored in MySQL
- Dashboard to view original and processed images
- Image preview and download functionality
- Delete uploaded images and their associated records
- Automatic dashboard refresh to display completed processing results

## System Architecture

```text
User
  |
  v
Web Application (Flask)
  |
  v
Upload Image
  |
  v
Amazon S3 (Original Images)
  |
  | S3 Event Notification
  v
AWS Lambda
  |
  v
Image Preprocessing (Pillow)
  |
  v
Amazon S3 (Processed Images)
  |
  v
Amazon RDS (MySQL)
  |
  v
Dashboard
  |
  v
Preview / Download Results
```

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development and image processing |
| Flask | Web application framework |
| HTML | Web page structure |
| CSS | Styling |
| JavaScript | Frontend interactions |
| Bootstrap | Responsive UI components |
| Pillow (PIL) | Image processing |
| Boto3 | AWS integration |
| Amazon S3 | Image storage |
| AWS Lambda | Automated image processing |
| Amazon RDS | Metadata storage |
| MySQL | Relational database |
| Amazon EC2 | Application deployment |
| Git & GitHub | Version control |

## AWS Services

### Amazon S3
Stores uploaded images and processed images separately.

```text
S3 Bucket
│
├── original/
│   └── Uploaded images
│
└── processed/
    └── Processed images
```

### AWS Lambda
Automatically executes the image preprocessing function when a new image is uploaded to the designated S3 location.

### Amazon RDS – MySQL
Stores image metadata, including filenames, S3 paths, file sizes, processing status, and compression information.

### Amazon EC2
Hosts the Flask web application, allowing users to access the application through a web browser.

## Workflow

1. The user opens the web application.
2. The user uploads an image.
3. The Flask application validates the image.
4. The original image is uploaded to Amazon S3.
5. Image metadata is recorded in the MySQL database.
6. S3 triggers the AWS Lambda function.
7. Lambda preprocesses the image.
8. The processed image is uploaded to the S3 `processed/` folder.
9. Processing information is updated in the database.
10. The dashboard displays the original and processed images.
11. Users can preview, download, or delete images.

## Project Structure

```text
Automated-Image-Preprocessing-System/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── app/
│
├── database/
│   ├── db.py
│   ├── schema.sql
│   └── test_connection.py
│
├── lambda/
│   └── lambda_function.py
│
├── lambda_package/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   └── dashboard.html
│
└── venv/
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Gurukumarpatil/Automated-Image-Preprocessing-System.git
```

```bash
cd Automated-Image-Preprocessing-System
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

```env
AWS_REGION=your-aws-region
S3_BUCKET_NAME=your-s3-bucket-name

DB_HOST=your-rds-endpoint
DB_NAME=image_preprocessing
DB_USER=your-database-username
DB_PASSWORD=your-database-password

SECRET_KEY=your-secret-key
```

**Never commit your `.env` file, AWS credentials, database passwords, or other secrets to GitHub.**

### 5. Configure AWS Services

Configure the following AWS resources:

- Create an Amazon S3 bucket.
- Create the `original/` and `processed/` storage folders.
- Create an AWS Lambda function for image preprocessing.
- Configure an S3 event notification to trigger Lambda when an image is uploaded.
- Create an Amazon RDS MySQL database.
- Create the required database tables.
- Configure IAM permissions for the AWS services.
- Configure EC2 security groups.

### 6. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Deployment

The application is deployed on Amazon EC2.

Deployment involves:

1. Launching an EC2 instance.
2. Installing Python and required dependencies.
3. Cloning the GitHub repository.
4. Configuring environment variables.
5. Connecting the application to Amazon S3 and RDS.
6. Running the Flask application.
7. Configuring security group rules to allow application access.

## Security

- AWS IAM roles are used to provide permissions to AWS resources.
- Amazon S3 buckets are configured with restricted public access.
- Database credentials are stored in environment variables.
- Security groups control network access.
- Database access is restricted to authorized resources.

## Future Enhancements

- User authentication and authorization
- Additional image preprocessing operations
- Image format conversion
- Batch image processing
- Processing history and analytics
- Improved error handling and monitoring
- Production deployment using Gunicorn and Nginx
- Cloud monitoring and notifications

## Project Objective

The primary objective of this project is to demonstrate how cloud computing and serverless architecture can automate image preprocessing, improve efficiency, and provide scalable image storage and processing capabilities.

---

**Developed as an academic cloud computing project.**

**Technologies:** Python · Flask · AWS · S3 · Lambda · RDS · MySQL · EC2
