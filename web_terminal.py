from flask import Flask, render_template_string, request
import subprocess

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Terminal Emulator Web Interface</title>
    <style>
        body { font-family: monospace; background: #222; color: #eee; }
        .container { max-width: 600px; margin: 40px auto; padding: 20px; background: #333; border-radius: 8px; }
        input[type=text] { width: 80%; padding: 8px; background: #222; color: #eee; border: 1px solid #555; border-radius: 4px; }
        input[type=submit] { padding: 8px 16px; background: #444; color: #eee; border: none; border-radius: 4px; cursor: pointer; }
        pre { background: #222; color: #eee; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Terminal Emulator</h2>
        <form method="post">
            <input type="text" name="command" placeholder="Enter command" autofocus required>
            <input type="submit" value="Run">
        </form>
        {% if output %}
        <h4>Output:</h4>
        <pre>{{ output }}</pre>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ''
    if request.method == 'POST':
        cmd = request.form['command']
        try:
            result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode() + result.stderr.decode()
        except Exception as e:
            output = str(e)
    return render_template_string(HTML, output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
