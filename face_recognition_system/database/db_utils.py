import sqlite3
import numpy as np
from typing import List, Optional
from cryptography.fernet import Fernet
import hashlib
import logging
import json
from pathlib import Path

class CriminalDatabase:
    def __init__(self, db_path: str = 'criminal_db.sqlite'):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
        
        self._init_db()

    def _load_or_generate_key(self) -> bytes:
        """Load encryption key or generate new one"""
        key_file = Path('encryption.key')
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            return key

    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS criminals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            encrypted_embedding BLOB NOT NULL,
            hash_id TEXT UNIQUE NOT NULL,
            image_hash TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def add_criminal(self, name: str, embedding: np.ndarray, image_hash: str = None, metadata: dict = None) -> int:
        """Add a new criminal record with encrypted embedding"""
        # Serialize and encrypt embedding
        embedding_bytes = embedding.tobytes()
        encrypted_embedding = self.cipher.encrypt(embedding_bytes)
        
        # Generate unique hash ID
        hash_id = hashlib.sha256(embedding_bytes).hexdigest()
        
        self.cursor.execute('''
        INSERT INTO criminals (name, encrypted_embedding, hash_id, image_hash, metadata)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, encrypted_embedding, hash_id, image_hash, json.dumps(metadata) if metadata else None))
        
        self.conn.commit()
        return self.cursor.lastrowid

    def find_match(self, query_embedding: np.ndarray, threshold: float = 0.85) -> Optional[dict]:
        """Find matching criminal record using cosine similarity"""
        query_bytes = query_embedding.tobytes()
        query_hash = hashlib.sha256(query_bytes).hexdigest()
        
        # Get all criminal records
        self.cursor.execute('SELECT id, name, encrypted_embedding, metadata FROM criminals')
        records = self.cursor.fetchall()
        
        best_match = None
        best_score = 0
        
        for record in records:
            # Decrypt stored embedding
            decrypted = self.cipher.decrypt(record[2])
            stored_embedding = np.frombuffer(decrypted, dtype=np.float32)
            
            # Calculate cosine similarity
            score = self._cosine_similarity(query_embedding, stored_embedding)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = {
                    'id': record[0],
                    'name': record[1],
                    'score': float(score),
                    'metadata': json.loads(record[3]) if record[3] else None
                }
        
        return best_match

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def init_db():
    """Initialize database singleton"""
    if not hasattr(init_db, 'db_instance'):
        init_db.db_instance = CriminalDatabase()
    return init_db.db_instance