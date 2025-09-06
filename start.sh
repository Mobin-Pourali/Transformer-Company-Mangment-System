#!/bin/bash

echo "🚀 Starting Customer Management System..."
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Please create a .env file with your database credentials:"
    echo "   Copy env.example to .env and update the values"
    echo ""
    echo "Example .env file:"
    echo "MYSQL_HOST=localhost"
    echo "MYSQL_USER=your_username"
    echo "MYSQL_PASSWORD=your_password"
    echo "MYSQL_DATABASE=your_database_name"
    echo "MYSQL_PORT=3306"
    echo ""
    read -p "Press Enter to continue after creating .env file..."
fi

# Start the application
echo "🌐 Starting Flask application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

python main.py
