"""Seed initial data - admin user and content tones

Revision ID: abcd1234567 # <-- Sesuaikan dengan nama file
Revises: daded42c90b2      # <-- SESUAIKAN dengan ID migrasi sebelumnya
Create Date: ...

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.sql import table, column
from sqlalchemy import String, Text, DateTime
from passlib.context import CryptContext 

revision = '1179c46ccd30' 
down_revision = 'daded42c90b2' 
branch_labels = None
depends_on = None

def upgrade() -> None:
    content_tones_table = table('content_tones',
        column('id', String),
        column('name', String),
        column('description', Text),
        column('prompt_modifier', Text)
    )

    tones_data = [
        {'id': 'friendly', 'name': 'Friendly', 'description': 'Warm and approachable', 'prompt_modifier': 'Use warm, welcoming language'},
        {'id': 'casual', 'name': 'Casual', 'description': 'Relaxed and informal', 'prompt_modifier': 'Keep it conversational'},
        {'id': 'modern', 'name': 'Modern', 'description': 'Contemporary and innovative', 'prompt_modifier': 'Use trendy language'},
        {'id': 'professional', 'name': 'Professional', 'description': 'Formal and business-like', 'prompt_modifier': 'Maintain professional tone'},
        {'id': 'humorous', 'name': 'Humorous', 'description': 'Funny and entertaining', 'prompt_modifier': 'Add humor and playfulness'}
    ]

    op.bulk_insert(content_tones_table, tones_data)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("password")

    users_table = table('users',
        column('id', sa.UUID()),
        column('username', String),
        column('email', String),
        column('password_hash', String),
        column('first_name', String),
        column('last_name', String),
    )

    admin_user_data = [{
        'id': uuid.uuid4(), 
        'username': 'admin',
        'email': 'admin@example.com',
        'password_hash': hashed_password,
        'first_name': 'Admin',
        'last_name': 'User',
    }]

    op.bulk_insert(users_table, admin_user_data)

def downgrade() -> None:
    op.execute(
        "DELETE FROM users WHERE username = 'admin'"
    )
    pass 