import React, { useState, useEffect } from 'react';
import { 
  X, 
  Search, 
  BookOpen, 
  Tag, 
  Check, 
  HelpCircle 
} from 'lucide-react';

export default function GlossaryModal({
  isOpen,
  onClose,
  activeMode,
  onSelectSign,
}) {
  const [glossarySigns, setGlossarySigns] = useState([]);
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetch('/api/models/glossary')
        .then((res) => res.json())
        .then((data) => {
          if (data.signs) setGlossarySigns(data.signs);
        })
        .catch((err) => console.error('Failed to load glossary:', err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const filteredSigns = glossarySigns.filter((item) => {
    const matchesFilter = filterType === 'ALL' || item.type === filterType;
    const matchesSearch = item.sign.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container modal-wide" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="section-label">SIGN REFERENCE LEXICON</span>
            <h3 className="modal-title font-display">46 Supported ISL Signs</h3>
          </div>
          <button onClick={onClose} className="modal-close-btn">
            <X size={18} />
          </button>
        </div>

        {/* Search & Filter Header */}
        <div className="glossary-filter-bar">
          <div className="glossary-search-wrapper">
            <Search size={15} className="search-icon" />
            <input
              type="text"
              placeholder="Search sign (e.g. 'Hello', 'A', 'ThankYou')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="glossary-search-input"
            />
          </div>

          <div className="filter-segmented-control">
            <button
              onClick={() => setFilterType('ALL')}
              className={`filter-btn ${filterType === 'ALL' ? 'active' : ''}`}
            >
              All (46)
            </button>
            <button
              onClick={() => setFilterType('STATIC')}
              className={`filter-btn ${filterType === 'STATIC' ? 'active' : ''}`}
            >
              Static (35)
            </button>
            <button
              onClick={() => setFilterType('DYNAMIC')}
              className={`filter-btn ${filterType === 'DYNAMIC' ? 'active' : ''}`}
            >
              Dynamic (11)
            </button>
          </div>
        </div>

        {/* Signs Grid */}
        <div className="glossary-grid-area">
          {filteredSigns.length === 0 ? (
            <div className="glossary-empty">
              <span>No signs match your search criteria.</span>
            </div>
          ) : (
            filteredSigns.map((item) => (
              <div 
                key={item.sign} 
                className="glossary-sign-card"
                onClick={() => {
                  if (onSelectSign) onSelectSign(item.sign);
                }}
              >
                <div className="sign-card-top">
                  <span className={`sign-type-badge badge-${item.type.toLowerCase()}`}>
                    {item.type}
                  </span>
                  <span className="sign-category-tag">{item.category}</span>
                </div>
                <h4 className="sign-card-name font-display">{item.sign}</h4>
                <p className="sign-card-desc">{item.description}</p>
              </div>
            ))
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <span className="footer-tip">
            💡 <strong>Tip:</strong> You can click any sign card to test adding it directly to your sentence builder!
          </span>
          <button onClick={onClose} className="primary-btn">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
