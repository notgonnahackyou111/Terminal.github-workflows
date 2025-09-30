interface CommandResult {
    output: string;
    error: string;
}

interface TerminalEmulator {
    runCommand(command: string): Promise<CommandResult>;
    onOutput(callback: (output: string) => void): void;
    onError(callback: (error: string) => void): void;
}

interface SSHClient {
    connect(): Promise<void>;
    executeCommand(command: string): Promise<CommandResult>;
    transferFile(source: string, destination: string): Promise<void>;
    close(): Promise<void>;
}