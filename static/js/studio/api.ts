/**
 * API client — re-exports generated client functions.
 *
 * The custom Orval mutator (custom-instance.ts) auto-extracts .data,
 * so every function returns the payload directly. No Proxy needed.
 *
 * Import from here:
 *   import { client as api, chunkAudioUrl, fullEpisodeAudioUrl } from './api.ts';
 */

import { getOpenVoxAPI } from './client.ts';

export const client = getOpenVoxAPI();

export const chunkAudioUrl = (episodeId: string, chunkIndex: number): string =>
  `/api/studio/episodes/${episodeId}/audio/${chunkIndex}`;

export const fullEpisodeAudioUrl = (episodeId: string): string =>
  `/api/studio/episodes/${episodeId}/audio/full`;

export const sourceCoverUrl = (sourceId: string): string =>
  `/api/studio/sources/${sourceId}/cover`;
