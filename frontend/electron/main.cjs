const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess = null;

const createWindow = () => {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: true,
      contextIsolation: false 
    }
  });

  const isDev = !app.isPackaged;

  if (isDev) {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools({ mode: 'detach' });
  } else {
    const indexPath = path.join(app.getAppPath(), 'dist', 'index.html');
    win.loadFile(indexPath);
  }
};


app.whenReady().then(() => {
  if (app.isPackaged) {
    const backendExecutable = path.join(process.resourcesPath, 'backend_server');
    console.log('Starting backend from:', backendExecutable);
    
    backendProcess = spawn(backendExecutable, [], {
      cwd: process.resourcesPath,
      stdio: 'inherit'
    });

    backendProcess.on('error', (err) => {
      console.error('Failed to start backend process:', err);
    });
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('will-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
