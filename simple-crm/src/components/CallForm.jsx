import { useState } from 'react';
import { todayString, addDays } from '../utils';

/*
  CallForm lets you log a phone call for a specific contact.
  - Date defaults to today so you don't have to pick it every time.
  - The "Quick follow-up" button auto-fills the follow-up date to 2 days from now
    (saves you from opening a date picker for the most common case).
*/
export default function CallForm({ contactId, onSave, onCancel }) {
  const [date, setDate] = useState(todayString());
  const [direction, setDirection] = useState('outgoing');
  const [summary, setSummary] = useState('');
  const [notes, setNotes] = useState('');
  const [followUpDate, setFollowUpDate] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (!summary.trim()) return;
    onSave({
      contactId,
      date,
      direction,
      summary: summary.trim(),
      notes,
      followUpDate: followUpDate || null,
    });
  }

  return (
    <form className="form-card call-form" onSubmit={handleSubmit}>
      <h3>Log a Call</h3>

      <div className="form-row">
        <label>
          Date
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </label>

        <label>
          Direction
          <select
            value={direction}
            onChange={(e) => setDirection(e.target.value)}
          >
            <option value="outgoing">Outgoing (I called them)</option>
            <option value="incoming">Incoming (They called me)</option>
          </select>
        </label>
      </div>

      <label>
        Summary <span className="required">*</span>
        <input
          type="text"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          placeholder="e.g. Discussed pricing, they'll think about it"
          autoFocus
        />
      </label>

      <label>
        Notes (optional)
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any extra details you want to remember…"
          rows={2}
        />
      </label>

      <label>
        Follow-up date (optional)
        <div className="follow-up-row">
          <input
            type="date"
            value={followUpDate}
            onChange={(e) => setFollowUpDate(e.target.value)}
          />
          <button
            type="button"
            className="btn btn-small"
            onClick={() => setFollowUpDate(addDays(todayString(), 2))}
            title="Set follow-up to 2 days from now"
          >
            +2 days
          </button>
          <button
            type="button"
            className="btn btn-small"
            onClick={() => setFollowUpDate(addDays(todayString(), 7))}
            title="Set follow-up to 1 week from now"
          >
            +1 week
          </button>
          {followUpDate && (
            <button
              type="button"
              className="btn btn-small"
              onClick={() => setFollowUpDate('')}
            >
              Clear
            </button>
          )}
        </div>
      </label>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          Save Call
        </button>
        <button type="button" className="btn" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}
