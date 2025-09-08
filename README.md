# Transformer Company Management System
A modern web application for managing and displaying Transformer Company contract information from a MySQL database. Built with Python Flask backend and modern HTML/CSS/JavaScript frontend.
## Features
- 📊  *Contract List Display: View all contracts in a clean, card-based layout
- 🔍 Search & Filter: Search contracts by customer, contract number, or serial
- 👥 Customer Filtering: Filter contracts by specific customers
- 📱 Responsive Design: Works perfectly on desktop, tablet, and mobile devices
- 🎨 Modern UI: Beautiful gradient design with glassmorphism effects
- ⚡ Real-time Updates: Live database connection status and contract count
- 📋 Contract Details: Click on any contract to view detailed information
- 🔄 Sorting Options: Sort contracts by customer, contract, serial, or power
- ⌨️ Keyboard Shortcuts: ESC to close modals, Ctrl+R to refresh

## Database Schema

The application works with the following table structure:

CREATE TABLE Customers (   
    serial    VARCHAR(64),   
    contract  VARCHAR(64),   
    customer  VARCHAR(200),   
    power     VARCHAR(32) ) 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_0900_ai_ci;

LOAD DATA LOCAL INFILE 'data.csv' 
INTO TABLE Customers 
CHARACTER SET utf8mb4 
FIELDS TERMINATED BY ','  
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES (@c1,@c2,@c3,@c4)
SET
  serial   = TRIM(@c1),   
  contract = TRIM(@c2),   
  customer = TRIM(@c3),   
  power    = TRIM(@c4);



## Tech Stack

### Backend
- Python 3.8+
- Flask - Web framework
- MySQL Connector - Database connectivity
- Flask-CORS - Cross-origin resource sharing

### Frontend
- HTML5 - Semantic markup
- CSS3 - Modern styling with CSS Grid and Flexbox
- JavaScript ES6+ - Class-based application architecture
- Font Awesome - Icons
- Google Fonts - Typography

## Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package installer)
- Existing database with `Customers` table

## Installation

1. Clone or download the project files

2. Install Python dependencies

   pip install -r requirements.txt
   


3. Configure environment variables
   - Copy `env.example` to `.env`
   - Update the values with your MySQL database credentials:

   cp env.example .env
   


   Edit `.env` file:


   MYSQL_HOST=localhost
   MYSQL_USER='your-user'
   MYSQL_PASSWORD='your-password'
   MYSQL_DATABASE=iran_transfo
   MYSQL_PORT=3306
   


4. Run the application

   python main.py
   # Or use the startup script:
   ./start.sh
   


5. Open your browser*   Navigate to `http://localhost:5000`
## Project Structure


iran-transfo/
├── main.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database connection and operations
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── iran_transfo.csv      # Your data file
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # CSS styles
    └── js/
        └── app.js        # JavaScript application logic


## API Endpoints
- `GET /` - Main application page- `GET /api/customers` - Get all contracts- `GET /api/customers/unique` - Get unique customer names- `GET /api/customers/<customer_name>/contracts` - Get contracts for a specific customer- `GET /api/customers/count` - Get total contract count- `GET /api/health` - Database health check
## Database Requirements
Make sure your MySQL database has:1. A database named `iran_transfo` (or update the name in your `.env` file)2. A table named `iran_transfo` with the correct schema3. Proper permissions for the MySQL user to read from the table
## Customization
### Database SchemaIf you need to modify the table structure, update the query in `database.py`:

query = """
    SELECT 
        serial,
        contract,
        customer,
        power
    FROM iran_transfo
    ORDER BY customer, serial
"""


### StylingModify `static/css/style.css` to change colors, fonts, and layout:
```
css:root { 
    --primary-color: #1e3c72;
    --secondary-color: #2a5298;
    --text-color: #1e3c72;
}
```

### Features
Add new functionality by extending the `CustomerApp` class in `static/js/app.js`.

## Troubleshooting

### Database Connection Issues
1. Verify MySQL server is running
2. Check database credentials in `.env` file
3. Ensure database and table exist
4. Check firewall settings
5. Verify table schema matches expected format

### Application Won't Start
1. Verify all dependencies are installed
2. Check Python version (3.8+ required)
3. Ensure port 5000 is available
4. Check console for error messages

### Frontend Issues
1. Clear browser cache
2. Check browser console for JavaScript errors
3. Verify all static files are in correct locations

## Development

### Adding New Features
1. Backend: Add new routes in `main.py`
2. Frontend: Extend JavaScript functionality in `app.js`
3. Styling: Update CSS in `style.css`

### Testing
- Test database connectivity: Visit `/api/health`
- Test contract loading: Visit `/api/customers`
- Test frontend: Use browser developer tools

## Production Deployment

For production use:

1. **Security**
   - Change `SECRET_KEY` to a strong, random value
   - Use environment variables for sensitive data
   - Enable HTTPS

2. **Performance**
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Set up reverse proxy (Nginx)
   - Enable database connection pooling

3. **Monitoring**
   - Set up logging
   - Monitor database performance
   - Set up health checks

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the console logs
3. Verify your database setup
4. Check that all files are in the correct locations

## Future Enhancements

- [ ] Add contract creation/editing forms
- [ ] Implement pagination for large contract lists
- [ ] Add export functionality (CSV, PDF, Excel)
- [ ] User authentication and roles
- [ ] Contract activity tracking
- [ ] Advanced filtering and reporting
- [ ] Power consumption analytics
- [ ] Customer performance metrics
