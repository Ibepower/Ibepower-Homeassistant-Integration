// =============================================================================
// Ibepower Custom Lovelace Cards v1.0.0
// Appears automatically in the Home Assistant card picker.
// Three card types: IBePlug, IBEDiv, IBEMeter
// =============================================================================

const IBEP_CARD_VERSION = '1.0.0';

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------
function ibepI18n(hass) {
  const bl = (typeof navigator !== 'undefined' && navigator.language) || '';
  const raw = String(
    hass?.language || hass?.selectedLanguage || hass?.locale?.language || bl || 'en'
  ).toLowerCase();
  const lang = raw.startsWith('es') ? 'es' : raw.startsWith('pt') ? 'pt' : 'en';
  const dict = {
    es: {
      on:'Encendido', off:'Apagado', today:'Hoy', yesterday:'Ayer', total:'Total',
      power:'Potencia', voltage:'Tensión', current:'Intensidad', pf:'Factor P.',
      energy:'Energía', peak:'Máx', nodev:'Sin dispositivos detectados',
      importing:'Importando', exporting:'Exportando', imp:'Imp', exp:'Exp',
      consumption:'Consumo', solar:'Solar', grid:'Red', home:'Casa', battery:'Batería',
      load:'Carga', diverter:'Derivador', auto:'Auto', manual:'Manual',
      manager:'Gestor', mode:'Modo', pwm:'PWM', soc:'SOC',
      select_device:'Seleccionar dispositivo', all_auto:'Auto (todos)',
      frequency:'Frecuencia',
      loading_devices:'Cargando dispositivos…',
      auto_detected_one:'Auto ({count} detectado)',
      auto_detected_other:'Auto ({count} detectados)',
      auto_hint:'Dejar en "Auto" para detectar automáticamente',
    },
    en: {
      on:'On', off:'Off', today:'Today', yesterday:'Yesterday', total:'Total',
      power:'Power', voltage:'Voltage', current:'Current', pf:'Power F.',
      energy:'Energy', peak:'Peak', nodev:'No devices detected',
      importing:'Importing', exporting:'Exporting', imp:'Imp', exp:'Exp',
      consumption:'Consumption', solar:'Solar', grid:'Grid', home:'Home', battery:'Battery',
      load:'Load', diverter:'Diverter', auto:'Auto', manual:'Manual',
      manager:'Manager', mode:'Mode', pwm:'PWM', soc:'SOC',
      select_device:'Select device', all_auto:'Auto (all)',
      frequency:'Frequency',
      loading_devices:'Loading devices…',
      auto_detected_one:'Auto ({count} detected)',
      auto_detected_other:'Auto ({count} detected)',
      auto_hint:'Leave on "Auto" for auto-detection',
    },
    pt: {
      on:'Ligado', off:'Desligado', today:'Hoje', yesterday:'Ontem', total:'Total',
      power:'Potência', voltage:'Tensão', current:'Corrente', pf:'Fator P.',
      energy:'Energia', peak:'Máx', nodev:'Nenhum dispositivo detectado',
      importing:'Importando', exporting:'Exportando', imp:'Imp', exp:'Exp',
      consumption:'Consumo', solar:'Solar', grid:'Rede', home:'Casa', battery:'Bateria',
      load:'Carga', diverter:'Desviador', auto:'Auto', manual:'Manual',
      manager:'Gestor', mode:'Modo', pwm:'PWM', soc:'SOC',
      select_device:'Selecionar dispositivo', all_auto:'Auto (todos)',
      frequency:'Frequência',
      loading_devices:'Carregando dispositivos…',
      auto_detected_one:'Auto ({count} detectado)',
      auto_detected_other:'Auto ({count} detectados)',
      auto_hint:'Deixe em "Auto" para detecção automática',
    },
  };
  return dict[lang] || dict.en;
}

function ibepGetSlugs(hass, model, markerField, entityDomain) {
  if (!hass?.devices || !hass?.entities) return [];
  const devIds = new Set(
    Object.values(hass.devices)
      .filter(d => d.model === model)
      .map(d => d.id)
  );
  const eids = Object.keys(hass.entities).filter(
    eid => eid.startsWith(entityDomain + '.') && devIds.has(hass.entities[eid]?.device_id)
  );
  const slugs = new Set();
  for (const eid of eids) {
    const suffix = eid.slice(entityDomain.length + 1);
    let m = suffix.match(new RegExp('^(.+)_' + markerField + '$'));
    if (m) { slugs.add(m[1]); continue; }
    m = suffix.match(new RegExp('^' + markerField + '_(.+)$'));
    if (m) { slugs.add(m[1]); }
  }
  return [...slugs].sort();
}

function ibepState(hass, base, field) {
  const e1 = hass?.states?.['sensor.' + base + '_' + field];
  const e2 = hass?.states?.['sensor.' + field + '_' + base];
  return e1 || e2 || null;
}

function ibepSwitchState(hass, base, suffix) {
  const e1 = hass?.states?.['switch.' + base + '_' + suffix];
  const e2 = hass?.states?.['switch.' + suffix + '_' + base];
  return e1 || e2 || null;
}

function ibepSwitchEid(hass, base, suffix) {
  if (hass?.states?.['switch.' + base + '_' + suffix]) return 'switch.' + base + '_' + suffix;
  if (hass?.states?.['switch.' + suffix + '_' + base]) return 'switch.' + suffix + '_' + base;
  return '';
}

function ibepSelectState(hass, base, field) {
  const e1 = hass?.states?.['select.' + base + '_' + field];
  const e2 = hass?.states?.['select.' + field + '_' + base];
  return e1 || e2 || null;
}

function ibepSelectEid(hass, base, field) {
  if (hass?.states?.['select.' + base + '_' + field]) return 'select.' + base + '_' + field;
  if (hass?.states?.['select.' + field + '_' + base]) return 'select.' + field + '_' + base;
  return '';
}

function ibepNumberState(hass, base, field) {
  const e1 = hass?.states?.['number.' + base + '_' + field];
  const e2 = hass?.states?.['number.' + field + '_' + base];
  return e1 || e2 || null;
}

function ibepNumberEid(hass, base, field) {
  if (hass?.states?.['number.' + base + '_' + field]) return 'number.' + base + '_' + field;
  if (hass?.states?.['number.' + field + '_' + base]) return 'number.' + field + '_' + base;
  return '';
}

function ibepValid(stateObj) {
  if (!stateObj) return false;
  const s = String(stateObj.state ?? '').trim().toLowerCase();
  return s && s !== 'unknown' && s !== 'unavailable' && s !== 'none' && s !== 'null';
}

function ibepNum(stateObj) {
  if (!ibepValid(stateObj)) return null;
  const v = Number(String(stateObj.state).replace(',', '.'));
  return Number.isFinite(v) ? v : null;
}

function ibepFmt(value, unit, digits) {
  if (value === null || value === undefined || !Number.isFinite(value)) return '-- ' + unit;
  return value.toFixed(digits) + ' ' + unit;
}

function ibepFmtK(value) { return ibepFmt(value, 'kWh', 2); }

function ibepLogoUrl(hass) {
  const base = '/ibepower_static/ibepower_logo.png';
  if (hass && typeof hass.hassUrl === 'function') return hass.hassUrl(base);
  return base;
}

function ibepIsCompactCard(cardEl, thresholdPx) {
  const w = Math.round(cardEl?.getBoundingClientRect?.().width || 0);
  return w > 0 && w <= thresholdPx;
}

// ---------------------------------------------------------------------------
// Shared CSS
// ---------------------------------------------------------------------------
const IBEP_SHARED_CSS = `
  :host {
    display: block;
    --ibep-green: #4cdf6b;
    --ibep-green-dim: rgba(76, 223, 107, 0.7);
    --ibep-bg: linear-gradient(145deg, rgba(38,118,58,0.92), rgba(52,148,74,0.90));
    --ibep-bg-overlay: radial-gradient(circle at 18% 14%, rgba(255,185,0,0.32), transparent 40%),
                        radial-gradient(circle at 84% 85%, rgba(0,210,255,0.22), transparent 44%),
                        radial-gradient(circle at 50% 88%, rgba(140,230,60,0.18), transparent 48%);
  }
  .card {
    border-radius: var(--ha-card-border-radius, 12px);
    padding: 16px;
    border: 1px solid rgba(120,220,80,0.90);
    background: var(--ibep-bg-overlay), var(--ibep-bg);
    box-shadow: 0 8px 32px rgba(0,0,0,0.58);
    color: #fff;
    font-family: inherit;
    box-sizing: border-box;
    overflow: hidden;
  }
  .logo-wrap {
    display: flex;
    justify-content: center;
    padding: 4px 0 8px;
  }
  .logo-wrap img {
    width: min(46vw, 180px);
    max-width: 100%;
    height: auto;
    object-fit: contain;
  }
  .device-name {
    text-align: center;
    font-size: 1.3rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    text-shadow: 0 1px 4px rgba(0,0,0,0.55);
    margin-bottom: 8px;
  }
  .no-devices {
    text-align: center;
    padding: 24px;
    font-size: 1.05rem;
    opacity: 0.8;
  }
  /* Dropdown selector */
  .dd { position: relative; width: 100%; max-width: 280px; margin: 0 auto 10px; z-index: 2; }
  .dd-header {
    display: flex; align-items: center; justify-content: center; position: relative;
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25);
    border-radius: 12px; padding: 8px 14px; cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
  }
  .dd-header:hover { border-color: var(--ibep-green-dim); background: rgba(255,255,255,0.18); }
  .dd.open .dd-header {
    border-color: var(--ibep-green-dim); background: rgba(255,255,255,0.18);
    border-radius: 12px 12px 0 0;
  }
  .dd-current {
    font-size: 1.25rem; font-weight: 700; color: #fff; text-transform: uppercase;
    letter-spacing: 0.04em; text-shadow: 0 1px 4px rgba(0,0,0,0.55);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .dd-arrow {
    position: absolute; right: 14px; top: 50%; transform: translateY(-50%);
    transition: transform 0.25s;
    --mdc-icon-size: 20px; color: rgba(255,255,255,0.6);
  }
  .dd.open .dd-arrow { transform: translateY(-50%) rotate(180deg); }
  .dd-list {
    max-height: 0; overflow: hidden; transition: max-height 0.3s, border-color 0.3s;
    background: rgba(20,35,20,0.96); border: none; border-radius: 0 0 12px 12px;
    backdrop-filter: blur(12px);
  }
  .dd.open .dd-list {
    max-height: 300px; border: 1px solid rgba(76,223,107,0.5); border-top: none;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  }
  .dd-option {
    padding: 10px 14px; font-size: 0.88rem; font-weight: 500;
    color: rgba(255,255,255,0.8); text-transform: capitalize; cursor: pointer;
    transition: background 0.15s;
  }
  .dd-option:hover { background: rgba(76,223,107,0.15); color: #fff; }
  .dd-option.active { color: var(--ibep-green); font-weight: 700; background: rgba(76,223,107,0.08); }
  .dd-option:last-child { border-radius: 0 0 12px 12px; }
  /* Metrics */
  .metrics { display: flex; justify-content: space-around; gap: 4px; margin: 8px 0; }
  .metric { text-align: center; flex: 1; }
  .metric-val { font-size: 1.05rem; font-weight: 600; margin-top: 2px; }
  .metric-lbl { font-size: 0.72rem; opacity: 0.7; margin-top: 1px; }
  /* Energy section */
  .energy-section {
    background: rgba(0,0,0,0.2); border-radius: 14px; padding: 10px 14px; margin-top: 8px;
  }
  .energy-title { font-size: 0.8rem; font-weight: 600; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
  .energy-row { display: flex; justify-content: space-between; padding: 3px 0; font-size: 0.9rem; }
  .energy-lbl { opacity: 0.75; }
  .energy-val { font-weight: 600; }
`;

// ---------------------------------------------------------------------------
// Dropdown helper
// ---------------------------------------------------------------------------
function ibepRenderDropdown(slugs, selected, storageKey, configDevice) {
  // If a specific device is pinned via config, just show the name (no dropdown)
  if (configDevice && slugs.indexOf(configDevice) !== -1) {
    return `<div class="device-name">${(configDevice).replace(/_/g, ' ')}</div>`;
  }
  if (slugs.length <= 1) {
    return `<div class="device-name">${(selected || '').replace(/_/g, ' ')}</div>`;
  }
  const opts = slugs.map(s =>
    `<div class="dd-option${s === selected ? ' active' : ''}" data-val="${s}">${s.replace(/_/g, ' ')}</div>`
  ).join('');
  return `
    <div class="dd" data-storage-key="${storageKey}">
      <div class="dd-header">
        <span class="dd-current">${(selected || '').replace(/_/g, ' ')}</span>
        <ha-icon icon="mdi:chevron-down" class="dd-arrow"></ha-icon>
      </div>
      <div class="dd-list">${opts}</div>
    </div>`;
}

function ibepSetupDropdown(shadow, onSelect, card) {
  const dd = shadow.querySelector('.dd');
  if (!dd) return;
  const closeDD = () => {
    dd.classList.remove('open');
    if (card) card._ddOpen = false;
  };
  dd.querySelector('.dd-header')?.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = dd.classList.toggle('open');
    if (card) card._ddOpen = isOpen;
  });
  dd.querySelectorAll('.dd-option').forEach(opt => {
    opt.addEventListener('click', (e) => {
      e.stopPropagation();
      const val = opt.dataset.val;
      const key = dd.dataset.storageKey;
      if (key) localStorage.setItem(key, val);
      closeDD();
      if (onSelect) onSelect(val);
    });
  });
  // Close on clicks within shadow but outside the dropdown
  shadow.addEventListener('click', (e) => {
    if (dd.classList.contains('open') && !dd.contains(e.target)) closeDD();
  });
  // Close on clicks completely outside the card (once-per-instance)
  if (card && !card._ddDocCleanup) {
    const handler = () => closeDD();
    document.addEventListener('click', handler);
    card._ddDocCleanup = handler;
  }
}

function ibepResolveSlug(slugs, storageKey, configDevice) {
  // If a device is pinned via config, use it directly without touching localStorage
  if (configDevice && slugs.indexOf(configDevice) !== -1) {
    return configDevice;
  }
  let base = localStorage.getItem(storageKey);
  if (!base || slugs.indexOf(base) === -1) {
    base = slugs[0] || '';
    if (base) localStorage.setItem(storageKey, base);
  }
  return base;
}

// =============================================================================
// IBePlug Card
// =============================================================================
const IBEPLUG_CSS = `
  ${IBEP_SHARED_CSS}
  /* Panel interior */
  .plug-panel {
    width: 100%; max-width: 460px; margin: 2px auto 0;
    border-radius: 16px; overflow: hidden;
    background: rgba(10, 18, 28, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.10);
    padding: 18px 16px 14px; box-sizing: border-box;
    display: flex; flex-direction: column; align-items: center; gap: 14px;
  }
  /* Toggle button */
  .plug-toggle {
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    cursor: pointer; user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  .plug-icon-ring {
    width: 86px; height: 86px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    border: 3px solid rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.08);
    transition: all 0.3s ease;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
  }
  .plug-toggle.is-on .plug-icon-ring {
    border-color: rgba(76, 223, 107, 0.7);
    background: rgba(76, 223, 107, 0.12);
    box-shadow: 0 0 20px rgba(76, 223, 107, 0.35), 0 2px 12px rgba(0,0,0,0.25);
    animation: plugGlow 2s ease-in-out infinite;
  }
  .plug-toggle.is-off .plug-icon-ring {
    border-color: rgba(170, 170, 170, 0.35);
    background: rgba(170, 170, 170, 0.08);
  }
  .plug-status {
    font-size: 0.92rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: rgba(255,255,255,0.85);
  }
  .plug-toggle.is-on .plug-status { color: var(--ibep-green); }
  .plug-toggle.is-off .plug-status { color: rgba(255,255,255,0.45); }
  /* Power section */
  .power-section { width: 100%; text-align: center; box-sizing: border-box; overflow: hidden; }
  .power-label {
    font-size: 0.74rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em; color: rgba(255,255,255,0.55); margin-bottom: 2px;
  }
  .power-value {
    font-size: 1.74rem; font-weight: 700; color: #fff;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4); margin-bottom: 6px;
  }
  .power-peak {
    font-size: 0.9rem; font-weight: 600; color: #fff;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4); text-align: right; margin-bottom: 2px;
  }
  .power-bar-track {
    width: 100%; height: 6px; border-radius: 3px;
    background: rgba(255,255,255,0.12); overflow: hidden;
  }
  .power-bar-fill {
    height: 100%; border-radius: 3px;
    transition: width 0.6s ease, background 0.6s ease;
  }
  /* Metrics row */
  .plug-metrics {
    display: flex; justify-content: space-around; width: 100%;
    gap: 4px; box-sizing: border-box; overflow: hidden;
  }
  .plug-metric {
    display: flex; flex-direction: column; align-items: center;
    gap: 2px; flex: 1; min-width: 0; overflow: hidden; max-width: 100%;
  }
  .plug-metric-val {
    font-size: 1.12rem; font-weight: 700; color: #fff;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;
  }
  .plug-metric-lbl {
    font-size: 0.67rem; font-weight: 600; color: rgba(255,255,255,0.5);
    text-transform: uppercase; letter-spacing: 0.03em;
  }
  /* Energy section */
  .plug-energy {
    width: 100%; background: rgba(255,255,255,0.06);
    border-radius: 10px; padding: 10px 12px; box-sizing: border-box; overflow: hidden;
  }
  .plug-energy-title {
    display: flex; align-items: center;
    font-size: 0.82rem; font-weight: 700; color: rgba(255,255,255,0.75);
    text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px;
  }
  .plug-energy-rows { display: flex; flex-direction: column; gap: 4px; }
  .plug-energy-row { display: flex; justify-content: space-between; align-items: center; }
  .plug-energy-lbl { font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.5); }
  .plug-energy-val {
    font-size: 0.86rem; font-weight: 700; color: #fff;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  /* Animations */
  @keyframes plugGlow {
    0%, 100% { box-shadow: 0 0 20px rgba(76, 223, 107, 0.35), 0 2px 12px rgba(0,0,0,0.25); }
    50% { box-shadow: 0 0 28px rgba(76, 223, 107, 0.55), 0 2px 12px rgba(0,0,0,0.25); }
  }
  @media (max-width: 540px) {
    .plug-panel { padding: 14px 12px 10px; gap: 10px; }
    .plug-icon-ring { width: 68px; height: 68px; }
    .power-value { font-size: 1.3rem; }
    .plug-metric-val { font-size: 0.92rem; }
  }
`;

class IbepowerIbeplugCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement('ibepower-card-editor');
  }
  static getStubConfig() {
    return { device_type: 'Ibeplug' };
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
    this._peakW = 0;
    this._ddOpen = false;
    this._peakFetchInflight = {};
  }

  setConfig(config) {
    this._config = { device_type: 'Ibeplug', ...config };
  }

  connectedCallback() {
    if (this._hass) {
      cancelAnimationFrame(this._rafId);
      this._rafId = requestAnimationFrame(() => {
        this._rafId = requestAnimationFrame(() => { if (!this._ddOpen) this._render(); });
      });
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._ddOpen) this._render();
  }

  getCardSize() { return 6; }

  _render() {
    const hass = this._hass;
    if (!hass) return;
    const t = ibepI18n(hass);
    const slugs = ibepGetSlugs(hass, 'Ibeplug', 'ibeplug', 'switch');
    if (slugs.length === 0) {
      this._structKey = '';
      this.shadowRoot.innerHTML = `<style>${IBEPLUG_CSS}</style><ha-card><div class="card"><div class="logo-wrap"><img src="${ibepLogoUrl(hass)}" alt="Ibepower"></div><div class="no-devices">${t.nodev}</div></div></ha-card>`;
      return;
    }
    const base = ibepResolveSlug(slugs, 'ibep_plug_selector', this._config.device);
    const switchObj = ibepSwitchState(hass, base, 'ibeplug');
    const switchEid = ibepSwitchEid(hass, base, 'ibeplug');
    const isOn = switchObj?.state === 'on';

    const powerW = ibepNum(ibepState(hass, base, 'power'));
    const voltageV = ibepNum(ibepState(hass, base, 'voltage'));
    const currentA = ibepNum(ibepState(hass, base, 'current'));
    const factorPct = ibepNum(ibepState(hass, base, 'factor'));
    const kwToday = ibepNum(ibepState(hass, base, 'consumption'));
    const kwYesterday = ibepNum(ibepState(hass, base, 'kw_yesterday'));
    const kwTotal = ibepNum(ibepState(hass, base, 'kw_total'));

    // Peak power (local + history API)
    const absPower = powerW !== null ? Math.abs(powerW) : 0;
    const peakKey = 'ibep_plug_peak_' + base;
    const histPeakKey = 'ibep_plug_peak_hist_' + base;
    const histPeakTsKey = 'ibep_plug_peak_hist_ts_' + base;
    const peakFetchTtlMs = 10 * 60 * 1000;
    const localPeakW = Number(localStorage.getItem(peakKey)) || 0;
    const histPeakW = Number(localStorage.getItem(histPeakKey)) || 0;
    const histTs = Number(localStorage.getItem(histPeakTsKey)) || 0;
    this._peakW = Math.max(localPeakW, histPeakW, absPower);
    if (absPower > localPeakW) localStorage.setItem(peakKey, String(this._peakW));

    // Fetch peak from HA history (30 days, refresh every 10 min)
    const powerEid = ibepState(hass, base, 'power')?.entity_id || '';
    const nowMs = Date.now();
    if (powerEid && (!histTs || (nowMs - histTs) > peakFetchTtlMs)) {
      if (!this._peakFetchInflight[base]) {
        this._peakFetchInflight[base] = true;
        const endIso = new Date().toISOString();
        const startIso = new Date(nowMs - 30 * 24 * 60 * 60 * 1000).toISOString();
        const histPath =
          '/api/history/period/' + encodeURIComponent(startIso) +
          '?filter_entity_id=' + encodeURIComponent(powerEid) +
          '&end_time=' + encodeURIComponent(endIso) +
          '&minimal_response&no_attributes';
        hass.callApi('GET', histPath)
          .then(rows => {
            let maxH = 0;
            if (Array.isArray(rows) && Array.isArray(rows[0])) {
              for (const r of rows[0]) {
                const v = Math.abs(Number(String(r?.state ?? '').replace(',', '.')));
                if (Number.isFinite(v) && v > maxH) maxH = v;
              }
            }
            if (maxH > 0) {
              localStorage.setItem(histPeakKey, String(maxH));
              localStorage.setItem(histPeakTsKey, String(Date.now()));
              if (maxH > this._peakW) localStorage.setItem(peakKey, String(maxH));
            } else {
              localStorage.setItem(histPeakTsKey, String(Date.now()));
            }
          })
          .catch(() => localStorage.setItem(histPeakTsKey, String(Date.now())))
          .finally(() => { delete this._peakFetchInflight[base]; });
      }
    }

    const barPct = this._peakW > 0 ? Math.min(100, Math.round((absPower / this._peakW) * 100)) : 0;
    const barColor = barPct > 75 ? '#e74c3c' : barPct > 40 ? '#f39c12' : '#2ecc71';

    // Incremental update: skip full re-render if structure unchanged
    const structKey = slugs.join(',') + '|' + base;
    if (this._structKey === structKey && this.shadowRoot.querySelector('.plug-panel')) {
      const sr = this.shadowRoot;
      const q = s => sr.querySelector(s);
      const toggle = sr.getElementById('toggle');
      if (toggle) toggle.className = 'plug-toggle ' + (isOn ? 'is-on' : 'is-off');
      const icon = q('#toggle ha-icon');
      if (icon) icon.style.color = isOn ? '#4cdf6b' : '#aaa';
      const setText = (s, txt) => { const e = q(s); if (e) e.textContent = txt; };
      setText('[data-v="status"]', isOn ? t.on : t.off);
      setText('[data-v="power"]', powerW !== null ? Math.round(powerW) + ' W' : '-- W');
      setText('[data-v="peak"]', t.peak + ': ' + (this._peakW > 0 ? Math.round(this._peakW) + ' W' : '-- W'));
      setText('[data-v="voltage"]', ibepFmt(voltageV, 'V', 1));
      setText('[data-v="current"]', ibepFmt(currentA, 'A', 2));
      setText('[data-v="factor"]', ibepFmt(factorPct, '%', 0));
      setText('[data-v="today"]', ibepFmtK(kwToday));
      setText('[data-v="yesterday"]', ibepFmtK(kwYesterday));
      setText('[data-v="total"]', ibepFmtK(kwTotal));
      const bar = q('[data-v="bar"]');
      if (bar) { bar.style.width = barPct + '%'; bar.style.background = barColor; }
      return;
    }
    this._structKey = structKey;

    this.shadowRoot.innerHTML = `
      <style>${IBEPLUG_CSS}</style>
      <ha-card>
        <div class="card">
          <div class="logo-wrap"><img src="${ibepLogoUrl(hass)}" alt="Ibepower"></div>
          ${ibepRenderDropdown(slugs, base, 'ibep_plug_selector', this._config.device)}
          <div class="plug-panel">
            <div class="plug-toggle ${isOn ? 'is-on' : 'is-off'}" id="toggle">
              <div class="plug-icon-ring" style="animation-delay:${-(Date.now() % 2000)}ms">
                <ha-icon icon="mdi:power-plug" style="--mdc-icon-size:44px; color:${isOn ? '#4cdf6b' : '#aaa'};"></ha-icon>
              </div>
              <div class="plug-status" data-v="status">${isOn ? t.on : t.off}</div>
            </div>
            <div class="power-section">
              <div class="power-label">${t.power}</div>
              <div class="power-value" data-v="power">${powerW !== null ? Math.round(powerW) + ' W' : '-- W'}</div>
              <div class="power-peak" data-v="peak">${t.peak}: ${this._peakW > 0 ? Math.round(this._peakW) + ' W' : '-- W'}</div>
              <div class="power-bar-track"><div class="power-bar-fill" data-v="bar" style="width:${barPct}%;background:${barColor};"></div></div>
            </div>
            <div class="plug-metrics">
              <div class="plug-metric">
                <ha-icon icon="mdi:flash" style="--mdc-icon-size:20px;color:#f1c40f;"></ha-icon>
                <div class="plug-metric-val" data-v="voltage">${ibepFmt(voltageV, 'V', 1)}</div>
                <div class="plug-metric-lbl">${t.voltage}</div>
              </div>
              <div class="plug-metric">
                <ha-icon icon="mdi:current-ac" style="--mdc-icon-size:20px;color:#3498db;"></ha-icon>
                <div class="plug-metric-val" data-v="current">${ibepFmt(currentA, 'A', 2)}</div>
                <div class="plug-metric-lbl">${t.current}</div>
              </div>
              <div class="plug-metric">
                <ha-icon icon="mdi:cosine-wave" style="--mdc-icon-size:20px;color:#9b59b6;"></ha-icon>
                <div class="plug-metric-val" data-v="factor">${ibepFmt(factorPct, '%', 0)}</div>
                <div class="plug-metric-lbl">${t.pf}</div>
              </div>
            </div>
            <div class="plug-energy">
              <div class="plug-energy-title">${t.energy}</div>
              <div class="plug-energy-rows">
                <div class="plug-energy-row"><span class="plug-energy-lbl">${t.today}</span><span class="plug-energy-val" data-v="today">${ibepFmtK(kwToday)}</span></div>
                <div class="plug-energy-row"><span class="plug-energy-lbl">${t.yesterday}</span><span class="plug-energy-val" data-v="yesterday">${ibepFmtK(kwYesterday)}</span></div>
                <div class="plug-energy-row"><span class="plug-energy-lbl">${t.total}</span><span class="plug-energy-val" data-v="total">${ibepFmtK(kwTotal)}</span></div>
              </div>
            </div>
          </div>
        </div>
      </ha-card>`;

    // Toggle handler
    this.shadowRoot.getElementById('toggle')?.addEventListener('click', () => {
      if (switchEid) hass.callService('switch', 'toggle', { entity_id: switchEid });
    });

    // Dropdown handler
    ibepSetupDropdown(this.shadowRoot, () => { this._render(); }, this);
  }
}

// =============================================================================
// IBEMeter Card
// =============================================================================
const IBEMETER_CSS = `
  ${IBEP_SHARED_CSS}
  /* ---- Triangle flow viewport ---- */
  .flow-viewport {
    position: relative;
    width: min(100%, 460px);
    aspect-ratio: 1.2 / 1;
    height: auto;
    min-height: 0;
    margin: 2px auto 0;
    border-radius: 16px;
    overflow: hidden;
    background: rgba(10, 18, 28, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.10);
  }
  .flow-wrap {
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    height: auto;
    min-height: 0;
  }
  /* ---- Animated connectors ---- */
  .ibep-flow-connector {
    position: absolute; z-index: 1; border-radius: 999px;
    --link-color: rgba(120, 132, 152, 0.24);
    background: var(--link-color);
    transition: opacity 0.2s ease;
    background-image: repeating-linear-gradient(90deg,
      rgba(255,255,255,0) 0px, rgba(255,255,255,0) 7px,
      var(--link-color) 7px, var(--link-color) 14px,
      rgba(255,255,255,0.8) 14px, rgba(255,255,255,0.8) 17px,
      rgba(255,255,255,0) 17px, rgba(255,255,255,0) 24px);
  }
  .ibep-flow-connector.is-idle  { opacity: 0.28; }
  .ibep-flow-connector.is-active { opacity: 0.85; }
  .ibep-flow-connector.flow-right.is-active {
    animation: flowRight 1.05s linear infinite, pipeGlow 1.9s ease-in-out infinite;
  }
  .ibep-flow-connector.flow-left.is-active {
    animation: flowLeft 1.05s linear infinite, pipeGlow 1.9s ease-in-out infinite;
  }
  .ibep-flow-connector.flow-down.is-active {
    background-image: repeating-linear-gradient(180deg,
      rgba(255,255,255,0) 0px, rgba(255,255,255,0) 7px,
      var(--link-color) 7px, var(--link-color) 14px,
      rgba(255,255,255,0.8) 14px, rgba(255,255,255,0.8) 17px,
      rgba(255,255,255,0) 17px, rgba(255,255,255,0) 24px);
    animation: flowDown 1.05s linear infinite, pipeGlow 1.9s ease-in-out infinite;
  }
  /* Connector positions (triangle) */
  .link-solar-grid {
    --link-color: rgba(255, 196, 61, 0.45);
    left: 20%; top: calc(20% - 1px); width: 60%; height: 2px;
  }
  .link-solar-home {
    --link-color: rgba(66, 153, 255, 0.45);
    left: 20%; top: calc(20% - 1px); width: 54%; height: 2px;
    transform-origin: left center; transform: rotate(56.31deg);
  }
  .link-grid-home {
    --link-color: rgba(156, 118, 255, 0.45);
    left: 80%; top: calc(20% - 1px); width: 54%; height: 2px;
    transform-origin: left center; transform: rotate(123.69deg);
  }
  /* ---- Circle nodes (absolute positioned) ---- */
  .ibep-flow-node {
    position: absolute; z-index: 3;
    width: min(130px, 28%); height: min(130px, 28%);
    transform: translate(-50%, -50%);
    border-radius: 50%;
    display: grid; grid-template-rows: 20px minmax(0, auto) minmax(0, auto);
    align-content: center; justify-items: center; align-items: center;
    text-align: center; padding: 8px 9px 10px; box-sizing: border-box;
    border: 2px solid var(--node-accent, #9aa5b8);
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
    box-shadow: 0 2px 9px rgba(0, 0, 0, 0.25);
    cursor: pointer;
  }
  .ibep-flow-node.node-active { opacity: 1; animation: nodeGlow 3s ease-in-out infinite; }
  .ibep-flow-node.node-idle   { opacity: 0.92; }
  .node-solar { top: 20%; left: 20%; --node-accent: #d8b548; --node-main: #8a6d00; }
  .node-grid  { top: 20%; left: 80%; --node-accent: #8660ce; --node-main: #5a3d9e; }
  .node-home  { top: 65%; left: 50%; --node-accent: #2f6fe8; --node-main: #1a56b0; }
  .node-home .node-sub { margin-top: 6px; }
  .node-icon {
    color: var(--node-accent, #7e8aa0); --mdc-icon-size: 26px;
    margin: 0; align-self: center; justify-self: center;
  }
  .node-main {
    color: var(--node-main, #2c3447); width: 100%; max-width: 100%;
    font-size: clamp(1.08rem, 3.25vw, 1.46rem); font-weight: 700;
    line-height: 1.02; margin-top: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .node-main.is-negative { color: #c0392b; }
  .node-sub {
    margin-top: 2px; font-size: clamp(0.60rem, 1.85vw, 0.80rem);
    font-weight: 600; line-height: 1.07; color: rgba(0, 0, 0, 0.6);
    width: 100%; max-width: 100%;
  }
  .node-sub-line:first-child { margin-bottom: 3px; }
  .node-sub-line {
    display: block; width: 100%; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
  }
  .node-sub-title { font-weight: 700; color: var(--node-accent, #7e8aa0); }
  /* ---- Animations ---- */
  @keyframes flowRight { 0%{background-position:0 0} 100%{background-position:24px 0} }
  @keyframes flowLeft  { 0%{background-position:0 0} 100%{background-position:-24px 0} }
  @keyframes flowDown  { 0%{background-position:0 0} 100%{background-position:0 24px} }
  @keyframes pipeGlow  { 0%,100%{filter:brightness(1)} 50%{filter:brightness(1.2)} }
  @keyframes nodeGlow { 0%,100%{box-shadow:0 2px 9px rgba(0,0,0,0.25), 0 0 6px var(--node-accent,rgba(120,132,152,0.15))} 50%{box-shadow:0 2px 9px rgba(0,0,0,0.25),0 0 16px var(--node-accent,rgba(120,132,152,0.45))} }
  /* ---- Responsive ---- */
  @media (max-width: 540px) {
    .flow-viewport { width: 100%; min-height: 0; }
    .flow-wrap { width: 100%; min-height: 0; }
    .ibep-flow-node { width: min(112px, 29%); height: min(112px, 29%); grid-template-rows: 21px minmax(0,auto) minmax(0,auto); padding: 6px 8px 8px; }
    .node-icon { --mdc-icon-size: 22px; }
  }
  .card.compact .ibep-flow-node {
    width: min(104px, 30%);
    height: min(104px, 30%);
    grid-template-rows: 16px minmax(0,auto) minmax(0,auto);
    padding: 5px 6px 7px;
  }
  .card.compact .node-icon { --mdc-icon-size: 17px; }
  .card.compact .node-main { font-size: clamp(0.62rem, 2vw, 0.86rem); margin-top: 1px; }
  .card.compact .node-sub { font-size: clamp(0.39rem, 1.1vw, 0.50rem); line-height: 1.02; margin-top: 1px; }
  .card.compact .node-home .node-sub { margin-top: 2px; }
`;

class IbepowerIbemeterCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement('ibepower-card-editor');
  }
  static getStubConfig() {
    return { device_type: 'Ibemeter' };
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
    this._ddOpen = false;
  }

  setConfig(config) {
    this._config = { device_type: 'Ibemeter', ...config };
  }

  connectedCallback() {
    if (this._hass) {
      cancelAnimationFrame(this._rafId);
      this._rafId = requestAnimationFrame(() => {
        this._rafId = requestAnimationFrame(() => { if (!this._ddOpen) this._render(); });
      });
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._ddOpen) this._render();
  }

  getCardSize() { return 5; }

  _render() {
    const hass = this._hass;
    if (!hass) return;
    const compact = ibepIsCompactCard(this, 330);
    const t = ibepI18n(hass);
    const slugs = ibepGetSlugs(hass, 'Ibemeter', 'grid_voltage', 'sensor');
    if (slugs.length === 0) {
      this._structKey = '';
      this.shadowRoot.innerHTML = `<style>${IBEMETER_CSS}</style><ha-card><div class="card"><div class="logo-wrap"><img src="${ibepLogoUrl(hass)}" alt="Ibepower"></div><div class="no-devices">${t.nodev}</div></div></ha-card>`;
      return;
    }
    const base = ibepResolveSlug(slugs, 'ibep_meter_selector', this._config.device);

    // ---- Sensor values ----
    const solarW  = ibepNum(ibepState(hass, base, 'solar_watts'));
    const gridW   = ibepNum(ibepState(hass, base, 'grid_watts'));
    const homeW   = (solarW !== null || gridW !== null) ? (solarW ?? 0) - (gridW ?? 0) : null;

    const gridV   = ibepNum(ibepState(hass, base, 'grid_voltage'));
    const gridC   = ibepNum(ibepState(hass, base, 'grid_current'));
    const gridF   = ibepNum(ibepState(hass, base, 'grid_frequency'));

    const solarK  = ibepNum(ibepState(hass, base, 'kw_solar_today'));
    const importK = ibepNum(ibepState(hass, base, 'kw_import_today'));
    const exportK = ibepNum(ibepState(hass, base, 'kw_export_today'));

    // ---- Entity availability ----
    const hasSolar       = ibepValid(ibepState(hass, base, 'solar_watts'));
    const hasGrid        = ibepValid(ibepState(hass, base, 'grid_watts'));
    const hasSolarToday  = ibepValid(ibepState(hass, base, 'kw_solar_today'));
    const hasImportToday = ibepValid(ibepState(hass, base, 'kw_import_today'));
    const hasExportToday = ibepValid(ibepState(hass, base, 'kw_export_today'));

    // ---- Active states ----
    const solarActive = hasSolar && Math.abs(solarW ?? 0) > 0;
    const gridActive  = hasGrid && Math.abs(gridW ?? 0) > 0;
    const homeActive  = homeW !== null && Math.abs(homeW) > 0;

    // ---- Direction text ----
    const gridDirText = hasGrid ? ((gridW ?? 0) >= 0 ? t.exporting : t.importing) : '';

    // ---- Formatting helpers ----
    const fmtAbsW  = v => v !== null ? Math.round(Math.abs(v)) + ' W' : '-- W';
    const fmtSignW = v => v !== null ? Math.round(v) + ' W' : '-- W';

    // ---- Display values ----
    const solarMain   = hasSolar ? fmtAbsW(solarW) : '-- W';
    const gridMain    = hasGrid ? fmtSignW(gridW) : '-- W';
    const homeMain    = fmtAbsW(homeW);
    const gridVCText  = compact
      ? (ibepFmt(gridV, 'V', 0) + ' ' + ibepFmt(gridC, 'A', 1))
      : (ibepFmt(gridV, 'V', 1) + ' (' + ibepFmt(gridC, 'A', 2) + ')');
    const gridFText   = ibepFmt(gridF, 'Hz', 2);

    // ---- Entity IDs for more-info ----
    const solarEid = ibepState(hass, base, 'solar_watts')?.entity_id || '';
    const gridEid  = ibepState(hass, base, 'grid_watts')?.entity_id || '';

    // ---- Animation delays (keep animations phase-continuous across re-renders) ----
    const _now = Date.now();
    const _fdel = -(_now % 1050) + 'ms';
    const _gdel = -(_now % 1900) + 'ms';
    const _ndel = -(_now % 3000) + 'ms';
    const _cDel = `animation-delay:${_fdel},${_gdel}`;
    const _nDel = `animation-delay:${_ndel}`;

    // ---- Connector classes ----
    const cSolarGrid = 'link-solar-grid ' + (solarActive && (gridW ?? 0) > 0 ? 'is-active flow-right' : 'is-idle');
    const cSolarHome = 'link-solar-home ' + (solarActive && (homeW ?? 0) > 0 ? 'is-active flow-right' : 'is-idle');
    const cGridHome  = 'link-grid-home '  + (gridActive && (gridW ?? 0) < 0 ? 'is-active flow-right' : 'is-idle');

    // Incremental update: skip full re-render if structure unchanged
    const structKey = slugs.join(',') + '|' + base + '|' + hasSolar + '|' + hasGrid + '|' + compact + '|' + hasSolarToday + '|' + hasImportToday + '|' + hasExportToday;
    if (this._structKey === structKey && this.shadowRoot.querySelector('.flow-wrap')) {
      const sr = this.shadowRoot;
      const q = s => sr.querySelector(s);
      const patchNode = (sel, active, mainText, mainNeg) => {
        const node = q(sel);
        if (!node) return;
        node.classList.toggle('node-active', active);
        node.classList.toggle('node-idle', !active);
        const main = node.querySelector('.node-main');
        if (main) {
          main.textContent = mainText;
          if (mainNeg !== undefined) main.classList.toggle('is-negative', mainNeg);
        }
      };
      patchNode('.node-solar', solarActive, solarMain);
      patchNode('.node-grid', gridActive, gridMain, (gridW ?? 0) < 0);
      patchNode('.node-home', homeActive, homeMain);
      const setText = (s, txt) => { const e = q(s); if (e) e.textContent = txt; };
      setText('[data-v="solar-today"]', ibepFmtK(solarK));
      setText('[data-v="grid-dir"]', gridDirText || '--');
      setText('[data-v="import-today"]', t.imp + '. ' + ibepFmtK(importK));
      setText('[data-v="export-today"]', t.exp + '. ' + ibepFmtK(exportK));
      setText('[data-v="grid-vc"]', gridVCText);
      setText('[data-v="grid-f"]', gridFText);
      const patchConn = (id, cls) => { const e = q('[data-conn="' + id + '"]'); if (e) e.className = 'ibep-flow-connector ' + cls; };
      patchConn('solar-grid', cSolarGrid);
      patchConn('solar-home', cSolarHome);
      patchConn('grid-home', cGridHome);
      return;
    }
    this._structKey = structKey;

    // ---- Build connectors HTML ----
    let connectorsHtml = '';
    if (hasSolar && hasGrid) connectorsHtml += `<div class="ibep-flow-connector ${cSolarGrid}" data-conn="solar-grid" style="${_cDel}"></div>`;
    if (hasSolar)            connectorsHtml += `<div class="ibep-flow-connector ${cSolarHome}" data-conn="solar-home" style="${_cDel}"></div>`;
    if (hasGrid)             connectorsHtml += `<div class="ibep-flow-connector ${cGridHome}" data-conn="grid-home" style="${_cDel}"></div>`;

    // ---- Build nodes HTML ----
    let nodesHtml = '';
    if (hasSolar) {
      nodesHtml += `
        <div class="ibep-flow-node node-solar ${solarActive ? 'node-active' : 'node-idle'}" data-entity="${solarEid}" style="${_nDel}">
          <ha-icon class="node-icon" icon="mdi:solar-power"></ha-icon>
          <div class="node-main">${solarMain}</div>
          ${hasSolarToday && !compact ? `<div class="node-sub" data-v="solar-today">${ibepFmtK(solarK)}</div>` : ''}
        </div>`;
    }
    if (hasGrid) {
      nodesHtml += `
        <div class="ibep-flow-node node-grid ${gridActive ? 'node-active' : 'node-idle'}" data-entity="${gridEid}" style="${_nDel}">
          <ha-icon class="node-icon" icon="mdi:transmission-tower"></ha-icon>
          <div class="node-main ${(gridW ?? 0) < 0 ? 'is-negative' : ''}">${gridMain}</div>
          <div class="node-sub">
            <span class="node-sub-line node-sub-title" data-v="grid-dir">${gridDirText || '--'}</span>
            ${hasImportToday && !compact ? `<span class="node-sub-line" data-v="import-today">${t.imp}. ${ibepFmtK(importK)}</span>` : ''}
            ${hasExportToday && !compact ? `<span class="node-sub-line" data-v="export-today">${t.exp}. ${ibepFmtK(exportK)}</span>` : ''}
          </div>
        </div>`;
    }
    nodesHtml += `
      <div class="ibep-flow-node node-home ${homeActive ? 'node-active' : 'node-idle'}" data-entity="${gridEid}" style="${_nDel}">
        <ha-icon class="node-icon" icon="mdi:home-outline"></ha-icon>
        <div class="node-main">${homeMain}</div>
        <div class="node-sub">
          <span class="node-sub-line" data-v="grid-vc">${gridVCText}</span>
          ${compact ? '' : `<span class="node-sub-line" data-v="grid-f">${gridFText}</span>`}
        </div>
      </div>`;

    // ---- Full render ----
    this.shadowRoot.innerHTML = `
      <style>${IBEMETER_CSS}</style>
      <ha-card>
        <div class="card${compact ? ' compact' : ''}">
          <div class="logo-wrap"><img src="${ibepLogoUrl(hass)}" alt="Ibepower"></div>
          ${ibepRenderDropdown(slugs, base, 'ibep_meter_selector', this._config.device)}
          <div class="flow-viewport">
            <div class="flow-wrap">
              ${connectorsHtml}
              ${nodesHtml}
            </div>
          </div>
        </div>
      </ha-card>`;

    // ---- More-info on node click ----
    this.shadowRoot.querySelectorAll('.ibep-flow-node[data-entity]').forEach(node => {
      node.addEventListener('click', () => {
        const eid = node.dataset.entity;
        if (eid) {
          this.dispatchEvent(new CustomEvent('hass-more-info', { detail: { entityId: eid }, bubbles: true, composed: true }));
        }
      });
    });

    // ---- Dropdown handler ----
    ibepSetupDropdown(this.shadowRoot, () => { this._render(); }, this);
  }
}

// =============================================================================
// IBEDiv Card — Full-featured energy flow with diamond layout,
// animated connectors, PV strings, temperatures, controls & PWM slider.
// =============================================================================
const IBEDIV_CSS = `
  ${IBEP_SHARED_CSS}
  /* ---- Diamond flow viewport ---- */
  .flow-wrap {
    position: relative;
    width: min(100%, 460px);
    aspect-ratio: 1 / 1;
    height: auto;
    min-height: 0;
    margin: 2px auto 0;
    border-radius: 16px;
    overflow: hidden;
    background: rgba(10, 18, 28, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.10);
    --ox: 0%;
  }
  .flow-wrap.layout-no-batt { --ox: -16.5%; }
  .flow-wrap.layout-no-grid { --ox: 16.5%; }

  /* ---- Animated connectors ---- */
  .ibep-flow-connector {
    position: absolute; z-index: 1; border-radius: 999px;
    --link-color: rgba(120, 132, 152, 0.24);
    background: var(--link-color);
    transition: opacity 0.2s;
    background-image: repeating-linear-gradient(90deg,
      rgba(255,255,255,0) 0px, rgba(255,255,255,0) 7px,
      var(--link-color) 7px, var(--link-color) 14px,
      rgba(255,255,255,0.8) 14px, rgba(255,255,255,0.8) 17px,
      rgba(255,255,255,0) 17px, rgba(255,255,255,0) 24px);
  }
  .ibep-flow-connector.is-idle  { opacity: 0.28; }
  .ibep-flow-connector.is-active { opacity: 0.85; }
  .ibep-flow-connector.flow-right.is-active { animation: flowRight 1.05s linear infinite, pipeGlow 1.9s ease-in-out infinite; }
  .ibep-flow-connector.flow-left.is-active  { animation: flowLeft  1.05s linear infinite, pipeGlow 1.9s ease-in-out infinite; }
  .ibep-flow-connector.flow-down.is-active {
    background-image: repeating-linear-gradient(180deg,
      rgba(255,255,255,0) 0px, rgba(255,255,255,0) 7px,
      var(--link-color) 7px, var(--link-color) 14px,
      rgba(255,255,255,0.8) 14px, rgba(255,255,255,0.8) 17px,
      rgba(255,255,255,0) 17px, rgba(255,255,255,0) 24px);
    animation: flowDown 1.05s linear infinite, pipeGlow 1.9s ease-in-out infinite;
  }
  .ibep-flow-connector.flow-up.is-active {
    background-image: repeating-linear-gradient(180deg,
      rgba(255,255,255,0) 0px, rgba(255,255,255,0) 7px,
      var(--link-color) 7px, var(--link-color) 14px,
      rgba(255,255,255,0.8) 14px, rgba(255,255,255,0.8) 17px,
      rgba(255,255,255,0) 17px, rgba(255,255,255,0) 24px);
    animation: flowUp 1.05s linear infinite, pipeGlow 1.9s ease-in-out infinite;
  }
  /* Connector positions (diamond) */
  .link-solar-center  { --link-color: rgba(255,196,61,0.45);  left: calc(50% - 1px + var(--ox)); top: 17%;  width: 2px; height: 33%; }
  .link-battery-center{ --link-color: rgba(86,201,120,0.45);  left: calc(17% + var(--ox)); top: calc(50% - 1px); width: 33%; height: 2px; }
  .link-grid-center   { --link-color: rgba(156,118,255,0.45); left: calc(50% + var(--ox)); top: calc(50% - 1px); width: 33%; height: 2px; }
  .link-home-center   { --link-color: rgba(66,153,255,0.45);  left: calc(50% - 1px + var(--ox)); top: 50%;  width: 2px; height: 33%; }
  .link-solar-battery { --link-color: rgba(255,196,61,0.45);  left: calc(50% + var(--ox)); top: calc(17% - 1px); width: 47%; height: 2px; transform-origin: left center; transform: rotate(135deg); }
  .link-solar-grid    { --link-color: rgba(255,196,61,0.45);  left: calc(50% + var(--ox)); top: calc(17% - 1px); width: 47%; height: 2px; transform-origin: left center; transform: rotate(45deg); }
  .link-battery-home  { --link-color: rgba(86,201,120,0.45);  left: calc(17% + var(--ox)); top: calc(50% - 1px); width: 47%; height: 2px; transform-origin: left center; transform: rotate(45deg); }
  .link-grid-home     { --link-color: rgba(156,118,255,0.45); left: calc(83% + var(--ox)); top: calc(50% - 1px); width: 47%; height: 2px; transform-origin: left center; transform: rotate(135deg); }

  /* ---- Diamond nodes (absolute) ---- */
  .ibep-flow-node {
    position: absolute; z-index: 3;
    width: min(130px, 28%); height: min(130px, 28%);
    transform: translate(-50%, -50%);
    border-radius: 50%;
    display: grid; grid-template-rows: 20px minmax(0,auto) minmax(0,auto);
    align-content: center; justify-items: center; align-items: center;
    text-align: center; padding: 8px 9px 10px; box-sizing: border-box;
    border: 2px solid var(--node-accent, #9aa5b8);
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
    box-shadow: 0 2px 9px rgba(0,0,0,0.25);
    cursor: pointer;
  }
  .ibep-flow-node.node-active { opacity: 1; animation: nodeGlow 3s ease-in-out infinite; }
  .ibep-flow-node.node-idle   { opacity: 0.92; }
  .node-solar    { top: 17%; left: calc(50% + var(--ox)); --node-accent: #d8b548; --node-main: #8a6d00; }
  .node-battery  { top: 50%; left: calc(17% + var(--ox)); --node-accent: #41aa56; --node-main: #1e7a34; }
  .node-grid     { top: 50%; left: calc(83% + var(--ox)); --node-accent: #8660ce; --node-main: #5a3d9e; }
  .node-home     { top: 83%; left: calc(50% + var(--ox)); --node-accent: #2f6fe8; --node-main: #1a56b0; }
  .node-diverter {
    z-index: 2; top: 50%; left: calc(50% + var(--ox));
    width: min(122px, 26%); height: min(122px, 26%);
    --node-accent: #7a8ea0; --node-main: #4a5568;
  }
  .node-diverter.node-active { animation: nodeGlow 3s ease-in-out infinite; }
  .node-icon { color: var(--node-accent, #7e8aa0); --mdc-icon-size: 26px; margin: 0; align-self: center; justify-self: center; }
  .node-icon-rotated { transform: rotate(90deg); }
  .node-main {
    color: var(--node-main, #2c3447); width: 100%; max-width: 100%;
    font-size: clamp(1.06rem, 3.2vw, 1.42rem); font-weight: 700;
    line-height: 1.02; margin-top: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .node-main.is-negative { color: #c0392b; }
  .node-diverter .node-main { font-size: clamp(1.14rem, 3.35vw, 1.52rem); }
  .node-sub-top { margin-top: 0; margin-bottom: 1px; font-size: clamp(0.70rem, 2.15vw, 0.92rem) !important; font-weight: 700; }
  .node-sub {
    margin-top: 2px; font-size: clamp(0.60rem, 1.82vw, 0.80rem);
    font-weight: 600; line-height: 1.07; color: rgba(0,0,0,0.6);
    width: 100%; max-width: 100%;
  }
  .node-sub-line:first-child { margin-bottom: 3px; }
  .node-sub-line { display: block; width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .node-sub-title { font-weight: 700; color: var(--node-accent, #7e8aa0); }
  .node-sub-spaced { margin-top: 3px; }
  .node-soc { color: #1e7a34; }

  /* ---- Animations ---- */
  @keyframes flowRight { 0%{background-position:0 0} 100%{background-position:24px 0} }
  @keyframes flowLeft  { 0%{background-position:0 0} 100%{background-position:-24px 0} }
  @keyframes flowDown  { 0%{background-position:0 0} 100%{background-position:0 24px} }
  @keyframes flowUp    { 0%{background-position:0 0} 100%{background-position:0 -24px} }
  @keyframes pipeGlow  { 0%,100%{filter:brightness(1)} 50%{filter:brightness(1.2)} }
  @keyframes nodeGlow { 0%,100%{box-shadow:0 2px 9px rgba(0,0,0,0.25), 0 0 6px var(--node-accent,rgba(120,132,152,0.15))} 50%{box-shadow:0 2px 9px rgba(0,0,0,0.25),0 0 16px var(--node-accent,rgba(120,132,152,0.45))} }

  /* ---- PV strings section ---- */
  .pv-section {
    border-radius: 14px; margin-top: 8px; padding: 0;
    background: transparent;
    border: none;
  }
  .pv-wrap { display: flex; flex-wrap: nowrap; align-items: stretch; gap: 8px; width: 100%; }
  .pv-pill {
    display: flex; flex-direction: column; align-items: stretch; justify-content: center;
    gap: 4px; flex: 1 1 0; min-width: 0; padding: 4px 6px; border-radius: 10px;
    background: linear-gradient(145deg, rgba(35,115,55,0.92), rgba(55,150,75,0.88));
    border: 1px solid rgba(140,230,90,0.85);
  }
  .pv-title { color: #60CFFF; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.02em; text-shadow: 0 1px 2px rgba(0,0,0,0.4); text-align: center; width: 100%; }
  .pv-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(0,1fr)); gap: 6px; width: 100%; }
  .pv-metric {
    display: flex; flex-direction: row; align-items: center; justify-content: center;
    min-width: 0; padding: 2px 4px; gap: 3px;
    font-size: 0.72rem; font-weight: 700; line-height: 1.1; font-variant-numeric: tabular-nums;
    border-radius: 8px; background: rgba(10,55,25,0.30); border: 1px solid rgba(120,220,80,0.35);
    text-align: center; cursor: pointer;
    -webkit-tap-highlight-color: transparent; touch-action: manipulation;
  }
  .pv-key { color: #fff; flex-shrink: 0; }
  .pv-val { color: #fff; text-shadow: 0 1px 3px rgba(0,0,0,0.45); white-space: nowrap; }

  /* ---- Temperature pills ---- */
  .temp-section {
    border-radius: 14px; margin-top: 8px; padding: 0;
    background: transparent;
    border: none;
  }
  .temp-wrap { display: flex; flex-wrap: nowrap; align-items: stretch; gap: 8px; width: 100%; }
  .temp-pill {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 2px; flex: 1 1 0; min-width: 0; padding: 4px 4px; border-radius: 10px;
    background: linear-gradient(145deg, rgba(35,115,55,0.92), rgba(55,150,75,0.88));
    border: 1px solid rgba(140,230,90,0.85); cursor: pointer;
    -webkit-tap-highlight-color: transparent; touch-action: manipulation;
  }
  .temp-title { color: #60CFFF; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.02em; text-shadow: 0 1px 2px rgba(0,0,0,0.4); text-align: center; width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .temp-val { color: #f0fff4; font-size: 0.78rem; font-weight: 700; text-shadow: 0 1px 3px rgba(0,0,0,0.35); text-align: center; white-space: nowrap; }

  /* ---- Controls grid ---- */
  .ctrl-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
  .ctrl-card {
    border-radius: 10px; padding: 6px 6px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 1px;
    cursor: pointer; user-select: none; transition: all 0.2s;
    -webkit-tap-highlight-color: transparent; touch-action: manipulation;
  }
  .ctrl-card .ctrl-label { color: #60CFFF; font-size: 0.80rem; font-weight: 600; letter-spacing: 0.02em; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }
  .ctrl-card .ctrl-state { color: #fff; font-size: 0.96rem; font-weight: 700; text-shadow: 0 1px 4px rgba(0,0,0,0.7); }
  .ctrl-manager-on {
    background: linear-gradient(145deg, rgba(52,138,24,0.92), rgba(36,108,16,0.90));
    border: 1px solid rgba(120,220,20,0.86);
    box-shadow: 0 0 14px rgba(120,220,20,0.34), inset 0 0 20px rgba(120,220,20,0.18);
  }
  .ctrl-manager-off {
    background: linear-gradient(145deg, rgba(138,24,24,0.92), rgba(108,16,16,0.90));
    border: 1px solid rgba(220,60,60,0.86);
    box-shadow: 0 0 14px rgba(220,60,60,0.34), inset 0 0 20px rgba(220,60,60,0.18);
  }
  .ctrl-mode-auto {
    background: linear-gradient(145deg, rgba(52,138,24,0.92), rgba(36,108,16,0.90));
    border: 1px solid rgba(220,165,0,0.68);
    box-shadow: 0 0 8px rgba(200,155,0,0.22), inset 0 0 12px rgba(200,155,0,0.10);
  }
  .ctrl-mode-manual {
    background: linear-gradient(145deg, rgba(210,180,30,0.92), rgba(180,150,20,0.90));
    border: 1px solid rgba(255,195,0,0.92);
    box-shadow: 0 0 16px rgba(255,185,0,0.42), inset 0 0 18px rgba(255,185,0,0.20);
  }
  .ctrl-mode-disabled {
    background: linear-gradient(145deg, rgba(28,24,12,0.72), rgba(20,18,8,0.70));
    border: 1px solid rgba(200,170,60,0.30);
    box-shadow: none; opacity: 0.58; pointer-events: none;
  }

  /* ---- PWM slider ---- */
  .slider-section { margin-top: 8px; }
  .slider-wrap {
    --ibep-fill: rgba(52,138,24,0.92);
    --ibep-track: rgba(120,220,80,0.22);
    position: relative; width: 100%; height: 30px; border-radius: 12px; overflow: hidden;
    background: linear-gradient(90deg, var(--ibep-fill) 0%, var(--ibep-fill) var(--ibep-pct), var(--ibep-track) var(--ibep-pct), var(--ibep-track) 100%);
  }
  .slider-wrap.is-disabled {
    --ibep-fill: rgba(52,138,24,0.55);
    --ibep-track: rgba(120,220,80,0.10);
  }
  .slider-input {
    -webkit-appearance: none; appearance: none;
    width: 100%; height: 100%; margin: 0; border: none; outline: none;
    background: transparent; cursor: pointer;
  }
  .slider-wrap.is-disabled .slider-input { cursor: not-allowed; }
  .slider-input::-webkit-slider-runnable-track { height: 30px; background: transparent; border: none; }
  .slider-input::-webkit-slider-thumb {
    -webkit-appearance: none; appearance: none;
    width: 6px; height: 18px; border: none; border-radius: 999px;
    background: #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.32); margin-top: 6px;
  }
  .slider-input::-moz-range-track { height: 30px; background: transparent; border: none; }
  .slider-input::-moz-range-progress { height: 30px; background: transparent; border: none; }
  .slider-input::-moz-range-thumb {
    width: 6px; height: 18px; border: none; border-radius: 999px;
    background: #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.32);
  }
  .slider-overlay {
    position: absolute; inset: 0; display: flex; align-items: center;
    justify-content: center; pointer-events: none; z-index: 2;
  }
  .slider-value {
    color: #fff; display: inline-flex; align-items: center; justify-content: center;
    min-width: 2.8ch; height: 20px; font-size: 0.86rem; font-weight: 700;
    text-shadow: 0 1px 2px rgba(0,0,0,0.55); line-height: 20px; white-space: nowrap;
    padding: 0 6px; border: 1px solid rgba(255,255,255,0.40); border-radius: 999px;
    background: rgba(0,0,0,0.16); box-sizing: border-box;
  }

  /* ---- Responsive ---- */
  @media (max-width: 540px) {
    .flow-wrap { width: 100%; min-height: 0; }
    .ibep-flow-node { width: min(112px, 29%); height: min(112px, 29%); grid-template-rows: 21px minmax(0,auto) minmax(0,auto); padding: 6px 8px 8px; }
    .node-diverter  { width: min(106px, 27%); height: min(106px, 27%); }
    .node-icon { --mdc-icon-size: 22px; }
  }
  .card.compact .ibep-flow-node {
    width: min(102px, 30%);
    height: min(102px, 30%);
    grid-template-rows: 16px minmax(0,auto) minmax(0,auto);
    padding: 5px 6px 7px;
  }
  .card.compact .node-diverter {
    width: min(94px, 27%);
    height: min(94px, 27%);
  }
  .card.compact .node-icon { --mdc-icon-size: 17px; }
  .card.compact .node-main { font-size: clamp(0.60rem, 1.95vw, 0.82rem); margin-top: 1px; }
  .card.compact .node-diverter .node-main { font-size: clamp(0.62rem, 2.0vw, 0.86rem); }
  .card.compact .node-sub-top { font-size: clamp(0.42rem, 1.1vw, 0.56rem) !important; }
  .card.compact .node-sub { font-size: clamp(0.38rem, 1.05vw, 0.48rem); line-height: 1.02; margin-top: 1px; }
  .card.compact .pv-wrap { gap: 6px; }
  .card.compact .pv-pill { padding: 3px 5px; border-radius: 8px; }
  .card.compact .pv-title { font-size: 0.56rem; }
  .card.compact .pv-metrics { gap: 4px; }
  .card.compact .pv-metric {
    padding: 1px 3px;
    gap: 2px;
    font-size: 0.60rem;
    border-radius: 6px;
  }
  .card.compact .temp-wrap { gap: 6px; }
  .card.compact .temp-pill { padding: 3px 3px; border-radius: 8px; }
  .card.compact .temp-title { font-size: 0.56rem; }
  .card.compact .temp-val { font-size: 0.66rem; }
`;

class IbepowerIbedivCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement('ibepower-card-editor');
  }
  static getStubConfig() {
    return { device_type: 'Ibediv' };
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
    this._ddOpen = false;
    this._sliderActive = false;
    this._sliderReleasedAt = 0;
    this._sliderDocCleanup = null;
  }

  setConfig(config) {
    this._config = { device_type: 'Ibediv', ...config };
  }

  connectedCallback() {
    if (this._hass) {
      cancelAnimationFrame(this._rafId);
      this._rafId = requestAnimationFrame(() => {
        this._rafId = requestAnimationFrame(() => { if (!this._ddOpen) this._render(); });
      });
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._ddOpen && !this._sliderActive) this._render();
  }

  _isSliderBusy() {
    return this._sliderActive || (this._sliderReleasedAt > 0 && (Date.now() - this._sliderReleasedAt) < 3000);
  }

  disconnectedCallback() {
    if (this._sliderDocCleanup) {
      this._sliderDocCleanup();
      this._sliderDocCleanup = null;
    }
  }

  getCardSize() { return 9; }

  // --- i18n extended for IBEDiv ---
  _t(hass) {
    const base = ibepI18n(hass);
    const bl = (typeof navigator !== 'undefined' && navigator.language) || '';
    const raw = String(hass?.language || hass?.selectedLanguage || hass?.locale?.language || bl || 'en').toLowerCase();
    const lang = raw.startsWith('es') ? 'es' : raw.startsWith('pt') ? 'pt' : 'en';
    const ext = {
      es: { charging:'Cargando', discharging:'Descargando', diverterToday:'Derivado Hoy', inverter:'Inversor', custom:'Personalizado', thermo:'Termo' },
      en: { charging:'Charging', discharging:'Discharging', diverterToday:'Diverted Today', inverter:'Inverter', custom:'Custom', thermo:'Thermo' },
      pt: { charging:'Carregando', discharging:'Descarregando', diverterToday:'Derivado Hoje', inverter:'Inversor', custom:'Personalizado', thermo:'Termo' },
    };
    return { ...base, ...(ext[lang] || ext.en) };
  }

  // --- Resolve UI mode with grace-period logic (identical to YAML) ---
  _resolveUiMode(base, managerOn, modeObj) {
    const rawMode = String(modeObj?.state ?? '').toUpperCase();
    const entityValid = rawMode && !['UNKNOWN','UNAVAILABLE','NONE','NULL',''].includes(rawMode);
    const modeFromEntity = rawMode.startsWith('MAN') ? 'MANUAL' : 'AUTO';
    const modeKey = 'ibepower_ui_mode_' + base;
    const mgrPrevKey = 'ibepower_mgr_prev_' + base;
    const mgrToggleKey = 'ibepower_mgr_toggle_ts_' + base;
    let uiMode;
    try {
      const curMgr = managerOn ? 'on' : 'off';
      const prevMgr = localStorage.getItem(mgrPrevKey);
      if (prevMgr !== null && prevMgr !== curMgr) {
        localStorage.setItem(mgrToggleKey, String(Date.now()));
      }
      localStorage.setItem(mgrPrevKey, curMgr);
      const toggleTs = Number(localStorage.getItem(mgrToggleKey)) || 0;
      const inGrace = toggleTs > 0 && (Date.now() - toggleTs) < 15000;
      const saved = localStorage.getItem(modeKey);
      const savedValid = saved === 'MANUAL' || saved === 'AUTO';
      if (managerOn && entityValid && !inGrace) {
        // Also check if user recently toggled mode directly
        const modeToggleTs = Number(localStorage.getItem('ibepower_mode_toggle_ts_' + base)) || 0;
        const inModeGrace = modeToggleTs > 0 && (Date.now() - modeToggleTs) < 8000;
        if (!inModeGrace) {
          localStorage.setItem(modeKey, modeFromEntity);
          uiMode = modeFromEntity;
        } else if (savedValid) {
          uiMode = saved;
        } else {
          uiMode = modeFromEntity;
        }
      } else if (savedValid) {
        uiMode = saved;
      } else {
        uiMode = entityValid ? modeFromEntity : 'AUTO';
      }
    } catch (e) {
      uiMode = entityValid ? modeFromEntity : 'AUTO';
    }
    return uiMode;
  }

  _render() {
    const hass = this._hass;
    if (!hass) return;
    const compact = ibepIsCompactCard(this, 360);
    const t = this._t(hass);
    const slugs = ibepGetSlugs(hass, 'Ibediv', 'calculated_watts', 'sensor');

    if (slugs.length === 0) {
      this._structKey = '';
      this.shadowRoot.innerHTML = `<style>${IBEDIV_CSS}</style><ha-card><div class="card"><div class="logo-wrap"><img src="${ibepLogoUrl(hass)}" alt="Ibepower"></div><div class="no-devices">${t.nodev}</div></div></ha-card>`;
      return;
    }
    const base = ibepResolveSlug(slugs, 'ibep_div_selector', this._config.device);

    // ---- Sensor values ----
    const solarW   = ibepNum(ibepState(hass, base, 'solar_watts'));
    const gridW    = ibepNum(ibepState(hass, base, 'grid_watts'));
    const loadW    = ibepNum(ibepState(hass, base, 'load_watts'));
    const batteryW = ibepNum(ibepState(hass, base, 'battery_power'));
    const batterySoc = ibepNum(ibepState(hass, base, 'battery_soc'));
    const diverterW = ibepNum(ibepState(hass, base, 'calculated_watts'));
    const pwmRaw   = ibepNum(ibepState(hass, base, 'pwm_value'));
    const pwmPct   = pwmRaw !== null ? Math.round(Math.max(0, Math.min(100, pwmRaw))) : null;
    const pwmText  = pwmPct !== null ? (pwmPct + ' %') : '-- %';

    const solarK    = ibepNum(ibepState(hass, base, 'kw_solar_today'));
    const importK   = ibepNum(ibepState(hass, base, 'kw_import_today'));
    const exportK   = ibepNum(ibepState(hass, base, 'kw_export_today'));
    const diverterK = ibepNum(ibepState(hass, base, 'kw_diverter_today'));

    // ---- Entity availability checks ----
    const hasSolar        = ibepValid(ibepState(hass, base, 'solar_watts'));
    const hasGrid         = ibepValid(ibepState(hass, base, 'grid_watts'));
    const hasHome         = ibepValid(ibepState(hass, base, 'load_watts'));
    const hasBatteryPower = ibepValid(ibepState(hass, base, 'battery_power'));
    const hasBatterySoc   = ibepValid(ibepState(hass, base, 'battery_soc'));
    const hasDiverter     = ibepValid(ibepState(hass, base, 'calculated_watts'));
    const hasPwm          = ibepValid(ibepState(hass, base, 'pwm_value'));
    const hasSolarToday   = ibepValid(ibepState(hass, base, 'kw_solar_today'));
    const hasImportToday  = ibepValid(ibepState(hass, base, 'kw_import_today'));
    const hasExportToday  = ibepValid(ibepState(hass, base, 'kw_export_today'));
    const hasDiverterToday= ibepValid(ibepState(hass, base, 'kw_diverter_today'));
    const hasBatt         = hasBatteryPower || hasBatterySoc;
    const hasAnyInverter  = hasHome || hasGrid || hasDiverter || hasSolar || hasBatteryPower;

    const fmtAbsW  = v => v !== null ? Math.round(Math.abs(v)) + ' W' : '-- W';
    const fmtSignW = v => v !== null ? Math.round(v) + ' W' : '-- W';

    // ---- Computed values ----
    let effectiveLoadW;
    if (hasHome && loadW !== null) {
      effectiveLoadW = loadW;
    } else if (hasSolar || hasGrid || hasBatteryPower) {
      effectiveLoadW = (solarW ?? 0) - (gridW ?? 0) - (batteryW ?? 0);
    } else {
      effectiveLoadW = null;
    }
    const solarActive    = hasSolar && Math.abs(solarW ?? 0) > 0;
    const gridActive     = hasGrid && Math.abs(gridW ?? 0) > 0;
    const homeActive     = effectiveLoadW !== null && Math.abs(effectiveLoadW) > 0;
    const batteryActive  = hasBatteryPower && Math.abs(batteryW ?? 0) > 0;
    const diverterActive = hasDiverter && Math.abs(diverterW ?? 0) > 0;
    const inverterW      = (effectiveLoadW ?? 0) + (gridW ?? 0);
    const inverterActive = Math.abs(inverterW) > 0;

    // ---- Connector classes ----
    const cSolarCenter   = 'link-solar-center ' + (solarActive ? 'is-active flow-down' : 'is-idle');
    const battCDir       = (batteryW ?? 0) < 0 ? 'flow-right' : 'flow-left';
    const cBatteryCenter = 'link-battery-center ' + (batteryActive ? ('is-active ' + battCDir) : 'is-idle');
    const gridCDir       = (gridW ?? 0) >= 0 ? 'flow-right' : 'flow-left';
    const cGridCenter    = 'link-grid-center ' + (gridActive ? ('is-active ' + gridCDir) : 'is-idle');
    const cHomeCenter    = 'link-home-center ' + (homeActive ? 'is-active flow-down' : 'is-idle');
    const cSolarBattery  = 'link-solar-battery ' + (solarActive && batteryActive && (batteryW ?? 0) >= 0 ? 'is-active flow-right' : 'is-idle');
    const cSolarGrid     = 'link-solar-grid ' + (solarActive && gridActive && (gridW ?? 0) >= 0 ? 'is-active flow-right' : 'is-idle');
    const cBatteryHome   = 'link-battery-home ' + (batteryActive && (batteryW ?? 0) < 0 && homeActive ? 'is-active flow-right' : 'is-idle');
    const cGridHome      = 'link-grid-home ' + (gridActive && (gridW ?? 0) < 0 && homeActive ? 'is-active flow-right' : 'is-idle');

    const layoutClass = (!hasBatt && hasGrid) ? ' layout-no-batt' : (hasBatt && !hasGrid) ? ' layout-no-grid' : '';

    // ---- Battery icon/color ----
    const battSoc = hasBatterySoc ? Math.max(0, Math.min(100, Math.round(batterySoc ?? 50))) : 50;
    const battIcon = battSoc >= 90 ? 'mdi:battery' : battSoc >= 70 ? 'mdi:battery-high' : battSoc >= 50 ? 'mdi:battery-medium' : battSoc >= 20 ? 'mdi:battery-low' : 'mdi:battery-alert-variant-outline';
    const battColor = battSoc >= 60 ? '#41aa56' : battSoc >= 30 ? '#d8a038' : '#d54343';

    // ---- Direction text ----
    const batteryDirText = hasBatteryPower ? ((batteryW ?? 0) >= 0 ? t.charging : t.discharging) : '';
    const gridDirText    = hasGrid ? ((gridW ?? 0) >= 0 ? t.exporting : t.importing) : '';
    const batterySocText = hasBatterySoc ? ('SoC ' + Math.round(batterySoc ?? 0) + ' %') : '';

    // ---- Entity IDs for more-info ----
    const solarEid    = ibepState(hass, base, 'solar_watts')?.entity_id || '';
    const batteryEid  = ibepState(hass, base, 'battery_power')?.entity_id || '';
    const gridEid     = ibepState(hass, base, 'grid_watts')?.entity_id || '';
    const homeEid     = ibepState(hass, base, 'load_watts')?.entity_id || '';
    const inverterEid = ibepState(hass, base, 'calculated_watts')?.entity_id || '';

    // ---- Switch & Select ----
    const managerObj = ibepSwitchState(hass, base, 'ibediv') || ibepSwitchState(hass, base, 'switch_on_off');
    const managerEid = ibepSwitchEid(hass, base, 'ibediv') || ibepSwitchEid(hass, base, 'switch_on_off');
    const managerOn  = managerObj?.state === 'on';

    const modeObj = ibepSelectState(hass, base, 'modo_de_trabajo') || ibepSelectState(hass, base, 'work_mode_select');
    const modeEid = ibepSelectEid(hass, base, 'modo_de_trabajo') || ibepSelectEid(hass, base, 'work_mode_select');
    const uiMode  = this._resolveUiMode(base, managerOn, modeObj);
    const isManual = uiMode === 'MANUAL';

    const pwmSetEid = ibepNumberEid(hass, base, 'manual') || ibepNumberEid(hass, base, 'pwm_value_setter');
    const pwmSetObj = ibepNumberState(hass, base, 'manual') || ibepNumberState(hass, base, 'pwm_value_setter');
    const pwmSetVal = Math.max(0, Math.min(100, Math.round(ibepNum(pwmSetObj) ?? 0)));

    // ---- PV Strings ----
    const buildPvPill = (label, key) => {
      const vObj = ibepState(hass, base, key + '_voltage');
      const aObj = ibepState(hass, base, key + '_current');
      const wObj = ibepState(hass, base, key + '_power');
      const metric = (obj, digits, unit) => {
        if (!ibepValid(obj)) return '';
        const v = ibepNum(obj);
        const txt = v !== null ? v.toFixed(digits) : '--';
        const eid = obj.entity_id || '';
        return `<span class="pv-metric" data-entity="${eid}"><span class="pv-val" data-v="${key}-${unit.toLowerCase()}">${txt}</span><span class="pv-key">${unit}</span></span>`;
      };
      const metrics = [metric(vObj,1,'V'), metric(aObj,1,'A'), metric(wObj,0,'W')].filter(Boolean);
      if (!metrics.length) return '';
      return `<div class="pv-pill"><span class="pv-title">${label}</span><div class="pv-metrics">${metrics.join('')}</div></div>`;
    };
    const pvCards = [buildPvPill('PV1','pv1'), buildPvPill('PV2','pv2')].filter(Boolean);
    const hasPv = pvCards.length > 0;

    // ---- Temperature pills ----
    const fmtTemp = (obj) => {
      if (!ibepValid(obj)) return '-- °C';
      const v = ibepNum(obj);
      return v !== null ? v.toFixed(1) + '°C' : '-- °C';
    };
    const thermoNameObj = ibepState(hass, base, 'thermo_sensor_name');
    const thermoNameRaw = ibepValid(thermoNameObj) ? String(thermoNameObj.state).trim() : '';
    const thermoLabel   = thermoNameRaw || t.thermo;
    const customNameObj = ibepState(hass, base, 'custom_sensor_name');
    const customNameRaw = ibepValid(customNameObj) ? String(customNameObj.state).trim() : '';
    const customLabel   = customNameRaw || t.custom;
    const tempDefs = [
      { key: 'inverter_temperature', label: t.inverter },
      { key: 'chip_temperature',     label: 'Chip' },
      { key: 'thermo_temperature',   label: thermoLabel },
      { key: 'ibepower_temperature', label: 'Ibepower' },
      { key: 'custom_temperature',   label: customLabel },
    ];
    const tempPills = [];
    for (const d of tempDefs) {
      const obj = ibepState(hass, base, d.key);
      if (!ibepValid(obj)) continue;
      const eid = obj.entity_id || '';
      tempPills.push(`<div class="temp-pill" data-entity="${eid}"><span class="temp-title">${d.label}</span><span class="temp-val" data-v="temp-${d.key}">${fmtTemp(obj)}</span></div>`);
    }
    const hasTemps = tempPills.length > 0;

    // ---- Home sub HTML (needed by both patch and full render) ----
    let homeSubHtml = '';
    if (hasDiverter) {
      if (!compact) homeSubHtml += `<span class="node-sub-line node-sub-title">${t.diverter}</span>`;
      if (hasPwm && !compact) homeSubHtml += `<span class="node-sub-line">${pwmText} - ${fmtAbsW(diverterW)}</span>`;
      else homeSubHtml += `<span class="node-sub-line">${fmtAbsW(diverterW)}</span>`;
    }
    if (hasDiverterToday && !compact) {
      homeSubHtml += `<span class="node-sub-line node-sub-spaced node-sub-title">${t.diverterToday}</span>`;
      homeSubHtml += `<span class="node-sub-line">${ibepFmtK(diverterK)}</span>`;
    }

    // ---- Mode button classes ----
    let modeClass = 'ctrl-mode-disabled';
    if (managerOn && modeObj) {
      modeClass = isManual ? 'ctrl-mode-manual' : 'ctrl-mode-auto';
    }

    // ---- Incremental update: skip full re-render if structure unchanged ----
    const tempKeysStr = tempDefs.filter(d => ibepValid(ibepState(hass, base, d.key))).map(d => d.key).join(',');
    const pvSig = ['pv1','pv2'].map(k => [ibepValid(ibepState(hass,base,k+'_voltage')),ibepValid(ibepState(hass,base,k+'_current')),ibepValid(ibepState(hass,base,k+'_power'))].join('')).join('|');
    const structKey = [slugs.join(','),base,hasSolar,hasGrid,hasBatt,hasBatteryPower,hasBatterySoc,hasDiverter,hasPwm,compact,isManual,!!pwmSetEid,!!modeObj,hasAnyInverter,hasSolarToday,hasImportToday,hasExportToday,hasDiverterToday,hasHome,managerOn,layoutClass,tempKeysStr,pvSig].join('|');
    if (this._structKey === structKey && this.shadowRoot.querySelector('.flow-wrap')) {
      const sr = this.shadowRoot;
      const q = s => sr.querySelector(s);
      // Nodes
      const patchNode = (sel, active, mainText, mainNeg) => {
        const node = q(sel);
        if (!node) return;
        node.classList.toggle('node-active', active);
        node.classList.toggle('node-idle', !active);
        const m = node.querySelector('.node-main');
        if (m) { m.textContent = mainText; if (mainNeg !== undefined) m.classList.toggle('is-negative', mainNeg); }
      };
      patchNode('.node-solar', solarActive, fmtAbsW(solarW));
      patchNode('.node-grid', gridActive, fmtSignW(gridW), (gridW ?? 0) < 0);
      patchNode('.node-home', homeActive, fmtAbsW(effectiveLoadW));
      patchNode('.node-diverter', inverterActive, fmtAbsW(inverterW));
      // Battery node
      const battNode = q('.node-battery');
      if (battNode) {
        battNode.classList.toggle('node-active', batteryActive);
        battNode.classList.toggle('node-idle', !batteryActive);
        const bm = battNode.querySelector('.node-main');
        if (bm) { bm.textContent = fmtSignW(batteryW); bm.classList.toggle('is-negative', (batteryW ?? 0) < 0); }
        const bi = battNode.querySelector('.node-icon');
        if (bi) { bi.setAttribute('icon', battIcon); bi.style.color = battColor; }
        const setText2 = (s, txt) => { const e = battNode.querySelector(s); if (e) e.textContent = txt; };
        setText2('[data-v="batt-dir"]', batteryDirText);
        setText2('[data-v="batt-soc"]', batterySocText);
      }
      // Grid sub text
      const setText = (s, txt) => { const e = q(s); if (e) e.textContent = txt; };
      setText('.node-grid [data-v="grid-dir"]', gridDirText || '--');
      setText('[data-v="div-import-today"]', t.imp + '. ' + ibepFmtK(importK));
      setText('[data-v="div-export-today"]', t.exp + '. ' + ibepFmtK(exportK));
      // Solar today
      const solarSub = q('.node-solar .node-sub');
      if (solarSub && hasSolarToday && !compact) solarSub.textContent = ibepFmtK(solarK);
      // Home sub (small innerHTML, won't cause reflow)
      const homeSub = q('.node-home .node-sub');
      if (homeSub) homeSub.innerHTML = homeSubHtml;
      // Connectors
      const patchConn = (id, cls) => { const e = q('[data-conn="' + id + '"]'); if (e) e.className = 'ibep-flow-connector ' + cls; };
      patchConn('solar-center', cSolarCenter);
      patchConn('battery-center', cBatteryCenter);
      patchConn('grid-center', cGridCenter);
      patchConn('home-center', cHomeCenter);
      patchConn('solar-battery', cSolarBattery);
      patchConn('solar-grid', cSolarGrid);
      patchConn('battery-home', cBatteryHome);
      patchConn('grid-home', cGridHome);
      // PV values
      ['pv1','pv2'].forEach(k => {
        const fMap = {v:['voltage',1],a:['current',1],w:['power',0]};
        Object.entries(fMap).forEach(([u,[field,digits]]) => {
          const el = q(`[data-v="${k}-${u}"]`);
          if (el) { const obj = ibepState(hass,base,k+'_'+field); el.textContent = ibepValid(obj) ? (ibepNum(obj)?.toFixed(digits) ?? '--') : '--'; }
        });
      });
      // Temperature values
      tempDefs.forEach(d => {
        const el = q(`[data-v="temp-${d.key}"]`);
        if (el) { const obj = ibepState(hass, base, d.key); el.textContent = fmtTemp(obj); }
      });
      // Controls
      const mgr = sr.getElementById('manager-toggle');
      if (mgr) { mgr.className = 'ctrl-card ' + (managerOn ? 'ctrl-manager-on' : 'ctrl-manager-off'); const s = mgr.querySelector('.ctrl-state'); if (s) s.textContent = managerOn ? t.on : t.off; }
      const mode = sr.getElementById('mode-toggle');
      if (mode) { mode.className = 'ctrl-card ' + modeClass; const s = mode.querySelector('.ctrl-state'); if (s) s.textContent = isManual ? t.manual : t.auto; }
      // PWM slider (skip if user is dragging or just released)
      if (!this._isSliderBusy()) {
        const sl = sr.getElementById('pwm-slider');
        const dp = sr.getElementById('pwm-display');
        if (sl) { sl.value = pwmSetVal; sl.disabled = !managerOn; }
        if (dp) dp.textContent = pwmSetVal + '%';
        const sw = sl?.parentElement;
        if (sw) { sw.style.setProperty('--ibep-pct', pwmSetVal + '%'); sw.classList.toggle('is-disabled', !managerOn); }
      }
      return;
    }
    this._structKey = structKey;

    // ---- Animation delays (keep animations phase-continuous across re-renders) ----
    const _now = Date.now();
    const _fdel = -(_now % 1050) + 'ms';
    const _gdel = -(_now % 1900) + 'ms';
    const _ndel = -(_now % 3000) + 'ms';
    const _cDel = `animation-delay:${_fdel},${_gdel}`;
    const _nDel = `animation-delay:${_ndel}`;

    // ---- Build connectors HTML ----
    let connectorsHtml = '';
    if (hasSolar)        connectorsHtml += `<div class="ibep-flow-connector ${cSolarCenter}" data-conn="solar-center" style="${_cDel}"></div>`;
    if (hasBatteryPower) connectorsHtml += `<div class="ibep-flow-connector ${cBatteryCenter}" data-conn="battery-center" style="${_cDel}"></div>`;
    if (hasGrid)         connectorsHtml += `<div class="ibep-flow-connector ${cGridCenter}" data-conn="grid-center" style="${_cDel}"></div>`;
    connectorsHtml += `<div class="ibep-flow-connector ${cHomeCenter}" data-conn="home-center" style="${_cDel}"></div>`;
    if (hasSolar && hasBatteryPower) connectorsHtml += `<div class="ibep-flow-connector ${cSolarBattery}" data-conn="solar-battery" style="${_cDel}"></div>`;
    if (hasSolar && hasGrid)         connectorsHtml += `<div class="ibep-flow-connector ${cSolarGrid}" data-conn="solar-grid" style="${_cDel}"></div>`;
    if (hasBatteryPower) connectorsHtml += `<div class="ibep-flow-connector ${cBatteryHome}" data-conn="battery-home" style="${_cDel}"></div>`;
    if (hasGrid)         connectorsHtml += `<div class="ibep-flow-connector ${cGridHome}" data-conn="grid-home" style="${_cDel}"></div>`;

    // ---- Build nodes HTML ----
    let nodesHtml = '';
    if (hasSolar) {
      nodesHtml += `
        <div class="ibep-flow-node node-solar ${solarActive?'node-active':'node-idle'}" data-entity="${solarEid}" style="${_nDel}">
          <ha-icon class="node-icon" icon="mdi:solar-power"></ha-icon>
          <div class="node-main">${fmtAbsW(solarW)}</div>
          ${hasSolarToday && !compact ? `<div class="node-sub">${ibepFmtK(solarK)}</div>` : ''}
        </div>`;
    }
    if (hasBatt) {
      nodesHtml += `
        <div class="ibep-flow-node node-battery ${batteryActive?'node-active':'node-idle'}" data-entity="${batteryEid}" style="${_nDel}">
          <ha-icon class="node-icon node-icon-rotated" icon="${battIcon}" style="color:${battColor};"></ha-icon>
          ${hasBatteryPower ? `<div class="node-main ${(batteryW??0)<0?'is-negative':''}">${fmtSignW(batteryW)}</div>` : ''}
          <div class="node-sub">
            ${compact
              ? (batterySocText ? `<span class="node-sub-line node-soc" data-v="batt-soc">${batterySocText}</span>` : '')
              : (batteryDirText ? `<span class="node-sub-line node-sub-title" data-v="batt-dir">${batteryDirText}</span>` : '') + (batterySocText ? `<span class="node-sub-line node-soc" data-v="batt-soc">${batterySocText}</span>` : '')}
          </div>
        </div>`;
    }
    if (hasGrid) {
      nodesHtml += `
        <div class="ibep-flow-node node-grid ${gridActive?'node-active':'node-idle'}" data-entity="${gridEid}" style="${_nDel}">
          <ha-icon class="node-icon" icon="mdi:transmission-tower"></ha-icon>
          <div class="node-main ${(gridW??0)<0?'is-negative':''}">${fmtSignW(gridW)}</div>
          <div class="node-sub">
            <span class="node-sub-line node-sub-title" data-v="grid-dir">${gridDirText || '--'}</span>
            ${hasImportToday && !compact ? `<span class="node-sub-line" data-v="div-import-today">${t.imp}. ${ibepFmtK(importK)}</span>` : ''}
            ${hasExportToday && !compact ? `<span class="node-sub-line" data-v="div-export-today">${t.exp}. ${ibepFmtK(exportK)}</span>` : ''}
          </div>
        </div>`;
    }
    nodesHtml += `
      <div class="ibep-flow-node node-home ${homeActive?'node-active':'node-idle'}" data-entity="${homeEid}" style="${_nDel}">
        <ha-icon class="node-icon" icon="mdi:home-outline"></ha-icon>
        <div class="node-main">${fmtAbsW(effectiveLoadW)}</div>
        <div class="node-sub">${homeSubHtml}</div>
      </div>`;

    // Inverter center node
    if (hasAnyInverter) {
      nodesHtml += `
        <div class="ibep-flow-node node-diverter ${inverterActive?'node-active':'node-idle'}" data-entity="${inverterEid}" style="${_nDel}">
          <ha-icon class="node-icon" icon="mdi:lightning-bolt"></ha-icon>
          <div class="node-sub node-sub-top">${compact ? '' : t.inverter}</div>
          <div class="node-main">${fmtAbsW(inverterW)}</div>
        </div>`;
    }

    // ---- Full render ----
    this.shadowRoot.innerHTML = `
      <style>${IBEDIV_CSS}</style>
      <ha-card>
        <div class="card${compact ? ' compact' : ''}">
          <div class="logo-wrap"><img src="${ibepLogoUrl(hass)}" alt="Ibepower"></div>
          ${ibepRenderDropdown(slugs, base, 'ibep_div_selector', this._config.device)}

          <!-- Diamond flow -->
          <div class="flow-wrap${layoutClass}">
            ${connectorsHtml}
            ${nodesHtml}
          </div>

          <!-- PV strings -->
          ${hasPv ? `<div class="pv-section"><div class="pv-wrap">${pvCards.join('')}</div></div>` : ''}

          <!-- Temperature sensors -->
          ${hasTemps ? `<div class="temp-section"><div class="temp-wrap">${tempPills.join('')}</div></div>` : ''}

          <!-- Controls -->
          <div class="ctrl-grid">
            <div class="ctrl-card ${managerOn ? 'ctrl-manager-on' : 'ctrl-manager-off'}" id="manager-toggle">
              <span class="ctrl-label">${t.manager}</span>
              <span class="ctrl-state">${managerOn ? t.on : t.off}</span>
            </div>
            ${modeObj ? `
            <div class="ctrl-card ${modeClass}" id="mode-toggle">
              <span class="ctrl-label">${t.mode}</span>
              <span class="ctrl-state">${isManual ? t.manual : t.auto}</span>
            </div>` : ''}
          </div>

          <!-- PWM slider (only in manual mode) -->
          ${isManual && pwmSetEid ? `
          <div class="slider-section">
            <div class="slider-wrap${managerOn ? '' : ' is-disabled'}" style="--ibep-pct:${pwmSetVal}%;">
              <input class="slider-input" type="range" min="0" max="100" step="1" value="${pwmSetVal}" id="pwm-slider" ${managerOn ? '' : 'disabled'}>
              <div class="slider-overlay"><span class="slider-value" id="pwm-display">${pwmSetVal}%</span></div>
            </div>
          </div>` : ''}
        </div>
      </ha-card>`;

    // ---- Event handlers ----

    // More-info on nodes & temp pills
    this.shadowRoot.querySelectorAll('.ibep-flow-node[data-entity], .temp-pill[data-entity], .pv-metric[data-entity]').forEach(el => {
      el.addEventListener('click', () => {
        const eid = el.dataset.entity;
        if (eid) this.dispatchEvent(new CustomEvent('hass-more-info', { detail: { entityId: eid }, bubbles: true, composed: true }));
      });
    });

    // Manager toggle
    this.shadowRoot.getElementById('manager-toggle')?.addEventListener('click', () => {
      if (managerEid) hass.callService('switch', 'toggle', { entity_id: managerEid });
    });

    // Mode toggle
    this.shadowRoot.getElementById('mode-toggle')?.addEventListener('click', () => {
      if (!managerOn || !modeEid || !modeObj) return;
      const opts = modeObj.attributes?.options || [];
      const raw = String(modeObj.state ?? '').toUpperCase();
      const target = raw.startsWith('MAN') ? 'AUTO' : 'MANUAL';
      try {
        localStorage.setItem('ibepower_ui_mode_' + base, target);
        localStorage.setItem('ibepower_mgr_toggle_ts_' + base, '0');
        localStorage.setItem('ibepower_mode_toggle_ts_' + base, String(Date.now()));
      } catch(e) {}
      const match = opts.find(o => o.toUpperCase() === target);
      if (match) hass.callService('select', 'select_option', { entity_id: modeEid, option: match });
    });

    // PWM slider
    const slider = this.shadowRoot.getElementById('pwm-slider');
    const display = this.shadowRoot.getElementById('pwm-display');
    const sliderWrap = slider?.parentElement;
    if (slider) {
      const markActive = () => { this._sliderActive = true; };
      slider.addEventListener('pointerdown', markActive);
      slider.addEventListener('touchstart', markActive, { passive: true });
      // Release listener on document so we catch releases outside the card
      if (this._sliderDocCleanup) this._sliderDocCleanup();
      const markInactive = () => {
        if (this._sliderActive) {
          this._sliderActive = false;
          this._sliderReleasedAt = Date.now();
        }
      };
      document.addEventListener('pointerup', markInactive);
      document.addEventListener('touchend', markInactive);
      document.addEventListener('pointercancel', markInactive);
      this._sliderDocCleanup = () => {
        document.removeEventListener('pointerup', markInactive);
        document.removeEventListener('touchend', markInactive);
        document.removeEventListener('pointercancel', markInactive);
      };
      slider.addEventListener('input', () => {
        const pct = Math.max(0, Math.min(100, Number(slider.value) || 0));
        if (display) display.textContent = pct + '%';
        if (sliderWrap) sliderWrap.style.setProperty('--ibep-pct', pct + '%');
      });
      slider.addEventListener('change', () => {
        if (pwmSetEid) {
          hass.callService('number', 'set_value', { entity_id: pwmSetEid, value: Number(slider.value) });
        }
      });
    }

    // Dropdown
    ibepSetupDropdown(this.shadowRoot, () => { this._render(); }, this);
  }
}

// =============================================================================
// Config Editor (shared by all three card types)
// =============================================================================
class IbepowerCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
    this._lastSlugsKey = '';
  }

  set hass(hass) {
    this._hass = hass;
    // Only re-render if the device list actually changed (avoid destroying the <select> while open)
    const slugsKey = this._computeSlugsKey(hass);
    if (slugsKey !== this._lastSlugsKey) {
      this._lastSlugsKey = slugsKey;
      this._render();
    }
  }

  setConfig(config) {
    this._config = { ...config };
    this._lastSlugsKey = '';
    if (this._hass) this._render();
  }

  _resolveDeviceType() {
    let deviceType = this._config.device_type;
    if (!deviceType) {
      const cfgType = String(this._config.type || '').toLowerCase();
      if (cfgType.includes('ibediv')) deviceType = 'Ibediv';
      else if (cfgType.includes('ibemeter')) deviceType = 'Ibemeter';
      else if (cfgType.includes('ibeplug')) deviceType = 'Ibeplug';
    }
    return deviceType;
  }

  _resolveMarker(model) {
    if (model === 'Ibeplug') return { markerField: 'ibeplug', entityDomain: 'switch' };
    if (model === 'Ibediv') return { markerField: 'calculated_watts', entityDomain: 'sensor' };
    return { markerField: 'grid_voltage', entityDomain: 'sensor' };
  }

  _computeSlugsKey(hass) {
    if (!hass) return '';
    const deviceType = this._resolveDeviceType();
    if (!deviceType) return '';
    const model = String(deviceType).charAt(0).toUpperCase() + String(deviceType).slice(1).toLowerCase();
    const { markerField, entityDomain } = this._resolveMarker(model);
    const slugs = ibepGetSlugs(hass, model, markerField, entityDomain);
    return model + ':' + slugs.join(',') + ':' + (this._config.device || '');
  }

  _render() {
    const hass = this._hass;
    if (!hass) return;
    const t = ibepI18n(hass);

    const deviceType = this._resolveDeviceType();

    if (!deviceType) {
      this.shadowRoot.innerHTML = `
        <style>
          .editor { padding: 16px; font-family: var(--paper-font-body1_-_font-family, inherit); }
          .hint { font-size: 0.84rem; color: var(--secondary-text-color); }
        </style>
        <div class="editor"><div class="hint">${t.loading_devices}</div></div>`;
      return;
    }

    // Get available devices of this type
    const model = String(deviceType).charAt(0).toUpperCase() + String(deviceType).slice(1).toLowerCase();
    const { markerField, entityDomain } = this._resolveMarker(model);

    const slugs = ibepGetSlugs(hass, model, markerField, entityDomain);
    const autoTpl = slugs.length === 1 ? t.auto_detected_one : t.auto_detected_other;
    const autoLabel = autoTpl.replace('{count}', String(slugs.length));

    this.shadowRoot.innerHTML = `
      <style>
        .editor { padding: 16px; font-family: var(--paper-font-body1_-_font-family, inherit); }
        .row { margin-bottom: 12px; }
        label { display: block; font-weight: 500; margin-bottom: 4px; font-size: 0.9rem; color: var(--primary-text-color); }
        .hint { font-size: 0.78rem; color: var(--secondary-text-color); margin-top: 4px; }
        select {
          width: 100%; padding: 8px 12px; border-radius: 8px;
          border: 1px solid var(--divider-color, #ccc);
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color); font-size: 0.9rem;
        }
      </style>
      <div class="editor">
        <div class="row">
          <label>${t.select_device}</label>
          <select id="device-select">
            <option value="">${autoLabel}</option>
            ${slugs.map(s => `<option value="${s}" ${this._config.device === s ? 'selected' : ''}>${s.replace(/_/g, ' ')}</option>`).join('')}
          </select>
          <div class="hint">${t.auto_hint}</div>
        </div>
      </div>`;

    this.shadowRoot.getElementById('device-select')?.addEventListener('change', (e) => {
      this._config = { ...this._config, device: e.target.value || undefined };
      this._lastSlugsKey = '';
      this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: this._config }, bubbles: true, composed: true }));
    });
  }
}

// =============================================================================
// Register custom elements and cards
// =============================================================================
if (!customElements.get('ibepower-ibeplug-card')) {
  customElements.define('ibepower-ibeplug-card', IbepowerIbeplugCard);
}
if (!customElements.get('ibepower-ibemeter-card')) {
  customElements.define('ibepower-ibemeter-card', IbepowerIbemeterCard);
}
if (!customElements.get('ibepower-ibediv-card')) {
  customElements.define('ibepower-ibediv-card', IbepowerIbedivCard);
}
if (!customElements.get('ibepower-card-editor')) {
  customElements.define('ibepower-card-editor', IbepowerCardEditor);
}

window.customCards = window.customCards || [];

const IBEP_PICKER_LANG = (() => {
  const raw = String((typeof navigator !== 'undefined' && navigator.language) || 'en').toLowerCase();
  if (raw.startsWith('es')) return 'es';
  if (raw.startsWith('pt')) return 'pt';
  return 'en';
})();

const IBEP_PICKER_I18N = {
  es: {
    ibeplug_name: 'Ibepower Ibeplug',
    ibediv_name: 'Ibepower Ibediv',
    ibemeter_name: 'Ibepower Ibemeter',
    ibeplug_desc: 'Tarjeta de enchufe inteligente con monitorización de potencia, control ON/OFF y seguimiento de energía.',
    ibediv_desc: 'Tarjeta de derivador con flujo solar/red/batería, controles del gestor y deslizador PWM.',
    ibemeter_desc: 'Tarjeta de medidor con visualización de flujo solar/red/casa y métricas de red.',
  },
  en: {
    ibeplug_name: 'Ibepower Ibeplug',
    ibediv_name: 'Ibepower Ibediv',
    ibemeter_name: 'Ibepower Ibemeter',
    ibeplug_desc: 'Smart plug card with power monitoring, ON/OFF toggle, and energy tracking.',
    ibediv_desc: 'Energy diverter card with solar/grid/battery flow, manager controls and PWM slider.',
    ibemeter_desc: 'Energy meter card with solar/grid/home flow visualization and grid metrics.',
  },
  pt: {
    ibeplug_name: 'Ibepower Ibeplug',
    ibediv_name: 'Ibepower Ibediv',
    ibemeter_name: 'Ibepower Ibemeter',
    ibeplug_desc: 'Cartão de tomada inteligente com monitoramento de potência, controle ON/OFF e acompanhamento de energia.',
    ibediv_desc: 'Cartão de desviador com fluxo solar/rede/bateria, controles do gestor e controle deslizante PWM.',
    ibemeter_desc: 'Cartão de medidor com visualização de fluxo solar/rede/casa e métricas da rede.',
  },
};

const ibepPickerText = IBEP_PICKER_I18N[IBEP_PICKER_LANG] || IBEP_PICKER_I18N.en;

window.customCards.push(
  {
    type: 'ibepower-ibeplug-card',
    name: ibepPickerText.ibeplug_name,
    description: ibepPickerText.ibeplug_desc,
    preview: true,
    documentationURL: 'https://github.com/Ibepower/Ibepower-Homeassistant-Integration',
  },
  {
    type: 'ibepower-ibediv-card',
    name: ibepPickerText.ibediv_name,
    description: ibepPickerText.ibediv_desc,
    preview: true,
    documentationURL: 'https://github.com/Ibepower/Ibepower-Homeassistant-Integration',
  },
  {
    type: 'ibepower-ibemeter-card',
    name: ibepPickerText.ibemeter_name,
    description: ibepPickerText.ibemeter_desc,
    preview: true,
    documentationURL: 'https://github.com/Ibepower/Ibepower-Homeassistant-Integration',
  }
);

console.info(`%c IBEPOWER CARDS %c v${IBEP_CARD_VERSION} `, 'background:#2e7d32;color:#fff;font-weight:700;', 'background:#1b5e20;color:#4cdf6b;font-weight:700;');
