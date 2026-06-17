const LANGUAGE_STORAGE_KEY = "tbh-web-monitor-language-v1";

export { LANGUAGE_STORAGE_KEY };

export const LOCALE_BY_LANGUAGE = {
  "pt-BR": "pt-BR",
  en: "en-US",
  es: "es-ES",
  fr: "fr-FR",
  zh: "zh-CN",
  ja: "ja-JP",
};

const SHARED_KEYS = {
  "pt-BR": {
    rowTimerReady: "Pronto",
    alertVolumeLabel: "Volume do alerta",
    testAlertButton: "Testar alerta",
    clearLogsButton: "Limpar",
    footerDevelopedBy: "Desenvolvido por -Neath",
    footerWikiData:
      'Dados de baus e fases com base na <a href="https://taskbarherowiki.com" target="_blank" rel="noopener noreferrer" class="font-medium text-amber-400 transition hover:text-amber-300">TaskBar Hero Wiki</a> (fan-made, nao oficial).',
    rowBossTimer: "Chefe",
    rowCommonTimer: "Comum",
    rowMap: "Mapa",
    rowRecommendedMap: "Mapa recomendado",
    rowClearTime: "Volta (s)",
    rowClearTimePlaceholder: "opcional",
    rowRemove: "Remover",
    mapNotAvailable: "Sem mapas para este bau",
    languageLabel: "Idioma",
    difficulty: {
      Normal: "Normal",
      Nightmare: "Pesadelo",
      Hell: "Inferno",
      Torment: "Tormenta",
    },
  },
  en: {
    rowTimerReady: "Ready",
    alertVolumeLabel: "Alert volume",
    testAlertButton: "Test alert",
    clearLogsButton: "Clear",
    footerDevelopedBy: "Developed by -Neath",
    footerWikiData:
      'Chest and stage data based on the <a href="https://taskbarherowiki.com" target="_blank" rel="noopener noreferrer" class="font-medium text-amber-400 transition hover:text-amber-300">TaskBar Hero Wiki</a> (fan-made, unofficial).',
    rowBossTimer: "Boss",
    rowCommonTimer: "Common",
    rowMap: "Map",
    rowRecommendedMap: "Recommended map",
    rowClearTime: "Clear (s)",
    rowClearTimePlaceholder: "optional",
    rowRemove: "Remove",
    mapNotAvailable: "No maps for this chest",
    languageLabel: "Language",
    difficulty: {
      Normal: "Normal",
      Nightmare: "Nightmare",
      Hell: "Hell",
      Torment: "Torment",
    },
  },
  es: {
    rowTimerReady: "Listo",
    alertVolumeLabel: "Volumen de alerta",
    testAlertButton: "Probar alerta",
    clearLogsButton: "Limpiar",
    footerDevelopedBy: "Desarrollado por -Neath",
    footerWikiData:
      'Datos de cofres y fases basados en la <a href="https://taskbarherowiki.com" target="_blank" rel="noopener noreferrer" class="font-medium text-amber-400 transition hover:text-amber-300">TaskBar Hero Wiki</a> (fan-made, no oficial).',
    rowBossTimer: "Jefe",
    rowCommonTimer: "Comun",
    rowMap: "Mapa",
    rowRecommendedMap: "Mapa recomendado",
    rowClearTime: "Vuelta (s)",
    rowClearTimePlaceholder: "opcional",
    rowRemove: "Eliminar",
    mapNotAvailable: "Sin mapas para este cofre",
    languageLabel: "Idioma",
    difficulty: {
      Normal: "Normal",
      Nightmare: "Pesadilla",
      Hell: "Infierno",
      Torment: "Tormento",
    },
  },
  fr: {
    rowTimerReady: "Pret",
    alertVolumeLabel: "Volume de l'alerte",
    testAlertButton: "Tester l'alerte",
    clearLogsButton: "Effacer",
    footerDevelopedBy: "Developpe par -Neath",
    footerWikiData:
      'Donnees de coffres et de phases basees sur le <a href="https://taskbarherowiki.com" target="_blank" rel="noopener noreferrer" class="font-medium text-amber-400 transition hover:text-amber-300">TaskBar Hero Wiki</a> (fan-made, non officiel).',
    rowBossTimer: "Boss",
    rowCommonTimer: "Commun",
    rowMap: "Carte",
    rowRecommendedMap: "Carte recommandee",
    rowClearTime: "Retour (s)",
    rowClearTimePlaceholder: "optionnel",
    rowRemove: "Supprimer",
    mapNotAvailable: "Aucune carte pour ce coffre",
    languageLabel: "Langue",
    difficulty: {
      Normal: "Normal",
      Nightmare: "Cauchemar",
      Hell: "Enfer",
      Torment: "Tourment",
    },
  },
  zh: {
    rowTimerReady: "就绪",
    alertVolumeLabel: "提示音量",
    testAlertButton: "测试提示",
    clearLogsButton: "清除",
    footerDevelopedBy: "由 -Neath 开发",
    footerWikiData:
      '宝箱与关卡数据来自 <a href="https://taskbarherowiki.com" target="_blank" rel="noopener noreferrer" class="font-medium text-amber-400 transition hover:text-amber-300">TaskBar Hero Wiki</a>（粉丝制作，非官方）。',
    rowBossTimer: "首领",
    rowCommonTimer: "普通",
    rowMap: "地图",
    rowRecommendedMap: "推荐地图",
    rowClearTime: "回程 (秒)",
    rowClearTimePlaceholder: "可选",
    rowRemove: "删除",
    mapNotAvailable: "该宝箱无可用地图",
    languageLabel: "语言",
    difficulty: {
      Normal: "普通",
      Nightmare: "噩梦",
      Hell: "地狱",
      Torment: "折磨",
    },
  },
  ja: {
    rowTimerReady: "準備完了",
    alertVolumeLabel: "アラート音量",
    clearLogsButton: "クリア",
    footerDevelopedBy: "Developed by -Neath",
    footerWikiData:
      '宝箱・ステージデータは <a href="https://taskbarherowiki.com" target="_blank" rel="noopener noreferrer" class="font-medium text-amber-400 transition hover:text-amber-300">TaskBar Hero Wiki</a>（ファンメイド、非公式）に基づきます。',
    rowBossTimer: "ボス",
    rowCommonTimer: "通常",
    rowMap: "マップ",
    rowRecommendedMap: "推奨マップ",
    rowClearTime: "復帰 (秒)",
    rowClearTimePlaceholder: "任意",
    rowRemove: "削除",
    mapNotAvailable: "この宝箱にマップがありません",
    languageLabel: "言語",
    difficulty: {
      Normal: "ノーマル",
      Nightmare: "ナイトメア",
      Hell: "ヘル",
      Torment: "トーメント",
    },
  },
};

const TRACKER_KEYS = {
  "pt-BR": {
    pageTitle: "TBH Live Tracker",
    brandSubtitle: "Live Tracker",
    navManualTimer: "Timer manual",
    navLiveTracker: "Live Tracker",
    navAutoBadge: "Auto",
    setupTitle: "Conecte o Player.log",
    setupDescription:
      "Selecione o log do Taskbar Hero. Drops sao detectados automaticamente.",
    setupBrowserWarning:
      'Seu navegador nao suporta monitoramento ao vivo. Use <strong class="text-amber-50">Chrome</strong> ou <strong class="text-amber-50">Edge</strong>.',
    setupStep1Title: "Copie a pasta do log",
    setupStep1Hint: "Cole no Explorer para abrir rapidamente.",
    setupCopyButton: "Copiar",
    setupCopied: "Copiado!",
    setupStep2Title: "Selecione o Player.log",
    setupStep2Hint:
      'Escolha o arquivo <span class="font-mono text-[#E5E7EB]">Player.log</span>, nao a pasta.',
    setupStep3Title: "Mantenha a aba aberta",
    setupStep3Hint: "Leitura a cada 2s enquanto voce joga.",
    setupConnectButton: "Selecionar Player.log",
    setupConnectOpening: "Abrindo arquivo...",
    setupFooterHint: "Chrome ou Edge · Leitura local, nada e enviado ao servidor",
    tabMonitor: "Monitoramento",
    browserWarning:
      "Seu navegador nao suporta monitoramento ao vivo. Use Chrome ou Edge.",
    monitorStatusActive: "Monitoramento ativo",
    monitorStatusInactive: "Monitoramento inativo",
    disconnectButton: "Desconectar",
    metaLastPoll: "Ultima leitura",
    logResetNotice:
      "O Player.log foi reiniciado pelo jogo. O tracker se reajustou automaticamente.",
    bossSoundLabel: "Som bau chefe",
    commonSoundLabel: "Som bau comum",
    eventsTitle: "Eventos",
    newEventsInSessionSuffix: "nesta sessao",
    filterLabel: "Filtro",
    filterAll: "Todos",
    chestTypeActBoss: "Act Boss",
    colTime: "Horario",
    colLevel: "Level",
    colChest: "Bau",
    colType: "Tipo",
    eventsEmptyDisconnected:
      "Nenhum evento ainda. Conecte o Player.log para comecar.",
    eventsEmptyMonitoring:
      "Monitorando ativamente — aguardando o proximo drop de bau no jogo.",
    eventsEmptyFilter: "Nenhum evento neste filtro.",
    timersSectionTitle: "Cooldown dos baus",
    timersSectionDesc:
      'Chefe <strong class="text-[#E5E7EB]">7 min</strong> · Comum <strong class="text-[#E5E7EB]">5 min</strong>. Defina a <strong class="text-[#E5E7EB]">Volta (s)</strong> — tempo de conclusao do mapa — para cada nivel.',
    timersSectionNote:
      'Os baus aparecem aqui <strong class="text-[#E5E7EB]">automaticamente ao dropar</strong> no jogo. Os tempos de cooldown serao sincronizados com o <strong class="text-[#E5E7EB]">servidor do jogo</strong>.',
    timersActiveTitle: "Em cooldown",
    timersActiveHint: "Chefe: rotacao · Comum: ate dropar",
    timersEmpty:
      "Nenhum bau ainda. Quando um drop for detectado, o nivel aparece aqui com o cronometro iniciado.",
    sessionTitle: "Sessao",
    sessionStart: "Inicio",
    sessionDuration: "Duracao",
    sessionMonitoring: "Monitoramento",
    sessionStatusActive: "Ativo",
    sessionStatusStopped: "Parado",
    sessionChestsCollected: "Baus pegos",
    chestsPerHour: "Baus/hora",
    lastEvent: "Ultimo evento",
    summaryTitle: "Resumo",
    summaryBossChests: "Baus chefe",
    summaryCommonChests: "Baus comuns",
    tipsTitle: "Dicas do tracker",
    tipsHtml:
      '<p>Defina a <strong class="text-[#E5E7EB]">Volta (s)</strong> — tempo de conclusao do mapa — para cada nivel. O mapa com <strong class="text-[#E5E7EB]">★</strong> e a fase recomendada automaticamente.</p><p>Quando um bau dropar, o evento aparece na tabela e o cronometro e iniciado automaticamente.</p><p>Clique em <strong class="text-[#E5E7EB]">Desconectar</strong> para trocar o arquivo.</p>',
    clearTimeHint: "Volta: {seconds}s",
    levelLabel: "Level {level}",
    chestLevelLabel: "Bau Lv {level}",
    alertOpenFileFailed: "Nao foi possivel abrir o arquivo. Tente novamente.",
    alertCatalogLoadFailed: "Erro ao carregar catalogo de baus.",
  },
  en: {
    pageTitle: "TBH Live Tracker",
    brandSubtitle: "Live Tracker",
    navManualTimer: "Manual timer",
    navLiveTracker: "Live Tracker",
    navAutoBadge: "Auto",
    setupTitle: "Connect Player.log",
    setupDescription:
      "Select the Taskbar Hero log file. Drops are detected automatically.",
    setupBrowserWarning:
      'Your browser does not support live monitoring. Use <strong class="text-amber-50">Chrome</strong> or <strong class="text-amber-50">Edge</strong>.',
    setupStep1Title: "Copy the log folder path",
    setupStep1Hint: "Paste it in Explorer to open quickly.",
    setupCopyButton: "Copy",
    setupCopied: "Copied!",
    setupStep2Title: "Select Player.log",
    setupStep2Hint:
      'Choose the <span class="font-mono text-[#E5E7EB]">Player.log</span> file, not the folder.',
    setupStep3Title: "Keep this tab open",
    setupStep3Hint: "Polls every 2s while you play.",
    setupConnectButton: "Select Player.log",
    setupConnectOpening: "Opening file...",
    setupFooterHint: "Chrome or Edge · Local read only, nothing is sent to a server",
    tabMonitor: "Monitoring",
    browserWarning:
      "Your browser does not support live monitoring. Use Chrome or Edge.",
    monitorStatusActive: "Monitoring active",
    monitorStatusInactive: "Monitoring inactive",
    disconnectButton: "Disconnect",
    metaLastPoll: "Last read",
    logResetNotice:
      "Player.log was reset by the game. The tracker adjusted automatically.",
    bossSoundLabel: "Boss chest sound",
    commonSoundLabel: "Common chest sound",
    eventsTitle: "Events",
    newEventsInSessionSuffix: "this session",
    filterLabel: "Filter",
    filterAll: "All",
    chestTypeActBoss: "Act Boss",
    colTime: "Time",
    colLevel: "Level",
    colChest: "Chest",
    colType: "Type",
    eventsEmptyDisconnected:
      "No events yet. Connect Player.log to get started.",
    eventsEmptyMonitoring:
      "Actively monitoring — waiting for the next chest drop in game.",
    eventsEmptyFilter: "No events in this filter.",
    timersSectionTitle: "Chest cooldowns",
    timersSectionDesc:
      'Boss <strong class="text-[#E5E7EB]">7 min</strong> · Common <strong class="text-[#E5E7EB]">5 min</strong>. Set <strong class="text-[#E5E7EB]">Clear (s)</strong> — map completion time — per level.',
    timersSectionNote:
      'Chests appear here <strong class="text-[#E5E7EB]">automatically when they drop</strong> in-game. Cooldown values sync with the <strong class="text-[#E5E7EB]">game server</strong>.',
    timersActiveTitle: "On cooldown",
    timersActiveHint: "Boss: rotation · Common: until drop",
    timersEmpty:
      "No chests yet. When a drop is detected, the level appears here with the timer started.",
    sessionTitle: "Session",
    sessionStart: "Start",
    sessionDuration: "Duration",
    sessionMonitoring: "Monitoring",
    sessionStatusActive: "Active",
    sessionStatusStopped: "Stopped",
    sessionChestsCollected: "Chests collected",
    chestsPerHour: "Chests/hour",
    lastEvent: "Last event",
    summaryTitle: "Summary",
    summaryBossChests: "Boss chests",
    summaryCommonChests: "Common chests",
    tipsTitle: "Tracker tips",
    tipsHtml:
      '<p>Set <strong class="text-[#E5E7EB]">Clear (s)</strong> — map completion time — per level. The <strong class="text-[#E5E7EB]">★</strong> map is picked automatically as the recommended stage.</p><p>When a chest drops, the event appears in the table and the timer starts automatically.</p><p>Click <strong class="text-[#E5E7EB]">Disconnect</strong> to switch the log file.</p>',
    clearTimeHint: "Return: {seconds}s",
    levelLabel: "Level {level}",
    chestLevelLabel: "Chest Lv {level}",
    alertOpenFileFailed: "Could not open the file. Please try again.",
    alertCatalogLoadFailed: "Error loading chest catalog.",
  },
  es: {
    pageTitle: "TBH Live Tracker",
    brandSubtitle: "Live Tracker",
    navManualTimer: "Timer manual",
    navLiveTracker: "Live Tracker",
    navAutoBadge: "Auto",
    setupTitle: "Conecta Player.log",
    setupDescription:
      "Selecciona el log de Taskbar Hero. Los drops se detectan automaticamente.",
    setupBrowserWarning:
      'Tu navegador no admite monitoreo en vivo. Usa <strong class="text-amber-50">Chrome</strong> o <strong class="text-amber-50">Edge</strong>.',
    setupStep1Title: "Copia la carpeta del log",
    setupStep1Hint: "Pegala en el Explorador para abrir rapido.",
    setupCopyButton: "Copiar",
    setupCopied: "Copiado!",
    setupStep2Title: "Selecciona Player.log",
    setupStep2Hint:
      'Elige el archivo <span class="font-mono text-[#E5E7EB]">Player.log</span>, no la carpeta.',
    setupStep3Title: "Mantén esta pestaña abierta",
    setupStep3Hint: "Lee cada 2 s mientras juegas.",
    setupConnectButton: "Seleccionar Player.log",
    setupConnectOpening: "Abriendo archivo...",
    setupFooterHint: "Chrome o Edge · Lectura local, nada se envia al servidor",
    tabMonitor: "Monitoreo",
    browserWarning:
      "Tu navegador no admite monitoreo en vivo. Usa Chrome o Edge.",
    monitorStatusActive: "Monitoreo activo",
    monitorStatusInactive: "Monitoreo inactivo",
    disconnectButton: "Desconectar",
    metaLastPoll: "Ultima lectura",
    logResetNotice:
      "Player.log fue reiniciado por el juego. El tracker se reajusto automaticamente.",
    bossSoundLabel: "Sonido cofre jefe",
    commonSoundLabel: "Sonido cofre comun",
    eventsTitle: "Eventos",
    newEventsInSessionSuffix: "en esta sesion",
    filterLabel: "Filtro",
    filterAll: "Todos",
    chestTypeActBoss: "Act Boss",
    colTime: "Hora",
    colLevel: "Nivel",
    colChest: "Cofre",
    colType: "Tipo",
    eventsEmptyDisconnected:
      "Sin eventos aun. Conecta Player.log para empezar.",
    eventsEmptyMonitoring:
      "Monitoreando activamente — esperando el proximo drop de cofre en el juego.",
    eventsEmptyFilter: "Ningun evento en este filtro.",
    timersSectionTitle: "Cooldown de cofres",
    timersSectionDesc:
      'Jefe <strong class="text-[#E5E7EB]">7 min</strong> · Comun <strong class="text-[#E5E7EB]">5 min</strong>. Define la <strong class="text-[#E5E7EB]">Vuelta (s)</strong> — tiempo de conclusion del mapa — por nivel.',
    timersSectionNote:
      'Los cofres aparecen aqui <strong class="text-[#E5E7EB]">automaticamente al dropear</strong> en el juego. Los tiempos de cooldown se sincronizaran con el <strong class="text-[#E5E7EB]">servidor del juego</strong>.',
    timersActiveTitle: "En cooldown",
    timersActiveHint: "Jefe: rotacion · Comun: hasta dropear",
    timersEmpty:
      "Ningun cofre aun. Cuando se detecte un drop, el nivel aparece aqui con el cronometro iniciado.",
    sessionTitle: "Sesion",
    sessionStart: "Inicio",
    sessionDuration: "Duracion",
    sessionMonitoring: "Monitoreo",
    sessionStatusActive: "Activo",
    sessionStatusStopped: "Detenido",
    sessionChestsCollected: "Cofres obtenidos",
    chestsPerHour: "Cofres/hora",
    lastEvent: "Ultimo evento",
    summaryTitle: "Resumen",
    summaryBossChests: "Cofres jefe",
    summaryCommonChests: "Cofres comunes",
    tipsTitle: "Consejos del tracker",
    tipsHtml:
      '<p>Define la <strong class="text-[#E5E7EB]">Vuelta (s)</strong> — tiempo de conclusion del mapa — por nivel. El mapa con <strong class="text-[#E5E7EB]">★</strong> es la fase recomendada automaticamente.</p><p>Cuando cae un cofre, el evento aparece en la tabla y el timer se inicia automaticamente.</p><p>Haz clic en <strong class="text-[#E5E7EB]">Desconectar</strong> para cambiar el archivo.</p>',
    clearTimeHint: "Vuelta: {seconds}s",
    levelLabel: "Nivel {level}",
    chestLevelLabel: "Cofre Lv {level}",
    alertOpenFileFailed: "No se pudo abrir el archivo. Intenta de nuevo.",
    alertCatalogLoadFailed: "Error al cargar el catalogo de cofres.",
  },
  fr: {
    pageTitle: "TBH Live Tracker",
    brandSubtitle: "Live Tracker",
    navManualTimer: "Timer manuel",
    navLiveTracker: "Live Tracker",
    navAutoBadge: "Auto",
    setupTitle: "Connectez Player.log",
    setupDescription:
      "Selectionnez le log Taskbar Hero. Les drops sont detectes automatiquement.",
    setupBrowserWarning:
      'Votre navigateur ne prend pas en charge la surveillance en direct. Utilisez <strong class="text-amber-50">Chrome</strong> ou <strong class="text-amber-50">Edge</strong>.',
    setupStep1Title: "Copiez le dossier du log",
    setupStep1Hint: "Collez-le dans l'Explorateur pour l'ouvrir rapidement.",
    setupCopyButton: "Copier",
    setupCopied: "Copie !",
    setupStep2Title: "Selectionnez Player.log",
    setupStep2Hint:
      'Choisissez le fichier <span class="font-mono text-[#E5E7EB]">Player.log</span>, pas le dossier.',
    setupStep3Title: "Gardez cet onglet ouvert",
    setupStep3Hint: "Lecture toutes les 2 s pendant que vous jouez.",
    setupConnectButton: "Selectionner Player.log",
    setupConnectOpening: "Ouverture du fichier...",
    setupFooterHint: "Chrome ou Edge · Lecture locale, rien n'est envoye au serveur",
    tabMonitor: "Surveillance",
    browserWarning:
      "Votre navigateur ne prend pas en charge la surveillance en direct. Utilisez Chrome ou Edge.",
    monitorStatusActive: "Surveillance active",
    monitorStatusInactive: "Surveillance inactive",
    disconnectButton: "Deconnecter",
    metaLastPoll: "Derniere lecture",
    logResetNotice:
      "Player.log a ete reinitialise par le jeu. Le tracker s'est ajuste automatiquement.",
    bossSoundLabel: "Son coffre boss",
    commonSoundLabel: "Son coffre commun",
    eventsTitle: "Evenements",
    newEventsInSessionSuffix: "cette session",
    filterLabel: "Filtre",
    filterAll: "Tous",
    chestTypeActBoss: "Act Boss",
    colTime: "Heure",
    colLevel: "Niveau",
    colChest: "Coffre",
    colType: "Type",
    eventsEmptyDisconnected:
      "Aucun evenement pour l'instant. Connectez Player.log pour commencer.",
    eventsEmptyMonitoring:
      "Surveillance active — en attente du prochain drop de coffre en jeu.",
    eventsEmptyFilter: "Aucun evenement dans ce filtre.",
    timersSectionTitle: "Cooldown des coffres",
    timersSectionDesc:
      'Boss <strong class="text-[#E5E7EB]">7 min</strong> · Commun <strong class="text-[#E5E7EB]">5 min</strong>. Definissez le <strong class="text-[#E5E7EB]">Retour (s)</strong> — temps de fin de carte — par niveau.',
    timersSectionNote:
      'Les coffres apparaissent ici <strong class="text-[#E5E7EB]">automatiquement au drop</strong> en jeu. Les temps de cooldown seront synchronises avec le <strong class="text-[#E5E7EB]">serveur du jeu</strong>.',
    timersActiveTitle: "En cooldown",
    timersActiveHint: "Boss : rotation · Commun : jusqu'au drop",
    timersEmpty:
      "Aucun coffre pour l'instant. Quand un drop est detecte, le niveau apparait ici avec le chrono demarre.",
    sessionTitle: "Session",
    sessionStart: "Debut",
    sessionDuration: "Duree",
    sessionMonitoring: "Surveillance",
    sessionStatusActive: "Actif",
    sessionStatusStopped: "Arrete",
    sessionChestsCollected: "Coffres obtenus",
    chestsPerHour: "Coffres/heure",
    lastEvent: "Dernier evenement",
    summaryTitle: "Resume",
    summaryBossChests: "Coffres boss",
    summaryCommonChests: "Coffres communs",
    tipsTitle: "Astuces du tracker",
    tipsHtml:
      '<p>Configurez la carte suggeree et le <strong class="text-[#E5E7EB]">Retour (s)</strong> (temps de fin de carte) dans le panneau de cooldown avant ou apres le drop.</p><p>Quand un coffre tombe, l\'evenement apparait dans le tableau et le chrono demarre automatiquement.</p><p>Cliquez sur <strong class="text-[#E5E7EB]">Deconnecter</strong> pour changer de fichier.</p>',
    clearTimeHint: "Retour : {seconds}s",
    levelLabel: "Niveau {level}",
    chestLevelLabel: "Coffre Lv {level}",
    alertOpenFileFailed: "Impossible d'ouvrir le fichier. Reessayez.",
    alertCatalogLoadFailed: "Erreur lors du chargement du catalogue de coffres.",
  },
  zh: {
    pageTitle: "TBH Live Tracker",
    brandSubtitle: "Live Tracker",
    navManualTimer: "手动计时",
    navLiveTracker: "Live Tracker",
    navAutoBadge: "自动",
    setupTitle: "连接 Player.log",
    setupDescription: "选择 Taskbar Hero 日志。掉落会自动检测。",
    setupBrowserWarning:
      '您的浏览器不支持实时监控。请使用 <strong class="text-amber-50">Chrome</strong> 或 <strong class="text-amber-50">Edge</strong>。',
    setupStep1Title: "复制日志文件夹路径",
    setupStep1Hint: "粘贴到资源管理器以快速打开。",
    setupCopyButton: "复制",
    setupCopied: "已复制！",
    setupStep2Title: "选择 Player.log",
    setupStep2Hint:
      '选择 <span class="font-mono text-[#E5E7EB]">Player.log</span> 文件，而非文件夹。',
    setupStep3Title: "保持此标签页打开",
    setupStep3Hint: "游戏时每 2 秒读取一次。",
    setupConnectButton: "选择 Player.log",
    setupConnectOpening: "正在打开文件...",
    setupFooterHint: "Chrome 或 Edge · 仅本地读取，不会发送到服务器",
    tabMonitor: "监控",
    browserWarning: "您的浏览器不支持实时监控。请使用 Chrome 或 Edge。",
    monitorStatusActive: "监控已启用",
    monitorStatusInactive: "监控未启用",
    disconnectButton: "断开连接",
    metaLastPoll: "上次读取",
    logResetNotice: "游戏已重置 Player.log。追踪器已自动调整。",
    bossSoundLabel: "首领宝箱提示音",
    commonSoundLabel: "普通宝箱提示音",
    eventsTitle: "事件",
    newEventsInSessionSuffix: "本次会话",
    filterLabel: "筛选",
    filterAll: "全部",
    chestTypeActBoss: "Act Boss",
    colTime: "时间",
    colLevel: "等级",
    colChest: "宝箱",
    colType: "类型",
    eventsEmptyDisconnected: "尚无事件。连接 Player.log 以开始。",
    eventsEmptyMonitoring: "正在积极监控 — 等待游戏中的下一个宝箱掉落。",
    eventsEmptyFilter: "此筛选下无事件。",
    timersSectionTitle: "宝箱冷却",
    timersSectionDesc:
      '首领 <strong class="text-[#E5E7EB]">7 分钟</strong> · 普通 <strong class="text-[#E5E7EB]">5 分钟</strong>。为每个等级设置 <strong class="text-[#E5E7EB]">回程 (秒)</strong> — 地图通关时间。',
    timersSectionNote:
      '宝箱会在游戏中<strong class="text-[#E5E7EB]">掉落时自动出现</strong>于此。冷却时间将与<strong class="text-[#E5E7EB]">游戏服务器</strong>同步更新。',
    timersActiveTitle: "冷却中",
    timersActiveHint: "首领：轮换 · 普通：直至掉落",
    timersEmpty: "尚无宝箱。检测到掉落时，等级会在此显示并自动启动计时器。",
    sessionTitle: "会话",
    sessionStart: "开始",
    sessionDuration: "时长",
    sessionMonitoring: "监控",
    sessionStatusActive: "活动中",
    sessionStatusStopped: "已停止",
    sessionChestsCollected: "已获得宝箱",
    chestsPerHour: "宝箱/小时",
    lastEvent: "最近事件",
    summaryTitle: "摘要",
    summaryBossChests: "首领宝箱",
    summaryCommonChests: "普通宝箱",
    tipsTitle: "追踪器提示",
    tipsHtml:
      '<p>为每个等级设置 <strong class="text-[#E5E7EB]">回程 (秒)</strong>（地图通关时间）。带 <strong class="text-[#E5E7EB]">★</strong> 的地图会自动选为推荐关卡。</p><p>宝箱掉落时，事件会出现在表格中，计时器会自动启动。</p><p>点击 <strong class="text-[#E5E7EB]">断开连接</strong> 以更换日志文件。</p>',
    clearTimeHint: "回程：{seconds}秒",
    levelLabel: "等级 {level}",
    chestLevelLabel: "宝箱 Lv {level}",
    alertOpenFileFailed: "无法打开文件。请重试。",
    alertCatalogLoadFailed: "加载宝箱目录时出错。",
  },
  ja: {
    pageTitle: "TBH Live Tracker",
    brandSubtitle: "Live Tracker",
    navManualTimer: "手動タイマー",
    navLiveTracker: "Live Tracker",
    navAutoBadge: "自動",
    setupTitle: "Player.log を接続",
    setupDescription:
      "Taskbar Hero のログを選択してください。ドロップは自動検出されます。",
    setupBrowserWarning:
      'お使いのブラウザはライブ監視に対応していません。<strong class="text-amber-50">Chrome</strong> または <strong class="text-amber-50">Edge</strong> をご利用ください。',
    setupStep1Title: "ログフォルダのパスをコピー",
    setupStep1Hint: "エクスプローラーに貼り付けて素早く開きます。",
    setupCopyButton: "コピー",
    setupCopied: "コピーしました！",
    setupStep2Title: "Player.log を選択",
    setupStep2Hint:
      'フォルダではなく <span class="font-mono text-[#E5E7EB]">Player.log</span> ファイルを選んでください。',
    setupStep3Title: "このタブを開いたままにする",
    setupStep3Hint: "プレイ中は 2 秒ごとに読み取ります。",
    setupConnectButton: "Player.log を選択",
    setupConnectOpening: "ファイルを開いています...",
    setupFooterHint: "Chrome または Edge · ローカル読み取りのみ、サーバーには送信されません",
    tabMonitor: "監視",
    browserWarning:
      "お使いのブラウザはライブ監視に対応していません。Chrome または Edge をご利用ください。",
    monitorStatusActive: "監視中",
    monitorStatusInactive: "監視停止",
    disconnectButton: "切断",
    metaLastPoll: "最終読み取り",
    logResetNotice:
      "ゲームにより Player.log がリセットされました。トラッカーは自動調整しました。",
    bossSoundLabel: "ボス宝箱サウンド",
    commonSoundLabel: "通常宝箱サウンド",
    eventsTitle: "イベント",
    newEventsInSessionSuffix: "このセッション",
    filterLabel: "フィルター",
    filterAll: "すべて",
    chestTypeActBoss: "Act Boss",
    colTime: "時刻",
    colLevel: "レベル",
    colChest: "宝箱",
    colType: "種類",
    eventsEmptyDisconnected:
      "イベントはまだありません。Player.log を接続して開始してください。",
    eventsEmptyMonitoring:
      "積極的に監視中 — ゲーム内の次の宝箱ドロップを待っています。",
    eventsEmptyFilter: "このフィルターにイベントはありません。",
    timersSectionTitle: "宝箱クールダウン",
    timersSectionDesc:
      'ボス <strong class="text-[#E5E7EB]">7 分</strong> · 通常 <strong class="text-[#E5E7EB]">5 分</strong>。レベルごとに <strong class="text-[#E5E7EB]">復帰 (秒)</strong> — マップクリア時間 — を設定します。',
    timersSectionNote:
      '宝箱はゲーム内で<strong class="text-[#E5E7EB]">ドロップすると自動的に表示</strong>されます。クールダウン時間は<strong class="text-[#E5E7EB]">ゲームサーバー</strong>と同期更新されます。',
    timersActiveTitle: "クールダウン中",
    timersActiveHint: "ボス：ローテーション · 通常：ドロップまで",
    timersEmpty:
      "宝箱はまだありません。ドロップが検出されると、レベルがここに表示されタイマーが開始されます。",
    sessionTitle: "セッション",
    sessionStart: "開始",
    sessionDuration: "経過時間",
    sessionMonitoring: "監視",
    sessionStatusActive: "アクティブ",
    sessionStatusStopped: "停止",
    sessionChestsCollected: "取得した宝箱",
    chestsPerHour: "宝箱/時間",
    lastEvent: "最終イベント",
    summaryTitle: "概要",
    summaryBossChests: "ボス宝箱",
    summaryCommonChests: "通常宝箱",
    tipsTitle: "トラッカーのヒント",
    tipsHtml:
      '<p>レベルごとに <strong class="text-[#E5E7EB]">復帰 (秒)</strong>（マップクリア時間）を設定してください。<strong class="text-[#E5E7EB]">★</strong> のマップが推奨ステージとして自動選択されます。</p><p>宝箱がドロップすると、イベントがテーブルに表示され、タイマーが自動的に開始されます。</p><p><strong class="text-[#E5E7EB]">切断</strong> をクリックしてログファイルを変更します。</p>',
    clearTimeHint: "復帰: {seconds}秒",
    levelLabel: "レベル {level}",
    chestLevelLabel: "宝箱 Lv {level}",
    alertOpenFileFailed: "ファイルを開けませんでした。もう一度お試しください。",
    alertCatalogLoadFailed: "宝箱カタログの読み込みエラー。",
  },
};

function mergeBuckets() {
  const languages = Object.keys(TRACKER_KEYS);
  const merged = {};
  for (const lang of languages) {
    merged[lang] = { ...SHARED_KEYS[lang], ...TRACKER_KEYS[lang] };
  }
  return merged;
}

export const TRACKER_I18N = mergeBuckets();

function isSupportedLanguage(code) {
  return Boolean(code && TRACKER_I18N[code]);
}

export function loadLanguagePreference() {
  try {
    const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (isSupportedLanguage(saved)) return saved;
  } catch {
    /* ignore */
  }
  return "pt-BR";
}

export function saveLanguagePreference(language) {
  if (!isSupportedLanguage(language)) return;
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  } catch {
    /* ignore */
  }
}

export function createTrackerI18n(initialLanguage = loadLanguagePreference()) {
  let currentLanguage = isSupportedLanguage(initialLanguage)
    ? initialLanguage
    : "pt-BR";

  function t(key, vars = {}) {
    const bucket = TRACKER_I18N[currentLanguage] ?? TRACKER_I18N.en;
    let text = bucket[key] ?? TRACKER_I18N.en[key] ?? key;
    for (const [name, value] of Object.entries(vars)) {
      text = text.replaceAll(`{${name}}`, String(value));
    }
    return text;
  }

  function getLocale() {
    return LOCALE_BY_LANGUAGE[currentLanguage] ?? "en-US";
  }

  function localizeDifficulty(difficulty) {
    const bucket = TRACKER_I18N[currentLanguage] ?? TRACKER_I18N.en;
    return bucket.difficulty?.[difficulty] ?? difficulty;
  }

  function applyStaticTranslations(root = document) {
    root.querySelectorAll("[data-i18n]").forEach((element) => {
      element.textContent = t(element.dataset.i18n);
    });
    root.querySelectorAll("[data-i18n-html]").forEach((element) => {
      element.innerHTML = t(element.dataset.i18nHtml);
    });
    root.querySelectorAll("[data-i18n-option]").forEach((element) => {
      element.textContent = t(element.dataset.i18nOption);
    });
    root.querySelectorAll("[data-i18n-aria]").forEach((element) => {
      element.setAttribute("aria-label", t(element.dataset.i18nAria));
    });
  }

  function applyLanguage({ onAfterApply } = {}) {
    document.documentElement.lang = currentLanguage;
    document.title = t("pageTitle");
    applyStaticTranslations();
    onAfterApply?.();
  }

  function setLanguage(language) {
    if (!isSupportedLanguage(language)) return;
    currentLanguage = language;
    saveLanguagePreference(language);
    applyLanguage();
  }

  function getLanguage() {
    return currentLanguage;
  }

  return {
    t,
    getLocale,
    applyLanguage,
    setLanguage,
    getLanguage,
    saveLanguagePreference,
    loadLanguagePreference,
    localizeDifficulty,
  };
}
