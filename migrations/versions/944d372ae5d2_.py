"""empty message

Revision ID: 944d372ae5d2
Revises: 
Create Date: 2017-08-30 17:19:36.657146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '944d372ae5d2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('pw_hash', sa.String(length=60), nullable=False),
    sa.Column('created_ts', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_ts', sa.DateTime(timezone=True), nullable=True),
    sa.Column('remote_addr', sa.String(length=20), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
