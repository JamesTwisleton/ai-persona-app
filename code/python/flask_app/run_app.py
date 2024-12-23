from app import create_app

# Create the application instance
app = create_app()

# Run the application
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
