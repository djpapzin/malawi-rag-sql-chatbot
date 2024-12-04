
try:
    from app.core.config import settings
    print("Import successful!")
    print(f"APP_NAME: {settings.APP_NAME}")
except Exception as e:
    print(f"Error: {str(e)}")
