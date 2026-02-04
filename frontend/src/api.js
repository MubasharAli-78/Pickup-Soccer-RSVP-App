/**
 * API Service for communicating with the FastAPI backend.
 * All business logic is on the backend - this is just a thin wrapper.
 */

import axios from 'axios';

// Backend API base URL
const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ============== Player API ==============

/**
 * Get all players categorized by status
 * @returns {Promise<{confirmed: [], waitlist: [], out: [], total_confirmed: number, total_waitlist: number, spots_available: number}>}
 */
export const getPlayers = async () => {
    const response = await api.get('/players');
    return response.data;
};

/**
 * Get a single player by ID
 * @param {number} playerId 
 * @returns {Promise<Object>}
 */
export const getPlayer = async (playerId) => {
    const response = await api.get(`/players/${playerId}`);
    return response.data;
};

// ============== RSVP API ==============

/**
 * RSVP a player IN or OUT
 * @param {string} name - Player name
 * @param {string} status - "IN" or "OUT"
 * @returns {Promise<{success: boolean, message: string, player: Object}>}
 */
export const rsvpPlayer = async (name, status) => {
    const response = await api.post('/players/rsvp', { name, status });
    return response.data;
};

// ============== Payment API ==============

/**
 * Mark a player as paid or unpaid
 * @param {number} playerId 
 * @param {boolean} paid 
 * @returns {Promise<{success: boolean, message: string, player: Object}>}
 */
export const markPlayerPaid = async (playerId, paid) => {
    const response = await api.put(`/players/${playerId}/pay`, { paid });
    return response.data;
};

// ============== Check-in API ==============

/**
 * Check in a player on game day
 * @param {number} playerId 
 * @returns {Promise<{success: boolean, message: string, player: Object}>}
 */
export const checkInPlayer = async (playerId) => {
    const response = await api.put(`/players/${playerId}/checkin`);
    return response.data;
};

/**
 * Undo a player's check-in
 * @param {number} playerId 
 * @returns {Promise<{success: boolean, message: string, player: Object}>}
 */
export const undoCheckIn = async (playerId) => {
    const response = await api.put(`/players/${playerId}/undo-checkin`);
    return response.data;
};

/**
 * Get check-in statistics
 * @returns {Promise<{total_confirmed: number, total_paid: number, total_checked_in: number}>}
 */
export const getCheckInStats = async () => {
    const response = await api.get('/checkin/stats');
    return response.data;
};

// ============== Export API ==============

/**
 * Export players to CSV and trigger download
 */
export const exportToCSV = async () => {
    const response = await api.get('/export/csv', {
        responseType: 'blob',
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;

    // Get filename from headers or generate one
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'rsvp_export.csv';
    if (contentDisposition) {
        const match = contentDisposition.match(/filename=(.+)/);
        if (match) {
            filename = match[1];
        }
    }

    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
};

// ============== Admin API ==============

/**
 * Delete a player
 * @param {number} playerId 
 * @returns {Promise<{success: boolean, message: string}>}
 */
export const deletePlayer = async (playerId) => {
    const response = await api.delete(`/players/${playerId}`);
    return response.data;
};

/**
 * Reset all player data
 * @returns {Promise<{success: boolean, message: string}>}
 */
export const resetAllData = async () => {
    const response = await api.post('/admin/reset');
    return response.data;
};

export default api;
