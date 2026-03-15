import { useState } from 'react';
import { formatDate } from '../utils';
import CallForm from './CallForm';

/*
  ContactDetail shows a single contact's info plus their call history.
  The call log is displayed in reverse chronological order (newest first).
  A "Log Call" button opens an inline CallForm.
*/
export default function ContactDetail({
  contact,
  calls,
  onBack,
  onEdit,
  onDelete,
  onAddCall,
}) {
  const [showCallForm, setShowCallForm] = useState(false);

  return (
    <div className="contact-detail">
      <button className="btn btn-back" onClick={onBack}>
        ← Back to Contacts
      </button>

      <div className="detail-card">
        <div className="detail-header">
          <h2>{contact.name}</h2>
          <div className="detail-actions">
            <button className="btn" onClick={onEdit}>
              Edit
            </button>
            <button className="btn btn-danger" onClick={onDelete}>
              Delete
            </button>
          </div>
        </div>

        <div className="detail-fields">
          {contact.phone && (
            <p>
              <strong>Phone:</strong> {contact.phone}
            </p>
          )}
          {contact.email && (
            <p>
              <strong>Email:</strong> {contact.email}
            </p>
          )}
          {contact.company && (
            <p>
              <strong>Company:</strong> {contact.company}
            </p>
          )}
          <p>
            <strong>Added:</strong> {formatDate(contact.createdAt)}
          </p>
          <p>
            <strong>Last contacted:</strong>{' '}
            {formatDate(contact.lastContactedAt)}
          </p>
        </div>

        {contact.notes && (
          <div className="detail-notes">
            <strong>Notes:</strong>
            <p>{contact.notes}</p>
          </div>
        )}
      </div>

      {/* Call log section */}
      <div className="call-log-section">
        <div className="list-header">
          <h3>Call Log</h3>
          <button
            className="btn btn-primary"
            onClick={() => setShowCallForm(true)}
          >
            + Log Call
          </button>
        </div>

        {showCallForm && (
          <CallForm
            contactId={contact.id}
            onSave={(data) => {
              onAddCall(data);
              setShowCallForm(false);
            }}
            onCancel={() => setShowCallForm(false)}
          />
        )}

        {calls.length === 0 ? (
          <div className="empty-state">
            No calls logged yet. Log your first call!
          </div>
        ) : (
          <div className="call-list">
            {calls.map((call) => (
              <div key={call.id} className="call-card">
                <div className="call-card-header">
                  <span className={`direction-badge ${call.direction}`}>
                    {call.direction === 'incoming' ? '📞 Incoming' : '📱 Outgoing'}
                  </span>
                  <span className="call-date">{formatDate(call.date)}</span>
                </div>
                <p className="call-summary">{call.summary}</p>
                {call.notes && <p className="call-notes">{call.notes}</p>}
                {call.followUpDate && (
                  <p className={`follow-up ${call.completed ? 'done' : ''}`}>
                    Follow-up: {formatDate(call.followUpDate)}
                    {call.completed && ' ✓ Done'}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
