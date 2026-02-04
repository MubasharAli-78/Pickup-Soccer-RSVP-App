import { useState } from 'react';
import { rsvpPlayer } from '../api';

/**
 * RSVP Form Component
 * Allows players to RSVP IN or OUT by entering their name
 */
function RSVPForm({ onRSVPComplete }) {
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (status) => {
        if (!name.trim()) {
            setError('Please enter your name');
            return;
        }

        setLoading(true);
        setError(null);
        setMessage(null);

        try {
            const result = await rsvpPlayer(name.trim(), status);
            setMessage(result.message);
            setName('');

            // Notify parent to refresh player list
            if (onRSVPComplete) {
                onRSVPComplete();
            }

            // Clear message after 3 seconds
            setTimeout(() => setMessage(null), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to submit RSVP');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="rsvp-form">
            <h2>⚽ RSVP for the Game</h2>

            <div className="form-group">
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your name..."
                    disabled={loading}
                    onKeyPress={(e) => e.key === 'Enter' && handleSubmit('IN')}
                />
            </div>

            <div className="button-group">
                <button
                    className="btn btn-primary"
                    onClick={() => handleSubmit('IN')}
                    disabled={loading || !name.trim()}
                >
                    {loading ? '⏳' : '✅'} I'm IN
                </button>

                <button
                    className="btn btn-secondary"
                    onClick={() => handleSubmit('OUT')}
                    disabled={loading || !name.trim()}
                >
                    {loading ? '⏳' : '❌'} I'm OUT
                </button>
            </div>

            {message && (
                <div className="message success">
                    ✓ {message}
                </div>
            )}

            {error && (
                <div className="message error">
                    ✗ {error}
                </div>
            )}
        </div>
    );
}

export default RSVPForm;
