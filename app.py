from flask import Flask, request, jsonify
from ocr_pipeline import process_text, process_image
import sys
import traceback

app = Flask(__name__)

# Root route to prevent 404 errors
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Amount Extractor API",
        "service": "amount-extractor",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "extract_text": "/api/v1/extract/text (POST)",
            "extract_image": "/api/v1/extract/image (POST)"
        }
    })

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "amount-extractor",
        "version": "1.0"
    })

# Text input endpoint
@app.route('/api/v1/extract/text', methods=['POST'])
def extract_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"status":"error","reason":"No text provided"}), 400
        
        if not isinstance(data['text'], str) or len(data['text'].strip()) == 0:
            return jsonify({"status":"error","reason":"Text must be a non-empty string"}), 400
        
        result = process_text(data['text'])
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in extract_text: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "reason": f"Internal server error: {str(e)}"
        }), 500

# Image input endpoint
@app.route('/api/v1/extract/image', methods=['POST'])
def extract_image():
    try:
        if 'file' not in request.files:
            return jsonify({"status":"error","reason":"No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status":"error","reason":"No file selected"}), 400
        
        # Check if file is an image
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({"status":"error","reason":"Invalid file type. Only image files are allowed"}), 400
        
        result = process_image(file)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in extract_image: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "reason": f"Internal server error: {str(e)}"
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "reason": "Endpoint not found",
        "message": "The requested URL was not found on the server. Please check the endpoint path."
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "status": "error",
        "reason": "Method not allowed",
        "message": "The HTTP method is not allowed for this endpoint."
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "reason": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    app.logger.error(traceback.format_exc())
    return jsonify({
        "status": "error",
        "reason": "Internal server error",
        "message": str(e) if app.debug else "An unexpected error occurred."
    }), 500

if __name__ == "__main__":
    # Configure for Windows compatibility
    import os
    # Suppress unnecessary warnings on Windows
    os.environ['PYTHONWARNINGS'] = 'ignore'
    
    print("=" * 50)
    print("Amount Extractor Backend Server")
    print("=" * 50)
    print(f"Server starting on http://localhost:5000")
    print(f"Health check: http://localhost:5000/health")
    print("=" * 50)
    
    try:
        app.run(host='localhost', port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        traceback.print_exc()
        sys.exit(1)
