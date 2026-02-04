import { useState, useEffect } from 'react';
import { getPlayers } from './api';
import RSVPForm from './components/RSVPForm';
import PlayerList from './components/PlayerList';
import AdminPanel from './components/AdminPanel';

/**
 * Main App Component
 * Pickup Soccer RSVP & Check-in System
 */
function App() {
    const [players, setPlayers] = useState({
        confirmed: [],
        waitlist: [],
        out: [],
        total_confirmed: 0,
        total_waitlist: 0,
        spots_available: 22
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('rsvp');

    const loadPlayers = async () => {
        try {
            const data = await getPlayers();
            setPlayers(data);
            setError(null);
        } catch (err) {
            setError('Failed to load players. Is the backend running?');
            console.error('Load players error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPlayers();

        // Auto-refresh every 5 seconds
        const interval = setInterval(loadPlayers, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="app">
            {/* Header */}
            <header className="header">
                <div className="header-content">
                    <h1>⚽ Pickup Soccer</h1>
                    <p className="subtitle">RSVP & Check-in System</p>
                </div>
                <div className="header-stats">
                    <div className="stat">
                        <span className="stat-number">{players.total_confirmed}</span>
                        <span className="stat-text">/22 Confirmed</span>
                    </div>
                    {players.total_waitlist > 0 && (
                        <div className="stat waitlist">
                            <span className="stat-number">{players.total_waitlist}</span>
                            <span className="stat-text">Waitlist</span>
                        </div>
                    )}
                </div>
            </header>

            {/* Navigation Tabs */}
            <nav className="tabs">
                <button
                    className={`tab ${activeTab === 'rsvp' ? 'active' : ''}`}
                    onClick={() => setActiveTab('rsvp')}
                >
                    📝 RSVP
                </button>
                <button
                    className={`tab ${activeTab === 'players' ? 'active' : ''}`}
                    onClick={() => setActiveTab('players')}
                >
                    👥 Players
                </button>
                <button
                    className={`tab ${activeTab === 'admin' ? 'active' : ''}`}
                    onClick={() => setActiveTab('admin')}
                >
                    🔧 Admin
                </button>
            </nav>

            {/* Main Content */}
            <main className="main-content">
                {error && (
                    <div className="error-banner">
                        ⚠️ {error}
                        <button onClick={loadPlayers}>Retry</button>
                    </div>
                )}

                {loading ? (
                    <div className="loading">
                        <div className="spinner"></div>
                        <p>Loading...</p>
                    </div>
                ) : (
                    <>
                        {activeTab === 'rsvp' && (
                            <div className="tab-content">
                                <RSVPForm onRSVPComplete={loadPlayers} />
                                <div className="quick-stats">
                                    <h3>Quick View</h3>
                                    <div className="mini-player-list">
                                        {players.confirmed.slice(0, 5).map((p, i) => (
                                            <div key={p.id} className="mini-player">
                                                {i + 1}. {p.name} {p.paid ? '💵' : ''} {p.checked_in ? '✓' : ''}
                                            </div>
                                        ))}
                                        {players.confirmed.length > 5 && (
                                            <div className="mini-player more">
                                                +{players.confirmed.length - 5} more...
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'players' && (
                            <div className="tab-content">
                                <PlayerList players={players} onUpdate={loadPlayers} />
                            </div>
                        )}

                        {activeTab === 'admin' && (
                            <div className="tab-content">
                                <AdminPanel onReset={loadPlayers} />
                            </div>
                        )}
                    </>
                )}
            </main>

            {/* Footer */}
            <footer className="footer">
                <p>Designed for WhatsApp integration • Made for Pickup Soccer 🌟</p>
            </footer>
        </div>
    );
}

export default App;
