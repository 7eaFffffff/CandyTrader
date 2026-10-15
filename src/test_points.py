
from auth import init_db, add_points, get_points

init_db()

# Change this to the child's registered username
CHILD_USERNAME = "child1"

# Add 50 points for testing
success, message = add_points(
    CHILD_USERNAME,
    50,
    source="developer_test"
)

print(message)

if success:
    print("Current balance:", get_points(CHILD_USERNAME))
