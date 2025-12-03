"""
ACID Transactions Module for Firestore
Provides atomic operations and rollback capabilities for database operations
"""
from typing import Callable, Any, Dict, List
from google.cloud import firestore
from app.db.firestore_client import get_db
import logging

logger = logging.getLogger(__name__)


class FirestoreTransaction:
    """
    Wrapper class for Firestore transactions with ACID guarantees
    Ensures Atomicity, Consistency, Isolation, and Durability
    """
    
    def __init__(self):
        self.db = get_db()
    
    def _execute_transaction_logic(self, transaction, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple operations atomically within a Firestore transaction
        If any operation fails, all operations are rolled back automatically
        
        Args:
            transaction: Firestore transaction object
            operations: List of operations to execute atomically
            
        Returns:
            Dict with results of all operations
            
        Raises:
            Exception if any operation fails (triggers automatic rollback)
        """
        results = {}
        
        for idx, operation in enumerate(operations):
            op_type = operation.get('type')
            collection = operation.get('collection')
            data = operation.get('data', {})
            doc_id = operation.get('doc_id')
            
            try:
                if op_type == 'create':
                    # Create new document
                    if doc_id:
                        doc_ref = self.db.collection(collection).document(doc_id)
                    else:
                        doc_ref = self.db.collection(collection).document()
                    
                    transaction.set(doc_ref, data)
                    results[f'operation_{idx}'] = {
                        'status': 'success',
                        'doc_id': doc_ref.id,
                        'type': 'create'
                    }
                    logger.info(f"✅ Transaction create: {collection}/{doc_ref.id}")
                
                elif op_type == 'update':
                    # Update existing document
                    if not doc_id:
                        raise ValueError("doc_id required for update operation")
                    
                    doc_ref = self.db.collection(collection).document(doc_id)
                    
                    # Verify document exists before update
                    snapshot = doc_ref.get(transaction=transaction)
                    if not snapshot.exists:
                        raise ValueError(f"Document {collection}/{doc_id} does not exist")
                    
                    transaction.update(doc_ref, data)
                    results[f'operation_{idx}'] = {
                        'status': 'success',
                        'doc_id': doc_id,
                        'type': 'update'
                    }
                    logger.info(f"✅ Transaction update: {collection}/{doc_id}")
                
                elif op_type == 'delete':
                    # Delete document
                    if not doc_id:
                        raise ValueError("doc_id required for delete operation")
                    
                    doc_ref = self.db.collection(collection).document(doc_id)
                    transaction.delete(doc_ref)
                    results[f'operation_{idx}'] = {
                        'status': 'success',
                        'doc_id': doc_id,
                        'type': 'delete'
                    }
                    logger.info(f"✅ Transaction delete: {collection}/{doc_id}")
                
                else:
                    raise ValueError(f"Unknown operation type: {op_type}")
                    
            except Exception as e:
                logger.error(f"❌ Transaction operation {idx} failed: {e}")
                raise  # Re-raise to trigger rollback
        
        return results
    
    def execute(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple Firestore operations atomically
        All operations succeed or all fail (ACID guarantee)
        
        Args:
            operations: List of operation dictionaries with format:
                {
                    'type': 'create' | 'update' | 'delete',
                    'collection': 'collection_name',
                    'data': {...},  # For create/update
                    'doc_id': 'doc_id'  # Optional for create, required for update/delete
                }
        
        Returns:
            Dictionary with results of all operations
            
        Example:
            >>> tx = FirestoreTransaction()
            >>> operations = [
            ...     {
            ...         'type': 'create',
            ...         'collection': 'roadmaps',
            ...         'data': {'title': 'Python Path', 'user': 'user@example.com'}
            ...     },
            ...     {
            ...         'type': 'create',
            ...         'collection': 'conversations',
            ...         'data': {'prompt': 'Create roadmap', 'response': 'Done'}
            ...     }
            ... ]
            >>> result = tx.execute(operations)
        """
        try:
            logger.info(f"🔄 Starting transaction with {len(operations)} operations")
            
            # Create a transactional function
            @firestore.transactional
            def run_transaction(transaction):
                return self._execute_transaction_logic(transaction, operations)
            
            # Execute the transaction
            transaction = self.db.transaction()
            results = run_transaction(transaction)
            
            logger.info(f"✅ Transaction completed successfully: {len(operations)} operations")
            return {
                'success': True,
                'operations': results,
                'total_operations': len(operations)
            }
            
        except Exception as e:
            logger.error(f"❌ Transaction failed and rolled back: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'All operations rolled back due to failure'
            }


class BatchWriter:
    """
    Batch write operations for better performance
    Not transactional but provides atomicity for write-only operations
    Use when you need high throughput without read-modify-write
    """
    
    def __init__(self):
        self.db = get_db()
        self.batch = self.db.batch()
        self.operations_count = 0
    
    def add_create(self, collection: str, data: Dict[str, Any], doc_id: str = None):
        """Add a create operation to the batch"""
        if doc_id:
            doc_ref = self.db.collection(collection).document(doc_id)
        else:
            doc_ref = self.db.collection(collection).document()
        
        self.batch.set(doc_ref, data)
        self.operations_count += 1
        logger.info(f"📝 Batch create queued: {collection}/{doc_ref.id}")
        return doc_ref.id
    
    def add_update(self, collection: str, doc_id: str, data: Dict[str, Any]):
        """Add an update operation to the batch"""
        doc_ref = self.db.collection(collection).document(doc_id)
        self.batch.update(doc_ref, data)
        self.operations_count += 1
        logger.info(f"📝 Batch update queued: {collection}/{doc_id}")
    
    def add_delete(self, collection: str, doc_id: str):
        """Add a delete operation to the batch"""
        doc_ref = self.db.collection(collection).document(doc_id)
        self.batch.delete(doc_ref)
        self.operations_count += 1
        logger.info(f"📝 Batch delete queued: {collection}/{doc_id}")
    
    def commit(self) -> Dict[str, Any]:
        """
        Commit all batched operations atomically
        All operations succeed or all fail
        """
        try:
            logger.info(f"🔄 Committing batch with {self.operations_count} operations")
            self.batch.commit()
            logger.info(f"✅ Batch committed successfully: {self.operations_count} operations")
            
            return {
                'success': True,
                'operations_count': self.operations_count
            }
        except Exception as e:
            logger.error(f"❌ Batch commit failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Batch operations failed'
            }


def with_retry(max_attempts: int = 3, backoff_multiplier: float = 2.0):
    """
    Decorator for automatic retry with exponential backoff
    Useful for handling transient failures
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_multiplier: Multiplier for exponential backoff delay
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            attempt = 0
            delay = 1  # Initial delay in seconds
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"❌ Max retry attempts ({max_attempts}) reached: {e}")
                        raise
                    
                    logger.warning(f"⚠️  Attempt {attempt} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
                    delay *= backoff_multiplier
            
        return wrapper
    return decorator
