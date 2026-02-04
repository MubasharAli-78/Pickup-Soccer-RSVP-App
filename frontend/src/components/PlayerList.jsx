import { useState } from 'react';
import { markPlayerPaid, checkInPlayer, deletePlayer, undoCheckIn } from '../api';

/**
 * Player List Component
 * Displays players in three categories: Confirmed, Waitlist, Out
 * Includes admin actions for each player
 */
function PlayerList({ players, onUpdate, showActions = true }) {
    const [loadingId, setLoadingId] = useState(null);
    const [error, setError] = useState(null);

    const handleAction = async (action, playerId, playerName) => {
        setLoadingId(playerId);
        setError(null);

        try {
            let result;
            switch (action) {
                case 'pay':
                    result = await markPlayerPaid(playerId, true);
                    break;
                case 'unpay':
                    result = await markPlayerPaid(playerId, false);
                    break;
                case 'checkin':
                    result = await checkInPlayer(playerId);
                    break;
                case 'undo-checkin':
                    result = await undoCheckIn(playerId);
                    break;
                case 'delete':
                    if (window.confirm(`Are you sure you want to remove ${playerName}?`)) {
                        result = await deletePlayer(playerId);
                    } else {
                        setLoadingId(null);
                        return;
                    }
                    break;
                default:
                    break;
            }

            if (onUpdate) {
                onUpdate();
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Action failed');
            setTimeout(() => setError(null), 3000);
        } finally {
            setLoadingId(null);
        }
    };

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const renderPlayerCard = (player, type) => {
        const isLoading = loadingId === player.id;

        return (
            <div key={player.id} className={`player-card ${type} ${player.checked_in ? 'checked-in' : ''}`}>
                <div className="player-info">
                    <span className="player-name">
                        {player.checked_in && '✓ '}
                        {player.name}
                    </span>
                    <span className="player-timestamp">{formatTimestamp(player.rsvp_timestamp)}</span>

                    <div className="player-badges">
                        {type === 'waitlist' && (
                            <span className="badge badge-waitlist">#{player.waitlist_position}</span>
                        )}
                        {player.paid && <span className="badge badge-paid">PAID</span>}
                        {player.checked_in && <span className="badge badge-checkin">CHECKED IN</span>}
                    </div>
                </div>

                {showActions && type !== 'out' && (
                    <div className="player-actions">
                        {/* Payment buttons */}
                        {!player.paid ? (
                            <button
                                className="btn btn-small btn-success"
                                onClick={() => handleAction('pay', player.id, player.name)}
                                disabled={isLoading}
                                title="Mark as paid"
                            >
                                💵 Pay
                            </button>
                        ) : (
                            <button
                                className="btn btn-small btn-outline"
                                onClick={() => handleAction('unpay', player.id, player.name)}
                                disabled={isLoading}
                                title="Mark as unpaid"
                            >
                                ↩️ Unpay
                            </button>
                        )}

                        {/* Check-in buttons (only for confirmed players) */}
                        {type === 'confirmed' && !player.checked_in && (
                            <button
                                className="btn btn-small btn-primary"
                                onClick={() => handleAction('checkin', player.id, player.name)}
                                disabled={isLoading || !player.paid}
                                title={player.paid ? 'Check in' : 'Must pay first'}
                            >
                                📋 Check In
                            </button>
                        )}

                        {type === 'confirmed' && player.checked_in && (
                            <button
                                className="btn btn-small btn-outline"
                                onClick={() => handleAction('undo-checkin', player.id, player.name)}
                                disabled={isLoading}
                                title="Undo check-in"
                            >
                                ↩️ Undo
                            </button>
                        )}

                        {/* Delete button */}
                        <button
                            className="btn btn-small btn-danger"
                            onClick={() => handleAction('delete', player.id, player.name)}
                            disabled={isLoading}
                            title="Remove player"
                        >
                            🗑️
                        </button>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="player-list">
            {error && (
                <div className="message error">
                    ✗ {error}
                </div>
            )}

            {/* Confirmed Players */}
            <div className="player-section">
                <h3 className="section-title confirmed">
                    ✅ Confirmed ({players.total_confirmed}/22)
                    <span className="spots-info">
                        {players.spots_available > 0
                            ? `${players.spots_available} spots left`
                            : 'FULL'}
                    </span>
                </h3>

                {players.confirmed.length === 0 ? (
                    <p className="empty-message">No confirmed players yet</p>
                ) : (
                    <div className="player-cards">
                        {players.confirmed.map((player, index) => (
                            <div key={player.id} className="player-row">
                                <span className="player-number">{index + 1}</span>
                                {renderPlayerCard(player, 'confirmed')}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Waitlist */}
            {players.waitlist.length > 0 && (
                <div className="player-section">
                    <h3 className="section-title waitlist">
                        ⏳ Waitlist ({players.total_waitlist})
                    </h3>
                    <div className="player-cards">
                        {players.waitlist.map(player => renderPlayerCard(player, 'waitlist'))}
                    </div>
                </div>
            )}

            {/* Out Players */}
            {players.out.length > 0 && (
                <div className="player-section">
                    <h3 className="section-title out">
                        ❌ Out ({players.out.length})
                    </h3>
                    <div className="player-cards collapsed">
                        {players.out.map(player => renderPlayerCard(player, 'out'))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default PlayerList;
