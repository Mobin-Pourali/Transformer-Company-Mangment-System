import mysql.connector
from mysql.connector import Error, pooling
from config import Config
import logging
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection_pool = None
        self._lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="iran_transfo_pool",
                pool_size=5,
                pool_reset_session=True,
                host=self.config.MYSQL_HOST,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE,
                port=self.config.MYSQL_PORT,
                autocommit=True,
                connection_timeout=60,
                use_unicode=True,
                charset='utf8mb4'
            )
            logger.info("Database connection pool initialized successfully")
        except Error as e:
            logger.error(f"Error initializing connection pool: {e}")
            self.connection_pool = None

    def get_connection(self):
        """Get a connection from the pool"""
        if not self.connection_pool:
            logger.error("Connection pool not initialized")
            return None
        
        try:
            connection = self.connection_pool.get_connection()
            if connection.is_connected():
                return connection
            else:
                logger.error("Failed to get valid connection from pool")
                return None
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            return None

    def connect(self):
        """Check if we can establish a connection (for health checks)"""
        try:
            connection = self.get_connection()
            if connection:
                connection.close()
                return True
            return False
        except Error as e:
            logger.error(f"Error in connect check: {e}")
            return False
    
    def disconnect(self):
        """Close all connections in the pool"""
        try:
            if self.connection_pool:
                # The pool will automatically close connections when the pool is destroyed
                self.connection_pool = None
                logger.info("Database connection pool closed")
        except Error as e:
            logger.error(f"Error closing connection pool: {e}")
    
    def get_customers(self):
        """Fetch all customers from the database"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor(dictionary=True)
            
            # Updated query to use the correct table name 'Customers'
            # Filter out records with empty or NULL values
            query = """
                SELECT 
                    serial,
                    contract,
                    customer,
                    power
                FROM Customers
                WHERE customer IS NOT NULL 
                AND customer != ''
                AND contract IS NOT NULL 
                AND contract != ''
                AND serial IS NOT NULL 
                AND serial != ''
                ORDER BY customer, serial
            """
            
            cursor.execute(query)
            customers = cursor.fetchall()
            
            return customers
            
        except Error as e:
            logger.error(f"Error fetching customers: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_customer_count(self):
        """Get total number of customers"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return 0
            
            cursor = connection.cursor()
            # Count only valid records (non-empty and non-NULL)
            cursor.execute("""
                SELECT COUNT(*) FROM Customers
                WHERE customer IS NOT NULL 
                AND customer != ''
                AND contract IS NOT NULL 
                AND contract != ''
                AND serial IS NOT NULL 
                AND serial != ''
            """)
            count = cursor.fetchone()[0]
            
            return count
            
        except Error as e:
            logger.error(f"Error getting customer count: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_unique_customers(self):
        """Get list of unique customer names"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor()
            # Get only unique customers from valid records
            cursor.execute("""
                SELECT DISTINCT customer FROM Customers
                WHERE customer IS NOT NULL 
                AND customer != ''
                AND contract IS NOT NULL 
                AND contract != ''
                AND serial IS NOT NULL 
                AND serial != ''
                ORDER BY customer
            """)
            customers = [row[0] for row in cursor.fetchall()]
            
            return customers
            
        except Error as e:
            logger.error(f"Error getting unique customers: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_contracts_by_customer(self, customer_name):
        """Get all contracts for a specific customer"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    serial,
                    contract,
                    customer,
                    power
                FROM Customers
                WHERE customer = %s
                AND customer IS NOT NULL 
                AND customer != ''
                AND contract IS NOT NULL 
                AND contract != ''
                AND serial IS NOT NULL 
                AND serial != ''
                ORDER BY contract, serial
            """
            
            cursor.execute(query, (customer_name,))
            contracts = cursor.fetchall()
            
            return contracts
            
        except Error as e:
            logger.error(f"Error getting contracts by customer: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_customers_with_contracts(self):
        """Get customers with their contract lists grouped by unique contract numbers"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor(dictionary=True)
            
            # Get all valid contracts grouped by customer
            query = """
                SELECT 
                    customer,
                    contract,
                    serial,
                    power
                FROM Customers
                WHERE customer IS NOT NULL 
                AND customer != ''
                AND contract IS NOT NULL 
                AND contract != ''
                AND serial IS NOT NULL 
                AND serial != ''
                ORDER BY customer, contract, serial
            """
            
            cursor.execute(query)
            contracts = cursor.fetchall()
            
            # Group contracts by customer and then by unique contract numbers
            customers_dict = {}
            for contract in contracts:
                customer_name = contract['customer']
                contract_number = contract['contract']
                power = float(contract['power'] or 0)
                
                if customer_name not in customers_dict:
                    customers_dict[customer_name] = {
                        'customer': customer_name,
                        'contracts': {},
                        'unique_contracts': 0,
                        'total_transformers': 0,
                        'total_power': 0
                    }
                
                # Group by unique contract numbers
                if contract_number not in customers_dict[customer_name]['contracts']:
                    customers_dict[customer_name]['contracts'][contract_number] = {
                        'contract': contract_number,
                        'transformers': [],
                        'transformer_count': 0,
                        'total_power': 0
                    }
                
                # Add transformer (each power entry = 1 transformer)
                transformer_info = {
                    'serial': contract['serial'],
                    'power': power
                }
                customers_dict[customer_name]['contracts'][contract_number]['transformers'].append(transformer_info)
                customers_dict[customer_name]['contracts'][contract_number]['transformer_count'] += 1
                customers_dict[customer_name]['contracts'][contract_number]['total_power'] += power
                
                # Update customer totals
                customers_dict[customer_name]['total_transformers'] += 1
                customers_dict[customer_name]['total_power'] += power
            
            # Convert to list format and calculate unique contracts
            customers_list = []
            for customer_name, customer_data in customers_dict.items():
                # Convert contracts dict to list
                contracts_list = []
                for contract_number, contract_data in customer_data['contracts'].items():
                    contracts_list.append(contract_data)
                    customer_data['unique_contracts'] += 1
                
                # Sort contracts by contract number
                contracts_list.sort(key=lambda x: x['contract'])
                
                customer_data['contracts'] = contracts_list
                customers_list.append(customer_data)
            
            # Sort customers by name
            customers_list.sort(key=lambda x: x['customer'])
            
            return customers_list
            
        except Error as e:
            logger.error(f"Error getting customers with contracts: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def cleanup_empty_records(self):
        """Remove records with empty or NULL values"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return 0
            
            cursor = connection.cursor()
            
            # Count records to be deleted
            cursor.execute("""
                SELECT COUNT(*) FROM Customers
                WHERE customer IS NULL 
                OR customer = ''
                OR contract IS NULL 
                OR contract = ''
                OR serial IS NULL 
                OR serial = ''
            """)
            count_to_delete = cursor.fetchone()[0]
            
            if count_to_delete > 0:
                # Delete empty records
                cursor.execute("""
                    DELETE FROM Customers
                    WHERE customer IS NULL 
                    OR customer = ''
                    OR contract IS NULL 
                    OR contract = ''
                    OR serial IS NULL 
                    OR serial = ''
                """)
                connection.commit()
                logger.info(f"Cleaned up {count_to_delete} empty records from database")
            
            return count_to_delete
            
        except Error as e:
            logger.error(f"Error cleaning up empty records: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_unique_contract_ids(self):
        """
        Fetch unique contract IDs from the Customers table
        and return them as a list.
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return []

            cursor = connection.cursor()
            query = """
                SELECT DISTINCT contract 
                FROM Customers
                WHERE contract IS NOT NULL
                AND contract != ''
                ORDER BY contract
            """
            cursor.execute(query)
            contracts = [row[0] for row in cursor.fetchall()]
            return contracts

        except Error as e:
            logger.error(f"Error fetching unique contract IDs: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
