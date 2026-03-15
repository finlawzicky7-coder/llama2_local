import { formatDate, todayString, daysDiff } from '../utils';

/*
  ReminderList shows follow-ups that need attention, split into two sections:
  1. "Overdue & Today" — anything with followUpDate <= today that isn't completed.
  2. "Upcoming (next 7 days)" — follow-ups in the near future.

  Each item shows the contact name (clickable), phone, call summary, and due date.
  "Mark Done" sets completed = true so the item disappears from the list.
*/
export default function ReminderList({
  calls,
  contacts,
  onMarkDone,
  onViewContact,
}) {
  const today = todayString();

  // Only calls that have a follow-up date and aren't completed
  const pending = calls.filter((c) => c.followUpDate && !c.completed);

  const overdue = pending
    .filter((c) => c.followUpDate <= today)
    .sort((a, b) => a.followUpDate.localeCompare(b.followUpDate));

  const upcoming = pending
    .filter((c) => {
      const diff = daysDiff(c.followUpDate);
      return diff > 0 && diff <= 7;
    })
    .sort((a, b) => a.followUpDate.localeCompare(b.followUpDate));

  // Helper to find a contact's name and phone by ID
  function getContact(contactId) {
    return contacts.find((c) => c.id === contactId) || { name: '(deleted)', phone: '' };
  }

  function ReminderItem({ call }) {
    const contact = getContact(call.contactId);
    const diff = daysDiff(call.followUpDate);
    let urgencyClass = '';
    if (diff < 0) urgencyClass = 'overdue';
    else if (diff === 0) urgencyClass = 'today';

    return (
      <div className={`reminder-card ${urgencyClass}`}>
        <div className="reminder-top">
          <button
            className="contact-link"
            onClick={() => onViewContact(call.contactId)}
          >
            {contact.name}
          </button>
          {contact.phone && (
            <span className="reminder-phone">{contact.phone}</span>
          )}
        </div>
        <p className="reminder-summary">{call.summary}</p>
        <div className="reminder-bottom">
          <span className="reminder-date">
            {diff < 0
              ? `Overdue by ${Math.abs(diff)} day${Math.abs(diff) !== 1 ? 's' : ''}`
              : diff === 0
                ? 'Due today'
                : `Due ${formatDate(call.followUpDate)}`}
          </span>
          <button
            className="btn btn-small btn-success"
            onClick={() => onMarkDone(call.id)}
          >
            ✓ Mark Done
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="reminder-list">
      <h2>Reminders</h2>

      <h3 className="section-title">
        Overdue & Today
        {overdue.length > 0 && (
          <span className="badge">{overdue.length}</span>
        )}
      </h3>
      {overdue.length === 0 ? (
        <div className="empty-state">
          Nothing due today — you're all caught up!
        </div>
      ) : (
        overdue.map((call) => <ReminderItem key={call.id} call={call} />)
      )}

      <h3 className="section-title">Upcoming (next 7 days)</h3>
      {upcoming.length === 0 ? (
        <div className="empty-state">No upcoming follow-ups this week.</div>
      ) : (
        upcoming.map((call) => <ReminderItem key={call.id} call={call} />)
      )}
    </div>
  );
}
