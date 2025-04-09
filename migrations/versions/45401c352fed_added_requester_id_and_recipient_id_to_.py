from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '45401c352fed'
down_revision = '9e4bbe1a527c'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('connections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('requester_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('recipient_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        
        # Drop the correct constraint
        batch_op.drop_constraint('fk_connections_user_id', type_='foreignkey')
        
        batch_op.create_foreign_key(None, 'users', ['requester_id'], ['id'])
        batch_op.create_foreign_key(None, 'users', ['recipient_id'], ['id'])
        batch_op.drop_column('user_id')
        batch_op.drop_column('friend_id')
        batch_op.drop_column('accepted_at')

def downgrade():
    with op.batch_alter_table('connections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('accepted_at', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('friend_id', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), nullable=False))

        # Drop the new foreign key constraints for rollback
        batch_op.drop_constraint('fk_connections_requester_id', type_='foreignkey')
        batch_op.drop_constraint('fk_connections_recipient_id', type_='foreignkey')

        # Recreate the old foreign key constraint
        batch_op.create_foreign_key('fk_connections_user_id', 'users', ['user_id'], ['id'])

        # Drop the new columns for rollback
        batch_op.drop_column('updated_at')
        batch_op.drop_column('recipient_id')
        batch_op.drop_column('requester_id')
