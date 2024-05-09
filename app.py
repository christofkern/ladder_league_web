from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/rotating_layouts/<path:filename>')
def serve_html(filename):
    return send_from_directory('rotating_layouts', filename)

@app.route('/')
def index():
    layout_files = os.listdir('rotating_layouts')
    
    print(layout_files)
    return render_template('rotating_info.html', layout_files = layout_files, interval = 2000, runner_data = runner_data)


if __name__ == '__main__':
    app.run(debug=True)
