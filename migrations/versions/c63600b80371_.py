"""empty message

Revision ID: c63600b80371
Revises: 
Create Date: 2019-10-16 11:11:43.480879

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c63600b80371'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=80), nullable=False),
                    sa.Column('default', sa.Boolean(), nullable=True),
                    sa.Column('permissions', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=80), nullable=False),
                    sa.Column('company_email', sa.String(length=80), nullable=False),
                    sa.Column('personal_email', sa.String(length=80), nullable=False),
                    sa.Column('company_email_confirmed', sa.Boolean(), nullable=True),
                    sa.Column('personal_email_confirmed', sa.Boolean(), nullable=True),
                    sa.Column('password', sa.LargeBinary(length=128), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('first_name', sa.String(length=30), nullable=True),
                    sa.Column('last_name', sa.String(length=30), nullable=True),
                    sa.Column('active', sa.Boolean(), nullable=True),
                    sa.Column('is_admin', sa.Boolean(), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('company_email'),
                    sa.UniqueConstraint('personal_email'),
                    sa.UniqueConstraint('username')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
