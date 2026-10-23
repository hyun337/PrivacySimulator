/**
 * Privacy Simulator - Frontend Application v3
 * 개인정보 노출 시뮬레이터 프론트엔드
 * Features: Search + Numbered Pagination
 */

// ============================================
// Configuration
// ============================================
const API_BASE_URL = 'http://localhost:5001';
const PER_PAGE = 12;

// ============================================
// State Management
// ============================================
let state = {
  allUsers: [],
  filteredUsers: [],
  totalUsers: 0,
  currentPage: 1,
  totalPages: 1,
  searchQuery: '',
  personaFilter: '',
  statistics: null,
  isLoading: false
};

// ============================================
// DOM Elements
// ============================================
const elements = {
  loadingOverlay: document.getElementById('loadingOverlay'),
  statusDot: document.getElementById('statusDot'),
  statusText: document.getElementById('statusText'),
  usersGrid: document.getElementById('usersGrid'),
  totalUsers: document.getElementById('totalUsers'),
  searchInput: document.getElementById('searchInput'),
  typeFilter: document.getElementById('typeFilter'),
  pagination: document.getElementById('pagination'),
  paginationNumbers: document.getElementById('paginationNumbers'),
  prevBtn: document.getElementById('prevBtn'),
  nextBtn: document.getElementById('nextBtn'),
  analysisModal: document.getElementById('analysisModal'),
  modalBody: document.getElementById('modalBody'),
  closeModal: document.getElementById('closeModal'),
  totalUsersStat: document.getElementById('totalUsersStat'),
  personaDistribution: document.getElementById('personaDistribution')
};

// ============================================
// Loading State Management
// ============================================
function showLoading(text = '로딩 중...') {
  elements.loadingOverlay.querySelector('.loading-text').textContent = text;
  elements.loadingOverlay.classList.add('active');
  state.isLoading = true;
}

function hideLoading() {
  elements.loadingOverlay.classList.remove('active');
  state.isLoading = false;
}

// ============================================
// API Functions
// ============================================
async function checkServerStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    if (response.ok) {
      const data = await response.json();
      elements.statusDot.classList.remove('disconnected');
      elements.statusDot.classList.add('connected');
      elements.statusText.textContent = `서버 연결됨 (${data.total_users}명)`;
      return true;
    }
  } catch (error) {
    console.error('Server connection failed:', error);
  }

  elements.statusDot.classList.remove('connected');
  elements.statusDot.classList.add('disconnected');
  elements.statusText.textContent = '서버 연결 실패';
  return false;
}

async function fetchAllUsers() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/users?page=1&per_page=200`);
    if (!response.ok) throw new Error('Failed to fetch users');

    const data = await response.json();
    state.allUsers = data.users;
    state.totalUsers = data.total;

    return data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
}

async function analyzeUser(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });

    if (!response.ok) throw new Error('Analysis failed');
    return await response.json();
  } catch (error) {
    console.error('Error analyzing user:', error);
    throw error;
  }
}

async function fetchStatistics() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/statistics`);
    if (!response.ok) throw new Error('Failed to fetch statistics');

    const data = await response.json();
    state.statistics = data;
    return data;
  } catch (error) {
    console.error('Error fetching statistics:', error);
    throw error;
  }
}

// ============================================
// Filter & Pagination Functions
// ============================================
function applyFilters() {
  let filtered = [...state.allUsers];

  if (state.searchQuery) {
    const query = state.searchQuery.toLowerCase();
    filtered = filtered.filter(user =>
      user.user_id.toLowerCase().includes(query)
    );
  }

  if (state.personaFilter) {
    filtered = filtered.filter(user =>
      user.persona === state.personaFilter
    );
  }

  state.filteredUsers = filtered;
  state.totalPages = Math.ceil(filtered.length / PER_PAGE);
  state.currentPage = 1;
}

function getCurrentPageUsers() {
  const start = (state.currentPage - 1) * PER_PAGE;
  const end = start + PER_PAGE;
  return state.filteredUsers.slice(start, end);
}

function goToPage(page) {
  if (page < 1 || page > state.totalPages) return;
  state.currentPage = page;
  renderUserCards();
  renderPagination();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// Rendering Functions
// ============================================
function getPersonaIcon(persona) {
  const icons = {
    'office_worker': '💼',
    'student': '📚',
    'freelancer': '💻',
    'parent': '👶',
    'business_owner': '🏢'
  };
  return icons[persona] || '👤';
}

function getPersonaLabel(persona) {
  const labels = {
    'office_worker': '직장인',
    'student': '학생',
    'freelancer': '프리랜서',
    'parent': '부모',
    'business_owner': '사업자'
  };
  return labels[persona] || persona;
}

// Estimate risk level based on persona (rough preview before full analysis)
function getEstimatedRisk(persona) {
  const riskMap = {
    'business_owner': { level: 'high', label: '높음' },
    'office_worker': { level: 'medium', label: '중간' },
    'freelancer': { level: 'medium', label: '중간' },
    'parent': { level: 'high', label: '높음' },
    'student': { level: 'low', label: '낮음' }
  };
  return riskMap[persona] || { level: 'medium', label: '중간' };
}

function renderUserCards() {
  const users = getCurrentPageUsers();

  if (users.length === 0) {
    elements.usersGrid.innerHTML = `
      <div class="no-results">
        <div class="icon">🔍</div>
        <h3>검색 결과가 없습니다</h3>
        <p>다른 검색어나 필터를 시도해보세요</p>
      </div>
    `;
    return;
  }

  elements.usersGrid.innerHTML = users.map(user => {
    const risk = getEstimatedRisk(user.persona);
    return `
    <div class="glass-card user-card" data-user-id="${user.user_id}">
      <div class="user-card-header">
        <div class="user-avatar">${getPersonaIcon(user.persona)}</div>
        <div class="user-info">
          <h3>${user.user_id}</h3>
          <p>가상 사용자</p>
        </div>
      </div>
      <div class="user-card-meta">
        <div class="meta-item">
          <span class="icon">🎂</span>
          <span>${user.age}세</span>
        </div>
        <div class="persona-badge">
          ${getPersonaIcon(user.persona)} ${getPersonaLabel(user.persona)}
        </div>
      </div>
      <div class="risk-indicator">
        <span class="risk-indicator-label">예상 위험도</span>
        <span class="risk-indicator-value ${risk.level}">${risk.label}</span>
      </div>
      <button class="analyze-btn" onclick="handleAnalyze('${user.user_id}')">
        <span>🔍</span>
        상세 분석하기
      </button>
    </div>
  `;
  }).join('');
}

function renderPagination() {
  // Update prev/next buttons
  elements.prevBtn.disabled = state.currentPage <= 1;
  elements.nextBtn.disabled = state.currentPage >= state.totalPages;

  // Generate page numbers
  const pages = [];
  const total = state.totalPages;
  const current = state.currentPage;

  if (total <= 7) {
    // Show all pages if 7 or fewer
    for (let i = 1; i <= total; i++) {
      pages.push(i);
    }
  } else {
    // Show first, last, current, and ellipsis
    pages.push(1);

    if (current > 3) {
      pages.push('...');
    }

    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      if (!pages.includes(i)) {
        pages.push(i);
      }
    }

    if (current < total - 2) {
      pages.push('...');
    }

    if (!pages.includes(total)) {
      pages.push(total);
    }
  }

  elements.paginationNumbers.innerHTML = pages.map(page => {
    if (page === '...') {
      return '<span class="page-ellipsis">...</span>';
    }
    return `
      <button class="page-number ${page === current ? 'active' : ''}" 
              onclick="goToPage(${page})">
        ${page}
      </button>
    `;
  }).join('');
}

function updateTotalBadge() {
  const isFiltered = state.searchQuery || state.personaFilter;

  elements.totalUsers.innerHTML = isFiltered
    ? `<span style="color: var(--accent-light); font-weight: 600;">검색 결과: ${state.filteredUsers.length}명 / ${state.totalUsers}명</span>`
    : `<span style="color: var(--accent-light); font-weight: 600;">총 ${state.totalUsers}명</span>`;
}

function renderStatistics(stats) {
  if (!stats) return;

  elements.totalUsersStat.textContent = stats.total;

  const distribution = stats.persona_distribution || {};
  const maxValue = Math.max(...Object.values(distribution));

  elements.personaDistribution.innerHTML = Object.entries(distribution)
    .sort((a, b) => b[1] - a[1])
    .map(([persona, count]) => {
      const percentage = (count / stats.total * 100).toFixed(1);
      const width = (count / maxValue * 100);

      return `
        <div class="persona-bar">
          <div class="persona-label">
            ${getPersonaIcon(persona)} ${getPersonaLabel(persona)}
          </div>
          <div class="persona-progress">
            <div class="persona-progress-fill ${persona.replace('_', '-')}" 
                 style="width: ${width}%">
              ${count}명 (${percentage}%)
            </div>
          </div>
        </div>
      `;
    }).join('');
}

// ============================================
// Analysis Result Rendering
// ============================================
function getRiskLevelClass(level) {
  const levelMap = {
    'Low': 'low',
    'Medium': 'medium',
    'High': 'high',
    'Critical': 'critical'
  };
  return levelMap[level] || 'low';
}

function getRiskLevelKorean(level) {
  const labels = {
    'Low': '낮음',
    'Medium': '중간',
    'High': '높음',
    'Critical': '매우 높음'
  };
  return labels[level] || level;
}

function renderRiskGauge(score, level) {
  const circumference = 2 * Math.PI * 75;
  const offset = circumference - (score / 100) * circumference;
  const levelClass = getRiskLevelClass(level);

  return `
    <div class="risk-gauge-container">
      <div class="risk-gauge">
        <svg viewBox="0 0 180 180">
          <circle class="risk-gauge-bg" cx="90" cy="90" r="75"/>
          <circle class="risk-gauge-fill ${levelClass}" 
                  cx="90" cy="90" r="75"
                  stroke-dasharray="${circumference}"
                  stroke-dashoffset="${offset}"/>
        </svg>
        <div class="risk-gauge-center">
          <div class="risk-score ${levelClass}">${score}</div>
          <div class="risk-label">/ 100</div>
        </div>
      </div>
      <div class="risk-level-badge ${levelClass}">
        위험도: ${getRiskLevelKorean(level)}
      </div>
    </div>
  `;
}

function renderInferenceCards(inference) {
  const items = [
    { key: 'residence_inferred', confKey: 'residence', icon: '🏠', label: '주거지' },
    { key: 'workplace_inferred', confKey: 'workplace', icon: '🏢', label: '직장 위치' },
    { key: 'lifestyle_pattern_inferred', confKey: 'lifestyle', icon: '📱', label: '생활 패턴' },
    { key: 'economic_level_inferred', confKey: 'economic', icon: '💰', label: '경제 수준' },
    { key: 'family_structure_inferred', confKey: 'family', icon: '👨‍👩‍👧‍👦', label: '가구 구성' }
  ];

  const confidences = inference.confidence_scores || {};

  return items.map(item => {
    const isInferred = inference[item.key];
    // 백엔드에서 보낸 항목별 신뢰도 값을 가져옴
    const confidence = confidences[item.confKey] || 0; 
    const confidencePercent = Math.round(confidence * 100);

    let detailHtml = '';
    if (isInferred && inference.inferred_details && inference.inferred_details[item.confKey]) {
      const detail = inference.inferred_details[item.confKey];
      if (detail.area) {
        detailHtml = `<div class="inference-detail"><strong>지역:</strong> ${detail.area}</div>`;
        if (detail.evidence_count) detailHtml += `<div class="inference-detail"><strong>증거:</strong> ${detail.evidence_count}개</div>`;
      } else if (detail.level) {
        detailHtml = `<div class="inference-detail"><strong>수준:</strong> ${detail.level}</div>`;
      } else if (detail.dominant_time) {
        detailHtml = `<div class="inference-detail"><strong>주 활동:</strong> ${detail.dominant_time}</div>`;
      } else if (detail.description) {
        detailHtml = `<div class="inference-detail"><strong>특징:</strong> ${detail.description}</div>`;
      }
    }

    return `
      <div class="inference-card ${isInferred ? 'inferred' : 'not-inferred'}">
        <div class="inference-card-header">
          <div class="inference-card-title">
            <span class="icon">${item.icon}</span>
            <span>${item.label}</span>
          </div>
          ${isInferred ? `<span class="confidence-badge">${confidencePercent}%</span>` : ''}
        </div>
        ${isInferred ? detailHtml : '<div class="inference-detail">추론 데이터 부족</div>'}
      </div>
    `;
  }).join('');
}

function renderRecommendations(recommendations) {
  if (!recommendations || recommendations.length === 0) return '';

  return `
    <div class="recommendations-section">
      <h3>📋 권장사항</h3>
      <ul class="recommendation-list">
        ${recommendations.map(rec => {
    let itemClass = '';
    if (rec.includes('[!]')) itemClass = 'warning';
    else if (rec.includes('[OK]')) itemClass = 'success';

    return `
            <li class="recommendation-item ${itemClass}">
              <span class="recommendation-text">${rec}</span>
            </li>
          `;
  }).join('')}
      </ul>
    </div>
  `;
}

function renderBreakdown(breakdown) {
  if (!breakdown) return '';

  return `
    <div class="glass-card" style="margin-top: var(--space-md);">
      <h4 style="margin-bottom: var(--space-md);">📊 점수 상세</h4>
      <div style="display: grid; gap: var(--space-sm); font-size: var(--font-size-sm);">
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">기본 점수</span>
          <span>${breakdown.base_score?.toFixed(1) || 0}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">신뢰도 조정</span>
          <span>${breakdown.confidence_adjusted?.toFixed(1) || 0}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">시너지 보너스</span>
          <span style="color: var(--risk-high);">+${breakdown.synergy_bonus?.toFixed(1) || 0}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">노출 패널티</span>
          <span style="color: var(--risk-critical);">+${breakdown.exposure_penalty?.toFixed(1) || 0}</span>
        </div>
        <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: var(--space-sm) 0;">
        <div style="display: flex; justify-content: space-between; font-weight: 600;">
          <span>최종 점수</span>
          <span style="color: var(--accent-primary);">${breakdown.total_score || 0}</span>
        </div>
      </div>
    </div>
  `;
}

function renderAnalysisResult(data) {
  const { inference_results, risk_assessment, recommendations } = data;

  elements.modalBody.innerHTML = `
    <div style="text-align: center; margin-bottom: var(--space-xl);">
      <div class="user-avatar" style="width: 72px; height: 72px; font-size: 2.2rem; margin: 0 auto var(--space-md);">
        ${getPersonaIcon(data.persona)}
      </div>
      <h3>${data.user_id}</h3>
      <div class="persona-badge" style="margin-top: var(--space-sm);">
        ${getPersonaLabel(data.persona)}
      </div>
    </div>
    
    ${renderRiskGauge(risk_assessment.score, risk_assessment.level)}
    ${renderBreakdown(risk_assessment.breakdown)}
    
    <div class="inference-section" style="margin-top: var(--space-xl);">
      <h3>🔍 추론된 정보</h3>
      <div class="inference-grid">
        ${renderInferenceCards(inference_results)}
      </div>
    </div>
    
    ${renderRecommendations(recommendations)}

    <div class="raw-data-section" style="margin-top: var(--space-2xl); border-top: 1px dashed rgba(255,255,255,0.1); padding-top: var(--space-xl);">
        <button id="toggle-raw-data-btn" class="analyze-btn" style="background: #2d2d42;">
            🔍 분석에 사용된 원시 데이터(Raw Data) 보기
        </button>
        <div id="raw-data-container" class="hidden" style="margin-top: var(--space-md);">
            <div class="data-tabs" style="display: flex; gap: var(--space-sm); margin-bottom: var(--space-md);">
                <button class="page-number active" data-tab="location">위치 기록</button>
                <button class="page-number" data-tab="sns">SNS 활동</button>
            </div>
            <div id="raw-data-table-wrapper" class="glass-card" style="padding: 0; overflow: hidden;">
                </div>
        </div>
    </div>
  `;

  const fullUserData = data;
  setupRawDataEvents(fullUserData);
}

function renderRawTable(userData, type) {
  const wrapper = document.getElementById('raw-data-table-wrapper');
  
  // 데이터가 아예 없는 경우 방어 로직
  if (!userData || !userData.inference_results) {
    wrapper.innerHTML = '<div style="padding:20px; text-align:center; color:var(--risk-high);">분석 데이터를 불러올 수 없습니다.</div>';
    return;
  }

  // 백엔드 구조상 데이터는 보통 data_fragments 혹은 원본 JSON의 일부로 전달됨
  // 만약 analyzeUser 결과(data)에 원본 데이터가 포함되어 있다면 아래와 같이 접근
  const fragments = userData.data_fragments || {};
  
  let html = '<table style="width: 100%; border-collapse: collapse; font-size: var(--font-size-sm); color: var(--text-primary);">';
  
  if (type === 'location') {
    const history = fragments.location_history || [];
    
    if (history.length === 0) {
      wrapper.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-muted);">수집된 위치 기록이 없습니다.</div>';
      return;
    }

    html += `
      <thead style="background: rgba(255,255,255,0.05); color: var(--accent-primary);">
        <tr>
          <th style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">시간</th>
          <th style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">지역</th>
          <th style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">유형</th>
        </tr>
      </thead>
      <tbody>`;

    // 최신순으로 최대 20개만 표시
    history.slice(0, 20).forEach(loc => {
      const time = loc.timestamp ? loc.timestamp.split('T')[1].substring(0, 5) : '00:00';
      html += `
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
          <td style="padding: 10px; text-align: center;">${time}</td>
          <td style="padding: 10px; text-align: center;">${loc.area || '알 수 없음'}</td>
          <td style="padding: 10px; text-align: center;">
            <span class="persona-badge" style="font-size: 10px; padding: 2px 6px;">${loc.type || '일반'}</span>
          </td>
        </tr>`;
    });

  } else {
    const sns = fragments.sns_activities || [];
    
    if (sns.length === 0) {
      wrapper.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-muted);">수집된 SNS 활동 내역이 없습니다.</div>';
      return;
    }

    html += `
      <thead style="background: rgba(255,255,255,0.05); color: var(--accent-primary);">
        <tr>
          <th style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">날짜</th>
          <th style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">플랫폼</th>
          <th style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">해시태그</th>
        </tr>
      </thead>
      <tbody>`;

    sns.slice(0, 20).forEach(act => {
      const date = act.timestamp ? act.timestamp.split('T')[0] : '0000-00-00';
      html += `
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
          <td style="padding: 10px; text-align: center;">${date}</td>
          <td style="padding: 10px; text-align: center; text-transform: capitalize;">${act.platform || 'SNS'}</td>
          <td style="padding: 10px; color: var(--accent-light);">
            ${act.hashtags ? act.hashtags.map(tag => `<span style="margin-right:5px;">${tag}</span>`).join('') : '-'}
          </td>
        </tr>`;
    });
  }
  
  html += '</tbody></table>';
  wrapper.innerHTML = html;
}

function setupRawDataEvents(userData) {
  const btn = document.getElementById('toggle-raw-data-btn');
  const container = document.getElementById('raw-data-container');
  
  if (!btn) return;

  btn.onclick = () => {
    container.classList.toggle('hidden');
    if (!container.classList.contains('hidden')) {
      renderRawTable(userData, 'location');
    }
  };

  document.querySelectorAll('.data-tabs .page-number').forEach(tab => {
    tab.onclick = (e) => {
      document.querySelectorAll('.data-tabs .page-number').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      renderRawTable(userData, e.target.dataset.tab);
    };
  });
}

// ============================================
// Event Handlers
// ============================================
async function handleAnalyze(userId) {
  if (state.isLoading) return;

  showLoading('사용자 분석 중...');

  try {
    const result = await analyzeUser(userId);
    renderAnalysisResult(result);
    openModal();
  } catch (error) {
    alert('분석 중 오류가 발생했습니다. 백엔드 서버를 확인하세요.');
  } finally {
    hideLoading();
  }
}

function handleSearch(e) {
  state.searchQuery = e.target.value.trim();
  applyFilters();
  renderUserCards();
  renderPagination();
  updateTotalBadge();
}

function handlePersonaFilter(e) {
  state.personaFilter = e.target.value;
  applyFilters();
  renderUserCards();
  renderPagination();
  updateTotalBadge();
}

function openModal() {
  elements.analysisModal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  elements.analysisModal.classList.remove('active');
  document.body.style.overflow = '';
}

// ============================================
// Event Listeners
// ============================================
let searchTimeout;
elements.searchInput.addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => handleSearch(e), 300);
});

elements.typeFilter.addEventListener('change', handlePersonaFilter);
elements.prevBtn.addEventListener('click', () => goToPage(state.currentPage - 1));
elements.nextBtn.addEventListener('click', () => goToPage(state.currentPage + 1));
elements.closeModal.addEventListener('click', closeModal);
elements.analysisModal.addEventListener('click', (e) => {
  if (e.target === elements.analysisModal) closeModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
  if (e.key === 'ArrowLeft' && !elements.prevBtn.disabled) goToPage(state.currentPage - 1);
  if (e.key === 'ArrowRight' && !elements.nextBtn.disabled) goToPage(state.currentPage + 1);
});

// ============================================
// Initialization
// ============================================
async function init() {
  showLoading('초기화 중...');

  try {
    const isConnected = await checkServerStatus();

    if (isConnected) {
      await Promise.all([
        fetchAllUsers(),
        fetchStatistics()
      ]);

      applyFilters();
      renderUserCards();
      renderPagination();
      updateTotalBadge();
      renderStatistics(state.statistics);
    } else {
      elements.usersGrid.innerHTML = `
        <div class="glass-card" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
          <div style="font-size: 3rem; margin-bottom: var(--space-md);">🔌</div>
          <h3 style="margin-bottom: var(--space-md);">서버에 연결할 수 없습니다</h3>
          <p style="color: var(--text-muted); margin-bottom: var(--space-lg);">
            백엔드 서버가 실행 중인지 확인하세요.<br>
            <code style="background: rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 4px;">python main.py</code>
          </p>
          <button class="analyze-btn" style="max-width: 200px; margin: 0 auto;" onclick="location.reload()">
            🔄 다시 시도
          </button>
        </div>
      `;
    }
  } catch (error) {
    console.error('Initialization error:', error);
  } finally {
    hideLoading();
  }
}

document.addEventListener('DOMContentLoaded', init);

// Expose functions globally
window.handleAnalyze = handleAnalyze;
window.goToPage = goToPage;

