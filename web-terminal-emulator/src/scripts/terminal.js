// This file contains the JavaScript code that implements the functionality of the terminal emulator.
// It handles user input, communicates with the backend, and updates the HTML elements to display output.

document.addEventListener('DOMContentLoaded', () => {
    const terminalInput = document.getElementById('terminal-input');
    const terminalOutput = document.getElementById('terminal-output');

    terminalInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            const command = terminalInput.value;
            executeCommand(command);
            terminalInput.value = '';
        }
    });

    function executeCommand(command) {
        // Send the command to the backend and handle the response
        fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command }),
        })
        .then(response => response.json())
        .then(data => {
            updateOutput(data.output);
        })
        .catch(error => {
            updateOutput(`Error: ${error.message}`);
        });
    }

    function updateOutput(output) {
        const outputElement = document.createElement('div');
        outputElement.textContent = output;
        terminalOutput.appendChild(outputElement);
        terminalOutput.scrollTop = terminalOutput.scrollHeight; // Auto-scroll to the bottom
    }
});