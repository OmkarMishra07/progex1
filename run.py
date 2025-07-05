from app import create_app

# Create the Flask app instance using the factory function
app = create_app()

if __name__ == '__main__':
    # Run the app in debug mode for development
    app.run(debug=True)