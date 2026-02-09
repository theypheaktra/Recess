const { app, BrowserWindow, Menu, shell, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

// 앱 경로
const APP_DIR = path.join(__dirname, 'app');
const isDev = !app.isPackaged;

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(__dirname, 'build', 'icon.ico'),
    title: 'RECESS IMS v3.0',
    backgroundColor: '#f8fafc',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,
    },
    autoHideMenuBar: false,
    show: false,
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.loadFile(path.join(APP_DIR, 'login.html'));

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// =============================================
// 메뉴 생성 — 4대 카테고리: 제작 / 거래 / 정산 / 인력
// =============================================
function createMenu() {
  const p = (...args) => path.join(APP_DIR, ...args);

  const template = [
    // ─────────────────────────────────────────
    // RECESS IMS (시스템)
    // ─────────────────────────────────────────
    {
      label: 'RECESS IMS',
      submenu: [
        {
          label: '로그인 (Home)',
          accelerator: 'CmdOrCtrl+H',
          click: () => mainWindow.loadFile(p('login.html')),
        },
        {
          label: '로그아웃',
          accelerator: 'CmdOrCtrl+Shift+L',
          click: () => {
            mainWindow.webContents.executeJavaScript(
              "localStorage.removeItem('recess_current_user'); localStorage.removeItem('recess_team_connected'); localStorage.removeItem('recess_session');"
            );
            mainWindow.loadFile(p('login.html'));
          },
        },
        { type: 'separator' },
        {
          label: '종료',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit(),
        },
      ],
    },

    // ─────────────────────────────────────────
    // 대시보드
    // ─────────────────────────────────────────
    {
      label: '대시보드',
      submenu: [
        {
          label: '메인 대시보드 (PM)',
          click: () => mainWindow.loadFile(p('index.html')),
        },
        {
          label: '제작위원회 대시보드 (Tier 0)',
          click: () => mainWindow.loadFile(p('index-tier0-committee.html')),
        },
        {
          label: '원청사 대시보드 (Tier 1)',
          click: () => mainWindow.loadFile(p('index-tier1-prime.html')),
        },
        {
          label: '하청사 대시보드 (Tier 2)',
          click: () => mainWindow.loadFile(p('index-tier2-sub.html')),
        },
        { type: 'separator' },
        {
          label: '워크플로 실행기',
          click: () => mainWindow.loadFile(p('workflow-launcher.html')),
        },
      ],
    },

    // ─────────────────────────────────────────
    // ★ 제작
    // ─────────────────────────────────────────
    {
      label: '제작',
      submenu: [
        {
          label: '프로젝트 대시보드',
          click: () => mainWindow.loadFile(p('pages', 'production', 'project-dashboard.html')),
        },
        { type: 'separator' },
        {
          label: '프리프로덕션',
          click: () => mainWindow.loadFile(p('pages', 'production', 'pre-production.html')),
        },
        {
          label: '메인 프로덕션',
          click: () => mainWindow.loadFile(p('pages', 'production', 'main-production.html')),
        },
        {
          label: '포스트프로덕션',
          click: () => mainWindow.loadFile(p('pages', 'production', 'post-production.html')),
        },
        { type: 'separator' },
        {
          label: '컷 관리',
          click: () => mainWindow.loadFile(p('pages', 'production', 'cut-management-live.html')),
        },
        {
          label: '일정 관리',
          click: () => mainWindow.loadFile(p('pages', 'production', 'schedule-management-v4.html')),
        },
        {
          label: 'QC 검수 (통합)',
          click: () => mainWindow.loadFile(p('pages', 'production', 'qc-review-unified.html')),
        },
      ],
    },

    // ─────────────────────────────────────────
    // ★ 거래
    // ─────────────────────────────────────────
    {
      label: '거래',
      submenu: [
        {
          label: '거래 대시보드',
          click: () => mainWindow.loadFile(p('pages', 'transactions', 'transaction-dashboard.html')),
        },
        { type: 'separator' },
        {
          label: '발주 목록',
          click: () => mainWindow.loadFile(p('pages', 'accounting', 'order-list.html')),
        },
        {
          label: '발주 생성',
          click: () => mainWindow.loadFile(p('pages', 'accounting', 'order-create.html')),
        },
        {
          label: '견적 목록',
          click: () => mainWindow.loadFile(p('pages', 'accounting', 'estimate-list.html')),
        },
        {
          label: '견적 생성',
          click: () => mainWindow.loadFile(p('pages', 'accounting', 'estimate-create.html')),
        },
        { type: 'separator' },
        {
          label: '계약 관리',
          click: () => mainWindow.loadFile(p('pages', 'contract', 'contract-management.html')),
        },
        {
          label: '납품 관리',
          click: () => mainWindow.loadFile(p('pages', 'transactions', 'delivery-main.html')),
        },
        { type: 'separator' },
        {
          label: '예산 승인',
          click: () => mainWindow.loadFile(p('pages', 'committee', 'budget-approval.html')),
        },
        {
          label: '예산 생성',
          click: () => mainWindow.loadFile(p('pages', 'production', 'budget-create-live.html')),
        },
        {
          label: '거래 분석',
          click: () => mainWindow.loadFile(p('pages', 'analytics', 'transaction-analysis-v3.html')),
        },
      ],
    },

    // ─────────────────────────────────────────
    // ★ 정산
    // ─────────────────────────────────────────
    {
      label: '정산',
      submenu: [
        {
          label: '정산 대시보드',
          click: () => mainWindow.loadFile(p('pages', 'settlement', 'settlement-dashboard.html')),
        },
        {
          label: '정산 워크플로',
          click: () => mainWindow.loadFile(p('pages', 'settlement', 'settlement-workflow.html')),
        },
        { type: 'separator' },
        {
          label: '인보이스 관리',
          click: () => mainWindow.loadFile(p('pages', 'settlement', 'invoice-main.html')),
        },
        {
          label: '실적 관리',
          click: () => mainWindow.loadFile(p('pages', 'settlement', 'performance-main.html')),
        },
        {
          label: '경비 관리',
          click: () => mainWindow.loadFile(p('pages', 'settlement', 'expense-management.html')),
        },
        { type: 'separator' },
        {
          label: '정산 원장',
          click: () => mainWindow.loadFile(p('pages', 'settlement', 'settlement-ledger-dashboard.html')),
        },
      ],
    },

    // ─────────────────────────────────────────
    // ★ 인력
    // ─────────────────────────────────────────
    {
      label: '인력',
      submenu: [
        {
          label: '파트너사 관리',
          click: () => mainWindow.loadFile(p('pages', 'master', 'partners.html')),
        },
        {
          label: '파트너 대시보드',
          click: () => mainWindow.loadFile(p('pages', 'master', 'partner-dashboard.html')),
        },
        {
          label: '파트너 평가',
          click: () => mainWindow.loadFile(p('pages', 'master', 'partner-evaluation.html')),
        },
        { type: 'separator' },
        {
          label: '인력 관리',
          click: () => mainWindow.loadFile(p('pages', 'master', 'personnel.html')),
        },
        {
          label: '인력 대시보드',
          click: () => mainWindow.loadFile(p('pages', 'personnel', 'personnel-dashboard.html')),
        },
        {
          label: '인사 평가',
          click: () => mainWindow.loadFile(p('pages', 'personnel', 'evaluation.html')),
        },
        { type: 'separator' },
        {
          label: '단가표',
          click: () => mainWindow.loadFile(p('pages', 'master', 'price-rates.html')),
        },
        {
          label: '팀 역할 관리',
          click: () => mainWindow.loadFile(p('pages', 'master', 'team-roles.html')),
        },
        {
          label: '작업 배정',
          click: () => mainWindow.loadFile(p('pages', 'personnel', 'work-assignment.html')),
        },
      ],
    },

    // ─────────────────────────────────────────
    // 가이드 (확장)
    // ─────────────────────────────────────────
    {
      label: '가이드',
      submenu: [
        {
          label: '📖 통합 가이드 (All-in-One)',
          click: () => mainWindow.loadFile(p('guide', 'user-guide-all-in-one.html')),
        },
        {
          label: '🏠 가이드 홈',
          click: () => mainWindow.loadFile(p('guide', 'user-guide-index.html')),
        },
        { type: 'separator' },
        {
          label: '시작하기',
          submenu: [
            {
              label: '📝 회원가입',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-signup.html')),
            },
            {
              label: '🔐 로그인 / 비밀번호',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-login.html')),
            },
            {
              label: '📊 대시보드 이해하기',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-dashboard.html')),
            },
          ],
        },
        {
          label: '역할별 가이드',
          submenu: [
            {
              label: '🎨 작업자 (L6-L7)',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-worker.html')),
            },
            {
              label: '👥 팀장 (L5)',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-teamlead.html')),
            },
            {
              label: '🏢 중간PM / 하청사 (L4)',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-subpm.html')),
            },
            {
              label: '🎬 원청PM (L3)',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-primepm.html')),
            },
            {
              label: '🏛️ 제작위원회 (L1-L2)',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-committee.html')),
            },
          ],
        },
        {
          label: '주요 기능',
          submenu: [
            {
              label: '📋 발주 / 수주',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-order.html')),
            },
            {
              label: '✅ QC 검수',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-qc.html')),
            },
            {
              label: '💰 정산 / 결제',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-settlement.html')),
            },
            {
              label: '⛓️ NFT / 블록체인',
              click: () => mainWindow.loadFile(p('guide', 'user-guide-nft.html')),
            },
          ],
        },
        { type: 'separator' },
        {
          label: '❓ FAQ / 문제해결',
          click: () => mainWindow.loadFile(p('guide', 'user-guide-faq.html')),
        },
      ],
    },

    // ─────────────────────────────────────────
    // 도구 (+ 권한/알림 이동)
    // ─────────────────────────────────────────
    {
      label: '도구',
      submenu: [
        {
          label: '뒤로 가기',
          accelerator: 'Alt+Left',
          click: () => {
            if (mainWindow.webContents.canGoBack()) mainWindow.webContents.goBack();
          },
        },
        {
          label: '앞으로 가기',
          accelerator: 'Alt+Right',
          click: () => {
            if (mainWindow.webContents.canGoForward()) mainWindow.webContents.goForward();
          },
        },
        {
          label: '새로고침',
          accelerator: 'F5',
          click: () => mainWindow.webContents.reload(),
        },
        { type: 'separator' },
        {
          label: '확대',
          accelerator: 'CmdOrCtrl+=',
          click: () => {
            const zoom = mainWindow.webContents.getZoomLevel();
            mainWindow.webContents.setZoomLevel(zoom + 0.5);
          },
        },
        {
          label: '축소',
          accelerator: 'CmdOrCtrl+-',
          click: () => {
            const zoom = mainWindow.webContents.getZoomLevel();
            mainWindow.webContents.setZoomLevel(zoom - 0.5);
          },
        },
        {
          label: '원래 크기',
          accelerator: 'CmdOrCtrl+0',
          click: () => mainWindow.webContents.setZoomLevel(0),
        },
        { type: 'separator' },
        {
          label: '전체 화면',
          accelerator: 'F11',
          click: () => mainWindow.setFullScreen(!mainWindow.isFullScreen()),
        },
        {
          label: '개발자 도구',
          accelerator: 'F12',
          click: () => mainWindow.webContents.toggleDevTools(),
        },
        { type: 'separator' },
        {
          label: '권한 매트릭스',
          click: () => mainWindow.loadFile(p('pages', 'system', 'role-permission-matrix.html')),
        },
        {
          label: '권한 관리',
          click: () => mainWindow.loadFile(p('pages', 'system', 'central-permission.html')),
        },
        {
          label: '알림 설정',
          click: () => mainWindow.loadFile(p('pages', 'system', 'notifications.html')),
        },
      ],
    },

    // ─────────────────────────────────────────
    // 정보
    // ─────────────────────────────────────────
    {
      label: '정보',
      submenu: [
        {
          label: 'RECESS IMS v3.0 정보',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'RECESS IMS v3.0',
              message: 'RECESS IMS v3.0 Final',
              detail: '애니메이션 제작 통합 관리 시스템\n\n'
                + '1CUT = 1NFT = 1BLOCK\n\n'
                + '© 2026 RECESS IMS / Ritera Pictures\n'
                + 'Build: 2026-02-04',
              icon: path.join(__dirname, 'build', 'icon.png'),
            });
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// 앱 시작
app.whenReady().then(() => {
  createWindow();
  createMenu();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// 모든 윈도우 닫히면 앱 종료 (Windows)
app.on('window-all-closed', () => {
  app.quit();
});
