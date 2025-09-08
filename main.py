from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from database import DatabaseManager
from config import Config
import logging
import signal
import sys
import atexit
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database manager
db_manager = DatabaseManager()

# Global shutdown flag
shutdown_flag = threading.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag.set()
    sys.exit(0)

def cleanup_resources():
    """Clean up resources on shutdown"""
    logger.info("Cleaning up resources...")
    try:
        db_manager.disconnect()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Register cleanup function
atexit.register(cleanup_resources)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/customers')
def get_customers():
    """API endpoint to get all customers with their contracts grouped"""
    if shutdown_flag.is_set():
        return jsonify({
            'success': False,
            'error': 'Server is shutting down',
            'customers': []
        }), 503
    
    try:
        customers = db_manager.get_customers_with_contracts()
        if customers is None:
            customers = []
        
        return jsonify({
            'success': True,
            'customers': customers,
            'count': len(customers)
        })
    except Exception as e:
        logger.error(f"Error in get_customers endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to fetch customers',
            'customers': []
        }), 500

@app.route('/api/customers/contracts')
def get_customers_contracts():
    """API endpoint to get all individual contracts (legacy endpoint)"""
    if shutdown_flag.is_set():
        return jsonify({
            'success': False,
            'error': 'Server is shutting down',
            'contracts': []
        }), 503
    
    try:
        contracts = db_manager.get_customers()
        contract = db_manager.get_unique_contract_ids()
        if contracts is None:
            contracts = []
        
        return jsonify({
            'success': True,
            'contracts': contracts,
            'count': len(contract)
        })
    except Exception as e:
        logger.error(f"Error in get_customers_contracts endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to fetch contracts',
            'contracts': []
        }), 500

@app.route('/api/customers/unique')
def get_unique_customers():
    """API endpoint to get unique customer names"""
    if shutdown_flag.is_set():
        return jsonify({
            'success': False,
            'error': 'Server is shutting down',
            'customers': []
        }), 503
    
    try:
        unique_customers = db_manager.get_unique_customers()
        if unique_customers is None:
            unique_customers = []
        
        return jsonify({
            'success': True,
            'customers': unique_customers,
            'count': len(unique_customers)
        })
    except Exception as e:
        logger.error(f"Error in get_unique_customers endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to fetch unique customers',
            'customers': []
        }), 500

@app.route('/api/customers/<customer_name>/contracts')
def get_customer_contracts(customer_name):
    """API endpoint to get contracts for a specific customer"""
    if shutdown_flag.is_set():
        return jsonify({
            'success': False,
            'error': 'Server is shutting down',
            'contracts': []
        }), 503
    
    try:
        contracts = db_manager.get_contracts_by_customer(customer_name)
        if contracts is None:
            contracts = []
        
        return jsonify({
            'success': True,
            'customer': customer_name,
            'contracts': contracts,
            'count': len(contracts)
        })
    except Exception as e:
        logger.error(f"Error in get_customer_contracts endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to fetch customer contracts',
            'contracts': []
        }), 500

@app.route('/api/customers/count')
def get_customer_count():
    """API endpoint to get unique customer count"""
    if shutdown_flag.is_set():
        return jsonify({
            'success': False,
            'error': 'Server is shutting down'
        }), 503
    
    try:
        customers = db_manager.get_customers_with_contracts()
        count = len(customers) if customers else 0
        
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        logger.error(f"Error in get_customer_count endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to get customer count'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    if shutdown_flag.is_set():
        return jsonify({
            'success': False,
            'status': 'shutting_down',
            'database': 'disconnected'
        }), 503
    
    try:
        if db_manager.connect():
            return jsonify({
                'success': True,
                'status': 'healthy',
                'database': 'connected'
            })
        else:
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'database': 'disconnected'
            }), 500
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_database():
    """Clean up empty records from database"""
    if shutdown_flag.is_set():
        return jsonify({
            'success': False,
            'error': 'Server is shutting down'
        }), 503
    
    try:
        deleted_count = db_manager.cleanup_empty_records()
        return jsonify({
            'success': True,
            'message': f'Successfully cleaned up {deleted_count} empty records',
            'deleted_count': deleted_count
        })
    except Exception as e:
        logger.error(f"Error in cleanup endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to clean up database'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        # Test database connection on startup
        logger.info("Starting Transformer Company Management System...")
        
        if db_manager.connect():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed on startup")
            logger.warning("Application will continue but database features may not work")
        
        logger.info("Starting Flask application...")
        logger.info(f"Debug mode: {app.config['DEBUG']}")
        logger.info("Application is ready to accept requests")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=app.config['DEBUG'],
            threaded=True,
            use_reloader=False  # Disable reloader to prevent issues with signal handlers
        )    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:        
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)
    finally:        
        logger.info("Shutting down application...")
        cleanup_resources()