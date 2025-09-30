from flask import Flask, request, jsonify, send_from_directory
import sys
import io
import os
import importlib.util

terminal_emulator_path = os.path.join(os.path.dirname(__file__), '.github', 'workflows', 'terminal_emulator.py')
if not os.path.exists(terminal_emulator_path):
    raise ImportError("terminal_emulator.py not found in .github/workflows")

spec = importlib.util.spec_from_file_location("terminal_emulator", terminal_emulator_path)
terminal_emulator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(terminal_emulator)
TerminalEmulator = terminal_emulator.TerminalEmulator

app = Flask(__name__)
terminal = TerminalEmulator()

@app.route('/run', methods=['POST'])
def run_command():
    data = request.get_json()
    command = data.get('command', '')
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    try:
        terminal.execute_command(command)
        output = mystdout.getvalue()
    except Exception as e:
        output = str(e)
    finally:
        sys.stdout = old_stdout
    return jsonify({'output': output})

@app.route('/commands', methods=['GET'])
def get_commands():
    return jsonify({'commands': terminal.get_command_index()})

@app.route('/')
def serve_html():
    return send_from_directory('.', 'web_terminal.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)