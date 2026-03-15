import { useState } from 'react';

/*
  ContactForm handles both "Add" and "Edit" modes.
  If a `contact` prop is provided, the form pre-fills with that contact's data.
  Only the name field is required — everything else is optional so you can
  quickly add someone and fill in details later.
*/
export default function ContactForm({ contact, onSave, onCancel }) {
  const [name, setName] = useState(contact?.name || '');
  const [phone, setPhone] = useState(contact?.phone || '');
  const [email, setEmail] = useState(contact?.email || '');
  const [company, setCompany] = useState(contact?.company || '');
  const [notes, setNotes] = useState(contact?.notes || '');

  function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;
    onSave({ name: name.trim(), phone, email, company, notes });
  }

  return (
    <div className="form-overlay">
      <form className="form-card" onSubmit={handleSubmit}>
        <h2>{contact ? 'Edit Contact' : 'Add Contact'}</h2>

        <label>
          Name <span className="required">*</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Jane Smith"
            autoFocus
          />
        </label>

        <label>
          Phone
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="e.g. (555) 123-4567"
          />
        </label>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="e.g. jane@example.com"
          />
        </label>

        <label>
          Company
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="e.g. Acme Corp"
          />
        </label>

        <label>
          Notes
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Anything you want to remember about this person…"
            rows={3}
          />
        </label>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary">
            {contact ? 'Save Changes' : 'Add Contact'}
          </button>
          <button type="button" className="btn" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
