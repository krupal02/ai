import React, { useState } from 'react';

const STEPS = ['Welcome', 'Basic Info', 'Travel Profile', 'Preferences', 'Confirm'];

export default function OnboardingModal({ onComplete }) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    full_name: '',
    pnr: '',
    age_group: '18-30',
    travel_frequency: 'first_time',
    loyalty_programs: [],
    special_assistance: [],
    language_preference: 'en',
    dietary_preference: 'both',
    dietary_restrictions: '',
    flight_number: '',
    departure_airport: 'DEL',
    travel_date: '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const update = (key, val) => {
    setForm(prev => ({ ...prev, [key]: val }));
    setErrors(prev => ({ ...prev, [key]: '' }));
  };

  const toggleAssistance = (val) => {
    setForm(prev => ({
      ...prev,
      special_assistance: prev.special_assistance.includes(val)
        ? prev.special_assistance.filter(v => v !== val)
        : [...prev.special_assistance, val]
    }));
  };

  const validateStep = () => {
    const e = {};
    if (step === 1) {
      if (!form.full_name.trim() || form.full_name.trim().length < 2) e.full_name = 'Please enter your full name';
      if (form.pnr && !/^[A-Z0-9]{6}$/i.test(form.pnr)) e.pnr = 'PNR must be 6 alphanumeric characters';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const next = () => {
    if (!validateStep()) return;
    if (step < STEPS.length - 1) setStep(step + 1);
  };
  const back = () => { if (step > 0) setStep(step - 1); };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await fetch('http://localhost:8000/api/users/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      const profile = { ...form, user_id: data.user_id, session_token: data.session_token };
      localStorage.setItem('aeroguide_user_profile', JSON.stringify(profile));
      onComplete(profile);
    } catch (err) {
      console.error('Profile creation error:', err);
      const profile = { ...form, user_id: 'local_' + Date.now(), session_token: '' };
      localStorage.setItem('aeroguide_user_profile', JSON.stringify(profile));
      onComplete(profile);
    } finally {
      setSubmitting(false);
    }
  };

  const frequencyOptions = [
    { value: 'first_time', label: 'First-Time Flyer', icon: '🎫', sub: 'New to air travel' },
    { value: 'occasional', label: 'Occasional Traveler', icon: '✈️', sub: '2-5 trips per year' },
    { value: 'frequent', label: 'Frequent Flyer', icon: '💼', sub: '6+ trips per year' },
  ];

  const assistanceOptions = [
    { value: 'wheelchair', label: 'Wheelchair assistance', icon: '♿' },
    { value: 'visual', label: 'Visual impairment', icon: '👁️' },
    { value: 'hearing', label: 'Hearing impairment', icon: '👂' },
    { value: 'infant', label: 'Traveling with infant', icon: '👶' },
    { value: 'medical', label: 'Medical condition', icon: '🏥' },
  ];

  const dietOptions = [
    { value: 'veg', label: 'Vegetarian', icon: '🥬' },
    { value: 'non_veg', label: 'Non-Vegetarian', icon: '🍗' },
    { value: 'both', label: 'Both', icon: '🍽️' },
    { value: 'vegan', label: 'Vegan', icon: '🌱' },
    { value: 'jain', label: 'Jain', icon: '🙏' },
  ];

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        {/* Progress */}
        <div className="onboarding-progress">
          {STEPS.map((s, i) => (
            <div key={s} className={`progress-step ${i < step ? 'done' : ''} ${i === step ? 'active' : ''}`}>
              <div className="progress-dot">{i < step ? '✓' : i + 1}</div>
              <span className="progress-label">{s}</span>
            </div>
          ))}
        </div>

        <div className="onboarding-body">
          {/* Step 0: Welcome */}
          {step === 0 && (
            <div className="onboarding-step welcome-step">
              <div className="welcome-icon">✈️</div>
              <h1>Welcome to <span className="gradient-text">AeroGuide</span></h1>
              <p>Your AI-powered airport companion. Let's personalize your experience for a smoother journey.</p>
              <button className="btn-primary btn-lg" onClick={next}>Get Started →</button>
            </div>
          )}

          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div className="onboarding-step">
              <h2>👤 Basic Information</h2>
              <p className="step-subtitle">Tell us about yourself</p>

              <div className="form-group">
                <label>Full Name <span className="required">*</span></label>
                <input type="text" value={form.full_name} onChange={e => update('full_name', e.target.value)}
                  placeholder="Enter your full name" className={errors.full_name ? 'input-error' : ''} />
                {errors.full_name && <span className="error-text">{errors.full_name}</span>}
              </div>

              <div className="form-group">
                <label>PNR Number</label>
                <input type="text" value={form.pnr} maxLength={6}
                  onChange={e => update('pnr', e.target.value.toUpperCase())}
                  placeholder="e.g., ABC123" className={errors.pnr ? 'input-error' : ''} />
                <span className="helper-text">Found on your booking confirmation</span>
                {errors.pnr && <span className="error-text">{errors.pnr}</span>}
              </div>

              <div className="form-group">
                <label>Age Group</label>
                <div className="chip-group">
                  {['18-30', '31-50', '51-65', '65+'].map(ag => (
                    <button key={ag} className={`chip ${form.age_group === ag ? 'active' : ''}`}
                      onClick={() => update('age_group', ag)}>
                      {ag === '65+' ? '👴 65+ (Senior)' : ag}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Flight Number <span className="optional">(optional)</span></label>
                <input type="text" value={form.flight_number}
                  onChange={e => update('flight_number', e.target.value.toUpperCase())}
                  placeholder="e.g., AI505, 6E123" />
              </div>
            </div>
          )}

          {/* Step 2: Travel Profile */}
          {step === 2 && (
            <div className="onboarding-step">
              <h2>🧳 Travel Profile</h2>
              <p className="step-subtitle">How often do you fly?</p>

              <div className="frequency-cards">
                {frequencyOptions.map(opt => (
                  <button key={opt.value}
                    className={`frequency-card ${form.travel_frequency === opt.value ? 'active' : ''}`}
                    onClick={() => update('travel_frequency', opt.value)}>
                    <span className="freq-icon">{opt.icon}</span>
                    <span className="freq-label">{opt.label}</span>
                    <span className="freq-sub">{opt.sub}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Preferences */}
          {step === 3 && (
            <div className="onboarding-step">
              <h2>⚙️ Preferences</h2>
              <p className="step-subtitle">Help us customize your experience</p>

              <div className="form-group">
                <label>Special Assistance</label>
                <div className="checkbox-group">
                  {assistanceOptions.map(opt => (
                    <label key={opt.value} className={`checkbox-card ${form.special_assistance.includes(opt.value) ? 'active' : ''}`}>
                      <input type="checkbox" checked={form.special_assistance.includes(opt.value)}
                        onChange={() => toggleAssistance(opt.value)} />
                      <span className="cb-icon">{opt.icon}</span>
                      <span>{opt.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Dietary Preference</label>
                <div className="chip-group">
                  {dietOptions.map(opt => (
                    <button key={opt.value} className={`chip ${form.dietary_preference === opt.value ? 'active' : ''}`}
                      onClick={() => update('dietary_preference', opt.value)}>
                      {opt.icon} {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Allergies / Dietary Restrictions <span className="optional">(optional)</span></label>
                <input type="text" value={form.dietary_restrictions}
                  onChange={e => update('dietary_restrictions', e.target.value)}
                  placeholder="e.g., Peanut allergy, Lactose intolerant" />
              </div>
            </div>
          )}

          {/* Step 4: Confirm */}
          {step === 4 && (
            <div className="onboarding-step">
              <h2>✅ Confirm Your Profile</h2>
              <p className="step-subtitle">Review your information</p>

              <div className="confirm-grid">
                <div className="confirm-item"><span className="confirm-label">Name</span><span className="confirm-value">{form.full_name || '—'}</span></div>
                <div className="confirm-item"><span className="confirm-label">PNR</span><span className="confirm-value">{form.pnr || '—'}</span></div>
                <div className="confirm-item"><span className="confirm-label">Age</span><span className="confirm-value">{form.age_group}</span></div>
                <div className="confirm-item"><span className="confirm-label">Travel Type</span><span className="confirm-value">{frequencyOptions.find(o=>o.value===form.travel_frequency)?.label}</span></div>
                <div className="confirm-item"><span className="confirm-label">Diet</span><span className="confirm-value">{dietOptions.find(o=>o.value===form.dietary_preference)?.label}</span></div>
                <div className="confirm-item"><span className="confirm-label">Flight</span><span className="confirm-value">{form.flight_number || '—'}</span></div>
                {form.special_assistance.length > 0 && (
                  <div className="confirm-item full-width"><span className="confirm-label">Assistance</span><span className="confirm-value">{form.special_assistance.join(', ')}</span></div>
                )}
                {form.dietary_restrictions && (
                  <div className="confirm-item full-width"><span className="confirm-label">Restrictions</span><span className="confirm-value">{form.dietary_restrictions}</span></div>
                )}
              </div>

              <button className="btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
                {submitting ? '⏳ Creating Profile...' : '🚀 Complete Setup'}
              </button>
            </div>
          )}
        </div>

        {/* Navigation */}
        {step > 0 && step < STEPS.length - 1 && (
          <div className="onboarding-nav">
            <button className="btn-secondary" onClick={back}>← Back</button>
            <button className="btn-primary" onClick={next}>Next →</button>
          </div>
        )}
        {step === 4 && (
          <div className="onboarding-nav">
            <button className="btn-secondary" onClick={back}>← Back</button>
          </div>
        )}
      </div>
    </div>
  );
}
