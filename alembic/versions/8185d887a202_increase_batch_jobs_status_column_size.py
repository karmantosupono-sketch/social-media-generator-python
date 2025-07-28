# alembic/versions/<timestamp>_increase_batch_jobs_status_column_size.py
"""Increase batch_jobs status column size

Revision ID: <timestamp_ini>
Revises: 1179c46ccd30 # <-- SESUAIKAN dengan ID revisi terakhir Anda
Create Date: ...

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8185d887a202' # Sesuaikan dengan nama file
down_revision = '1179c46ccd30' # <-- SESUAIKAN dengan ID revisi sebelumnya
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Perbesar ukuran kolom status dari VARCHAR(20) menjadi VARCHAR(25) atau lebih
    op.alter_column('batch_jobs', 'status',
                   existing_type=sa.VARCHAR(20),
                   type_=sa.VARCHAR(25), # Cukup untuk 'completed_with_errors' (22 chars)
                   existing_nullable=True,
                   existing_server_default=sa.text("'pending'::character varying"))

def downgrade() -> None:
    # Kembalikan ukuran kolom status ke VARCHAR(20)
    # Hati-hati: ini bisa menyebabkan error jika ada data status yang panjangnya > 20
    op.alter_column('batch_jobs', 'status',
                   existing_type=sa.VARCHAR(25),
                   type_=sa.VARCHAR(20),
                   existing_nullable=True,
                   existing_server_default=sa.text("'pending'::character varying"))