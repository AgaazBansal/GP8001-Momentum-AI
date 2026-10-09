import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import App from './App';
jest.mock('axios', () => ({ get: jest.fn(), post: jest.fn() }));

beforeEach(() => {
    axios.get.mockResolvedValue({ data: { mode: 'demo', audio_enabled: false, notion_enabled: false } });
});

test('demo transcript workflow works without credentials', async () => {
    axios.post.mockResolvedValueOnce({ data: {
        overall_sentiment: 'Not assessed (demo)', topics: ['Transcript preview'],
        discussion_points: [{ id: 1, topic: 'Transcript excerpt 1', summary: 'Priya will prepare slides.' }],
        action_items: [], transcript: 'Priya will prepare slides.'
    }});
    render(<App />);
    await screen.findByText(/Demo mode:/);
    expect(screen.getByRole('button', { name: 'Generate Minutes' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Load sample transcript' }));
    fireEvent.click(screen.getByRole('button', { name: 'Process Transcript' }));
    await screen.findByText('Meeting Minutes Draft');
    expect(axios.post).toHaveBeenCalledWith(expect.stringContaining('/process-transcript'), expect.objectContaining({ transcript: expect.stringContaining('Priya') }));
    expect(screen.getByText('Priya will prepare slides.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Confirm & Export to Notion' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'New Meeting' }));
    await waitFor(() => expect(screen.getByText('Process a New Meeting')).toBeInTheDocument());
});
