"""empty message

Revision ID: 02c70247a8c9
Revises: 
Create Date: 2020-05-02 01:22:19.730347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02c70247a8c9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('student_experiments',
    sa.Column('experiment_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['experiment_id'], ['experiment.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], )
    )
    op.drop_constraint('student_experiment_id_fkey', 'student', type_='foreignkey')
    op.drop_column('student', 'experiment_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student', sa.Column('experiment_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('student_experiment_id_fkey', 'student', 'experiment', ['experiment_id'], ['id'])
    op.drop_table('student_experiments')
    # ### end Alembic commands ###