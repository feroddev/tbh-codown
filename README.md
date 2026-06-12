# TBH Monitor

Ferramentas de apoio ao farm de baús de chefe em **Taskbar Hero** (Tesseract Studio). O projeto inclui um aplicativo desktop para Windows e um site estático com funções semelhantes.

## O que é cada parte

### TBH Monitor (desktop)

Aplicativo Windows que monitora o jogo em tempo real e ajuda na rotação entre mapas de farm.

- Lê o `Player.log` e o save (`SaveFile_Live.es3` e backups de rotação) automaticamente
- Detecta drops de baú de chefe (e baú comum, se habilitado)
- Inicia cronômetros por nível de baú (Lv 65, 50, 40, 30…)
- Indica o próximo mapa da rotação configurada
- Interface gráfica com timers, farm por baú e log de eventos

### Web Monitor (`web-monitor/`)

Site estático hospedado via GitHub Pages. Oferece praticamente as mesmas funções de planejamento:

- Cronômetros de baús por nível e mapa
- Guia de rota e recomendações de farm
- Suporte a idiomas (pt-BR, en, es, fr, zh, ja)

A diferença principal: no site você confirma o drop manualmente com **"Baú dropou"**. No desktop, isso acontece automaticamente ao ler os logs do jogo.

O site também disponibiliza o download do TBH Monitor (`TBH-Monitor.zip`).

## Requisitos

- **Desktop:** Windows 10+, Taskbar Hero instalado (Steam)
- **Desenvolvimento:** Python 3.10+
- **Site:** navegador moderno (sem backend)

## Configuração do desktop

As configurações ficam em `config.yaml`, ao lado do executável (ou na raiz do projeto em desenvolvimento).

Na primeira execução, o app tenta detectar automaticamente os caminhos do jogo. Você também pode ajustar pela interface gráfica e salvar.

Exemplo mínimo:

```yaml
paths:
  player_log: C:/Users/SEU_USUARIO/AppData/LocalLow/TesseractStudio/TaskbarHero/Player.log
  save_file: C:/Users/Usuario/AppData/LocalLow/TesseractStudio/TaskbarHero/SaveFile_Live.es3
  state_file: state.json
  es3_password: emuMqG3bLYJ938ZDCfieWJ

monitor:
  poll_interval_seconds: 0.5
  save_poll_interval_seconds: 2.0
  debounce_seconds: 4.0
  average_drop_minutes: 12.0
  window_title: TaskBarHero
  dry_run: false

strategy:
  consider_common_chest: true

ui:
  language: pt-BR

chest_farms:
  - chest_level: 65
    stage_key: 3205
    enabled: true
    priority: 1
  - chest_level: 50
    stage_key: 2305
    enabled: true
    priority: 2
  - chest_level: 40
    stage_key: 2109
    enabled: true
    priority: 3
  - chest_level: 30
    stage_key: 1308
    enabled: true
    priority: 4
```

### Campos principais

| Seção | Descrição |
|-------|-----------|
| `paths.player_log` | Log do Unity (`Player.log`) |
| `paths.save_file` | Save principal do jogo |
| `paths.state_file` | Estado persistido do monitor (rotação, timers) |
| `paths.es3_password` | Senha do save ES3 (detectada automaticamente se omitida) |
| `chest_farms` | Baús monitorados, mapa (`stage_key`) e ordem de rotação (`priority`: 1 = maior prioridade) |
| `strategy.consider_common_chest` | Se `true`, baús comuns também são detectados |
| `monitor.dry_run` | Detecta drops sem sugerir troca de mapa |

Para verificar caminhos detectados:

```bash
python -m src.main paths
```

Para consultar o stage atual do save:

```bash
python -m src.main status
```

## Desenvolvimento local (desktop)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m src.main gui
```

Outros comandos:

```bash
python -m src.main monitor    # monitor no terminal
python -m src.main status     # stage e contagem de baús
python -m src.main paths      # caminhos detectados do jogo
```

### Build do executável

```bash
build.bat
```

O build gera `dist/TBH-Monitor/TBH-Monitor.exe` com `config.yaml` incluído.

### Testes

```bash
venv\Scripts\python.exe -m unittest discover -s tests -q
```

## Site (`web-monitor/`)

Conteúdo estático em `web-monitor/index.html`. Para usar localmente, abra o arquivo no navegador ou sirva a pasta com qualquer servidor estático.

Deploy automático para GitHub Pages ao fazer push na branch `main`/`master` com alterações em `web-monitor/` (workflow `.github/workflows/deploy-web-monitor-pages.yml`).

O estado do site (timers, idioma, duração) fica no `localStorage` do navegador.

## Estrutura do repositório

```
tbh/
├── src/                 # Código do TBH Monitor (desktop)
├── web-monitor/         # Site estático + TBH-Monitor.zip
├── tests/               # Testes unitários
├── scripts/             # Build e utilitários
├── config.yaml          # Configuração de desenvolvimento
└── TBH-Monitor.spec     # PyInstaller
```

## Jogo suportado

**Taskbar Hero** — arquivos em `%USERPROFILE%/AppData/LocalLow/TesseractStudio/TaskbarHero/`.
