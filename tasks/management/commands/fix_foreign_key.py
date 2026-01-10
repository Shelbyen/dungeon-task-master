from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix the foreign key constraint in tasks_task table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Disable foreign key constraints temporarily
            cursor.execute("PRAGMA foreign_keys = OFF;")
            
            # Get all tasks data
            cursor.execute("SELECT id, name, description, status, created_at, due_date, priority, updated_at, user_id FROM tasks_task;")
            rows = cursor.fetchall()
            
            # Drop the current tasks_task table
            cursor.execute("DROP TABLE tasks_task;")
            
            # Create the tasks_task table with correct foreign key constraint
            cursor.execute("""
                CREATE TABLE tasks_task (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name varchar(255) NOT NULL,
                    description text,
                    status varchar(20) NOT NULL,
                    created_at datetime NOT NULL,
                    due_date datetime NOT NULL,
                    priority varchar(10) NOT NULL,
                    updated_at datetime NOT NULL,
                    user_id integer NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users_user (id)
                );
            """)
            
            # Insert the data back
            for row in rows:
                cursor.execute("""
                    INSERT INTO tasks_task (id, name, description, status, created_at, due_date, priority, updated_at, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, row)
            
            # Create the index
            cursor.execute("CREATE INDEX tasks_task_user_id_f0e531b0 ON tasks_task (user_id);")
            
            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            self.stdout.write(
                self.style.SUCCESS('Successfully fixed the foreign key constraint!')
            )