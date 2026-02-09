const { contextBridge, ipcRenderer } = require('electron');

// 앱 정보를 렌더러 프로세스에 노출
contextBridge.exposeInMainWorld('recessApp', {
  version: '3.0.0',
  platform: process.platform,
  isDesktop: true,
  
  // 앱 정보
  getInfo: () => ({
    name: 'RECESS IMS',
    version: '3.0.0',
    build: '2026-02-03',
    platform: 'Desktop (Electron)',
  }),
});
