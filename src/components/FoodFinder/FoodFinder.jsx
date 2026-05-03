import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';

const CUISINE_CATEGORIES = {
  'Indian':           { icon: '🍛', items: ['North Indian','South Indian','Punjabi','Mughlai','Gujarati','Street Food','Momos'] },
  'Asian':            { icon: '🥢', items: ['Chinese','Thai','Japanese','Korean'] },
  'Continental':      { icon: '🍝', items: ['Continental','Italian','Multi-cuisine','Premium'] },
  'Quick Bites':      { icon: '🍔', items: ['Burgers','Pizza','Sandwiches','Wraps','Fast Food','Fried Chicken'] },
  'Beverages':        { icon: '☕', items: ['Coffee','Tea','Cafe','Juice Bar','Smoothies'] },
  'Bakery & Desserts': { icon: '🍩', items: ['Bakery','Desserts','Donuts'] },
};

export default function FoodFinder({ onClose }) {
  const { coordinates, userProfile } = useApp();
  const [selectedCuisines, setSelectedCuisines] = useState([]);
  const [dietFilter, setDietFilter] = useState(userProfile?.dietary_preference || 'both');
  const [sortBy, setSortBy] = useState('rating');
  const [priceRange, setPriceRange] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState(null);

  const toggleCuisine = (c) => {
    setSelectedCuisines(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  };

  const togglePrice = (p) => {
    setPriceRange(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]);
  };

  const search = async () => {
    setLoading(true);
    setSearched(true);
    try {
      const res = await fetch('http://localhost:8000/api/food/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cuisine_types: selectedCuisines,
          dietary_filter: dietFilter,
          sort_by: sortBy,
          price_range: priceRange,
          latitude: coordinates?.lat || null,
          longitude: coordinates?.lng || null,
          user_id: userProfile?.user_id || null,
        })
      });
      const data = await res.json();
      setResults(data.recommendations || []);
    } catch (err) {
      console.error('Food search error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Auto-search on mount
  useEffect(() => { search(); }, []);

  return (
    <div className="modal-overlay" onClick={(e) => e.target.className === 'modal-overlay' && onClose()}>
      <div className="food-modal">
        <div className="food-modal-header">
          <h2>🍽️ Find Food & Dining</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="food-modal-body">
          {/* Filters */}
          <div className="food-filters">
            {/* Cuisine Category Accordion */}
            <div className="filter-section">
              <label className="filter-label">Cuisine Type</label>
              <div className="cuisine-categories">
                {Object.entries(CUISINE_CATEGORIES).map(([cat, data]) => (
                  <div key={cat} className="cuisine-cat">
                    <button className={`cuisine-cat-header ${expandedCategory === cat ? 'expanded' : ''}`}
                      onClick={() => setExpandedCategory(expandedCategory === cat ? null : cat)}>
                      <span>{data.icon} {cat}</span>
                      <span className="expand-arrow">{expandedCategory === cat ? '▲' : '▼'}</span>
                    </button>
                    {expandedCategory === cat && (
                      <div className="cuisine-items">
                        {data.items.map(item => (
                          <button key={item}
                            className={`cuisine-chip ${selectedCuisines.includes(item) ? 'active' : ''}`}
                            onClick={() => toggleCuisine(item)}>
                            {item}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {selectedCuisines.length > 0 && (
                <div className="selected-cuisines">
                  {selectedCuisines.map(c => (
                    <span key={c} className="selected-tag">{c} <button onClick={() => toggleCuisine(c)}>×</button></span>
                  ))}
                </div>
              )}
            </div>

            <div className="filter-row">
              <div className="filter-section compact">
                <label className="filter-label">Dietary</label>
                <div className="chip-group small">
                  {[{v:'both',l:'All'},{v:'veg',l:'🥬 Veg'},{v:'non_veg',l:'🍗 Non-Veg'},{v:'vegan',l:'🌱 Vegan'},{v:'jain',l:'🙏 Jain'}].map(d => (
                    <button key={d.v} className={`chip small ${dietFilter === d.v ? 'active' : ''}`}
                      onClick={() => setDietFilter(d.v)}>{d.l}</button>
                  ))}
                </div>
              </div>

              <div className="filter-section compact">
                <label className="filter-label">Sort by</label>
                <div className="chip-group small">
                  {[{v:'rating',l:'⭐ Rating'},{v:'price',l:'💰 Price'},{v:'wait_time',l:'⏱️ Wait'},{v:'distance',l:'📍 Distance'}].map(s => (
                    <button key={s.v} className={`chip small ${sortBy === s.v ? 'active' : ''}`}
                      onClick={() => setSortBy(s.v)}>{s.l}</button>
                  ))}
                </div>
              </div>
            </div>

            <button className="btn-primary search-btn" onClick={search}>
              {loading ? '⏳ Searching...' : '🔍 Search Restaurants'}
            </button>
          </div>

          {/* Results */}
          <div className="food-results">
            {loading && <div className="food-loading"><div className="typing-dot"></div><div className="typing-dot"></div><div className="typing-dot"></div></div>}
            {!loading && searched && results.length === 0 && (
              <div className="food-empty">No restaurants match your filters. Try adjusting your criteria.</div>
            )}
            {!loading && results.map(r => (
              <div key={r.id} className="restaurant-card">
                <div className="rest-header">
                  <div className="rest-name">{r.name}</div>
                  <div className="rest-rating">⭐ {r.rating}</div>
                </div>
                <div className="rest-meta">
                  <span>{r.cuisine_types?.join(' • ')}</span>
                  <span className="rest-price">{r.price_range}</span>
                </div>
                <div className="rest-details">
                  <span>📍 {r.terminal}, {r.zone?.replace(/_/g, ' ')}</span>
                  {r.walk_time_min && <span>🚶 {r.walk_time_min} min walk</span>}
                  <span>⏱️ Wait: {r.estimated_wait_time}</span>
                </div>
                <div className="rest-diet-tags">
                  {r.dietary_options?.vegetarian && <span className="diet-tag veg">✓ Veg</span>}
                  {r.dietary_options?.non_vegetarian && <span className="diet-tag nonveg">✓ Non-Veg</span>}
                  {r.dietary_options?.vegan && <span className="diet-tag vegan">✓ Vegan</span>}
                  {r.dietary_options?.jain && <span className="diet-tag jain">✓ Jain</span>}
                </div>
                <div className="rest-menu">
                  <span className="menu-label">Popular:</span>
                  {r.menu_highlights?.slice(0, 3).map(m => (
                    <span key={m.name} className="menu-item">{m.name} <small>₹{m.price}</small></span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
