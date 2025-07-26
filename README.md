## Monitoring

A lightweight **Flask application** for monitoring server resources, Nginx, and MySQL.

## 📋 Table of Contents

- Overview
- Setup
- Environment Configuration
- Running the Application
- API Endpoints
- License

## 🌟 Overview

This application provides real-time monitoring of server resources, Nginx, and MySQL, built with Flask for simplicity and efficiency.

## 🛠️ Setup

Follow these steps to set up the project locally:

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MySQL database**:

   - Use the credentials provided in the `.env` file.
   - Ensure MySQL is running and accessible.

## ⚙️ Environment Configuration

1. Create a `.env` file based on `.env.example`.

2. Configure the following variables:

   ```env
   API_KEY="your-api-key"
   
   FLASK_DEBUG=True
   
   APP_PORT=5000
   APP_HOST=127.0.0.1
   
   DB_USERNAME=your-username
   DB_PASSWORD=your-password
   DB_HOST=your-db-host
   DB_NAME=your-db-name
   ```

## 🚀 Running the Application

Start the application with:

```bash
python server.py
```

## 🌐 API Endpoints

- **GET** `/api/v1/comprehensive`: Returns comprehensive server statistics.

## 📜 License

This project is licensed under the MIT License.

---

*Built with ❤️ by Your Name*
