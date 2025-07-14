import os

# Ensure database URL components exist for module imports
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_USER', 'user')
os.environ.setdefault('DB_PASSWORD', 'pass')
os.environ.setdefault('DB_NAME', 'testdb')
os.environ.setdefault('SECRET_KEY', 'secret')
os.environ.setdefault('SECRET_KEY_AUTH', 'secret')
os.environ.setdefault('AWS_REGION', 'us-east-1')
os.environ.setdefault('PROBLEM_BUCKET', 'test-bucket')
os.environ.setdefault('REPORT_BUCKET', 'test-bucket')
os.environ.setdefault('PROFILE_IMAGE_BUCKET', 'test-bucket')

