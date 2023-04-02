from waitress import serve
import app

print("Serving the app on 5000")
serve(app.app, host='0.0.0.0', port=5000)
