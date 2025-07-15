# models.py - Database models for production
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BuktiSetor(db.Model):
    """Model untuk menyimpan data bukti setor pajak"""
    __tablename__ = 'bukti_setor'
    
    id = db.Column(db.Integer, primary_key=True)
    kode_setor = db.Column(db.String(100), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    jumlah = db.Column(db.Numeric(15, 2), nullable=False)
    ntpn = db.Column(db.String(100), nullable=True)
    preview_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'kode_setor': self.kode_setor,
            'tanggal': self.tanggal.strftime('%Y-%m-%d') if self.tanggal else '',
            'jumlah': float(self.jumlah) if self.jumlah else 0,
            'ntpn': self.ntpn,
            'preview_filename': self.preview_filename,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
    
    def __repr__(self):
        return f'<BuktiSetor {self.kode_setor} - {self.tanggal}>'
