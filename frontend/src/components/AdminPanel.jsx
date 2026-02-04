import { useState, useEffect } from 'react';
import { exportToCSV, resetAllData, getCheckInStats } from '../api';

/**
 * Admin Panel Component
 * Provides admin functions: Export CSV, View Stats, Reset Data
 */
function AdminPanel({ onReset }) {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    const loadStats = async () => {
        try {
            const data = await getCheckInStats();
            setStats(data);
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    };

    useEffect(() => {
        loadStats();
        // Refresh stats every 10 seconds
        const interval = setInterval(loadStats, 10000);
        return () => clearInterval(interval);
    }, []);

    const handleExport = async () => {
        setLoading(true);
        setMessage(null);

        try {
            await exportToCSV();
            setMessage('CSV exported successfully!');
            setTimeout(() => setMessage(null), 3000);
        } catch (err) {
            setMessage('Export failed: ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    const handleReset = async () => {
        if (!window.confirm('⚠️ Are you sure you want to reset ALL player data? This cannot be undone!')) {
            return;
        }

        if (!window.confirm('⚠️ FINAL WARNING: This will delete all players. Continue?')) {
            return;
        }

        setLoading(true);
        setMessage(null);

        try {
            await resetAllData();
            setMessage('All data has been reset');
            if (onReset) {
                onReset();
            }
            loadStats();
            setTimeout(() => setMessage(null), 3000);
        } catch (err) {
            setMessage('Reset failed: ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="admin-panel">
            <h2>🔧 Admin Panel</h2>

            {/* Stats */}
            {stats && (
                <div className="stats-grid">
                    <div className="stat-card">
                        <span className="stat-value">{stats.total_confirmed}</span>
                        <span className="stat-label">Confirmed</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-value">{stats.total_paid}</span>
                        <span className="stat-label">Paid</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-value">{stats.total_checked_in}</span>
                        <span className="stat-label">Checked In</span>
                    </div>
                    <div className="stat-card highlight">
                        <span className="stat-value">{stats.awaiting_payment}</span>
                        <span className="stat-label">Awaiting Payment</span>
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="admin-actions">
                <button
                    className="btn btn-primary"
                    onClick={handleExport}
                    disabled={loading}
                >
                    📥 Export to CSV
                </button>

                <button
                    className="btn btn-danger"
                    onClick={handleReset}
                    disabled={loading}
                >
                    🗑️ Reset All Data
                </button>
            </div>

            {message && (
                <div className={`message ${message.includes('failed') ? 'error' : 'success'}`}>
                    {message}
                </div>
            )}
        </div>
    );
}

export default AdminPanel;
