import http.server
import socketserver
import os
import argparse

def serve_data(port=8080):
    """
    Start a simple HTTP server to serve data files for testing.
    
    Args:
        port (int): Port number to listen on
    """
    # Get the current directory
    current_dir = os.getcwd()
    
    # Set up the HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    
    # Create the server
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving data files at http://localhost:{port}")
        print(f"Sample data URL: http://localhost:{port}/sample_data.csv")
        print("\nPress Ctrl+C to stop the server.")
        
        # Start the server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Serve data files for testing')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    
    args = parser.parse_args()
    
    serve_data(args.port) 