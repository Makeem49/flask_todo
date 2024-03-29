"""add suspend_at column to db

Revision ID: dad65ab5171f
Revises: b147f47cefde
Create Date: 2023-01-26 17:45:36.860579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dad65ab5171f'
down_revision = 'b147f47cefde'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('suspend_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.drop_column('suspend_at')

    # ### end Alembic commands ###
