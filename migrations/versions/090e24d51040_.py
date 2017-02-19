"""empty message

Revision ID: 090e24d51040
Revises: ffdafb736090
Create Date: 2017-02-01 23:35:25.827920

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '090e24d51040'
down_revision = 'ffdafb736090'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('readmore_body', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'readmore_body')
    # ### end Alembic commands ###
