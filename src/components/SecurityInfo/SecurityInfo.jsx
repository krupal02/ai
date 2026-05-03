import React, { useState, useEffect } from 'react';

export default function SecurityInfo({ onClose }) {
  const [activeTab, setActiveTab] = useState('procedure');
  const [rules, setRules] = useState(null);
  const [flightType, setFlightType] = useState('domestic');
  const [airportCode, setAirportCode] = useState('DEL');
  const [destination, setDestination] = useState('');
  const [loading, setLoading] = useState(true);

  const AIRPORTS = [
    { code: 'DEL', label: '🛫 Delhi (DEL)' },
    { code: 'BOM', label: '🛫 Mumbai (BOM)' },
    { code: 'BLR', label: '🛫 Bangalore (BLR)' },
  ];

  const DESTINATIONS = [
    { code: 'UAE', label: '🇦🇪 UAE / Dubai' },
    { code: 'USA', label: '🇺🇸 USA' },
    { code: 'Singapore', label: '🇸🇬 Singapore' },
    { code: 'UK', label: '🇬🇧 United Kingdom' },
    { code: 'Japan', label: '🇯🇵 Japan' },
    { code: 'Australia', label: '🇦🇺 Australia' },
  ];

  const tabs = [
    { id: 'procedure', label: '📋 Procedure', icon: '📋' },
    { id: 'prohibited', label: '🚫 Prohibited', icon: '🚫' },
    { id: 'destination', label: '🌍 Destination', icon: '🌍' },
    { id: 'penalties', label: '⚖️ Penalties', icon: '⚖️' },
    { id: 'tips', label: '💡 Tips', icon: '💡' },
  ];

  const fetchRules = async () => {
    setLoading(true);
    try {
      const url = `http://localhost:8000/api/security/rules?airport_code=${airportCode}&flight_type=${flightType}&destination=${destination}`;
      const res = await fetch(url);
      const data = await res.json();
      setRules(data);
    } catch (err) {
      console.error('Security data error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRules(); }, [flightType, destination, airportCode]);

  const getSeverityClass = (sev) => {
    if (sev === 'critical') return 'severity-critical';
    if (sev === 'high') return 'severity-high';
    if (sev === 'medium') return 'severity-medium';
    return 'severity-low';
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target.className === 'modal-overlay' && onClose()}>
      <div className="security-modal">
        <div className="security-modal-header">
          <h2>🛂 Security Information</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Airport Selector */}
        <div className="security-type-toggle" style={{marginBottom: '4px'}}>
          {AIRPORTS.map(a => (
            <button key={a.code} className={`type-btn ${airportCode === a.code ? 'active' : ''}`}
              onClick={() => setAirportCode(a.code)}>{a.label}</button>
          ))}
        </div>

        {/* Flight type toggle */}
        <div className="security-type-toggle">
          <button className={`type-btn ${flightType === 'domestic' ? 'active' : ''}`}
            onClick={() => setFlightType('domestic')}>🇮🇳 Domestic</button>
          <button className={`type-btn ${flightType === 'international' ? 'active' : ''}`}
            onClick={() => setFlightType('international')}>🌍 International</button>
        </div>

        {/* Tabs */}
        <div className="security-tabs">
          {tabs.map(t => (
            <button key={t.id} className={`sec-tab ${activeTab === t.id ? 'active' : ''}`}
              onClick={() => setActiveTab(t.id)}>{t.label}</button>
          ))}
        </div>

        <div className="security-body">
          {loading ? (
            <div className="food-loading"><div className="typing-dot"></div><div className="typing-dot"></div><div className="typing-dot"></div></div>
          ) : !rules ? (
            <div className="food-empty">Unable to load security data</div>
          ) : (
            <>
              {/* Procedure Tab */}
              {activeTab === 'procedure' && (
                <div className="sec-panel">
                  <div className="sec-time-badge">
                    ⏱️ Estimated time: <strong>{rules.procedures?.estimated_time || '15-25 min'}</strong>
                  </div>
                  <div className="sec-steps">
                    {(rules.procedures?.all_steps || rules.procedures?.steps || []).map((s, i) => (
                      <div key={i} className="sec-step-card">
                        <div className="sec-step-num">{s.step || i + 1}</div>
                        <div className="sec-step-content">
                          <div className="sec-step-title">{s.title}</div>
                          <div className="sec-step-desc">{s.description}</div>
                          {s.time && <div className="sec-step-time">⏱️ ~{s.time}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Prohibited Tab */}
              {activeTab === 'prohibited' && (
                <div className="sec-panel">
                  <h3 className="sec-section-title">❌ Prohibited Items</h3>
                  <div className="prohibited-list">
                    {(rules.procedures?.prohibited_items || []).map((item, i) => (
                      <div key={i} className="prohibited-card">
                        <span className="prohibited-icon">{item.icon || '🚫'}</span>
                        <div>
                          <div className="prohibited-name">{item.item}</div>
                          <div className="prohibited-detail">{item.examples}</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {rules.procedures?.allowed_with_restrictions && (
                    <>
                      <h3 className="sec-section-title" style={{marginTop: '20px'}}>⚠️ Allowed with Restrictions</h3>
                      <div className="prohibited-list">
                        {rules.procedures.allowed_with_restrictions.map((item, i) => (
                          <div key={i} className="prohibited-card restricted">
                            <span className="prohibited-icon">{item.icon || '⚠️'}</span>
                            <div>
                              <div className="prohibited-name">{item.item}</div>
                              <div className="prohibited-detail">{item.rule}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Destination Tab */}
              {activeTab === 'destination' && (
                <div className="sec-panel">
                  <div className="form-group">
                    <label className="filter-label">Select Destination Country</label>
                    <div className="chip-group">
                      {DESTINATIONS.map(d => (
                        <button key={d.code}
                          className={`chip ${destination === d.code ? 'active' : ''}`}
                          onClick={() => setDestination(destination === d.code ? '' : d.code)}>
                          {d.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {rules.country_warnings && rules.country_warnings.length > 0 ? (
                    <div className="warnings-list">
                      {rules.country_warnings.map((w, i) => (
                        <div key={i} className={`warning-card ${getSeverityClass(w.severity)}`}>
                          <span className="warning-severity">
                            {w.severity === 'critical' ? '🚨' : w.severity === 'high' ? '⚠️' : 'ℹ️'}
                          </span>
                          <span className="warning-text">{w.warning}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="food-empty" style={{marginTop: '20px'}}>
                      Select a destination country above to see specific warnings
                    </div>
                  )}
                </div>
              )}

              {/* Penalties Tab */}
              {activeTab === 'penalties' && (
                <div className="sec-panel">
                  {Object.entries(rules.penalties || {}).map(([region, items]) => (
                    <div key={region}>
                      <h3 className="sec-section-title">{region === 'India' ? '🇮🇳' : '🌍'} {region}</h3>
                      <div className="penalties-list">
                        {items.map((p, i) => (
                          <div key={i} className={`penalty-card ${getSeverityClass(p.severity)}`}>
                            <div className="penalty-violation">{p.violation}</div>
                            <div className="penalty-consequence">{p.consequence}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Tips Tab */}
              {activeTab === 'tips' && (
                <div className="sec-panel">
                  <div className="tips-list">
                    {(rules.tips || []).map((tip, i) => (
                      <div key={i} className="security-tip-card">
                        <span className="tip-number">{i + 1}</span>
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
