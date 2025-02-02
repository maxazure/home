"""添加分类排序字段

Revision ID: af90b1b6c237
Revises: 49fd44a5afe9
Create Date: 2025-02-02 19:58:54.989481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af90b1b6c237'
down_revision = '49fd44a5afe9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('section_order', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_column('section_order')

    # ### end Alembic commands ###
