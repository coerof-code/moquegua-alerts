"""
Database management for Moquegua Alert System
Handles SQLite database operations for alert history tracking
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class AlertDatabase:
    """Manages alert history in SQLite database"""
    
    def __init__(self, db_path: str = "data/alerts.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create alerts_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aviso TEXT NOT NULL,
                nro TEXT NOT NULL,
                nivel TEXT NOT NULL,
                inicio DATE NOT NULL,
                fin DATE NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nro, inicio)
            )
        """)
        
        # Create affected_districts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affected_districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER NOT NULL,
                distrito TEXT NOT NULL,
                provincia TEXT NOT NULL,
                departamento TEXT NOT NULL,
                FOREIGN KEY (alert_id) REFERENCES alerts_history(id)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alert_status 
            ON alerts_history(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alert_dates 
            ON alerts_history(inicio, fin)
        """)
        
        conn.commit()
        conn.close()
    
    def add_alert(self, alert_data: Dict) -> int:
        """
        Add or update an alert in the database
        Returns: alert_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if alert already exists
        cursor.execute("""
            SELECT id FROM alerts_history 
            WHERE nro = ? AND inicio = ?
        """, (alert_data['nro'], alert_data['inicio']))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing alert
            alert_id = existing[0]
            cursor.execute("""
                UPDATE alerts_history 
                SET aviso = ?, nivel = ?, fin = ?, status = ?, updated_at = ?
                WHERE id = ?
            """, (
                alert_data['aviso'],
                alert_data['nivel'],
                alert_data['fin'],
                alert_data['status'],
                datetime.now(),
                alert_id
            ))
        else:
            # Insert new alert
            cursor.execute("""
                INSERT INTO alerts_history (aviso, nro, nivel, inicio, fin, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert_data['aviso'],
                alert_data['nro'],
                alert_data['nivel'],
                alert_data['inicio'],
                alert_data['fin'],
                alert_data['status']
            ))
            alert_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return alert_id
    
    def add_affected_districts(self, alert_id: int, districts: List[Dict]):
        """Add affected districts for an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing districts for this alert
        cursor.execute("DELETE FROM affected_districts WHERE alert_id = ?", (alert_id,))
        
        # Insert new districts
        for district in districts:
            cursor.execute("""
                INSERT INTO affected_districts (alert_id, distrito, provincia, departamento)
                VALUES (?, ?, ?, ?)
            """, (
                alert_id,
                district['distrito'],
                district['provincia'],
                district['departamento']
            ))
        
        conn.commit()
        conn.close()
    
    def get_active_alerts(self) -> pd.DataFrame:
        """Get all active alerts"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM alerts_history 
            WHERE status = 'active'
            ORDER BY inicio DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_alert_history(self, days: int = 30) -> pd.DataFrame:
        """Get alert history for the last N days"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM alerts_history 
            WHERE inicio >= date('now', '-{} days')
            ORDER BY inicio DESC
        """.format(days)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_district_history(self, distrito: str) -> pd.DataFrame:
        """Get alert history for a specific district"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT ah.*, ad.distrito, ad.provincia
            FROM alerts_history ah
            JOIN affected_districts ad ON ah.id = ad.alert_id
            WHERE ad.distrito = ?
            ORDER BY ah.inicio DESC
        """
        df = pd.read_sql_query(query, conn, params=(distrito,))
        conn.close()
        return df
    
    def update_alert_status(self, nro: str, status: str):
        """Update alert status (active/expired)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alerts_history 
            SET status = ?, updated_at = ?
            WHERE nro = ?
        """, (status, datetime.now(), nro))
        conn.commit()
        conn.close()
    
    def cleanup_old_alerts(self, days: int = 365):
        """Remove alerts older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM alerts_history 
            WHERE inicio < date('now', '-{} days')
        """.format(days))
        conn.commit()
        conn.close()
